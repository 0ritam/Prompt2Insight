#!/usr/bin/env python3
"""
Simple RAG Server - Direct access to your enhanced data scraper
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Add app directory to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Create the FastAPI app
app = FastAPI(
    title="Prompt2Insight Simple RAG API",
    description="Direct RAG with enhanced data scraper (RSS + Google News + Google Search API)",
    version="1.0.0"
)

# Add CORS middleware for frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ProductQuery(BaseModel):
    product_name: str
    question: str

class ScrapingRequest(BaseModel):
    product_name: str

# Check environment variables
google_api_key = os.getenv("GOOGLE_CSE_API_KEY")
google_engine_id = os.getenv("GOOGLE_CSE_ENGINE_ID")
gemini_api_key = os.getenv("GOOGLE_API_KEY")

@app.get("/")
def read_root():
    """Welcome endpoint"""
    return {
        "message": "✅ Prompt2Insight Simple RAG API is running!", 
        "status": "healthy",
        "features": [
            "RSS Feed Scraping",
            "Google News Fallback", 
            "Google Search API Fallback",
            "ChromaDB Vector Storage",
            "Gemini AI RAG Pipeline"
        ],
        "api_keys": {
            "google_search_api": "✅" if google_api_key else "❌",
            "google_engine": "✅" if google_engine_id else "❌",
            "gemini_api": "✅" if gemini_api_key else "❌"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Simple RAG server is running properly"}

@app.post("/test-scraper")
def test_data_scraper(request: ScrapingRequest):
    """Test the enhanced data scraper with all fallbacks"""
    try:
        from app.services.data_scraper import DataScraper
        
        scraper = DataScraper()
        documents = scraper.get_documents(request.product_name)
        
        return {
            "status": "success",
            "product_name": request.product_name,
            "documents_found": len(documents),
            "documents": documents[:2] if documents else [],  # Return first 2 docs for testing
            "message": f"Found {len(documents)} documents using enhanced scraper with Google Search API fallback"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Enhanced scraping failed: {str(e)}",
            "product_name": request.product_name
        }

@app.post("/api/v1/product/ask")
def ask_question_simple(request: ProductQuery):
    """Simple RAG using direct Gemini integration (no complex LangChain)"""
    try:
        # Step 1: Get documents using enhanced scraper
        from app.services.data_scraper import DataScraper
        from app.services.vector_store import VectorStoreService
        import re
        
        scraper = DataScraper()
        vector_service = VectorStoreService()
        
        # Sanitize collection name
        collection_name = re.sub(r'[^a-zA-Z0-9_-]', '', request.product_name.lower().replace(' ', '_'))
        if not collection_name:
            collection_name = "product_data"
        
        print(f"📦 Using collection: {collection_name}")
        
        # Check if we have existing documents
        try:
            retriever = vector_service.get_retriever(collection_name)
            print("✅ Using existing vector store")
        except Exception:
            print("📥 No existing data found, scraping new documents...")
            # Scrape new documents using enhanced scraper with all fallbacks
            documents = scraper.get_documents(request.product_name)
            
            if not documents:
                return {
                    "status": "error",
                    "message": f"❌ No documents found for '{request.product_name}' using any scraping method (RSS, Google News, Google Search API)",
                    "product_name": request.product_name,
                    "question": request.question
                }
            
            print(f"📄 Found {len(documents)} documents, building vector store...")
            # Build vector store
            vector_service.build_vector_store(collection_name, documents)
            retriever = vector_service.get_retriever(collection_name)
        
        # Step 2: Retrieve relevant documents
        print(f"🔍 Searching for: {request.question}")
        relevant_docs = retriever.get_relevant_documents(request.question)
        
        if not relevant_docs:
            return {
                "status": "error",
                "message": f"❌ No relevant information found for '{request.question}' about '{request.product_name}'",
                "product_name": request.product_name,
                "question": request.question
            }
        
        # Step 3: Prepare context from retrieved documents
        context = "\n\n".join([doc.page_content for doc in relevant_docs[:3]])
        print(f"📚 Retrieved {len(relevant_docs)} relevant documents")
        
        # Step 4: Generate answer using Google Gemini directly (no complex LangChain)
        if not gemini_api_key:
            return {
                "status": "error",
                "message": "❌ Google Gemini API key not found. Please set GOOGLE_API_KEY in environment variables.",
                "product_name": request.product_name,
                "question": request.question
            }
        
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Create prompt
        prompt = f"""You are an expert product analyst. Based on the following context about {request.product_name}, answer the user's question accurately and concisely.

Context:
{context}

Question: {request.question}

Instructions:
- Provide a clear, helpful answer based on the context
- If the context doesn't contain enough information, say so
- Focus on facts from the reviews and data provided
- Keep your response concise but informative

Answer:"""

        # Generate response
        print("🤖 Generating answer with Gemini...")
        response = model.generate_content(prompt)
        
        if response and response.text:
            return {
                "status": "success",
                "product_name": request.product_name,
                "question": request.question,
                "answer": response.text.strip(),
                "sources_used": len(relevant_docs),
                "scraping_method": "Enhanced (RSS + Google News + Google Search API)"
            }
        else:
            return {
                "status": "error",
                "message": "❌ Failed to generate response from Gemini",
                "product_name": request.product_name,
                "question": request.question
            }
            
    except Exception as e:
        print(f"❌ Simple RAG Error: {str(e)}")
        return {
            "status": "error",
            "message": f"Simple RAG query failed: {str(e)}",
            "product_name": request.product_name,
            "question": request.question
        }

@app.get("/api/v1/product/chromadb/collections")
def get_chromadb_collections():
    """Get ChromaDB collections information"""
    try:
        from app.services.vector_store import VectorStoreService
        
        vector_service = VectorStoreService()
        # Get list of collections from ChromaDB client
        collections_info = vector_service.client.list_collections()
        
        # Extract collection names
        collection_names = [col.name for col in collections_info]
        
        return {
            "status": "success",
            "collections": collection_names,
            "count": len(collection_names),
            "message": f"Found {len(collection_names)} collections"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get collections: {str(e)}",
            "collections": [],
            "count": 0
        }

# Frontend compatibility endpoints
class StructuredScrapeRequest(BaseModel):
    intent: str
    products: list
    filters: dict = {}
    attributes: list = []
    site: str = "general"
    max_products_per_query: int = 5

class GoogleSearchRequest(BaseModel):
    query: str
    num_results: int = 3

@app.post("/scrape-structured")
def scrape_structured_frontend(request: StructuredScrapeRequest):
    """Frontend compatibility endpoint - converts structured requests to simple scraping"""
    try:
        from app.services.data_scraper import DataScraper
        
        scraper = DataScraper()
        all_results = []
        
        # Process each product in the request
        for product_name in request.products:
            try:
                documents = scraper.get_documents(product_name)
                
                if documents:
                    # Convert documents to frontend-expected format
                    for i, doc in enumerate(documents[:request.max_products_per_query]):
                        result = {
                            "title": f"{product_name} - Review {i+1}",
                            "description": doc[:200] + "..." if len(doc) > 200 else doc,
                            "content": doc,
                            "source": "Enhanced Scraper (RSS + Google News + Google Search API)",
                            "product_query": product_name
                        }
                        all_results.append(result)
                        
            except Exception as e:
                print(f"Error processing {product_name}: {e}")
                continue
        
        return {
            "success": True,
            "intent": request.intent,
            "products_requested": request.products,
            "products_found": len(all_results),
            "execution_time": 2.5,  # Placeholder
            "results": all_results,
            "source": "enhanced-scraper",
            "timestamp": __import__('time').time()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "intent": request.intent,
            "products_requested": request.products,
            "products_found": 0,
            "results": []
        }

@app.post("/google-search")
def google_search_frontend(request: GoogleSearchRequest):
    """Frontend compatibility endpoint - uses enhanced scraper for search"""
    try:
        from app.services.data_scraper import DataScraper
        
        scraper = DataScraper()
        
        # Use Google Search API method directly
        documents = scraper.scrape_google_search_api(request.query, request.num_results)
        
        # Convert to frontend format
        results = []
        for i, doc in enumerate(documents):
            results.append({
                "title": f"Search Result {i+1} - {request.query}",
                "url": f"#search-result-{i+1}",
                "description": doc[:300] + "..." if len(doc) > 300 else doc,
                "image": "https://via.placeholder.com/300x200?text=Search+Result",
                "source": "google_search_api"
            })
        
        return {
            "success": True,
            "query": request.query,
            "results_found": len(results),
            "results": results,
            "timestamp": __import__('time').time()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": request.query,
            "results_found": 0,
            "results": []
        }

if __name__ == "__main__":
    print("🚀 Starting Simple RAG Server...")
    print(f"🔑 Google Search API Key: {'✅' if google_api_key else '❌'}")
    print(f"🔍 Google Engine ID: {'✅' if google_engine_id else '❌'}")
    print(f"🤖 Gemini API Key: {'✅' if gemini_api_key else '❌'}")
    print("📍 Server: http://localhost:8001")
    print("📖 Docs: http://localhost:8001/docs")
    print("✅ Health: http://localhost:8001/health")
    print("")
    print("📋 Available API Endpoints:")
    print("   POST /api/v1/product/ask - RAG Questions (Enhanced Scraper)")
    print("   POST /test-scraper - Test enhanced data scraper")
    print("   GET /api/v1/product/chromadb/collections - List ChromaDB collections")
    print("🛑 Press Ctrl+C to stop")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=False
    )
