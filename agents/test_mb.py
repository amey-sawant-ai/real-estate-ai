import requests
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
r = requests.get('https://www.magicbricks.com/property-rates-and-price-trends-in-Jogeshwari-Mumbai', headers=headers)
print(f"Status: {r.status_code}")
print(f"Content length: {len(r.text)}")
if "Average Locality Price" in r.text:
    print("Found 'Average Locality Price'")
else:
    print("NOT Found 'Average Locality Price'")
