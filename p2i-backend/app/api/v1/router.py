from fastapi import APIRouter
from app.api.v1.endpoints import rag, scraper, query_handler, amazon_scraper_endpoint

# Create the main router
api_router = APIRouter()

# Include the new Central Query Handler (Phase 8)
api_router.include_router(query_handler.router, prefix="/query", tags=["Central Query Handler"])

# Include the RAG endpoint router with correct prefix
api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])

# Include the scraper endpoint router
api_router.include_router(scraper.router, prefix="/scraper", tags=["Scraper"])

# Include the Amazon scraper endpoint router (Phase 9)
api_router.include_router(amazon_scraper_endpoint.router, prefix="/amazon", tags=["Amazon Scraper"])
