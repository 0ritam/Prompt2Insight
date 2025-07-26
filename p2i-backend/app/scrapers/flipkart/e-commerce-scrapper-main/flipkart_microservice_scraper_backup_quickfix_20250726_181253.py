"""
Optimized Flipkart Scraper for Microservice
- Resilient scraping using Selenium and undetected-chromedriver
- Structured for API integration
- Clean implementation without duplicated code
- Python 3.12+ compatible
"""

import json
import time
import re
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass

# Handle distutils compatibility for Python 3.12+
try:
    import undetected_chromedriver as uc
except ImportError as e:
    if "distutils" in str(e):
        print("⚠️  undetected-chromedriver has distutils compatibility issues")
        print("   Falling back to regular selenium ChromeDriver")
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        uc = None
    else:
        raise e

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

@dataclass
class ProductData:
    """Product data structure"""
    title: str
    price: str
    rating: str
    url: str
    image: str
    in_stock: str

class FlipkartScraper:
    def __init__(self, headless: bool = True, max_products: int = 5):
        """Initialize scraper with a Selenium WebDriver"""
        self.max_products = max_products
        self.config = self.load_config()
        self.driver = None
        self._init_driver(headless)

    def _init_driver(self, headless: bool):
        """Initialize the Chrome driver with optimal settings"""
        if uc is not None:
            # Use undetected-chromedriver if available
            options = uc.ChromeOptions()
            if headless:
                options.add_argument('--headless')
            
            # Add arguments to make the browser appear more human
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            try:
                self.driver = uc.Chrome(options=options)
                print("✅ Chrome driver initialized with undetected-chromedriver")
            except Exception as e:
                print(f"❌ Failed to initialize undetected Chrome driver: {e}")
                raise
        else:
            # Fallback to regular selenium
            print("📌 Using regular selenium ChromeDriver as fallback")
            options = Options()
            if headless:
                options.add_argument('--headless')
            
            # Add arguments to make the browser appear more human
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                print("✅ Chrome driver initialized with regular selenium")
            except Exception as e:
                print(f"❌ Failed to initialize Chrome driver: {e}")
                raise

    def load_config(self):
        """Load scraper configuration"""
        try:
            with open("scraper_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration if file is not found
            return {
                "selectors": {
                    "product_container": "[data-id], ._1AtVbE, ._4rR01T, ._2kHMtA, ._13oc-S",
                    "title": "._4rR01T, .s1Q9rs, .B_NuCI",
                    "price": "._30jeq3, ._1_WHN1",
                    "rating": "._3LWZlK",
                    "url": "a",
                    "image": "img"
                },
                "search_url": "https://www.flipkart.com/search?q={query}"
            }

    def search_products(self, query: str) -> List[Dict]:
        """Main method to search and scrape products"""
        if not self.driver:
            raise Exception("Driver not initialized")
            
        products = []
        try:
            # Build search URL
            search_url = self.config["search_url"].format(query=query.replace(' ', '+'))
            print(f"🔍 Navigating to: {search_url}")
            
            self.driver.get(search_url)
            
            # Wait for page to load
            self._wait_for_page_load()
            
            # Get product elements
            elements = self._get_product_elements()
            
            if not elements:
                print("❌ No product elements found")
                return products
                
            print(f"✅ Found {len(elements)} potential product elements")
            
            # Extract data from each element
            for i, element in enumerate(elements[:self.max_products]):
                try:
                    product_data = self._extract_product_data(element)
                    if self._is_valid_product(product_data):
                        products.append({
                            "title": product_data.title,
                            "price": product_data.price,
                            "rating": product_data.rating,
                            "url": product_data.url,
                            "image": product_data.image,
                            "in_stock": product_data.in_stock,
                            "method": "selenium_search"
                        })
                        print(f"   ✅ Product {i+1}: {product_data.title[:50]}...")
                except Exception as e:
                    print(f"   ❌ Failed to extract product {i+1}: {e}")
                    continue

        except TimeoutException:
            print("❌ Timed out waiting for product page to load")
        except Exception as e:
            print(f"❌ An error occurred during scraping: {e}")

        return products

    def _wait_for_page_load(self):
        """Wait for the page to load properly"""
        wait = WebDriverWait(self.driver, 20)
        product_container_selector = self.config["selectors"]["product_container"]
        
        # Wait for at least one product container to appear
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, product_container_selector)))
        
        # Scroll to load more products
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(2)

    def _get_product_elements(self):
        """Find all product elements on the page"""
        product_container_selector = self.config["selectors"]["product_container"]
        return self.driver.find_elements(By.CSS_SELECTOR, product_container_selector)

    def _extract_product_data(self, element) -> Optional[ProductData]:
        """Extract product data from a Selenium WebElement"""
        title = self._extract_title(element)
        price = self._extract_price(element)
        rating = self._extract_rating(element)
        url = self._extract_url(element)
        image = self._extract_image(element)
        
        return ProductData(
            title=title,
            price=price,
            rating=rating,
            url=url,
            image=image,
            in_stock="In Stock"  # Assume in stock if visible on search
        )

    def _extract_title(self, element) -> str:
        """Extract product title from element"""
        title_selectors = self.config["selectors"]["title"].split(", ")
        for selector in title_selectors:
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, selector.strip())
                title = title_elem.text.strip()
                if title and len(title) > 3:
                    return title
            except NoSuchElementException:
                continue
        return "N/A"

    def _extract_price(self, element) -> str:
        """Extract product price from element"""
        price_selectors = self.config["selectors"]["price"].split(", ")
        for selector in price_selectors:
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, selector.strip())
                price = price_elem.text.strip()
                if price and '₹' in price:
                    return price
            except NoSuchElementException:
                continue
        return "N/A"

    def _extract_rating(self, element) -> str:
        """Extract product rating from element"""
        rating_selectors = self.config["selectors"]["rating"].split(", ")
        for selector in rating_selectors:
            try:
                rating_elem = element.find_element(By.CSS_SELECTOR, selector.strip())
                rating = rating_elem.text.strip()
                if rating and re.match(r'\d+\.?\d*', rating):
                    return rating
            except NoSuchElementException:
                continue
        return "N/A"

    def _extract_url(self, element) -> str:
        """Extract product URL from element"""
        try:
            link_elem = element.find_element(By.TAG_NAME, 'a')
            href = link_elem.get_attribute('href')
            if href:
                if href.startswith('/'):
                    return f"https://www.flipkart.com{href}"
                return href
        except NoSuchElementException:
            pass
        return "N/A"

    def _extract_image(self, element) -> str:
        """Extract product image from element"""
        try:
            img_elem = element.find_element(By.TAG_NAME, 'img')
            src = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')
            if src:
                if src.startswith('//'):
                    return f"https:{src}"
                elif src.startswith('/'):
                    return f"https://www.flipkart.com{src}"
                return src
        except NoSuchElementException:
            pass
        return ""

    def _is_valid_product(self, product_data: ProductData) -> bool:
        """Check if the extracted product data is valid"""
        return (
            product_data.title != "N/A" and
            len(product_data.title) > 5 and
            product_data.price != "N/A" and
            '₹' in product_data.price
        )

    def scrape_for_microservice(self, query: str, filters: Dict = None) -> Dict:
        """Microservice-ready method using Selenium"""
        start_time = time.time()
        
        try:
            products = self.search_products(query)
            
            if filters:
                products = self._apply_filters(products, filters)

            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "query": query,
                "products_found": len(products),
                "execution_time": round(execution_time, 2),
                "products": products,
                "timestamp": int(time.time()),
                "scraper_method": "selenium_undetected_chrome"
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "execution_time": round(execution_time, 2),
                "products_found": 0,
                "products": [],
                "timestamp": int(time.time())
            }
            
    def _apply_filters(self, products: List[Dict], filters: Dict) -> List[Dict]:
        """Apply price and other filters to the scraped products"""
        filtered = products
        
        # Price filters
        if "max_price" in filters:
            max_price = filters["max_price"]
            filtered = [p for p in filtered if self._extract_price_number(p["price"]) <= max_price]

        if "min_price" in filters:
            min_price = filters["min_price"]
            filtered = [p for p in filtered if self._extract_price_number(p["price"]) >= min_price]
        
        # Rating filter
        if "min_rating" in filters:
            min_rating = filters["min_rating"]
            filtered = [p for p in filtered if self._extract_rating_number(p["rating"]) >= min_rating]
        
        # Brand filter
        if "brand" in filters:
            brand = filters["brand"].lower()
            filtered = [p for p in filtered if brand in p["title"].lower()]
            
        return filtered

    def _extract_price_number(self, price_str: str) -> float:
        """Extract numeric price from price string"""
        try:
            # Remove currency symbols and commas, keep only digits and dots
            price_clean = re.sub(r'[^\d.]', '', price_str.replace(',', ''))
            return float(price_clean) if price_clean else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _extract_rating_number(self, rating_str: str) -> float:
        """Extract numeric rating from rating string"""
        try:
            # Extract first number from rating string
            match = re.search(r'(\d+\.?\d*)', str(rating_str))
            return float(match.group(1)) if match else 0.0
        except (ValueError, TypeError):
            return 0.0

    def close(self):
        """Close the Selenium WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Chrome driver closed successfully")
            except Exception as e:
                print(f"❌ Error closing driver: {e}")
            finally:
                self.driver = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

# Example usage for testing
if __name__ == "__main__":
    # Test the scraper
    with FlipkartScraper(headless=False, max_products=3) as scraper:
        try:
            result = scraper.scrape_for_microservice(
                query="laptops under 60000",
                filters={"max_price": 60000}
            )
            
            print("\n" + "="*50)
            print("SCRAPING RESULTS")
            print("="*50)
            print(f"Success: {result['success']}")
            print(f"Query: {result['query']}")
            print(f"Products Found: {result['products_found']}")
            print(f"Execution Time: {result['execution_time']}s")
            
            if result['products']:
                print("\nProducts:")
                for i, product in enumerate(result['products'], 1):
                    print(f"\n{i}. {product['title']}")
                    print(f"   Price: {product['price']}")
                    print(f"   Rating: {product['rating']}")
                    print(f"   URL: {product['url'][:50]}...")
            
        except Exception as e:
            print(f"Error during testing: {e}")
