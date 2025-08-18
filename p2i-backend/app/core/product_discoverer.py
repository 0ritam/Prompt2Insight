"""
AI Product Discoverer Module for Prompt2Insight
Uses Gemini 2.5 Flash API with Tool Use to discover products in structured format
"""

import os
import json
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

logger = logging.getLogger(__name__)

class AIProductDiscoverer:
    def __init__(self):
        """Initialize the AI Product Discoverer with Gemini API"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            return
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Define the tool schema for structured product extraction
        self.extract_products_tool = Tool(
            function_declarations=[
                FunctionDeclaration(
                    name="extract_products",
                    description="Extract structured product information from research",
                    parameters={
                        "type": "object",
                        "properties": {
                            "products": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "description": "Product name"
                                        },
                                        "price_value": {
                                            "type": "number",
                                            "description": "Numeric price value for sorting (single number, no commas)"
                                        },
                                        "price_display": {
                                            "type": "string",
                                            "description": "Price as displayed (e.g., '₹55,000 - ₹60,000')"
                                        },
                                        "specs": {
                                            "type": "object",
                                            "description": "Numerical specifications for charts",
                                            "properties": {
                                                "ram_gb": {
                                                    "type": "number",
                                                    "description": "RAM in GB (use 0 if not available)"
                                                },
                                                "storage_gb": {
                                                    "type": "number", 
                                                    "description": "Storage in GB (use 0 if not available)"
                                                },
                                                "battery_mah": {
                                                    "type": "number",
                                                    "description": "Battery capacity in mAh (use 0 if not available)"
                                                }
                                            },
                                            "required": ["ram_gb", "storage_gb", "battery_mah"]
                                        },
                                        "purchase_url": {
                                            "type": "string",
                                            "description": "Site name where product is available (e.g., 'Flipkart', 'Amazon.in', 'Croma', 'Reliance Digital')"
                                        }
                                    },
                                    "required": ["name", "price_value", "price_display", "specs", "purchase_url"]
                                }
                            }
                        },
                        "required": ["products"]
                    }
                )
            ]
        )

    def find_products_with_ai(self, query: str) -> List[Dict[str, Any]]:
        """
        Find products using AI with structured output
        
        Args:
            query: User's product search query
            
        Returns:
            List of structured product dictionaries
        """
        if not self.api_key:
            logger.error("Gemini API key not configured")
            return []
        
        try:
            # Construct the detailed prompt for product discovery
            prompt = f"""
You are an expert data extraction agent for the Indian market. Your task is to find products matching the user's query and return them as a structured list using the 'extract_products' tool.

User Query: "{query}"

**CRITICAL INSTRUCTIONS for Data Extraction:**
- Find a maximum of 5 products.
- For each product, you MUST extract its key specifications and place them in the 'specs' object. The values for 'ram_gb', 'storage_gb', and 'battery_mah' must be numbers. If a spec is not mentioned, use a value of 0.
- **Price Extraction Rules:**
    - You MUST extract a `price_display` string (e.g., "₹58,990").
    - You MUST also extract a `price_value` which is a single integer or float, removing all currency symbols and commas.
    - If the price is a range (e.g., "₹55,000 - ₹60,000"), use the **lower number** for `price_value` (55000).

- **Specifications Extraction Rules:**
    - `ram_gb`: Extract RAM in GB as a number (e.g., 8, 16, 32). Use 0 if not available.
    - `storage_gb`: Extract storage in GB as a number (e.g., 256, 512, 1024). Use 0 if not available.
    - `battery_mah`: Extract battery capacity in mAh as a number (e.g., 3000, 4500, 5000). Use 0 if not available.

- **Site Information**: For `purchase_url`, provide only the site name where the product is typically available (e.g., "Flipkart", "Amazon.in", "Croma", "Reliance Digital").

Please research and use the extract_products tool to return accurate, current product information with complete numerical specifications.
"""

            logger.info(f"Discovering products for query: {query}")
            
            # Generate content with tool use
            response = self.model.generate_content(
                prompt,
                tools=[self.extract_products_tool],
                tool_config={'function_calling_config': 'ANY'}
            )
            
            # Parse the tool response
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        if function_call.name == "extract_products":
                            # Extract the products from the function call arguments
                            # Convert protobuf MapComposite to regular dict to avoid serialization issues
                            try:
                                import json
                                # First, convert the args to a dict recursively
                                def convert_protobuf_to_dict(obj):
                                    """Recursively convert protobuf objects to Python dictionaries"""
                                    if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
                                        if hasattr(obj, 'items'):  # dict-like object
                                            return {str(k): convert_protobuf_to_dict(v) for k, v in obj.items()}
                                        else:  # list-like object
                                            return [convert_protobuf_to_dict(item) for item in obj]
                                    else:
                                        return obj
                                
                                # Convert the protobuf args to clean Python objects
                                clean_args = convert_protobuf_to_dict(function_call.args)
                                products = clean_args.get("products", [])
                                
                                # Ensure products is a list of proper dictionaries
                                if isinstance(products, list):
                                    clean_products = []
                                    for product in products:
                                        if isinstance(product, dict):
                                            clean_products.append(product)
                                        else:
                                            # Convert any remaining protobuf objects
                                            clean_products.append(convert_protobuf_to_dict(product))
                                    
                                    logger.info(f"AI Product Discoverer found {len(clean_products)} products")
                                    return clean_products
                                else:
                                    logger.warning(f"Products data is not a list: {type(products)}")
                                    return []
                                    
                            except Exception as conversion_error:
                                logger.warning(f"Error converting protobuf response: {conversion_error}")
                                # Fallback: try manual extraction
                                try:
                                    products = []
                                    raw_products = function_call.args.get("products", [])
                                    for item in raw_products:
                                        # Convert each product manually
                                        product_dict = {}
                                        if hasattr(item, 'items'):
                                            for key, value in item.items():
                                                product_dict[str(key)] = value
                                        products.append(product_dict)
                                    
                                    logger.info(f"AI Product Discoverer found {len(products)} products (manual conversion)")
                                    return products
                                except Exception as fallback_error:
                                    logger.error(f"Manual conversion also failed: {fallback_error}")
                                    return []
            
            logger.warning("No structured products returned from AI")
            return []
            
        except Exception as e:
            logger.error(f"Error in AI Product Discoverer: {e}")
            return []

# Global instance
ai_product_discoverer = AIProductDiscoverer()

def find_products_with_ai(query: str) -> List[Dict[str, Any]]:
    """
    Convenience function to find products using AI
    
    Args:
        query: User's product search query
        
    Returns:
        List of structured product dictionaries
    """
    return ai_product_discoverer.find_products_with_ai(query)
