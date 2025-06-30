#!/usr/bin/env python3
"""
Health check system for scraper selectors
Automatically detects when selectors break and suggests alternatives
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

class ScraperHealthChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def check_selector_health(self) -> dict:
        """Check if current selectors are working"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "unknown",
            "selector_status": {},
            "recommendations": []
        }
        
        try:
            # Test search page access
            search_url = "https://www.flipkart.com/search?q=laptop"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code != 200:
                results["overall_health"] = "critical"
                results["recommendations"].append("Cannot access Flipkart search page")
                return results
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Test product container selectors
            container_selectors = [
                'div[data-id]',
                'div._1AtVbE', 
                'div._13oc-S'
            ]
            
            container_found = False
            for selector in container_selectors:
                elements = soup.select(selector)
                results["selector_status"][f"container_{selector}"] = len(elements)
                if len(elements) > 0:
                    container_found = True
            
            # Test title selectors within containers
            if container_found:
                containers = soup.select('div[data-id]')[:3]  # Test first 3 containers
                
                title_selectors = [
                    'div._4rR01T',
                    'a._1fQZEK', 
                    'div._2WkVRV',
                    'span._35KyD6'
                ]
                
                titles_found = 0
                for container in containers:
                    for selector in title_selectors:
                        title_elem = container.select_one(selector)
                        if title_elem and title_elem.text.strip():
                            titles_found += 1
                            break
                
                results["selector_status"]["titles_extracted"] = titles_found
                results["selector_status"]["containers_tested"] = len(containers)
            
            # Test price selectors
            price_selectors = [
                'div._30jeq3',
                'div._1_WHN1', 
                'span._30jeq3'
            ]
            
            prices_found = 0
            for container in containers:
                for selector in price_selectors:
                    price_elem = container.select_one(selector)
                    if price_elem and price_elem.text.strip():
                        prices_found += 1
                        break
            
            results["selector_status"]["prices_extracted"] = prices_found
            
            # Determine overall health
            if titles_found >= len(containers) * 0.8 and prices_found >= len(containers) * 0.5:
                results["overall_health"] = "good"
            elif titles_found >= len(containers) * 0.5:
                results["overall_health"] = "degraded"
                results["recommendations"].append("Some selectors not working optimally")
            else:
                results["overall_health"] = "critical"
                results["recommendations"].append("Major selector issues detected")
            
            # Suggest new selectors if needed
            if results["overall_health"] != "good":
                new_selectors = self._discover_new_selectors(soup)
                if new_selectors:
                    results["recommended_selectors"] = new_selectors
            
        except Exception as e:
            results["overall_health"] = "error"
            results["error"] = str(e)
        
        return results
    
    def _discover_new_selectors(self, soup) -> dict:
        """Try to discover new working selectors"""
        suggestions = {
            "title_selectors": [],
            "price_selectors": []
        }
        
        # Look for elements that might be titles (longer text, product-like)
        all_elements = soup.find_all(['div', 'span', 'a', 'h1', 'h2', 'h3'])
        
        for elem in all_elements:
            text = elem.get_text(strip=True)
            
            # Potential title: 20-200 chars, contains letters
            if 20 <= len(text) <= 200 and any(c.isalpha() for c in text):
                classes = ' '.join(elem.get('class', []))
                if classes and classes not in suggestions["title_selectors"]:
                    suggestions["title_selectors"].append(f".{classes.replace(' ', '.')}")
            
            # Potential price: contains ₹ symbol
            if '₹' in text and len(text) < 20:
                classes = ' '.join(elem.get('class', []))
                if classes and classes not in suggestions["price_selectors"]:
                    suggestions["price_selectors"].append(f".{classes.replace(' ', '.')}")
        
        return suggestions

def run_health_check():
    """Run health check and save results"""
    checker = ScraperHealthChecker()
    results = checker.check_selector_health()
    
    # Save results
    with open("scraper_health_check.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("🏥 Scraper Health Check Results:")
    print(f"   Overall Health: {results['overall_health'].upper()}")
    print(f"   Containers Found: {results['selector_status'].get('container_div[data-id]', 0)}")
    print(f"   Titles Extracted: {results['selector_status'].get('titles_extracted', 0)}")
    print(f"   Prices Extracted: {results['selector_status'].get('prices_extracted', 0)}")
    
    if results.get("recommendations"):
        print("\n⚠️ Recommendations:")
        for rec in results["recommendations"]:
            print(f"   - {rec}")
    
    if results.get("recommended_selectors"):
        print("\n🔧 Suggested New Selectors:")
        for selector_type, selectors in results["recommended_selectors"].items():
            print(f"   {selector_type}: {selectors[:3]}")  # Show first 3
    
    print(f"\n💾 Full results saved to scraper_health_check.json")
    
    return results

if __name__ == "__main__":
    run_health_check()
