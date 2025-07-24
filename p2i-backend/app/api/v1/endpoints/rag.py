from fastapi import APIRouter
from pydantic import BaseModel
from app.core.rag_pipeline import run_rag_query

# Pydantic model for the request body
class RAGQuery(BaseModel):
    product_name: str
    question: str

# Create a new router
router = APIRouter()

@router.post("/ask")
async def ask_product_question(query: RAGQuery):
    """
    Accepts a product name and a question, and returns an AI-generated
    answer based on scraped web context.
    """
    print(f"Received query for product: '{query.product_name}'")
    print(f"Question: '{query.question}'")
    
    # Call the RAG pipeline function
    answer = run_rag_query(
        product_name=query.product_name,
        question=query.question
    )
    
    # Return the answer in a JSON response
    return {"answer": answer}
