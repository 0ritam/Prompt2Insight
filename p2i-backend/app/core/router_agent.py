"""
Master Router Agent for Prompt2Insight
The central decision-making brain that classifies user intent and routes to appropriate tools
"""

import os
import json
import logging
from typing import Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)

class MasterRouterAgent:
    def __init__(self):
        """Initialize the Master Router Agent with Gemini API"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            return
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def route_query(self, user_prompt: str) -> Dict[str, str]:
        """
        Analyze user prompt and determine the correct tool/workflow to use
        
        Args:
            user_prompt: The user's raw input query
            
        Returns:
            Dictionary with 'intent' and 'query' keys
        """
        if not self.api_key:
            logger.error("Gemini API key not configured")
            return {"intent": "discovery_query", "query": user_prompt}
        
        try:
            # Construct the router prompt for intent classification
            prompt = f"""
You are an expert query router for an e-commerce assistant. Your job is to analyze the user's prompt and determine the correct tool to use. 

CRITICAL: You must respond with ONLY a valid JSON object, no additional text, no markdown formatting, no explanation.

The available intents are:
1. `discovery_query`: Use for finding, searching, or discovering products. This includes broad searches, specific product searches, and comparison requests. Examples: "vivo phones", "best gaming laptops under 60000", "show me some smartwatches", "compare iPhone 15 vs Samsung Galaxy S24", "find me Samsung phones under 30000".
2. `analytical_query`: Use ONLY for deep analysis questions about products that the user already knows exist, "why" questions, or requests for news/reviews. Examples: "why should I buy an iPhone 15", "latest news about the Apple Vision Pro", "detailed review analysis of MacBook Pro M3".

Based on the user's prompt, respond with this exact JSON structure:
{{"intent": "discovery_query", "query": "extracted search term"}}
OR
{{"intent": "analytical_query", "query": "extracted search term"}}

User Prompt: "{user_prompt}"

JSON Response:"""

            logger.info(f"Routing query: {user_prompt}")
            
            # Generate the routing decision
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
                    route_decision = json.loads(json_text)
                    
                    # Validate the response structure
                    if "intent" in route_decision and "query" in route_decision:
                        intent = route_decision["intent"]
                        query = route_decision["query"]
                        
                        # Validate intent values
                        if intent not in ["discovery_query", "analytical_query"]:
                            logger.warning(f"Invalid intent '{intent}', defaulting to discovery_query")
                            intent = "discovery_query"
                        
                        logger.info(f"Routed to: {intent} with query: {query}")
                        return {"intent": intent, "query": query}
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse router response as JSON: {e}")
                    logger.debug(f"Raw response: {response.text}")
                except Exception as e:
                    logger.error(f"Error processing router response: {e}")
                    logger.debug(f"Raw response: {response.text}")
            
            # Fallback to discovery_query if parsing fails
            logger.warning("Router response parsing failed, defaulting to discovery_query")
            return {"intent": "discovery_query", "query": user_prompt}
            
        except Exception as e:
            logger.error(f"Error in Master Router Agent: {e}")
            # Fallback to discovery_query on any error
            return {"intent": "discovery_query", "query": user_prompt}

# Global instance
master_router = MasterRouterAgent()

def route_query(user_prompt: str) -> Dict[str, str]:
    """
    Convenience function to route user queries
    
    Args:
        user_prompt: The user's raw input query
        
    Returns:
        Dictionary with 'intent' and 'query' keys
    """
    return master_router.route_query(user_prompt)
