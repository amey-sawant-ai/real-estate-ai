import requests
import urllib.parse
import time

def fetch_osm_data(location: str) -> dict:
    headers = {"User-Agent": "RealEstateInvestmentBot/1.0 (bot@ameysawant.com)"}
    
    # 1. Geocode location using Nominatim
    formatted_location = urllib.parse.quote(location)
    nom_url = f"https://nominatim.openstreetmap.org/search?q={formatted_location}&format=json&limit=1"
    
    nom_resp = requests.get(nom_url, headers=headers)
    if nom_resp.status_code != 200:
        return {"error": f"Failed to fetch coordinates from Nominatim, status: {nom_resp.status_code}"}
        
    nom_data = nom_resp.json()
    if not nom_data:
        return {"error": f"Location not found on OpenStreetMap: '{location}'"}
        
    lat = nom_data[0].get("lat")
    lon = nom_data[0].get("lon")
    display_name = nom_data[0].get("display_name")
    
    # 2. Fetch infrastructure data using Overpass API
    # 3km radius = 3000m
    overpass_query = f"""
    [out:json][timeout:25];
    (
      nwr["railway"~"station|subway"](around:3000,{lat},{lon});
      nwr["highway"="bus_stop"](around:3000,{lat},{lon});
      nwr["amenity"="school"](around:3000,{lat},{lon});
      nwr["amenity"="hospital"](around:3000,{lat},{lon});
      nwr["shop"="mall"](around:3000,{lat},{lon});
      nwr["amenity"="bank"](around:3000,{lat},{lon});
    );
    out tags;
    """
    
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    max_retries = 3
    op_resp = None
    
    for attempt in range(max_retries):
        time.sleep(2)  # Add 2 second delay before every Overpass call
        op_resp = requests.post(overpass_url, data={"data": overpass_query}, headers=headers)
        
        if op_resp.status_code == 429:
            if attempt < max_retries - 1:
                time.sleep(10)  # Wait 10 seconds and retry
                continue
            else:
                return {"error": "Failed to fetch infrastructure from Overpass, status: 429 after 3 retries"}
        elif op_resp.status_code != 200:
            return {"error": f"Failed to fetch infrastructure from Overpass, status: {op_resp.status_code}"}
        else:
            break
            
    if op_resp is None or op_resp.status_code != 200:
        return {"error": "Failed to fetch infrastructure from Overpass due to unknown issues."}
        
    op_data = op_resp.json()
    elements = op_data.get("elements", [])
    
    counts = {
        "metro_subway_stations": 0,
        "bus_stops": 0,
        "schools": 0,
        "hospitals": 0,
        "shopping_malls": 0,
        "banks": 0
    }
    
    for el in elements:
        tags = el.get("tags", {})
        if tags.get("railway") in ["station", "subway"]:
            counts["metro_subway_stations"] += 1
        elif tags.get("highway") == "bus_stop":
            counts["bus_stops"] += 1
        elif tags.get("amenity") == "school":
            counts["schools"] += 1
        elif tags.get("amenity") == "hospital":
            counts["hospitals"] += 1
        elif tags.get("shop") == "mall":
            counts["shopping_malls"] += 1
        elif tags.get("amenity") == "bank":
            counts["banks"] += 1
            
    return {
        "location": display_name,
        "coordinates": {
            "lat": lat,
            "lng": lon
        },
        "infrastructure_counts_3km": counts
    }
