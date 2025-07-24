from fastapi import APIRouter
from app.api.v1.endpoints import rag

# Create the main router
api_router = APIRouter()

# Include the RAG endpoint router
api_router.include_router(rag.router, prefix="/product", tags=["RAG"])
