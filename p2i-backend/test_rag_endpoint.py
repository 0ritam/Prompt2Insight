import requests
import json

# The URL of the RAG API endpoint
API_URL = "http://127.0.0.1:8001/api/v1/product/ask"

# The payload to send to the endpoint
test_payload = {
    "product_name": "Google Pixel 8",
    "question": "how is the camera quality for photos?"
}

def test_rag_endpoint():
    """
    Sends a test request to the RAG API endpoint and prints the response.
    """
    print(f"🚀 Sending POST request to: {API_URL}")
    print(f"📦 Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        # Send the POST request with the JSON payload
        response = requests.post(API_URL, json=test_payload, timeout=300) # Long timeout for first run
        
        # Check if the request was successful (i.e., status code 2xx)
        response.raise_for_status()
        
        # Parse the JSON response
        response_data = response.json()
        
        # Print the answer in a clean format
        print("\n" + "="*20 + " ✅ SUCCESS " + "="*20)
        print("\n🤖 AI-Generated Answer:\n")
        print(response_data.get("answer", "No answer key found in the response."))
        print("\n" + "="*51)

    except requests.exceptions.RequestException as e:
        # Handle connection errors, timeouts, etc.
        print("\n" + "="*20 + " ❌ ERROR " + "="*21)
        print(f"\nAn error occurred while trying to connect to the API endpoint.")
        print(f"Error details: {e}")
        print("\nPlease ensure the backend server is running and accessible at the specified URL.")
        print("="*51)

if __name__ == "__main__":
    test_rag_endpoint()
