import requests
import urllib.parse

def fetch_wikipedia_data(location: str) -> dict:
    headers = {"User-Agent": "RealEstateApp/1.0 (contact@example.com)"}
    
    # 1. Fetch the page summary with a fallback strategy 
    search_term = location
    summary_data = {}
    
    while True:
        formatted_location = urllib.parse.quote(search_term)
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_location}"
        summary_resp = requests.get(summary_url, headers=headers)
        
        if summary_resp.status_code == 200:
            summary_data = summary_resp.json()
            break
        elif summary_resp.status_code == 404:
            parts = search_term.split()
            if len(parts) > 1:
                search_term = " ".join(parts[:-1])
                continue
            else:
                return {"error": f"Wikipedia page not found for '{location}'"}
        else:
            return {"error": f"Failed to fetch Wikipedia summary, status code: {summary_resp.status_code}"}
            
    summary_text = summary_data.get("description", "") or summary_data.get("extract", "")
    page_url = summary_data.get("content_urls", {}).get("desktop", {}).get("page", "")

    # 2. Fetch the full introduction section 
    # Use exact title from the summary API to ensure it matches
    exact_title = summary_data.get("title", location)
    formatted_title = urllib.parse.quote(exact_title)
    
    intro_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=true&titles={formatted_title}&format=json&explaintext=true"
    intro_resp = requests.get(intro_url, headers=headers)
    
    intro_text = ""
    if intro_resp.status_code == 200:
        intro_data = intro_resp.json()
        pages = intro_data.get("query", {}).get("pages", {})
        # The pages dict is keyed by page ID, grab the first/only value
        for page_id, page_info in pages.items():
            if page_id != "-1": # -1 means missing
                intro_text = page_info.get("extract", "")
                break

    # 3. Return clean dictionary
    return {
        "location": exact_title,
        "summary": summary_text,
        "introduction": intro_text,
        "url": page_url
    }
