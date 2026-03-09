import requests
import time

# URL of the deployed backend
BASE_URL = "https://santhinani-enterprise-rag-backend.hf.space"

def test_query():
    question = "What is the most important issue?"
    print(f"\nAttempting query to {BASE_URL}/api/query/answer ...")
    print(f"Question: {question}")
    
    start_time = time.time()
    try:
        # Note: server timeout is default, client timeout 120s
        resp = requests.post(f"{BASE_URL}/api/query/answer", params={'question': question}, timeout=120)
        end_time = time.time()
        
        print(f"Status: {resp.status_code}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        
        if resp.status_code == 200:
            data = resp.json()
            print("\nResponse:")
            print(f"Answer: {data.get('answer')}")
            print(f"Confidence: {data.get('confidence')}")
            print(f"Sources: {len(data.get('retrieved_chunks', []))}")
        else:
            print("Error:", resp.text)
            
    except Exception as e:
        print(f"Query failed: {e}")

if __name__ == "__main__":
    test_query()
