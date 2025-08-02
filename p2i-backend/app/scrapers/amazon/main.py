import urllib.parse
import csv
import requests
from bs4 import BeautifulSoup

# This script scrapes Amazon search results for laptops under 50k and saves the data to a CSV file.

# Our token provided by 'scrape.do'
token = "<token_here>"

current_result_page = 1
max_result_page = 5  # Set to 5 pages for testing, you can increase this

# Initialize list to store product data
all_products = []

print("Starting Amazon search results scraper...")
print(f"Target: Laptops under 50k")
print(f"Max pages to scrape: {max_result_page}")

# Loop through all result pages
while True:
    # break the loop when max page number is reached
    if current_result_page > max_result_page:
        break

    print(f"\nProcessing page {current_result_page}...")
    
    targetUrl = urllib.parse.quote("https://www.amazon.in/s?k=laptops+under+50k&crid=32IAGWWR9UW7B&sprefix=laptops+u%2Caps%2C240&ref=nb_sb_ss_mvt-t11-ranker_1_9&page={}".format(current_result_page))
    apiUrl = "https://api.scrape.do/?token={}&url={}".format(token, targetUrl)
    
    try:
        response = requests.request("GET", apiUrl)
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to fetch page {current_result_page}. Status: {response.status_code}")
            current_result_page += 1
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Parse products on the current page
        product_elements = soup.find_all("div", {"class": "s-result-item"})
        print(f"Found {len(product_elements)} product elements on page {current_result_page}")

        products_found_on_page = 0
        
        for product in product_elements:
            try:
                # Extract product name
                name_element = product.select_one("h2 span")
                if not name_element:
                    name_element = product.select_one("h2 a span")
                if not name_element:
                    name_element = product.select_one(".a-size-medium")
                
                if name_element:
                    name = name_element.text.strip()
                else:
                    continue  # Skip products without names
                
                # Extract price
                price = "Price not available"
                try:
                    # Try multiple price selectors
                    price_element = product.select_one("span.a-price-whole")
                    if not price_element:
                        price_element = product.select_one("span.a-price")
                    if not price_element:
                        price_element = product.select_one(".a-price .a-offscreen")
                    
                    if price_element:
                        price = price_element.text.strip()
                    else:
                        # Try to extract from price range
                        price_text = str(product.select("span.a-price"))
                        if 'a-offscreen">' in price_text:
                            price = price_text.split('a-offscreen">')[1].split('</span>')[0]
                except Exception as e:
                    print(f"Error extracting price: {e}")
                
                # Extract link
                link = ""
                try:
                    link_element = product.select_one(".a-link-normal")
                    if link_element:
                        link = link_element.get("href")
                        if link and not link.startswith("http"):
                            link = "https://www.amazon.in" + link
                except Exception as e:
                    print(f"Error extracting link: {e}")
                
                # Extract image
                image = ""
                try:
                    img_element = product.select_one("img")
                    if img_element:
                        image = img_element.get("src")
                        if not image:
                            image = img_element.get("data-src")
                except Exception as e:
                    print(f"Error extracting image: {e}")
                
                # Only add products that have at least a name
                if name and name != "":
                    all_products.append({
                        "Name": name, 
                        "Price": price, 
                        "Link": link, 
                        "Image": image
                    })
                    products_found_on_page += 1
                    
            except Exception as e:
                print(f"Error processing product: {e}")
                continue
        
        print(f"Successfully extracted {products_found_on_page} products from page {current_result_page}")
        
    except Exception as e:
        print(f"Error processing page {current_result_page}: {e}")
    
    current_result_page += 1

print(f"\nScraping completed!")
print(f"Total products found: {len(all_products)}")

# Export the data to a CSV file
csv_file = "amazon_search_results.csv"
headers = ["Name", "Price", "Link", "Image"]

try:
    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_products)
    
    print(f"Data successfully exported to {csv_file}")
    print(f"Total products saved: {len(all_products)}")
    
except Exception as e:
    print(f"Error saving to CSV: {e}")

# Print first few products as preview
if all_products:
    print("\nFirst 3 products preview:")
    for i, product in enumerate(all_products[:3]):
        print(f"{i+1}. {product['Name'][:50]}... - {product['Price']}")
