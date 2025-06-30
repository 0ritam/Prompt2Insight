#!/usr/bin/env python3
"""
Price Finder - Helps identify correct price selectors from debug HTML
Run this after running the main scraper to analyze the HTML structure
"""

from bs4 import BeautifulSoup
import re

def analyze_flipkart_html():
    try:
        with open("flipkart_debug.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        print("🔍 ANALYZING FLIPKART HTML FOR PRICE ELEMENTS")
        print("=" * 50)
        
        # Find all elements containing rupee symbol
        price_elements = soup.find_all(string=lambda text: text and '₹' in text)
        
        print(f"Found {len(price_elements)} elements containing ₹ symbol:")
        print("-" * 30)
        
        for i, element in enumerate(price_elements[:10]):  # Show first 10
            parent = element.parent if element.parent else None
            if parent:
                # Get parent's classes and attributes
                classes = parent.get('class', [])
                class_str = '.'.join(classes) if classes else 'No classes'
                
                print(f"{i+1}. Text: '{element.strip()}'")
                print(f"   Parent tag: <{parent.name}>")
                print(f"   Classes: {class_str}")
                print(f"   CSS Selector: {parent.name}.{'.'.join(classes) if classes else 'no-class'}")
                print()
        
        # Look for numeric prices specifically
        print("\n💰 POTENTIAL ACTUAL PRICES:")
        print("-" * 30)
        
        for element in price_elements:
            text = element.strip()
            # Check if it contains actual price (numbers with rupee)
            if re.search(r'₹\s*[\d,]+', text) and not any(word in text.lower() for word in ['off', 'extra', 'save', 'discount', 'cashback']):
                parent = element.parent
                if parent:
                    classes = parent.get('class', [])
                    class_str = '.'.join(classes) if classes else 'No classes'
                    print(f"✅ LIKELY PRICE: '{text}'")
                    print(f"   CSS Selector: {parent.name}.{'.'.join(classes) if classes else 'no-class'}")
                    print()
    
    except FileNotFoundError:
        print("❌ flipkart_debug.html not found. Run the main scraper first.")
    except Exception as e:
        print(f"❌ Error analyzing HTML: {e}")

if __name__ == "__main__":
    analyze_flipkart_html()
