#!/usr/bin/env python3
"""
Script to inspect ChromaDB contents and collections.
"""
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

try:
    from services.vector_store import VectorStoreService
    import chromadb
    from dotenv import load_dotenv
    
    def inspect_chromadb():
        """Inspect ChromaDB collections and their contents."""
        print("🔍 ChromaDB Inspector")
        print("=" * 50)
        
        try:
            # Load environment variables
            load_dotenv()
            
            # Initialize the vector store service
            vector_service = VectorStoreService()
            client = vector_service.client
            
            print(f"📂 ChromaDB Path: {vector_service.persist_directory}")
            print()
            
            # List all collections
            collections = client.list_collections()
            print(f"📚 Found {len(collections)} collections:")
            print()
            
            if not collections:
                print("   No collections found. Try running a RAG query first to create some data.")
                return
            
            for i, collection in enumerate(collections, 1):
                print(f"[{i}] Collection: {collection.name}")
                print(f"    📊 Document Count: {collection.count()}")
                
                # Get a few sample documents
                try:
                    result = collection.get(limit=3)
                    if result['documents']:
                        print(f"    📄 Sample Documents:")
                        for j, doc in enumerate(result['documents'][:2], 1):
                            preview = doc[:100] + "..." if len(doc) > 100 else doc
                            print(f"        [{j}] {preview}")
                    print()
                except Exception as e:
                    print(f"    ❌ Error getting documents: {e}")
                    print()
            
            # Interactive selection
            if len(collections) > 0:
                print("\n🔍 Want to inspect a specific collection?")
                try:
                    choice = input(f"Enter collection number (1-{len(collections)}) or 'q' to quit: ")
                    if choice.lower() != 'q':
                        collection_idx = int(choice) - 1
                        if 0 <= collection_idx < len(collections):
                            inspect_collection_details(collections[collection_idx])
                except (ValueError, IndexError):
                    print("Invalid selection.")
                except KeyboardInterrupt:
                    print("\nExiting...")
        
        except Exception as e:
            print(f"❌ Error inspecting ChromaDB: {e}")
            print(f"Make sure you have run at least one RAG query to create collections.")
    
    def inspect_collection_details(collection):
        """Inspect detailed information about a specific collection."""
        print(f"\n🔍 Detailed view of collection: {collection.name}")
        print("=" * 60)
        
        try:
            # Get collection metadata
            print(f"📊 Total documents: {collection.count()}")
            
            # Get all documents (limit to avoid overwhelming output)
            result = collection.get(limit=10)
            
            if result['documents']:
                print(f"\n📄 Documents (showing first {len(result['documents'])}):")
                for i, doc in enumerate(result['documents'], 1):
                    print(f"\n[{i}] Document ID: {result['ids'][i-1] if result['ids'] else 'N/A'}")
                    print(f"    Content: {doc[:200]}{'...' if len(doc) > 200 else ''}")
                    
                    if result['metadatas'] and result['metadatas'][i-1]:
                        print(f"    Metadata: {result['metadatas'][i-1]}")
            else:
                print("No documents found in this collection.")
        
        except Exception as e:
            print(f"❌ Error inspecting collection details: {e}")
    
    if __name__ == "__main__":
        inspect_chromadb()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the p2i-backend directory and have installed all dependencies.")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
