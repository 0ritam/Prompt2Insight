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
                                        "specifications": {
                                            "type": "string",
                                            "description": "Key product specifications"
                                        },
                                        "price_display": {
                                            "type": "string",
                                            "description": "Price as displayed (e.g., '₹55,000 - ₹60,000')"
                                        },
                                        "price_value": {
                                            "type": "number",
                                            "description": "Numeric price value for sorting"
                                        },
                                        "purchase_url": {
                                            "type": "string",
                                            "description": "Site name where product is available (e.g., 'Flipkart', 'Amazon.in', 'Croma', 'Reliance Digital')"
                                        }
                                    },
                                    "required": ["name", "specifications", "price_display", "price_value", "purchase_url"]
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
You are an expert product researcher for the Indian market. Your task is to find products matching the user's query and return them as a structured list using the 'extract_products' tool.

User Query: "{query}"

**CRITICAL INSTRUCTIONS for Data Extraction:**
- Find a maximum of 5 products that match the user's query.
- Research current products available in the Indian market with realistic pricing.
- For each product, provide detailed specifications similar to this format:
  
  Example: "HP Victus 15 (Intel Core i5 12th Gen / RTX 2050)"
  - Processor: Intel Core i5-12450H (12th Gen)
  - Graphics: NVIDIA GeForce RTX 2050 (4GB GDDR6)  
  - RAM: 8GB/16GB DDR4 (configurable)
  - Storage: 512GB PCIe Gen4 NVMe SSD
  - Display: 15.6-inch FHD (1920x1080) IPS, 144Hz refresh rate

- **Price Extraction Rules:**
    - Extract a `price_display` string exactly as it appears (e.g., "₹58,990", "₹55,000 - ₹60,000").
    - Extract a `price_value` as a single number (remove commas and currency symbols).
    - If the price is a range (e.g., "₹55,000 - ₹60,000"), use the **lower number** for `price_value` (55000).

- **Site Information**: For `purchase_url`, provide only the site name where the product is typically available (e.g., "Flipkart", "Amazon.in", "Croma", "Reliance Digital").

Please research and use the extract_products tool to return accurate, current product information.
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
                            products_data = dict(function_call.args)
                            products = products_data.get("products", [])
                            
                            logger.info(f"AI Product Discoverer found {len(products)} products")
                            return products
            
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
