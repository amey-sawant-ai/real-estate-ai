import requests
import json

def test_analyze_endpoint():
    payload = {
        'query': 'Should I buy a house in Bandra West Mumbai for investment?',
        'budget': '$2M',
        'risk': 'Medium'
    }

    print(f"Sending request with budget: {payload['budget']}")
    r = requests.post('http://localhost:8000/analyze', json=payload)
    
    try:
        data = r.json()
    except json.JSONDecodeError:
        print("Failed to decode JSON. Server response was:")
        print(r.status_code, r.text)
        assert False, f"Server returned non-JSON response with status {r.status_code}"

    print("\n--- RESPONSE ---")
    print("Budget received:", data.get('budget'))
    print("Keys in report:", data.get('report', {}).keys())

    if 'news_analysis' in data.get('report', {}):
        print("\nNEWS ANALYSIS IS PRESENT!")
        # Just print first 100 chars
        out = data['report']['news_analysis']
        if isinstance(out, dict):
            out = out.get('output', str(out))
        print(out[:100])
    else:
        print("\nNEWS ANALYSIS IS MISSING!")

if __name__ == '__main__':
    test_analyze_endpoint()
