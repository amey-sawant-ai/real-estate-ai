import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import time

def generate_location_variants(location: str):
    """
    Generates location variants to handle things like "Andheri West Mumbai" 
    or "Austin Texas" for Numbeo's URL pattern.
    """
    parts = location.strip().split()
    # 1. Try stripping from left to right (e.g. Andheri West Mumbai -> West Mumbai -> Mumbai)
    for i in range(len(parts)):
        yield " ".join(parts[i:])
    # 2. Try stripping from right to left (e.g. Austin Texas -> Austin)
    for i in range(len(parts) - 1, 0, -1):
        yield " ".join(parts[:i])

def fetch_numbeo_data(location: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.numbeo.com/"
    }
    
    html_content = None
    city_used = location
    indices = {}
    
    metrics = [
        "Quality of Life Index",
        "Safety Index",
        "Cost of Living Index",
        "Property Price to Income Ratio",
        "Purchasing Power Index",
        "Health Care Index",
        "Climate Index"
    ]
    
    # Try different location variations until we get a 200 OK from Numbeo
    for variant in generate_location_variants(location):
        formatted_city = variant.title().replace(" ", "-")
        url = f"https://www.numbeo.com/quality-of-life/in/{formatted_city}"
        
        success = False
        for attempt in range(3):  # up to 2 retries (3 total attempts)
            time.sleep(2)  # Delay before every request
            
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    temp_html = resp.text
                    
                    # Verify this page actually contains the data we need (Numbeo returns 200 for missing cities sometimes)
                    qol_pattern = re.compile(re.escape("Quality of Life Index") + r'(?:<[^>]*>|\s|:)+([\d.]+)')
                    if qol_pattern.search(temp_html):
                        html_content = temp_html
                        city_used = formatted_city
                        success = True
                        break
                    else:
                        break # Valid response but no data, don't retry, move to next variant
                else:
                    time.sleep(3)  # Wait 3 seconds before retry
            except Exception:
                time.sleep(3)  # Wait 3 seconds before retry
                continue
                
        if success:
            break
            
    if not html_content:
        return {"error": f"City not found or no data on Numbeo for location: '{location}'"}
        
    try:
        for metric in metrics:
            # Look for metric name, followed by any combination of HTML tags, whitespace, or colons, then a number
            pattern = re.compile(re.escape(metric) + r'(?:<[^>]*>|\s|:)+([\d.]+)')
            match = pattern.search(html_content)
            if match:
                indices[metric] = float(match.group(1))
            else:
                indices[metric] = 0
                    
        return {
            "city": city_used.replace("-", " "),
            "quality_of_life_index": indices.get("Quality of Life Index", 0),
            "safety_index": indices.get("Safety Index", 0),
            "cost_of_living_index": indices.get("Cost of Living Index", 0),
            "property_price_to_income_ratio": indices.get("Property Price to Income Ratio", 0),
            "purchasing_power_index": indices.get("Purchasing Power Index", 0),
            "health_care_index": indices.get("Health Care Index", 0),
            "climate_index": indices.get("Climate Index", 0)
        }
    except Exception as e:
        return {"error": f"Numbeo parsing error: {str(e)}"}
        

