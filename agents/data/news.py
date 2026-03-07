import os
import time
import requests
import urllib.parse
import json
from groq import Groq

def extract_city_and_country(location: str):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f'''Extract the primary city name and country name from this location string: "{location}".
Return ONLY a valid JSON object in this exact format, nothing else:
{{"city": "...", "country": "..."}}'''
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"}
        )
        result = json.loads(completion.choices[0].message.content)
        return result.get("city", location.split()[-1]), result.get("country", location.split()[-1])
    except Exception:
        # Fallback to last word
        parts = location.split()
        return parts[-1], parts[-1]

def fetch_gdelt(query_str: str) -> dict:
    url_query = urllib.parse.quote(query_str)
    url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={url_query}&mode=artlist&maxrecords=10&format=json&sort=DateDesc"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    
    if resp.status_code == 200:
        try:
            data = resp.json()
            if "articles" in data and len(data["articles"]) > 0:
                return data
        except Exception:
            pass
    return None

def fetch_news_data(location: str) -> dict:
    if not location:
        return {"error": "Location not provided"}
        
    try:
        city_name, country_name = extract_city_and_country(location)
        
        # 1. Try specifically with the extracted city
        query_str = f"{city_name} real estate investment"
        data = fetch_gdelt(query_str)
        
        # 2. If nothing or error, fallback to country
        if not data:
            time.sleep(6) # wait 6s to avoid GDELT 429 error
            fallback_query_str = f"real estate {country_name}"
            data = fetch_gdelt(fallback_query_str)
                
        if not data or "articles" not in data:
            return {
                "location": location,
                "total_articles": 0,
                "articles": []
            }
            
        articles_list = []
        # Return maximum 5 most recent articles
        for art in data["articles"][:5]:
            articles_list.append({
                "title": art.get("title", ""),
                "url": art.get("url", ""),
                "seendate": art.get("seendate", ""),
                "domain": art.get("domain", "")
            })
            
        return {
            "location": location,
            "total_articles": len(articles_list),
            "articles": articles_list
        }
        
    except Exception as e:
        return {"error": f"News internal error: {str(e)}"}
