import requests
import json

try:
    response = requests.post(
        "http://localhost:8000/api/query/answer",
        params= {"question": "What is the subject of Section 6 in the ML Engineer Study Guide?"},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response:", json.dumps(response.json(), indent=2))
    else:
        print("Error Response:", response.text)
except Exception as e:
    print(f"Request failed: {e}")
