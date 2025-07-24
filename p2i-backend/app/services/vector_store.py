import os
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from typing import List

class VectorStoreService:
    """
    A service class for managing a ChromaDB vector store with LangChain.
    """

    def __init__(self):
        """
        Initializes the service, loading environment variables and setting up
        the embedding model and ChromaDB client.
        """
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")

        self.embedding_function = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
        self.persist_directory = "./chroma_db_store"
        self.client = chromadb.PersistentClient(path=self.persist_directory)

    def get_or_create_collection(self, collection_name: str):
        """
        Gets or creates a ChromaDB collection.

        Args:
            collection_name: The name of the collection.

        Returns:
            A chromadb.Collection object.
        """
        return self.client.get_or_create_collection(name=collection_name)

    def build_vector_store(self, collection_name: str, documents: List[str]) -> Chroma:
        """
        Creates and persists a vector store from a list of documents.

        Args:
            collection_name: The name of the collection to store the vectors in.
            documents: A list of text documents to be vectorized and stored.

        Returns:
            A LangChain Chroma vector store object.
        """
        vector_store = Chroma.from_texts(
            texts=documents,
            embedding=self.embedding_function,
            collection_name=collection_name,
            persist_directory=self.persist_directory
        )
        # Note: persist() is no longer needed in newer versions of langchain-chroma
        # Persistence is handled automatically
        return vector_store

    def get_retriever(self, collection_name: str):
        """
        Loads an existing vector store and returns a retriever object.

        Args:
            collection_name: The name of the collection for the vector store.

        Returns:
            A LangChain retriever object configured to return the top 3 documents.
        """
        vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_function,
            collection_name=collection_name
        )
        return vector_store.as_retriever(search_kwargs={"k": 3})

if __name__ == '__main__':
    # This block demonstrates how to use the VectorStoreService.
    # Note: You must have a .env file with your GOOGLE_API_KEY.
    
    try:
        # 1. Initialize the service
        vector_service = VectorStoreService()
        print("VectorStoreService initialized.")

        # 2. Define collection name and documents
        collection_name = "product_reviews_test"
        sample_documents = [
            "The camera on this phone is fantastic, producing sharp and vibrant photos.",
            "Battery life is a major issue; it barely lasts a full day with moderate use.",
            "The display is bright and clear, making it great for watching videos.",
            "Performance is smooth for everyday tasks, but it can lag with heavy gaming.",
            "I found the user interface to be intuitive and easy to navigate."
        ]
        
        # 3. Build the vector store
        print(f"\nBuilding vector store for collection: '{collection_name}'...")
        vector_service.build_vector_store(collection_name, sample_documents)
        print("Vector store built successfully.")

        # 4. Get a retriever
        print("\nGetting retriever...")
        retriever = vector_service.get_retriever(collection_name)
        print("Retriever created.")

        # 5. Use the retriever to find relevant documents
        query = "What are the comments on the phone's battery?"
        print(f"\nQuerying for: '{query}'")
        relevant_docs = retriever.get_relevant_documents(query)
        
        print("\n--- Relevant Documents Found ---")
        for i, doc in enumerate(relevant_docs):
            print(f"Doc {i+1}: {doc.page_content}")
        print("---------------------------------")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Please ensure you have a .env file with GOOGLE_API_KEY and have installed all required packages.")

