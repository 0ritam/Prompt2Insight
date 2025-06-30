"""
Test script to debug the Flipkart scraper
"""

from flipkart_microservice_scraper import FlipkartScraper

def test_scraper():
    print("🧪 Testing Flipkart Scraper...")
    
    scraper = FlipkartScraper(max_products=3)
    
    try:
        # Test with a simple query
        result = scraper.scrape_for_microservice("gaming laptop")
        
        print(f"\n📊 Results:")
        print(f"Success: {result['success']}")
        print(f"Products found: {result['products_found']}")
        print(f"Execution time: {result['execution_time']}s")
        
        if result['success'] and result['products']:
            print(f"\n📦 Products:")
            for i, product in enumerate(result['products'], 1):
                print(f"  {i}. {product['title']}")
                print(f"     Price: {product['price']}")
                print(f"     Rating: {product['rating']}")
                print(f"     Method: {product['method']}")
                print(f"     URL: {product['url']}")
                print()
        else:
            print(f"❌ Error: {result.get('error', 'No products found')}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    test_scraper()
