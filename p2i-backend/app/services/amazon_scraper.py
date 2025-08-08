import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import json
import re
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AmazonScraper:
    """
    Amazon scraper that automatically generates target URLs from parsed prompt JSON
    and returns scraped data in JSON format.
    """
    
    def __init__(self):
        """Initialize the Amazon scraper with scrape.do token from environment variables."""
        self.token = os.getenv("SCRAPEDO_API_KEY")
        if not self.token:
            raise ValueError("SCRAPEDO_API_KEY not found in environment variables")
        self.max_products = 5  # Maximum products to scrape from first page
        
    def _build_search_query(self, products: List[str], filters: Dict[str, Any], attributes: List[str]) -> str:
        """
        Build Amazon search query from parsed prompt JSON.
        
        Args:
            products: List of product types (e.g., ["laptops"])
            filters: Dictionary containing price, brand filters
            attributes: List of additional attributes (e.g., ["gaming", "intel"])
            
        Returns:
            Formatted search query string
        """
        query_parts = []
        
        # Add product types
        if products:
            query_parts.extend(products)
        
        # Add price filter
        if filters and "price" in filters:
            price_filter = filters["price"]
            if "under" in price_filter.lower():
                # Extract price value and convert to number
                price_match = re.search(r'₹?(\d+)', price_filter)
                if price_match:
                    price_value = price_match.group(1)
                    query_parts.append(f"under {price_value}")
        
        # Add brand filter
        if filters and "brand" in filters and filters["brand"] != "any":
            query_parts.append(filters["brand"])
        
        # Add attributes
        if attributes:
            query_parts.extend(attributes)
        
        # Join all parts with spaces
        search_query = " ".join(query_parts)
        return search_query
    
    def _build_amazon_url(self, search_query: str) -> str:
        """
        Build Amazon.in search URL from search query.
        
        Args:
            search_query: The search query string
            
        Returns:
            Amazon.in search URL
        """
        # Encode the search query for URL
        encoded_query = urllib.parse.quote(search_query)
        
        # Build Amazon.in search URL
        base_url = "https://www.amazon.in/s"
        params = {
            "k": search_query,
            "ref": "nb_sb_noss"
        }
        
        # Convert params to URL query string
        query_string = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
        url = f"{base_url}?{query_string}"
        
        return url
    
    def _extract_product_data(self, product_element) -> Optional[Dict[str, Any]]:
        """
        Extract product data from a single product element.
        
        Args:
            product_element: BeautifulSoup element representing a product
            
        Returns:
            Dictionary containing product data or None if extraction fails
        """
        try:
            # Extract product name
            name_element = product_element.select_one("h2 span")
            if not name_element:
                name_element = product_element.select_one("h2 a span")
            if not name_element:
                name_element = product_element.select_one(".a-size-medium")
            
            if not name_element:
                return None
            
            name = name_element.text.strip()
            if not name:
                return None
            
            # Extract price
            price = "Price not available"
            try:
                # Try multiple price selectors
                price_element = product_element.select_one("span.a-price-whole")
                if not price_element:
                    price_element = product_element.select_one("span.a-price")
                if not price_element:
                    price_element = product_element.select_one(".a-price .a-offscreen")
                
                if price_element:
                    price = price_element.text.strip()
                else:
                    # Try to extract from price range
                    price_text = str(product_element.select("span.a-price"))
                    if 'a-offscreen">' in price_text:
                        price = price_text.split('a-offscreen">')[1].split('</span>')[0]
            except Exception:
                pass
            
            # Extract link
            link = ""
            try:
                link_element = product_element.select_one(".a-link-normal")
                if link_element:
                    link = link_element.get("href")
                    if link and not link.startswith("http"):
                        link = "https://www.amazon.in" + link
            except Exception:
                pass
            
            # Extract image
            image = ""
            try:
                img_element = product_element.select_one("img")
                if img_element:
                    image = img_element.get("src")
                    if not image:
                        image = img_element.get("data-src")
            except Exception:
                pass
            
            # Extract rating using improved logic from provided code
            rating = "Rating not available"
            try:
                # Try multiple rating selectors
                rating_element = product_element.select_one("span[aria-label*='stars']")
                if not rating_element:
                    rating_element = product_element.select_one("span.a-icon-alt")
                if not rating_element:
                    rating_element = product_element.select_one("i.a-icon-star")
                if not rating_element:
                    rating_element = product_element.select_one("span[class*='star']")
                
                if rating_element:
                    rating_text = rating_element.get("aria-label", "") or rating_element.text.strip()
                    if "out of" in rating_text:
                        rating = rating_text.split(" out of")[0]
                    elif "stars" in rating_text:
                        rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                        if rating_match:
                            rating = rating_match.group(1) + " stars"
                    else:
                        rating = rating_text
            except Exception:
                pass
            
            return {
                "name": name,
                "price": price,
                "link": link,
                "image": image,
                "rating": rating
            }
            
        except Exception as e:
            print(f"Error extracting product data: {e}")
            return None
    
    def scrape_products(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to scrape Amazon products based on parsed prompt JSON.
        
        Args:
            prompt_data: Dictionary containing parsed prompt data with structure:
                {
                    "intent": "search",
                    "products": ["laptops"],
                    "filters": {
                        "price": "under ₹80000",
                        "brand": "any"
                    },
                    "attributes": ["gaming", "intel"],
                    "max_products_per_query": 5
                }
                
        Returns:
            Dictionary containing scraped products and metadata
        """
        try:
            # Extract data from prompt
            products = prompt_data.get("products", [])
            filters = prompt_data.get("filters", {})
            attributes = prompt_data.get("attributes", [])
            max_products = prompt_data.get("max_products_per_query", 5)
            
            # Build search query
            search_query = self._build_search_query(products, filters, attributes)
            print(f"🔍 Built search query: {search_query}")
            
            # Build Amazon URL
            amazon_url = self._build_amazon_url(search_query)
            print(f"🌐 Target URL: {amazon_url}")
            
            # Scrape using scrape.do
            target_url = urllib.parse.quote(amazon_url)
            api_url = f"https://api.scrape.do/?token={self.token}&url={target_url}"
            
            print(f"📡 Fetching data from Amazon...")
            response = requests.get(api_url, timeout=30)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to fetch data. Status: {response.status_code}",
                    "search_query": search_query,
                    "target_url": amazon_url
                }
            
            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find product elements
            product_elements = soup.find_all("div", {"class": "s-result-item"})
            print(f"📦 Found {len(product_elements)} product elements")
            
            # Extract product data
            scraped_products = []
            products_found = 0
            
            for product_element in product_elements:
                if products_found >= max_products:
                    break
                    
                product_data = self._extract_product_data(product_element)
                if product_data:
                    scraped_products.append(product_data)
                    products_found += 1
                    print(f"✅ Extracted product {products_found}: {product_data['name'][:50]}...")
            
            # Prepare response with simple timestamp
            result = {
                "success": True,
                "search_query": search_query,
                "target_url": amazon_url,
                "products_found": len(scraped_products),
                "max_products_requested": max_products,
                "products": scraped_products,
                "metadata": {
                    "scraper": "Amazon",
                    "source": "amazon.in",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            print(f"🎯 Scraping completed! Found {len(scraped_products)} products")
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Scraping failed: {str(e)}",
                "search_query": search_query if 'search_query' in locals() else "Unknown",
                "target_url": amazon_url if 'amazon_url' in locals() else "Unknown"
            }

# Example usage and testing
if __name__ == "__main__":
    scraper = AmazonScraper()
    
    # Test with sample prompt data
    test_prompt = {
        "intent": "search",
        "products": ["laptops"],
        "filters": {
            "price": "under ₹50000",
            "brand": "any"
        },
        "attributes": ["gaming", "intel"],
        "max_products_per_query": 5
    }
    
    result = scraper.scrape_products(test_prompt)
    print(json.dumps(result, indent=2, ensure_ascii=False)) 