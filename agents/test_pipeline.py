import requests
import json

BASE_URL = "http://localhost:8000"

payload = {
    "query": "Jogeshwari Mumbai",
    "budget": "1 crore",
    "risk": "medium"
}

print("Running full pipeline test...")
r = requests.post(f"{BASE_URL}/analyze", json=payload)
print(json.dumps(r.json(), indent=2))
