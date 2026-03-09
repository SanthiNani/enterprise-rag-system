import requests
import time

# URL of the deployed backend
BASE_URL = "https://santhinani-enterprise-rag-backend.hf.space"

def test_health():
    print(f"Checking health at {BASE_URL}/health ...")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Health Status: {resp.status_code}")
        print(resp.json())
    except Exception as e:
        print(f"Health check failed: {e}")

def test_upload():
    print(f"\nAttempting upload to {BASE_URL}/api/documents/upload ...")
    
    # Create a dummy small text file
    files = {
        'file': ('test_upload.txt', 'This is a test document for connectivity check.', 'text/plain')
    }
    
    start_time = time.time()
    try:
        resp = requests.post(f"{BASE_URL}/api/documents/upload", files=files, timeout=120)
        end_time = time.time()
        
        print(f"Upload Status: {resp.status_code}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print("Response:", resp.text)
        
    except Exception as e:
        print(f"Upload failed: {e}")

if __name__ == "__main__":
    test_health()
    test_upload()
