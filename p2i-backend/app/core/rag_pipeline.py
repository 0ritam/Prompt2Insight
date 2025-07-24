import os
import re
from dotenv import load_dotenv

# Import framework-specific components
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

# Import local application services
from app.services.data_scraper import DataScraper
from app.services.vector_store import VectorStoreService

def _sanitize_collection_name(name: str) -> str:
    """
    Sanitizes a string to be a valid ChromaDB collection name.
    - Replaces spaces with underscores.
    - Removes characters other than alphanumerics, hyphens, and underscores.
    - Converts to lowercase.
    """
    name = name.lower().replace(' ', '_')
    name = re.sub(r'[^a-z0-9_-]', '', name)
    # Ensure the name is between 3 and 63 characters
    return name[:63]

def run_rag_query(product_name: str, question: str) -> str:
    """
    Executes a full RAG pipeline for a given product and question.

    This function will:
    1. Scrape data for the product if it's not already in the vector store.
    2. Build a vector store for the product.
    3. Use a RAG chain to answer the question based on the scraped context.

    Args:
        product_name: The name of the product to query.
        question: The user's question about the product.

    Returns:
        The AI-generated answer as a string.
    """
    load_dotenv()

    # 1. Instantiate services
    data_scraper = DataScraper()
    vector_service = VectorStoreService()
    
    # 2. Define a sanitized collection name for the product
    collection_name = _sanitize_collection_name(product_name)
    print(f"Using collection: '{collection_name}'")

    # 3. Check if the collection exists. If not, create it.
    try:
        vector_service.client.get_collection(name=collection_name)
        print(f"Collection '{collection_name}' already exists. Skipping scraping.")
    except Exception:
        print(f"Collection '{collection_name}' not found. Building new collection...")
        
        # Scrape documents from news and YouTube
        print("Scraping Google News...")
        news_docs = data_scraper.scrape_google_news(product_name)
        print(f"Found {len(news_docs)} news articles.")
        
        print("Scraping YouTube reviews...")
        youtube_docs = data_scraper.scrape_youtube_reviews(product_name)
        print(f"Found {len(youtube_docs)} YouTube transcripts.")
        
        documents = news_docs + youtube_docs
        
        if not documents:
            return "I'm sorry, but I couldn't find enough information about this product to answer your question."
            
        # Build the vector store with the new documents
        print("Building vector store...")
        vector_service.build_vector_store(collection_name, documents)
        print("Vector store built successfully.")

    # 4. Get the retriever for the product's collection
    retriever = vector_service.get_retriever(collection_name)

    # 5. Define the prompt template
    template = """Use the following context to answer the question. If you don't know the answer, just say that you don't know.
Context: {context}
Question: {question}
Answer: """
    prompt = PromptTemplate.from_template(template)

    # 6. Initialize the LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    # 7. Define the RAG chain using LCEL
    setup_and_retrieval = RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    )
    rag_chain = setup_and_retrieval | prompt | llm | StrOutputParser()

    # 8. Invoke the chain and get the answer
    print("\nInvoking RAG chain to answer the question...")
    answer = rag_chain.invoke(question)
    
    return answer

if __name__ == '__main__':
    # Example usage of the RAG pipeline
    # Make sure you have a .env file with your GOOGLE_API_KEY
    
    product = "iPhone 15 Pro"
    user_question = "What are the main criticisms about its battery life and heat?"
    
    print(f"--- Running RAG pipeline for Product: '{product}' ---")
    print(f"Question: {user_question}\n")
    
    final_answer = run_rag_query(product_name=product, question=user_question)
    
    print("\n--- Final Answer ---")
    print(final_answer)
    print("--------------------")
    
    # Second run to show it uses the existing collection
    print("\n--- Running RAG pipeline again to test persistence ---")
    another_question = "How is the camera system described in reviews?"
    print(f"Question: {another_question}\n")
    
    second_answer = run_rag_query(product_name=product, question=another_question)
    
    print("\n--- Final Answer ---")
    print(second_answer)
    print("--------------------")
