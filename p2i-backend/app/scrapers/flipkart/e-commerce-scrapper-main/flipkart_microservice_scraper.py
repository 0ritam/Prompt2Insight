"""
Optimized Flipkart Scraper for Microservice
- Resilient scraping using Selenium and undetected-chromedriver
- Structured for API integration
- Clean implementation without duplicated code
- Python 3.12+ compatible with ChromeDriver fallback
"""

import json
import time
import re
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass

# Handle Chrome driver compatibility issues
try:
    import undetected_chromedriver as uc
except ImportError as e:
    if "distutils" in str(e):
        print("⚠️  undetected-chromedriver has distutils compatibility issues")
        print("   Falling back to regular selenium ChromeDriver")
        uc = None
    else:
        raise e

# Always import regular selenium as fallback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
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
        """Initialize the Chrome driver with optimal settings and fallback support"""
        # First try undetected-chromedriver if available
        if uc is not None:
            try:
                options = uc.ChromeOptions()
                if headless:
                    options.add_argument('--headless')
                
                # Add arguments to make the browser appear more human
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--start-maximized')
                options.add_argument('--disable-web-security')
                options.add_argument('--disable-features=VizDisplayCompositor')
                options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                
                self.driver = uc.Chrome(options=options)
                print("✅ Chrome driver initialized with undetected-chromedriver")
                return
                
            except Exception as e:
                print(f"⚠️  undetected-chromedriver failed: {e}")
                print("   Falling back to regular selenium...")
        
        # Fallback to regular selenium with webdriver-manager
        try:
            print("📌 Using regular selenium ChromeDriver with webdriver-manager")
            options = Options()
            if headless:
                options.add_argument('--headless')
            
            # Add arguments to make the browser appear more human
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Use webdriver-manager to automatically handle ChromeDriver version
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            print("✅ Chrome driver initialized with regular selenium + webdriver-manager")
            
        except Exception as e:
            print(f"❌ Failed to initialize Chrome driver with webdriver-manager: {e}")
            print("💡 Please ensure Chrome is installed and up to date")
            raise

    def load_config(self):
        """Load scraper configuration"""
        try:
            with open("scraper_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Updated configuration with current Flipkart selectors (as of 2025)
            return {
                "selectors": {
                    # Based on actual DOM inspection from Flipkart 2025
                    "product_container": "div[data-id^='COM'], div[data-id^='LAPTOP'], div[data-id^='COMPUTER'], div[data-id]",
                    "title": ".KzDlHZ, .WKTcLC, .IRpwTa, .s1Q9rs, ._4rR01T, .B_NuCI, .wjcEIp",
                    "price": ".Nx9bqj.CxhGGd, .Nx9bqj, ._30jeq3, ._1_WHN1, ._4b5DiR, .WMfIhL, ._1vC4OE",
                    "rating": "._3LWZlK, .XQDdHH, ._2_R_DZ, .Y1HWO0, ._13vcmD, ._3k-BhJ",
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
            
            # Debug: show what we found
            for i, element in enumerate(elements[:3]):  # Show first 3 elements
                try:
                    element_text = element.text[:100] if element.text else "No text"
                    data_id = element.get_attribute("data-id") or "No data-id"
                    print(f"   📋 Element {i+1}: data-id='{data_id}', text='{element_text}...'")
                except:
                    print(f"   📋 Element {i+1}: Could not get details")
            
            if len(elements) > 3:
                print(f"   ... and {len(elements) - 3} more elements")
            
            # Extract data from each element
            for i, element in enumerate(elements[:self.max_products]):
                try:
                    print(f"   🔍 Processing element {i+1}/{min(len(elements), self.max_products)}...")
                    product_data = self._extract_product_data(element)
                    print(f"   📝 Product {i+1} extracted: title='{product_data.title[:30] if len(product_data.title) > 30 else product_data.title}', price='{product_data.price}'")
                    
                    is_valid = self._is_valid_product(product_data)
                    print(f"   🔍 Validation result for product {i+1}: {is_valid}")
                    
                    if is_valid:
                        products.append({
                            "title": product_data.title,
                            "price": product_data.price,
                            "rating": product_data.rating,
                            "url": product_data.url,
                            "image": product_data.image,
                            "in_stock": product_data.in_stock,
                            "method": "selenium_search"
                        })
                        print(f"   ✅ Product {i+1} ADDED: {product_data.title[:50] if len(product_data.title) > 50 else product_data.title}")
                    else:
                        print(f"   ❌ Product {i+1} REJECTED by validation")
                except Exception as e:
                    print(f"   ❌ Failed to extract product {i+1}: {e}")
                    import traceback
                    traceback.print_exc()
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
        # Try multiple approaches to find product containers
        product_elements = []
        
        # Approach 1: Look for specific product container patterns
        selectors_to_try = [
            "div[data-id^='COM']",  # Product containers with COM prefix (computers)
            "div[data-id^='LAPTOP']",  # Direct laptop data-ids
            "div[data-id^='COMPUTER']",  # Computer data-ids
            "div[data-id]",  # Any element with data-id
            "div.cPHDOP.col-12-12[style*='padding']",
            "div._4ddWXP"
        ]
        
        for selector in selectors_to_try:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   🎯 Found {len(elements)} elements with selector: {selector}")
                    # Filter these elements
                    filtered = self._filter_product_elements(elements)
                    if filtered:
                        product_elements.extend(filtered)
                        break  # Use the first successful selector
            except Exception as e:
                print(f"   ❌ Selector {selector} failed: {e}")
                continue
        
        # If no specific selectors worked, try a broader approach
        if not product_elements:
            print("   🔄 Trying broader selector approach...")
            all_elements = self.driver.find_elements(By.CSS_SELECTOR, "div")
            product_elements = self._filter_product_elements(all_elements)
        
        print(f"   📦 Final result: {len(product_elements)} actual product elements")
        return product_elements[:10]  # Limit to avoid too many results

    def _filter_product_elements(self, elements):
        """Filter elements to get only actual product elements"""
        product_elements = []
        for element in elements:
            try:
                element_text = element.text.lower()
                
                # Must have price indicator
                has_price_indicator = '₹' in element_text
                if not has_price_indicator:
                    continue
                
                # Look for specific laptop/computer product terms
                laptop_terms = ['laptop', 'intel', 'amd', 'ryzen', 'core i', 'processor', 'gb ram', 'ssd', 'hdd', 
                              'windows', 'display', 'inch', 'screen']
                brand_terms = ['asus', 'hp', 'dell', 'lenovo', 'acer', 'infinix', 'macbook', 'apple', 'msi', 
                             'vivobook', 'ideapad', 'thinkpad', 'zerobook']
                
                has_laptop_terms = any(term in element_text for term in laptop_terms)
                has_brand_terms = any(brand in element_text for brand in brand_terms)
                
                # Must have either laptop terms or brand terms
                if not (has_laptop_terms or has_brand_terms):
                    continue
                
                # Strong exclusions for non-product elements
                exclude_terms = ['reviews for popular', 'sponsored', 'advertisement', 'compare products',
                               'sort by', 'filter', 'home', 'categories', 'show more', 'view all']
                
                is_excluded = any(term in element_text for term in exclude_terms)
                if is_excluded:
                    continue
                
                # Additional checks for product validity
                has_sufficient_content = len(element_text) > 40
                has_links = len(element.find_elements(By.TAG_NAME, "a")) > 0
                
                # Check if it has data-id (strong indicator of product)
                data_id = element.get_attribute("data-id")
                has_product_data_id = data_id and (data_id.startswith('COM') or 'LAPTOP' in data_id or 'COMPUTER' in data_id)
                
                if (has_sufficient_content and has_links) or has_product_data_id:
                    product_elements.append(element)
                    
            except Exception:
                continue
                
        return product_elements

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
        # Try current selectors first
        title_selectors = self.config["selectors"]["title"].split(", ")
        for selector in title_selectors:
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, selector.strip())
                title = title_elem.text.strip()
                if title and len(title) > 3:
                    print(f"         📝 Found title with selector '{selector}': {title[:50]}...")
                    return title
            except NoSuchElementException:
                continue
        
        # Try additional common Flipkart selectors
        additional_selectors = [
            "div._4rR01T",  # Common product title class
            "a.IRpwTa",     # Link with product title
            "a.s1Q9rs",     # Another title link class
            "div.col-7-12 a",  # Title in product column
            "h3 a",         # H3 with link
            "h4 a",         # H4 with link
            ".wjcEIp",      # Another title class
            "div[data-id] a", # Any link in product container
        ]
        
        for selector in additional_selectors:
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, selector)
                title = title_elem.text.strip()
                if title and len(title) > 5:
                    print(f"         📝 Found title with additional selector '{selector}': {title[:50]}...")
                    return title
            except NoSuchElementException:
                continue
        
        # Fallback: try to get title from any text content or link title attribute
        try:
            # Try getting from link title attribute first
            links = element.find_elements(By.TAG_NAME, "a")
            for link in links:
                title_attr = link.get_attribute("title")
                if title_attr and len(title_attr) > 5:
                    print(f"         📝 Found title from link attribute: {title_attr[:50]}...")
                    return title_attr.strip()
                
                # Try link text
                link_text = link.text.strip()
                if link_text and len(link_text) > 5 and not '₹' in link_text:
                    print(f"         📝 Found title from link text: {link_text[:50]}...")
                    return link_text
        except:
            pass
            
        # Final fallback: get any meaningful text
        try:
            text_content = element.text.strip()
            if text_content and len(text_content) > 10:
                # Take first line that looks like a title
                lines = text_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if len(line) > 8 and not '₹' in line and not line.isdigit() and not line.lower() in ['free delivery', 'sold by', 'flipkart assured']:
                        print(f"         📝 Found title from text content: {line[:50]}...")
                        return line
        except:
            pass
            
        print(f"         ❌ No title found for element")
        return "N/A"

    def _extract_price(self, element) -> str:
        """Extract product price from element"""
        # Try current selectors first
        price_selectors = self.config["selectors"]["price"].split(", ")
        for selector in price_selectors:
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, selector.strip())
                price = price_elem.text.strip()
                if price and '₹' in price:
                    print(f"         💰 Found price with selector '{selector}': {price}")
                    return price
            except NoSuchElementException:
                continue
        
        # Try additional common price selectors
        additional_price_selectors = [
            "div._30jeq3",    # Common price class
            "div._1_WHN1",    # Another price class
            "span.Nx9bqj",    # Price span
            "div.WMfIhL",     # Price div
            "span._1vC4OE",   # Another price span
            "div[data-id] span", # Any span in product container
            "div[data-id] div", # Any div in product container
        ]
        
        for selector in additional_price_selectors:
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, selector)
                price = price_elem.text.strip()
                if price and '₹' in price:
                    print(f"         💰 Found price with additional selector '{selector}': {price}")
                    return price
            except NoSuchElementException:
                continue
        
        # Fallback: search for any text containing ₹
        try:
            text_content = element.text
            if '₹' in text_content:
                # Extract price using regex
                import re
                price_patterns = [
                    r'₹[\d,]+',           # Basic rupee pattern
                    r'₹\s*[\d,]+',        # With optional space
                    r'₹[\d,]+\.?\d*',     # With optional decimals
                ]
                
                for pattern in price_patterns:
                    price_match = re.search(pattern, text_content)
                    if price_match:
                        price = price_match.group(0)
                        print(f"         💰 Found price with regex '{pattern}': {price}")
                        return price
        except:
            pass
            
        print(f"         ❌ No price found for element")
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
        has_title = product_data.title != "N/A" and len(product_data.title) > 3
        has_price = product_data.price != "N/A"
        
        # Basic validation - just ensure we have meaningful title and price
        is_real_product = True
        
        # Only exclude obvious non-products
        exclude_exact_terms = ['computers', 'laptops category', 'mobiles category', 'electronics category', 
                              'accessories category', 'home category', 'furniture category', 'sort by', 
                              'filter', 'show more', 'view all', 'sponsored']
        if product_data.title.lower().strip() in exclude_exact_terms:
            is_real_product = False
        
        # Exclude very short titles that are likely navigation elements
        if has_title and len(product_data.title) < 8:
            is_real_product = False
            
        # Check for obvious navigation/filter elements
        if has_title:
            title_lower = product_data.title.lower()
            navigation_keywords = ['sort by', 'filter by', 'show more', 'view all', 'home', 'categories']
            if any(keyword in title_lower for keyword in navigation_keywords):
                is_real_product = False
            
        print(f"      🔍 Validation: title='{product_data.title}' (valid: {has_title}), price='{product_data.price}' (valid: {has_price}), real_product: {is_real_product}")
        
        return has_title and has_price and is_real_product

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
                "scraper_method": "selenium_webdriver_manager_fallback"
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
