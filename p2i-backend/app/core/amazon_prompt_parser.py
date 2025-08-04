"""
Amazon Prompt Parser for Prompt2Insight
Extracts structured data from user queries to feed into Amazon scraper
"""

import os
import json
import re
import logging
from typing import Dict, List, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)

class AmazonPromptParser:
    def __init__(self):
        """Initialize the Amazon Prompt Parser with Gemini API"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            return
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def parse_query_for_amazon(self, user_query: str) -> Dict[str, Any]:
        """
        Parse user query into structured format for Amazon scraper
        
        Args:
            user_query: The user's natural language query
            
        Returns:
            Dictionary in Amazon scraper format:
            {
                "intent": "search",
                "products": ["laptops"],
                "filters": {"price": "under ₹60000", "brand": "any"},
                "attributes": ["gaming", "intel"],
                "max_products_per_query": 5
            }
        """
        if not self.api_key:
            logger.error("Gemini API key not configured")
            return self._create_fallback_parse(user_query)
        
        try:
            # Construct the parsing prompt
            prompt = f"""
You are an expert query parser for e-commerce product searches. Your job is to extract structured information from user queries to search Amazon.in effectively.

CRITICAL: You must respond with ONLY a valid JSON object, no additional text, no markdown formatting, no explanation.

User Query: "{user_query}"

Extract the following information and respond with this exact JSON structure:

{{
    "intent": "search",
    "products": ["category1", "category2"],
    "filters": {{
        "price": "extracted price constraint or 'any'",
        "brand": "extracted brand or 'any'"
    }},
    "attributes": ["attribute1", "attribute2"],
    "max_products_per_query": 5
}}

**Extraction Rules:**

1. **products**: Main product categories (e.g., ["laptops"], ["phones"], ["headphones"])
   - For comparisons like "iPhone vs Samsung": extract both brands as ["iphone", "samsung galaxy"]
   - For specific models: ["iphone 15", "samsung galaxy s24"]

2. **filters.price**: 
   - Extract budget constraints: "under 60000" → "under ₹60000"
   - Extract ranges: "between 30000 and 50000" → "₹30000-₹50000"  
   - If no price mentioned: "any"

3. **filters.brand**:
   - Extract specific brands: "hp laptops" → "hp"
   - For brand comparisons: use dominant brand or "any"
   - If no brand mentioned: "any"

4. **attributes**: 
   - Extract descriptive keywords: ["gaming", "intel", "professional", "lightweight", "4k"]
   - Technical specs: ["i5", "16gb ram", "ssd"]
   - Use cases: ["office work", "video editing", "students"]

**Examples:**

Query: "best gaming laptops under 60000"
Response: {{"intent": "search", "products": ["laptops"], "filters": {{"price": "under ₹60000", "brand": "any"}}, "attributes": ["gaming"], "max_products_per_query": 5}}

Query: "compare iPhone 15 vs Samsung Galaxy S24"  
Response: {{"intent": "search", "products": ["iphone 15", "samsung galaxy s24"], "filters": {{"price": "any", "brand": "any"}}, "attributes": ["flagship", "premium"], "max_products_per_query": 5}}

Query: "HP laptops for office work around 40000"
Response: {{"intent": "search", "products": ["laptops"], "filters": {{"price": "around ₹40000", "brand": "hp"}}, "attributes": ["office work", "professional"], "max_products_per_query": 5}}

Now parse this query: "{user_query}"

JSON Response:"""

            logger.info(f"Parsing query for Amazon: {user_query}")
            
            # Generate the parsing result
            response = self.model.generate_content(prompt)
            
            if response.text:
                try:
                    # Clean the response text to extract JSON
                    response_text = response.text.strip()
                    
                    # Try to find JSON in the response
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    
                    if json_start != -1 and json_end > json_start:
                        json_text = response_text[json_start:json_end]
                    else:
                        json_text = response_text
                    
                    # Parse the JSON response from the LLM
                    parsed_result = json.loads(json_text)
                    
                    # Validate the response structure
                    if self._validate_parse_result(parsed_result):
                        logger.info(f"Successfully parsed query: {parsed_result}")
                        return parsed_result
                    else:
                        logger.warning("Invalid parse result structure, using fallback")
                        return self._create_fallback_parse(user_query)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    logger.debug(f"Raw response: {response.text}")
                    return self._create_fallback_parse(user_query)
                except Exception as e:
                    logger.error(f"Error processing parse response: {e}")
                    return self._create_fallback_parse(user_query)
            
            # Fallback if no response
            logger.warning("No response from parser, using fallback")
            return self._create_fallback_parse(user_query)
            
        except Exception as e:
            logger.error(f"Error in Amazon prompt parser: {e}")
            return self._create_fallback_parse(user_query)

    def _validate_parse_result(self, result: Dict[str, Any]) -> bool:
        """Validate that the parse result has the correct structure"""
        required_keys = ["intent", "products", "filters", "attributes", "max_products_per_query"]
        
        if not all(key in result for key in required_keys):
            return False
        
        if not isinstance(result["products"], list):
            return False
            
        if not isinstance(result["filters"], dict):
            return False
            
        if not isinstance(result["attributes"], list):
            return False
            
        return True

    def _create_fallback_parse(self, user_query: str) -> Dict[str, Any]:
        """Create a fallback parse result using simple regex patterns"""
        logger.info(f"Creating fallback parse for: {user_query}")
        
        # Simple fallback logic
        query_lower = user_query.lower()
        
        # Extract products using common patterns
        products = []
        if "laptop" in query_lower:
            products.append("laptops")
        elif "phone" in query_lower or "mobile" in query_lower:
            products.append("phones")
        elif "headphone" in query_lower or "earphone" in query_lower:
            products.append("headphones")
        elif "tablet" in query_lower:
            products.append("tablets")
        else:
            # Use the first word as product type
            products.append(user_query.split()[0])
        
        # Extract price using regex
        price_filter = "any"
        price_patterns = [
            r"under\s*₹?(\d+)",
            r"below\s*₹?(\d+)", 
            r"less than\s*₹?(\d+)",
            r"budget\s*₹?(\d+)"
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, query_lower)
            if match:
                price_filter = f"under ₹{match.group(1)}"
                break
        
        # Extract brand
        brand_filter = "any"
        common_brands = ["hp", "dell", "lenovo", "asus", "acer", "apple", "samsung", "oneplus", "xiaomi", "realme"]
        for brand in common_brands:
            if brand in query_lower:
                brand_filter = brand
                break
        
        # Extract attributes
        attributes = []
        common_attributes = ["gaming", "office", "student", "professional", "lightweight", "premium", "budget"]
        for attr in common_attributes:
            if attr in query_lower:
                attributes.append(attr)
        
        return {
            "intent": "search",
            "products": products,
            "filters": {
                "price": price_filter,
                "brand": brand_filter
            },
            "attributes": attributes,
            "max_products_per_query": 5
        }

# Global instance
amazon_parser = AmazonPromptParser()

def parse_query_for_amazon(user_query: str) -> Dict[str, Any]:
    """
    Convenience function to parse user queries for Amazon scraper
    
    Args:
        user_query: The user's natural language query
        
    Returns:
        Dictionary in Amazon scraper format
    """
    return amazon_parser.parse_query_for_amazon(user_query)
