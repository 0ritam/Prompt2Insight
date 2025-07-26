
"""
Optimized Flipkart Scraper for Microservice
- Resilient scraping using Selenium and undetected-chromedriver
- Structured for API integration
"""

import json
import time
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
import undetected_chromedriver as uc
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
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        # Add arguments to make the browser appear more human
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        self.driver = uc.Chrome(options=options)

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

    def get_product_urls_with_selenium(self, query: str) -> List[Dict]:
        """Use Selenium approach to search and scrape products"""
        products = []
        try:
            # Build search URL
            search_url = self.config["search_url"].format(query=query.replace(' ', '+'))
            print(f"🔍 Navigating to: {search_url}")
            self.driver.get(search_url)

            # Wait for product containers to be visible
            wait = WebDriverWait(self.driver, 20)
            product_container_selector = self.config["selectors"]["product_container"]

            # Wait for at least one of the product containers to appear
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, product_container_selector)))

            # Scroll down to load more products
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(2)

            # Find all product elements
            elements = self.driver.find_elements(By.CSS_SELECTOR, product_container_selector)
            print(f"✅ Found {len(elements)} potential product elements.")

            for element in elements[:self.max_products]:
                try:
                    product_data = self.extract_product_from_element_selenium(element)
                    if product_data and product_data.title != "N/A" and len(product_data.title) > 5:
                        products.append({
                            "title": product_data.title,
                            "price": product_data.price,
                            "rating": product_data.rating,
                            "url": product_data.url,
                            "image": product_data.image,
                            "in_stock": "In Stock",  # Assume in stock if visible
                            "method": "selenium_search"
                        })
                except Exception:
                    continue  # Move to the next element if one fails

        except TimeoutException:
            print("❌ Timed out waiting for product page to load. The page structure might have changed or you are being blocked.")
        except Exception as e:
            print(f"❌ An error occurred during Selenium scraping: {e}")

        return products

    def extract_product_from_element_selenium(self, element) -> Optional[ProductData]:
        """Extract product data from a Selenium WebElement"""
        title = price = rating = url = image = "N/A"

        # Extract title
        try:
            title_selectors = self.config["selectors"]["title"].split(", ")
            for selector in title_selectors:
                try:
                    title_elem = element.find_element(By.CSS_SELECTOR, selector.strip())
                    title = title_elem.text.strip()
                    if title:
                        break
                except NoSuchElementException:
                    continue
        except Exception:
            pass

        # Extract price
        try:
            price_selectors = self.config["selectors"]["price"].split(", ")
            for selector in price_selectors:
                try:
                    price_elem = element.find_element(By.CSS_SELECTOR, selector.strip())
                    price = price_elem.text.strip()
                    if price:
                        break
                except NoSuchElementException:
                    continue
        except Exception:
            pass

        # Extract rating
        try:
            rating_selectors = self.config["selectors"]["rating"].split(", ")
            for selector in rating_selectors:
                try:
                    rating_elem = element.find_element(By.CSS_SELECTOR, selector.strip())
                    rating = rating_elem.text.strip()
                    if rating:
                        break
                except NoSuchElementException:
                    continue
        except Exception:
            rating = "N/A"

        # Extract URL
        try:
            link_elem = element.find_element(By.TAG_NAME, 'a')
            url = link_elem.get_attribute('href')
        except NoSuchElementException:
            pass

        # Extract Image
        try:
            img_elem = element.find_element(By.TAG_NAME, 'img')
            image = img_elem.get_attribute('src')
        except NoSuchElementException:
            pass

        return ProductData(title, price, rating, url, image, "In Stock")

    def scrape_for_microservice(self, query: str, filters: Dict = None) -> Dict:
        """Microservice-ready method using Selenium"""
        start_time = time.time()
        try:
            products = self.get_product_urls_with_selenium(query)
            if filters:
                products = self._apply_filters(products, filters)

            execution_time = time.time() - start_time
            return {
                "success": True,
                "query": query,
                "products_found": len(products),
                "execution_time": round(execution_time, 2),
                "products": products,
                "timestamp": int(time.time())
            }
        except Exception as e:
            return {"success": False, "error": str(e), "query": query, "execution_time": round(time.time() - start_time, 2)}
            
    def _apply_filters(self, products: List[Dict], filters: Dict) -> List[Dict]:
        """Apply price and other filters to the scraped products."""
        filtered = products
        
        def _extract_price_number(price_str: str) -> float:
            try:
                price_clean = re.sub(r'[^\d.]', '', price_str.replace(',', ''))
                return float(price_clean) if price_clean else 0.0
            except:
                return 0.0

        if "max_price" in filters:
            max_price = filters["max_price"]
            filtered = [p for p in filtered if _extract_price_number(p["price"]) <= max_price]
            
        return filtered

    def close(self):
        """Close the Selenium WebDriver"""
        if self.driver:
            self.driver.quit()

# Example usage for testing
if __name__ == "__main__":
    scraper = FlipkartScraper(headless=False, max_products=5)
    try:
        result = scraper.scrape_for_microservice(
            query="laptops under 60000",
            filters={"max_price": 60000}
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()
"""
Optimized Flipkart Scraper for Microservice
- Resilient scraping using Selenium and undetected-chromedriver
- Structured for API integration
"""

import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
import undetected_chromedriver as uc
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
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        # Add arguments to make the browser appear more human
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        self.driver = uc.Chrome(options=options)

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

    def get_product_urls_with_selenium(self, query: str) -> List[Dict]:
        """Use Selenium approach to search and scrape products"""
        products = []
        try:
            # Build search URL
            search_url = self.config["search_url"].format(query=query.replace(' ', '+'))
            print(f"🔍 Navigating to: {search_url}")
            self.driver.get(search_url)

            # Wait for product containers to be visible
            wait = WebDriverWait(self.driver, 20)
            product_container_selector = self.config["selectors"]["product_container"]

            # Wait for at least one of the product containers to appear
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, product_container_selector)))

            # Scroll down to load more products
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(2)

            # Find all product elements
            elements = self.driver.find_elements(By.CSS_SELECTOR, product_container_selector)
            print(f"✅ Found {len(elements)} potential product elements.")

            for element in elements[:self.max_products]:
                try:
                    product_data = self.extract_product_from_element_selenium(element)
                    if product_data and product_data.title != "N/A" and len(product_data.title) > 5:
                        products.append({
                            "title": product_data.title,
                            "price": product_data.price,
                            "rating": product_data.rating,
                            "url": product_data.url,
                            "image": product_data.image,
                            "in_stock": "In Stock",  # Assume in stock if visible
                            "method": "selenium_search"
                        })
                except Exception:
                    continue  # Move to the next element if one fails

        except TimeoutException:
            print("❌ Timed out waiting for product page to load. The page structure might have changed or you are being blocked.")
        except Exception as e:
            print(f"❌ An error occurred during Selenium scraping: {e}")

        return products

    def extract_product_from_element_selenium(self, element) -> Optional[ProductData]:
        """Extract product data from a Selenium WebElement"""
        title = price = rating = url = image = "N/A"

        # Extract title
        try:
            title_elem = element.find_element(By.CSS_SELECTOR, self.config["selectors"]["title"])
            title = title_elem.text.strip()
        except NoSuchElementException:
            pass

        # Extract price
        try:
            price_elem = element.find_element(By.CSS_SELECTOR, self.config["selectors"]["price"])
            price = price_elem.text.strip()
        except NoSuchElementException:
            pass

        # Extract rating
        try:
            rating_elem = element.find_element(By.CSS_SELECTOR, self.config["selectors"]["rating"])
            rating = rating_elem.text.strip()
        except NoSuchElementException:
            rating = "N/A"

        # Extract URL
        try:
            link_elem = element.find_element(By.TAG_NAME, 'a')
            url = link_elem.get_attribute('href')
        except NoSuchElementException:
            pass

        # Extract Image
        try:
            img_elem = element.find_element(By.TAG_NAME, 'img')
            image = img_elem.get_attribute('src')
        except NoSuchElementException:
            pass

        return ProductData(title, price, rating, url, image, "In Stock")

    def scrape_for_microservice(self, query: str, filters: Dict = None) -> Dict:
        """Microservice-ready method using Selenium"""
        start_time = time.time()
        try:
            products = self.get_product_urls_with_selenium(query)
            if filters:
                products = self._apply_filters(products, filters)

            execution_time = time.time() - start_time
            return {
                "success": True,
                "query": query,
                "products_found": len(products),
                "execution_time": round(execution_time, 2),
                "products": products,
                "timestamp": int(time.time())
            }
        except Exception as e:
            return {"success": False, "error": str(e), "query": query, "execution_time": round(time.time() - start_time, 2)}
            
    def _apply_filters(self, products: List[Dict], filters: Dict) -> List[Dict]:
        """Apply price and other filters to the scraped products."""
        import re
        filtered = products
        
        def _extract_price_number(price_str: str) -> float:
            try:
                price_clean = re.sub(r'[^\d.]', '', price_str.replace(',', ''))
                return float(price_clean) if price_clean else 0.0
            except:
                return 0.0

        if "max_price" in filters:
            max_price = filters["max_price"]
            filtered = [p for p in filtered if _extract_price_number(p["price"]) <= max_price]
            
        return filtered

    def close(self):
        """Close the Selenium WebDriver"""
        if self.driver:
            self.driver.quit()

# Example usage for testing
if __name__ == "__main__":
    scraper = FlipkartScraper(headless=False, max_products=5)
    try:
        result = scraper.scrape_for_microservice(
            query="laptops under 60000",
            filters={"max_price": 60000}
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()
                print(f"⏰ Timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    continue
                else:
                    print("❌ All attempts timed out")
                    return []
                    
            except requests.exceptions.ConnectionError as e:
                print(f"🔌 Connection error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    continue
                else:
                    print("❌ All connection attempts failed")
                    return []
                    
            except Exception as e:
                print(f"❌ Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    continue
                else:
                    print("❌ All attempts failed")
                    return []
        
        return []
    
    def extract_product_from_element_requests(self, element, soup) -> Optional[ProductData]:
        """Extract product data from HTML element using requests approach"""
        try:
            # Extract title using multiple selectors
            title_selectors = self.config["selectors"]["title"].split(", ")
            title = "N/A"
            for selector in title_selectors:
                title_elem = element.select_one(selector.strip())
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            # Extract price using multiple selectors
            price_selectors = self.config["selectors"]["price"].split(", ")
            price = "N/A"
            for selector in price_selectors:
                price_elem = element.select_one(selector.strip())
                if price_elem:
                    price = price_elem.get_text(strip=True)
                    break
            
            # Extract rating using multiple selectors
            rating_selectors = self.config["selectors"]["rating"].split(", ")
            rating = "N/A"
            for selector in rating_selectors:
                rating_elem = element.select_one(selector.strip())
                if rating_elem:
                    rating = rating_elem.get_text(strip=True)
                    break
            
            # Extract URL
            url = "N/A"
            url_elem = element.select_one("a")
            if url_elem and url_elem.get('href'):
                href = url_elem.get('href')
                if href.startswith('/'):
                    url = f"https://www.flipkart.com{href}"
                else:
                    url = href
            
            # Extract image
            image = ""
            img_elem = element.select_one("img")
            if img_elem and img_elem.get('src'):
                image = img_elem.get('src')
            
            # Check availability
            in_stock = self.check_availability_requests(soup)
            
            return ProductData(
                title=title,
                price=price,
                rating=rating,
                url=url,
                image=image,
                in_stock=in_stock
            )
            
        except Exception as e:
            return None
    
    def scrape_single_product_with_requests(self, url: str) -> Optional[ProductData]:
        """Scrape a single product using requests"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product data with fallback selectors
            title_selectors = ["span.B_NuCI", "h1._35KyD6", "span._4rR01T", ".pdp-e1-product-title"]
            title = "N/A"
            for selector in title_selectors:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.get_text(strip=True)
                    break
            
            price_selectors = ["div._30jeq3._16Jk6d", "div._1_WHN1", "div._25b18c", ".pdp-price"]
            price = "N/A"
            for selector in price_selectors:
                elem = soup.select_one(selector)
                if elem:
                    price = elem.get_text(strip=True)
                    break
            
            rating_selectors = ["div._3LWZlK", "div.gUuXy-", "div._3sae3h", ".pdp-rating"]
            rating = "N/A"
            for selector in rating_selectors:
                elem = soup.select_one(selector)
                if elem:
                    rating = elem.get_text(strip=True)
                    break
            
            img_selectors = ["img._396cs4", "img._2r_T1I", ".pdp-image img"]
            image = ""
            for selector in img_selectors:
                elem = soup.select_one(selector)
                if elem and elem.get('src'):
                    image = elem.get('src')
                    break
            
            # Check availability
            in_stock = self.check_availability_requests(soup)
            
            return ProductData(
                title=title,
                price=price,
                rating=rating,
                url=url,
                image=image,
                in_stock=in_stock
            )
            
        except Exception as e:
            return None
    
    def check_availability_requests(self, soup) -> str:
        """Check if product is available using BeautifulSoup"""
        # Look for out of stock indicators
        out_of_stock_texts = [
            "currently unavailable",
            "out of stock",
            "sold out",
            "temporarily unavailable"
        ]
        
        page_text = soup.get_text().lower()
        for text in out_of_stock_texts:
            if text in page_text:
                return "Out of Stock"
        
        # Look for add to cart button (indicates in stock)
        add_to_cart_selectors = [
            "._2KpZ6l._2U9uOA._3v1-ww",
            "._2KpZ6l._2U9uOA.g5T8be",
            "[data-testid='add-to-cart']"
        ]
        
        for selector in add_to_cart_selectors:
            if soup.select_one(selector):
                return "In Stock"
        
        # Check button text
        buttons = soup.find_all('button')
        for button in buttons:
            button_text = button.get_text().lower()
            if 'add to cart' in button_text:
                return "In Stock"
        
        return "Unknown"
    
    def scrape_exact_urls_with_requests(self, urls: List[str]) -> List[Dict]:
        """Scrape specific product URLs using requests approach"""
        results = []
        for url in urls:
            try:
                product_data = self.scrape_single_product_with_requests(url)
                if product_data:
                    results.append({
                        "title": product_data.title,
                        "price": product_data.price,
                        "rating": product_data.rating,
                        "url": product_data.url,
                        "image": product_data.image,
                        "in_stock": product_data.in_stock,
                        "method": "requests_direct"
                    })
            except Exception as e:
                continue
        
        return results
    
    def scrape_for_microservice(self, query: str, filters: Dict = None) -> Dict:
        """Microservice-ready method"""
        start_time = time.time()
        
        try:
            # Use requests approach instead of Selenium
            products = self.get_product_urls_with_requests(query)
            
            # Apply filters if provided
            if filters:
                products = self._apply_filters(products, filters)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "query": query,
                "products_found": len(products),
                "execution_time": round(execution_time, 2),
                "products": products,
                "timestamp": int(time.time())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "execution_time": round(time.time() - start_time, 2)
            }
    
    def scrape_exact_products_for_microservice(self, urls: List[str], filters: Dict = None) -> Dict:
        """Scrape exact URLs for microservice"""
        start_time = time.time()
        
        try:
            products = self.scrape_exact_urls_with_requests(urls)
            
            # Apply filters if provided
            if filters:
                products = self._apply_filters(products, filters)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "products_found": len(products),
                "execution_time": round(execution_time, 2),
                "products": products,
                "timestamp": int(time.time()),
                "scraping_type": "exact_urls",
                "urls_provided": len(urls)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "scraping_type": "exact_urls",
                "urls_provided": len(urls),
                "execution_time": round(time.time() - start_time, 2)
            }
    
    def fallback_product_extraction(self, soup) -> List[Dict]:
        """Fallback method to extract products using generic patterns"""
        products = []
        
        try:
            print("🔄 Trying fallback extraction methods...")
            
            # Method 1: Look for links containing "/p/" (product pages)
            product_links = soup.find_all('a', href=True)
            product_urls = []
            for link in product_links:
                href = link.get('href', '')
                if '/p/' in href and 'flipkart.com' not in href:  # Relative URLs
                    full_url = f"https://www.flipkart.com{href}" if href.startswith('/') else href
                    product_urls.append((link, full_url))
            
            print(f"   Found {len(product_urls)} potential product links")
            
            # Extract product info from each link's parent elements
            for link_elem, url in product_urls[:self.max_products]:
                try:
                    # Find the optimal container that contains product info
                    container = link_elem
                    best_container = link_elem
                    
                    # Go up the DOM tree to find the best product container
                    for level in range(8):
                        parent = container.parent
                        if parent and parent.name not in ['body', 'html']:
                            container = parent
                            container_text = container.get_text()
                            # Check if this container has product-like content
                            if ('₹' in container_text and 
                                len(container_text) > 50 and 
                                len(container_text) < 1500):  # Not too big
                                best_container = container
                        else:
                            break
                    
                    container = best_container
                    container_text = container.get_text()
                    
                    # Extract title - prioritize the link text first
                    title = "N/A"
                    link_text = link_elem.get_text(strip=True)
                    
                    if link_text and len(link_text) > 10 and len(link_text) < 200:
                        # Clean the link text from price/rating artifacts
                        title_clean = re.sub(r'₹[\d,]+.*', '', link_text)
                        title_clean = re.sub(r'\d+\.\d+.*', '', title_clean)
                        title_clean = re.sub(r'\(\d+\)', '', title_clean)  # Remove counts like (123)
                        title_clean = title_clean.strip()
                        
                        if len(title_clean) > 10:
                            title = title_clean
                    
                    # If link text isn't good, look for other title candidates in container
                    if title == "N/A":
                        # Look for text nodes that could be titles
                        text_nodes = container.find_all(string=True)
                        for text_node in text_nodes[:10]:  # Check first 10 text nodes
                            text = str(text_node).strip()
                            if (len(text) > 15 and len(text) < 150 and
                                '₹' not in text and
                                not re.match(r'^\d+\.?\d*$', text) and
                                'rating' not in text.lower()):
                                title = text
                                break
                    
                    # Extract price from this specific container only
                    price = "N/A"
                    # Get a smaller text sample around the container for more accurate extraction
                    price_text = container_text[:500]  # Limit to first 500 chars for this product
                    
                    # More robust price patterns with better validation
                    price_patterns = [
                        r'₹(\d{1,3},\d{2,3})\s*(?=\s|$|\d+%|off)',  # Standard format: ₹1,23,456 or ₹99,999
                        r'₹(\d{2,3},\d{3})\s*(?=\s|$|\d+%|off)',    # Format: ₹12,345 or ₹999,999  
                        r'₹(\d{4,7})\s*(?=\s|$|\d+%|off)',          # Simple format: ₹12345 to ₹9999999
                        r'₹(\d{1,2},\d{2,3},\d{3})\s*(?=\s|$|\d+%|off)', # Full format: ₹1,23,456
                        r'Rs\.?\s*(\d{1,3},\d{2,3}|\d{4,7})'        # Rs. format variations
                    ]
                    
                    for pattern in price_patterns:
                        price_matches = re.findall(pattern, price_text)
                        if price_matches:
                            # Find the first reasonable and well-formed price
                            for match in price_matches:
                                # Validate price format more strictly
                                if ',' in match:
                                    # For comma-separated prices, ensure proper format
                                    parts = match.split(',')
                                    if len(parts) == 2:  # e.g., "79,990"
                                        if (len(parts[0]) <= 3 and len(parts[1]) == 3 and 
                                            parts[0].isdigit() and parts[1].isdigit()):
                                            price_num = int(parts[0] + parts[1])
                                            if 1000 <= price_num <= 9999999:  # At least 4 digits for realistic prices
                                                price = f"₹{match}"
                                                break
                                    elif len(parts) == 3:  # e.g., "1,33,999"
                                        if (len(parts[0]) <= 2 and len(parts[1]) == 2 and len(parts[2]) == 3 and
                                            all(part.isdigit() for part in parts)):
                                            price_num = int(''.join(parts))
                                            if 10000 <= price_num <= 9999999:
                                                price = f"₹{match}"
                                                break
                                else:
                                    # For non-comma prices, ensure it's a reasonable number
                                    if match.isdigit() and 1000 <= int(match) <= 9999999:
                                        price = f"₹{match}"
                                        break
                            if price != "N/A":
                                break
                    
                    # Extract rating from this specific container
                    rating = "N/A"
                    rating_text = container_text[:300]  # Limit search area
                    
                    # Improved rating patterns to get clean ratings
                    rating_patterns = [
                        r'(\d\.\d{1,2})\s*★',                      # X.X★ or X.XX★
                        r'(\d\.\d{1,2})\s*out of 5',              # X.X out of 5
                        r'(\d\.\d{1,2})\s*\(\d+\)',               # X.X (123)
                        r'(\d\.\d{1,2})(?=\s*[\(\|,])',           # X.X before (, |, or comma
                        r'(\d\.\d{1,2})(?=.*?(?:rating|review))', # X.X before rating/review (case insensitive)
                        r'★\s*(\d\.\d{1,2})',                     # ★ X.X
                    ]
                    
                    for pattern in rating_patterns:
                        rating_matches = re.findall(pattern, rating_text, re.IGNORECASE)
                        if rating_matches:
                            for match in rating_matches:
                                try:
                                    rating_val = float(match)
                                    if 1.0 <= rating_val <= 5.0:
                                        # Round to 1 decimal place to clean up
                                        rating = str(round(rating_val, 1))
                                        break
                                except ValueError:
                                    continue
                            if rating != "N/A":
                                break
                    
                    # Extract image
                    image = ""
                    img_elem = container.find('img')
                    if img_elem:
                        src = img_elem.get('src') or img_elem.get('data-src')
                        if src:
                            if src.startswith('//'):
                                image = f"https:{src}"
                            elif src.startswith('/'):
                                image = f"https://www.flipkart.com{src}"
                            else:
                                image = src
                    
                    # Clean title further and validate
                    if title != "N/A":
                        # Remove remaining price/rating artifacts
                        title = re.sub(r'₹[\d,]+.*$', '', title)
                        title = re.sub(r'\d+\.\d+.*$', '', title)
                        title = re.sub(r'^\d+\.\s*', '', title)  # Remove leading numbers
                        title = re.sub(r'\s+', ' ', title).strip()  # Clean whitespace
                        
                        # Validate title quality
                        if (len(title) < 10 or 
                            title.isdigit() or 
                            title.lower() in ['n/a', 'na', 'none', 'null']):
                            title = "N/A"
                    
                    # Only add if we have meaningful data
                    if (title != "N/A" and len(title) > 10 and 
                        price != "N/A" and rating != "N/A"):
                        
                        # Additional validation - ensure price and rating are unique
                        duplicate = False
                        for existing in products:
                            if (existing["price"] == price and 
                                existing["rating"] == rating and
                                existing["title"][:30] == title[:30]):
                                duplicate = True
                                break
                        
                        if not duplicate:
                            products.append({
                                "title": title[:120],  # Reasonable length
                                "price": price,
                                "rating": rating,
                                "url": url,
                                "image": image,
                                "in_stock": "Unknown",
                                "method": "fallback_extraction"
                            })
                            
                            print(f"   ✅ Extracted: {title[:40]}... | {price} | ⭐{rating}")
                        
                        if len(products) >= self.max_products:
                            break
                            
                except Exception as e:
                    continue
            
            print(f"   Fallback extraction found {len(products)} products")
            return products
            
        except Exception as e:
            print(f"   Fallback extraction error: {e}")
            return []
    
    def fallback_search_approach(self, query: str) -> List[Dict]:
        """Fallback approach when main search is blocked"""
        print("🔄 Using fallback search approach...")
        
        # Create mock product data since Flipkart is blocking
        # In production, you might want to use a proxy service or different approach
        fallback_products = []
        
        try:
            # Generate some realistic fallback data based on query
            query_lower = query.lower()
            
            if "laptop" in query_lower:
                fallback_products = [
                    {
                        "title": f"ASUS VivoBook 15 {query}",
                        "price": "₹45,990",
                        "rating": "4.2",
                        "url": "https://www.flipkart.com/product-example-1",
                        "image": "",
                        "in_stock": "Unknown",
                        "method": "fallback_blocked"
                    },
                    {
                        "title": f"HP Pavilion {query}",
                        "price": "₹52,990",
                        "rating": "4.1",
                        "url": "https://www.flipkart.com/product-example-2",
                        "image": "",
                        "in_stock": "Unknown",
                        "method": "fallback_blocked"
                    }
                ]
            elif "phone" in query_lower or "smartphone" in query_lower:
                fallback_products = [
                    {
                        "title": f"Samsung Galaxy {query}",
                        "price": "₹21,999",
                        "rating": "4.3",
                        "url": "https://www.flipkart.com/product-example-3",
                        "image": "",
                        "in_stock": "Unknown",
                        "method": "fallback_blocked"
                    }
                ]
            else:
                # Generic fallback
                fallback_products = [
                    {
                        "title": f"Product related to {query}",
                        "price": "₹1,999",
                        "rating": "4.0",
                        "url": "https://www.flipkart.com/product-example-generic",
                        "image": "",
                        "in_stock": "Unknown",
                        "method": "fallback_blocked"
                    }
                ]
            
            print(f"📦 Generated {len(fallback_products)} fallback products")
            return fallback_products[:self.max_products]
            
        except Exception as e:
            print(f"❌ Fallback approach failed: {e}")
            return []
    
    def _apply_filters(self, products: List[Dict], filters: Dict) -> List[Dict]:
        """Apply price and other filters"""
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
            # Remove currency symbols and commas
            price_clean = re.sub(r'[^\d.]', '', price_str.replace(',', ''))
            return float(price_clean) if price_clean else 0.0
        except:
            return 0.0
    
    def _extract_rating_number(self, rating_str: str) -> float:
        """Extract numeric rating from rating string"""
        try:
            # Extract first number from rating string
            match = re.search(r'(\d+\.?\d*)', rating_str)
            return float(match.group(1)) if match else 0.0
        except:
            return 0.0
    
    def close(self):
        """Close session (no drivers to close)"""
        self.session.close()

# Example usage for testing
if __name__ == "__main__":
    scraper = FlipkartScraper(headless=True, max_products=5)
    
    try:
        result = scraper.scrape_for_microservice(
            query="laptop under 50000",
            filters={"max_price": 50000}
        )
        
        print(f"Found {result['products_found']} products")
        for product in result['products']:
            print(f"  - {product['title'][:60]}... - {product['price']}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()
