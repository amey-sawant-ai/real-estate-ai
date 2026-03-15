import requests
import json

BASE_URL = "http://localhost:8000"

print("\n" + "="*60)
print("TEST 1: NHB RESIDEX - Mumbai")
print("="*60)
r = requests.get(f"{BASE_URL}/data/residex?city=Mumbai")
print(json.dumps(r.json(), indent=2))

print("\n" + "="*60)
print("TEST 2: NHB RESIDEX - Jogeshwari Mumbai (suburb)")
print("="*60)
r = requests.get(f"{BASE_URL}/data/residex?city=Jogeshwari Mumbai")
print(json.dumps(r.json(), indent=2))

print("\n" + "="*60)
print("TEST 3: NHB RESIDEX - Bangalore")
print("="*60)
r = requests.get(f"{BASE_URL}/data/residex?city=Bangalore")
print(json.dumps(r.json(), indent=2))

print("\n" + "="*60)
print("TEST 4: NHB RESIDEX - Unknown city")
print("="*60)
r = requests.get(f"{BASE_URL}/data/residex?city=Nashik")
print(json.dumps(r.json(), indent=2))

print("\n" + "="*60)
print("TEST 5: Property Listings - Jogeshwari Mumbai")
print("="*60)
r = requests.get(
    f"{BASE_URL}/data/listings",
    params={"location": "Jogeshwari Mumbai", "budget": "1 crore"}
)
print(json.dumps(r.json(), indent=2))

print("\n" + "="*60)
print("TEST 6: Property Listings - Bandra West Mumbai")
print("="*60)
r = requests.get(
    f"{BASE_URL}/data/listings",
    params={"location": "Bandra West Mumbai", "budget": "2000000 USD"}
)
print(json.dumps(r.json(), indent=2))

print("\n" + "="*60)
print("ALL TESTS COMPLETE")
print("="*60)
