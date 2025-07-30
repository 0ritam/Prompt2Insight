import os
import re
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Import framework-specific components
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

# Import local application services
from app.services.data_scraper import DataScraper
from app.services.vector_store import VectorStoreService

# Define persona-specific prompt engineering templates
PERSONA_PROMPTS = {
    "budget_student": {
        "system_prompt": """You are a Budget-Conscious Student Advisor. Provide practical, concise advice for students with limited finances.

RESPONSE GUIDELINES:
- Keep responses under 300 words
- Focus on value for money and essential features
- Use simple, friendly language
- Include specific price comparisons when available
- Mention student discounts or deals
- Structure: Quick recommendation → Key pros/cons → Bottom line

Your role: Help students make smart purchasing decisions within budget constraints.""",
        
        "context_filter": "Focus on pricing, deals, durability, essential features, and cost comparisons."
    },
    
    "power_user": {
        "system_prompt": """You are a Tech Enthusiast Expert. Provide detailed technical insights for users who want performance details.

RESPONSE GUIDELINES:
- Keep responses under 400 words
- Focus on specifications, performance, and technical features
- Use technical terms but keep it accessible
- Include benchmarks or performance metrics when available
- Compare with similar products in the category
- Structure: Quick verdict → Technical highlights → Performance notes → Recommendation

Your role: Help tech-savvy users understand the technical aspects and performance potential.""",
        
        "context_filter": "Prioritize technical specifications, performance data, and advanced capabilities."
    },
    
    "general": {
        "system_prompt": """You are a Balanced Product Analyst. Provide well-rounded, easy-to-understand product analysis for general consumers.

RESPONSE GUIDELINES:
- Keep responses under 350 words
- Balance technical details with practical benefits
- Use clear, accessible language
- Cover pros and cons fairly
- Include real-world usage scenarios
- Structure: Summary → Key strengths → Potential concerns → Final recommendation

Your role: Help general consumers make informed decisions with balanced, practical advice.""",
        
        "context_filter": "Include comprehensive information covering features, user experience, and overall value."
    }
}

def _post_process_response(response: str, persona: str, max_words: int = 350) -> str:
    """
    Post-process the RAG response to ensure it's well-formatted and appropriately sized.
    """
    # Remove excessive whitespace and normalize line breaks
    response = ' '.join(response.split())
    
    # If response is too long, truncate intelligently
    words = response.split()
    
    if len(words) > max_words:
        # Try to end at a sentence boundary near the limit
        truncated = ' '.join(words[:max_words])
        
        # Find the last sentence ending
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        
        sentence_end = max(last_period, last_exclamation, last_question)
        
        if sentence_end > len(truncated) * 0.8:  # If we can trim to a sentence ending
            response = truncated[:sentence_end + 1]
        else:
            response = truncated + "..."
    
    return response.strip()

def _sanitize_collection_name(name: str) -> str:
    """
    Sanitizes a string to be a valid ChromaDB collection name.
    - Replaces spaces with underscores.
    - Removes characters other than alphanumerics, hyphens, and underscores.
    - Converts to lowercase.
    - Ensures name starts and ends with alphanumeric characters.
    """
    name = name.lower().replace(' ', '_')
    name = re.sub(r'[^a-z0-9_-]', '', name)
    # Remove leading/trailing underscores and hyphens
    name = name.strip('_-')
    # Ensure the name starts with alphanumeric if it doesn't
    if name and not name[0].isalnum():
        name = 'product_' + name
    # Ensure the name ends with alphanumeric if it doesn't  
    if name and not name[-1].isalnum():
        name = name.rstrip('_-') + '_data'
    # Ensure minimum length of 3 characters
    if len(name) < 3:
        name = 'product_data'
    # Ensure the name is between 3 and 63 characters
    return name[:63]

def run_rag_query(product_name: str, question: str, persona: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes a full RAG pipeline for a given product and question with persona-based analysis.

    This function will:
    1. Scrape data for the product if it's not already in the vector store.
    2. Build a vector store for the product.
    3. Use a RAG chain with persona-specific prompting to answer the question.

    Args:
        product_name: The name of the product to query.
        question: The user's question about the product.
        persona: Optional persona type ('budget_student', 'power_user', 'general', or None)

    Returns:
        Dictionary containing:
        - answer: The AI-generated answer as a string
        - sources: List of source documents used
        - execution_time: Time taken to process the query
        - persona_used: The actual persona applied
    """
    start_time = time.time()
    load_dotenv()

    # Determine which persona to use
    persona_used = persona if persona in PERSONA_PROMPTS else "general"
    persona_config = PERSONA_PROMPTS[persona_used]
    
    print(f"Using persona: '{persona_used}'")

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
        
        # Use the new primary document collection method (RSS + fallback)
        documents = data_scraper.get_documents(product_name)
        
        # Also try to get YouTube transcripts as supplementary content
        print("Scraping YouTube reviews...")
        youtube_docs = data_scraper.scrape_youtube_reviews(product_name)
        print(f"Found {len(youtube_docs)} YouTube transcripts.")
        
        # Combine all documents
        all_documents = documents + youtube_docs
        
        if not all_documents:
            return {
                "answer": "I'm sorry, but I couldn't find enough information about this product to answer your question.",
                "sources": [],
                "execution_time": time.time() - start_time,
                "persona_used": persona_used
            }
            
        # Build the vector store with the new documents
        print("Building vector store...")
        vector_service.build_vector_store(collection_name, all_documents)
        print("Vector store built successfully.")

    # 4. Get the retriever for the product's collection
    retriever = vector_service.get_retriever(collection_name)

    # 5. Define the persona-specific prompt template with improved formatting
    persona_instruction = persona_config["system_prompt"]
    
    template = f"""{persona_instruction}

Use the following context to answer the question about the product. Your response MUST be in user-friendly markdown format.

**Formatting Rules:**
- Start with a '### **Summary**' heading
- Follow with a '---' separator
- Add a '### **Key Strengths**' heading. Under it, list each strength as a bullet point (`* **Feature:** Description`)
- Follow with a '---' separator  
- Add a '### **Potential Concerns**' heading. Under it, list each concern as a bullet point (`* **Aspect:** Description`)
- End with a '---' separator and a '### **Recommendation**' heading with your final advice
- Do not include any text before the '### **Summary**' heading

Context: {{context}}

Question: {{question}}

Answer:"""

    prompt = PromptTemplate.from_template(template)

    # 6. Initialize the LLM with appropriate settings for focused responses
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",  # Try a different model
        temperature=0.3,
        max_output_tokens=1000  # Increase token limit
    )

    # 7. Define the RAG chain using LCEL
    setup_and_retrieval = RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    )
    rag_chain = setup_and_retrieval | prompt | llm | StrOutputParser()

    # 8. Invoke the chain and get the answer
    print(f"\nInvoking RAG chain with {persona_used} persona...")
    
    try:
        raw_answer = rag_chain.invoke(question)
        
        # If empty response, try a simpler approach
        if not str(raw_answer).strip():
            print("⚠️ Empty response from LLM, trying fallback...")
            
            # Get context directly and try a simple question
            context_docs = retriever.invoke(question)
            context_text = "\n\n".join([doc.page_content[:500] for doc in context_docs[:2]])
            
            fallback_prompt = f"""Based on this information about gaming laptops:
            
{context_text}

Question: {question}

Provide a helpful answer in 2-3 sentences:"""
            
            raw_answer = llm.invoke(fallback_prompt)
        
    except Exception as e:
        print(f"❌ Error invoking LLM: {e}")
        raw_answer = f"I encountered an error while analyzing this product. Error: {str(e)}"
    
    # Post-process the response for better formatting and length
    processed_answer = _post_process_response(str(raw_answer), persona_used)
    
    # 9. Get source documents for transparency
    source_docs = retriever.invoke(question)  # Use invoke instead of deprecated method
    sources = [{"source": doc.metadata.get("source", "Unknown"), 
                "content_preview": doc.page_content[:150] + "..."} 
               for doc in source_docs[:3]]  # Top 3 sources
    
    execution_time = time.time() - start_time
    
    return {
        "answer": processed_answer,
        "sources": sources,
        "execution_time": execution_time,
        "persona_used": persona_used
    }

if __name__ == '__main__':
    # Example usage of the RAG pipeline with persona testing
    # Make sure you have a .env file with your GOOGLE_API_KEY
    
    product = "iPhone 15 Pro"
    user_question = "What are the main criticisms about its battery life and heat?"
    
    print(f"--- Testing RAG pipeline with different personas ---")
    print(f"Product: '{product}'")
    print(f"Question: {user_question}\n")
    
    # Test with budget student persona
    print("=== BUDGET STUDENT PERSONA ===")
    budget_result = run_rag_query(product_name=product, question=user_question, persona="budget_student")
    print(f"Answer: {budget_result['answer']}")
    print(f"Execution time: {budget_result['execution_time']:.2f}s")
    print(f"Sources used: {len(budget_result['sources'])}")
    
    print("\n=== POWER USER PERSONA ===")
    power_result = run_rag_query(product_name=product, question=user_question, persona="power_user")
    print(f"Answer: {power_result['answer']}")
    print(f"Execution time: {power_result['execution_time']:.2f}s")
    
    print("\n=== GENERAL PERSONA ===")
    general_result = run_rag_query(product_name=product, question=user_question, persona="general")
    print(f"Answer: {general_result['answer']}")
    print(f"Execution time: {general_result['execution_time']:.2f}s")
    
    print("\n--- Testing different question ---")
    camera_question = "How is the camera system described in reviews?"
    
    print(f"\nQuestion: {camera_question}")
    print("=== POWER USER PERSONA (Camera Analysis) ===")
    camera_result = run_rag_query(product_name=product, question=camera_question, persona="power_user")
    print(f"Answer: {camera_result['answer']}")
    print("--------------------")
