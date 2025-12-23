import requests
import sys

print("Checking API...")
try:
    print("--- Documents ---")
    r_docs = requests.get('http://127.0.0.1:8000/api/documents', timeout=5)
    print(r_docs.status_code)
    print(r_docs.text[:500])  # Print first 500 chars

    print("\n--- Index Status ---")
    r_idx = requests.get('http://127.0.0.1:8000/api/index/status', timeout=5)
    print(r_idx.status_code)
    print(r_idx.text)

except Exception as e:
    print(f"Error: {e}")
