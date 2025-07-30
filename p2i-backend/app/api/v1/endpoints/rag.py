from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.rag_pipeline import run_rag_query
from app.services.vector_store import VectorStoreService
from typing import List, Dict, Any, Optional

# Pydantic model for the request body
class RAGQuery(BaseModel):
    product_name: str
    question: str
    persona: Optional[str] = None  # Add persona field for personalized responses

# Pydantic models for ChromaDB responses
class CollectionInfo(BaseModel):
    name: str
    document_count: int
    sample_documents: List[str]

class DocumentDetail(BaseModel):
    id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    relevance_score: Optional[str] = None

class CollectionDetail(BaseModel):
    name: str
    document_count: int
    documents: List[DocumentDetail]

# Create a new router
router = APIRouter()

@router.post("/ask")
async def ask_product_question(query: RAGQuery):
    """
    Accepts a product name, a question, and optional persona, 
    and returns an AI-generated answer based on scraped web context.
    """
    print(f"Received query for product: '{query.product_name}'")
    print(f"Question: '{query.question}'")
    print(f"Persona: '{query.persona}'")
    
    try:
        # Call the RAG pipeline function with persona
        result = run_rag_query(
            product_name=query.product_name,
            question=query.question,
            persona=query.persona  # Pass persona to pipeline
        )
        
        # Return enhanced response with persona information
        return {
            "success": True,
            "product_name": query.product_name,
            "question": query.question,
            "persona": query.persona,
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "execution_time": result.get("execution_time", 0),
            "persona_used": result.get("persona_used", "general")
        }
        
    except Exception as e:
        print(f"Error in RAG query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG processing failed: {str(e)}")

@router.get("/chromadb/collections", response_model=List[CollectionInfo])
async def get_chromadb_collections():
    """
    Get all ChromaDB collections with basic information.
    """
    try:
        vector_service = VectorStoreService()
        client = vector_service.client
        
        collections = client.list_collections()
        collection_info = []
        
        for collection in collections:
            try:
                # Get sample documents
                result = collection.get(limit=3)
                sample_docs = []
                if result['documents']:
                    for doc in result['documents'][:2]:
                        # Extract relevance score if present
                        preview = doc[:150] + "..." if len(doc) > 150 else doc
                        sample_docs.append(preview)
                
                collection_info.append(CollectionInfo(
                    name=collection.name,
                    document_count=collection.count(),
                    sample_documents=sample_docs
                ))
            except Exception as e:
                collection_info.append(CollectionInfo(
                    name=collection.name,
                    document_count=0,
                    sample_documents=[f"Error getting documents: {str(e)}"]
                ))
        
        return collection_info
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing ChromaDB: {str(e)}")

@router.get("/chromadb/collections/{collection_name}", response_model=CollectionDetail)
async def get_collection_details(collection_name: str, limit: int = 10):
    """
    Get detailed information about a specific ChromaDB collection.
    """
    try:
        vector_service = VectorStoreService()
        client = vector_service.client
        
        try:
            collection = client.get_collection(name=collection_name)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
        
        # Get documents with metadata
        result = collection.get(limit=limit)
        documents = []
        
        if result['documents']:
            for i, doc in enumerate(result['documents']):
                doc_id = result['ids'][i] if result['ids'] else f"doc_{i}"
                metadata = result['metadatas'][i] if result['metadatas'] and i < len(result['metadatas']) else None
                
                # Extract relevance score from document content if present
                relevance_score = None
                content = doc
                if doc.startswith('[Relevance:'):
                    end_bracket = doc.find(']')
                    if end_bracket != -1:
                        relevance_score = doc[1:end_bracket]
                        content = doc[end_bracket + 1:].strip()
                
                documents.append(DocumentDetail(
                    id=doc_id,
                    content=content,
                    metadata=metadata,
                    relevance_score=relevance_score
                ))
        
        return CollectionDetail(
            name=collection.name,
            document_count=collection.count(),
            documents=documents
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing collection: {str(e)}")

@router.delete("/chromadb/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """
    Delete a specific ChromaDB collection.
    """
    try:
        vector_service = VectorStoreService()
        client = vector_service.client
        
        try:
            client.delete_collection(name=collection_name)
            return {"message": f"Collection '{collection_name}' deleted successfully"}
        except Exception:
            raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting collection: {str(e)}")

@router.get("/chromadb/search/{collection_name}")
async def search_collection(collection_name: str, query: str, limit: int = 5):
    """
    Search for similar documents in a specific collection.
    """
    try:
        vector_service = VectorStoreService()
        
        # Get retriever for the collection
        retriever = vector_service.get_retriever(collection_name)
        retriever.search_kwargs["k"] = limit
        
        # Search for relevant documents
        docs = retriever.get_relevant_documents(query)
        
        results = []
        for i, doc in enumerate(docs):
            content = doc.page_content
            relevance_score = None
            
            # Extract relevance score if present
            if content.startswith('[Relevance:'):
                end_bracket = content.find(']')
                if end_bracket != -1:
                    relevance_score = content[1:end_bracket]
                    content = content[end_bracket + 1:].strip()
            
            results.append({
                "rank": i + 1,
                "content": content[:500] + "..." if len(content) > 500 else content,
                "relevance_score": relevance_score,
                "metadata": getattr(doc, 'metadata', None)
            })
        
        return {
            "query": query,
            "collection": collection_name,
            "results_count": len(results),
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching collection: {str(e)}")
