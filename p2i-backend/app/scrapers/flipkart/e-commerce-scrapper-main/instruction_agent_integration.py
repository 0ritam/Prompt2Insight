"""
Direct Integration Example - How your instruction agent calls the scraper
"""

import requests
import json

class ScrapingMicroservice:
    """Simple client for your instruction agent"""
    
    def __init__(self, scraper_url="http://localhost:8000"):
        self.scraper_url = scraper_url
    
    def execute_scrape_task(self, prompt_parser_output):
        """
        Execute scraping based on prompt parser output
        
        Args:
            prompt_parser_output: Exact JSON from your PROMPT_TEMPLATE
            {
                "intent": "compare" or "search" or "recommend",
                "products": ["product1", "product2"],
                "filters": {"price": "under ₹20000", "brand": "Apple"} or null,
                "attributes": ["attribute1", "attribute2"] or null
            }
        """
        
        # Convert to scraper API format
        scraper_request = {
            "intent": prompt_parser_output["intent"],
            "products": prompt_parser_output["products"],
            "filters": prompt_parser_output.get("filters"),
            "attributes": prompt_parser_output.get("attributes"),
            "max_products_per_query": 5
        }
        
        try:
            response = requests.post(
                f"{self.scraper_url}/scrape-structured",
                json=scraper_request,
                timeout=120  # 2 minute timeout
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Example: How your instruction agent would use this
def main():
    scraper = ScrapingMicroservice()
    
    # Example 1: Direct output from your prompt parser
    prompt_parser_result_1 = {
        "intent": "compare",
        "products": ["iPhone 14", "Poco X5"],
        "filters": {
            "price": "under ₹20000"
        },
        "attributes": None
    }
    
    print("🤖 Instruction Agent: Executing scrape task...")
    print(f"📋 Prompt Parser Output: {json.dumps(prompt_parser_result_1, indent=2)}")
    
    result = scraper.execute_scrape_task(prompt_parser_result_1)
    
    if result["success"]:
        data = result["data"]
        print(f"✅ Scraping completed successfully!")
        print(f"🎯 Intent: {data['intent']}")
        print(f"📱 Products found: {data['products_found']}")
        print(f"⚡ Time taken: {data['execution_time']}s")
        
        # Process results for comparison
        if data["intent"] == "compare":
            print("\n🔍 Comparison Results:")
            for product_name in data["products_requested"]:
                matching = [r for r in data["results"] if r["source_query"] == product_name]
                print(f"\n📱 {product_name}: {len(matching)} options found")
                
                if matching:
                    best_option = min(matching, key=lambda x: float(x["price"]) if x["price"].isdigit() else float('inf'))
                    print(f"   💰 Best price: ₹{best_option['price']}")
                    print(f"   📝 Title: {best_option['title'][:50]}...")
    
    else:
        print(f"❌ Scraping failed: {result['error']}")
    
    # Example 2: Another prompt parser output
    prompt_parser_result_2 = {
        "intent": "search",
        "products": ["gaming laptop"],
        "filters": {
            "price": "under ₹60000",
            "brand": "ASUS"
        },
        "attributes": ["nvidia graphics", "i5 processor"]
    }
    
    print(f"\n\n🤖 Second task...")
    print(f"📋 Prompt Parser Output: {json.dumps(prompt_parser_result_2, indent=2)}")
    
    result2 = scraper.execute_scrape_task(prompt_parser_result_2)
    
    if result2["success"]:
        data2 = result2["data"]
        print(f"✅ Second task completed!")
        print(f"💻 Gaming laptops found: {data2['products_found']}")
        
        # Show top 3 results
        for i, product in enumerate(data2["results"][:3], 1):
            print(f"   {i}. ₹{product['price']} - {product['title'][:40]}...")
    
    print("\n🎯 Integration complete!")

if __name__ == "__main__":
    main()
