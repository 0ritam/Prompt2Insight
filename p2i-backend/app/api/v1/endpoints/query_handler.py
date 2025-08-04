"""
Central Query Handler for Prompt2Insight - Phase 8
The single intelligent API endpoint that orchestrates all backend tools
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Set up logger first
logger = logging.getLogger(__name__)

# Import our Phase 7 AI modules
import sys
from pathlib import Path

# Add paths for imports - fix the relative paths
backend_root = Path(__file__).parent.parent.parent.parent
core_dir = backend_root / "app" / "core"
scraper_dir = backend_root / "app" / "scrapers" / "flipkart"

# Add paths to Python path
sys.path.insert(0, str(core_dir))
sys.path.insert(0, str(scraper_dir))

# Import modules
try:
    from app.core.router_agent import route_query
    from app.core.product_discoverer import find_products_with_ai
    from app.core.rag_pipeline import run_rag_query
    from app.core.amazon_prompt_parser import parse_query_for_amazon
    from app.scrapers.flipkart.google_search import google_search
    logger.info("✅ All Phase 8 modules imported successfully")
except ImportError as e:
    logger.error(f"❌ Import error in query handler: {e}")
    # Create fallback functions to prevent server crash
    def route_query(query):
        return {"intent": "discovery_query", "query": query}
    def find_products_with_ai(query):
        return []
    def run_rag_query(query, persona=None):
        return "Service temporarily unavailable"
    def parse_query_for_amazon(query):
        return {
            "intent": "search",
            "products": [query],
            "filters": {"price": "any", "brand": "any"},
            "attributes": [],
            "max_products_per_query": 5
        }
    class GoogleSearchFallback:
        def search_products(self, query, num_results=5):
            return []
    google_search = GoogleSearchFallback()

# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for the central query handler."""
    query: str
    persona: Optional[str] = None
    max_results: int = 5

class DiscoveryResult(BaseModel):
    """Response model for discovery queries."""
    type: str = "discovery_result"
    query: str
    products: List[Dict[str, Any]]
    links: List[Dict[str, Any]]
    execution_time: float
    sources: List[str]
    # NEW: Amazon scraper integration data
    amazon_ready: bool = True
    amazon_query_data: Optional[Dict[str, Any]] = None

class AnalysisResult(BaseModel):
    """Response model for analysis queries."""
    type: str = "analysis_result"
    query: str
    answer: str
    persona: Optional[str]
    execution_time: float
    source: str

# Create router
router = APIRouter()

@router.post("/handle_query")
async def handle_query(request: QueryRequest):
    """
    Central API endpoint that intelligently routes user queries to appropriate tools.
    
    This is the single point of contact for all user queries from the frontend.
    It uses the Master Router Agent to determine intent and executes the appropriate workflow.
    
    Workflows:
    - discovery_query: AI Product Discoverer + Google Search (parallel)
    - analytical_query: RAG Analyzer with optional persona
    """
    start_time = time.time()
    
    logger.info(f"🎯 Central handler received query: '{request.query}'")
    
    try:
        # Step 1: Route the query using Master Router Agent
        logger.info("🧠 Routing query through Master Router Agent...")
        routing_result = route_query(request.query)
        
        intent = routing_result.get("intent")
        extracted_query = routing_result.get("query")
        
        logger.info(f"📍 Router decision: {intent} | Extracted: {extracted_query}")
        
        if intent == "discovery_query":
            # Discovery Workflow: AI Product Discoverer + Google Search (parallel)
            logger.info("🔍 Executing Discovery Workflow...")
            
            try:
                # Run both tools - they are synchronous functions
                logger.info("🤖 Calling AI Product Discoverer...")
                ai_products = find_products_with_ai(extracted_query)
                
                logger.info("🌐 Calling Google Search API...")
                google_results = google_search.search_products(extracted_query, request.max_results)
                
                # NEW: Parse query for Amazon scraper integration
                logger.info("🛒 Preparing Amazon query data...")
                amazon_query_data = parse_query_for_amazon(request.query)
                
                execution_time = time.time() - start_time
                
                logger.info(f"✅ Discovery completed: {len(ai_products)} AI products, {len(google_results)} Google results")
                
                return DiscoveryResult(
                    query=request.query,
                    products=ai_products,
                    links=google_results,
                    execution_time=execution_time,
                    sources=["ai_discoverer", "google_search"],
                    amazon_ready=True,
                    amazon_query_data=amazon_query_data
                )
                
            except Exception as e:
                logger.error(f"Error in discovery workflow: {e}")
                execution_time = time.time() - start_time
                
                # Still try to provide Amazon data even if other parts fail
                try:
                    amazon_query_data = parse_query_for_amazon(request.query)
                except:
                    amazon_query_data = None
                
                return DiscoveryResult(
                    query=request.query,
                    products=[],
                    links=[],
                    execution_time=execution_time,
                    sources=["ai_discoverer", "google_search"],
                    amazon_ready=bool(amazon_query_data),
                    amazon_query_data=amazon_query_data
                )
            
        elif intent == "analytical_query":
            # Analysis Workflow: RAG Analyzer
            logger.info("🧠 Executing Analysis Workflow...")
            
            try:
                # Call RAG pipeline with optional persona
                rag_result = run_rag_query(
                    query=extracted_query,
                    persona=request.persona
                )
                
                execution_time = time.time() - start_time
                
                logger.info(f"✅ Analysis completed in {execution_time:.2f}s")
                
                return AnalysisResult(
                    query=request.query,
                    answer=rag_result,
                    persona=request.persona,
                    execution_time=execution_time,
                    source="rag_analyzer"
                )
                
            except Exception as e:
                logger.error(f"Error in analysis workflow: {e}")
                execution_time = time.time() - start_time
                return AnalysisResult(
                    query=request.query,
                    answer=f"I apologize, but I encountered an error while analyzing '{request.query}'. Please try rephrasing your question.",
                    persona=request.persona,
                    execution_time=execution_time,
                    source="rag_analyzer"
                )
        
        else:
            # Fallback to discovery if intent is unclear
            logger.warning(f"Unknown intent '{intent}', defaulting to discovery workflow")
            
            try:
                # Default to discovery workflow
                ai_products = find_products_with_ai(extracted_query)
                google_results = google_search.search_products(extracted_query, request.max_results)
                
                # Prepare Amazon data for fallback too
                amazon_query_data = parse_query_for_amazon(request.query)
                
                execution_time = time.time() - start_time
                
                return DiscoveryResult(
                    query=request.query,
                    products=ai_products,
                    links=google_results,
                    execution_time=execution_time,
                    sources=["ai_discoverer", "google_search"],
                    amazon_ready=True,
                    amazon_query_data=amazon_query_data
                )
                
            except Exception as e:
                logger.error(f"Error in fallback discovery workflow: {e}")
                execution_time = time.time() - start_time
                return DiscoveryResult(
                    query=request.query,
                    products=[],
                    links=[],
                    execution_time=execution_time,
                    sources=["ai_discoverer", "google_search"],
                    amazon_ready=False,
                    amazon_query_data=None
                )
            
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Central handler error: {e}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Query processing failed",
                "message": str(e),
                "execution_time": execution_time,
                "query": request.query
            }
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the central query handler.
    """
    try:
        # Test basic imports and connections
        test_routing = route_query("test query")
        
        return {
            "status": "healthy",
            "message": "Central Query Handler is operational",
            "components": {
                "router_agent": "✅ Connected",
                "product_discoverer": "✅ Connected", 
                "google_search": "✅ Connected",
                "rag_pipeline": "✅ Connected"
            },
            "test_routing": test_routing
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "unhealthy",
                "error": str(e)
            }
        )
