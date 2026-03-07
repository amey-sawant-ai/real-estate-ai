import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path so we can import 'data' package modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.worldbank import fetch_worldbank_data
from data.wikipedia import fetch_wikipedia_data
from data.openstreetmap import fetch_osm_data
from data.numbeo import fetch_numbeo_data

locations = [
    {"location": "Andheri West Mumbai", "country": "India"},
    {"location": "Dubai Marina", "country": "United Arab Emirates"},
    {"location": "Austin Texas", "country": "United States"},
    {"location": "Bandra West Mumbai", "country": "India"},
    {"location": "Downtown Singapore", "country": "Singapore"},
]

def analyze_data(source_name, data):
    useful = []
    missing = []
    
    if "error" in data:
        missing.append(f"Error encountered: {data['error']}")
        return useful, missing

    if source_name == "World Bank":
        metrics = data.get("metrics", {})
        for key, val in metrics.items():
            if isinstance(val, dict) and "value" in val:
                useful.append(f"{key}: {val['value']}")
            else:
                missing.append(f"{key} data missing or unavailable")
                
    elif source_name == "Wikipedia":
        summary = data.get("summary", "")
        intro = data.get("introduction", "")
        url = data.get("url", "")
        
        if summary: useful.append("Summary text extracted")
        else: missing.append("Summary missing")
        
        if intro: useful.append("Introduction text extracted")
        else: missing.append("Introduction missing")
        
        if url: useful.append("URL extracted")
        else: missing.append("URL missing")
        
    elif source_name == "OpenStreetMap":
        counts = data.get("infrastructure_counts_3km", {})
        for amenity, count in counts.items():
            if count > 0:
                useful.append(f"Found {count} {amenity}")
            else:
                missing.append(f"No {amenity} found in 3km radius")
                
    elif source_name == "Numbeo":
        for key, val in data.items():
            if key == "city": continue
            if val != 0 and val != "N/A":
                useful.append(f"{key}: {val}")
            else:
                missing.append(f"{key} data missing or 0")
                
    return useful, missing

def run_tests():
    report_path = os.path.join(os.path.dirname(__file__), "data_report.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Data Sources Test Report\n\n")
        f.write(f"**Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        for loc in locations:
            location_name = loc["location"]
            country_name = loc["country"]
            
            print(f"Fetching data for {location_name}...")
            
            # Fetch data
            wb_data = fetch_worldbank_data(country_name)
            wiki_data = fetch_wikipedia_data(location_name)
            osm_data = fetch_osm_data(location_name)
            
            f.write(f"## Location: {location_name} ({country_name})\n\n")
            
            # World Bank Section
            f.write("### 1. World Bank Macroeconomic Data\n")
            f.write("```json\n" + json.dumps(wb_data, indent=2) + "\n```\n")
            wb_useful, wb_missing = analyze_data("World Bank", wb_data)
            f.write("**Useful Data:**\n" + ("\n".join(f"- {u}" for u in wb_useful) if wb_useful else "- None") + "\n\n")
            f.write("**Missing/Empty:**\n" + ("\n".join(f"- {m}" for m in wb_missing) if wb_missing else "- None") + "\n\n")
            
            # Wikipedia Section
            f.write("### 2. Wikipedia Context Data\n")
            f.write("```json\n" + json.dumps(wiki_data, indent=2) + "\n```\n")
            wiki_useful, wiki_missing = analyze_data("Wikipedia", wiki_data)
            f.write("**Useful Data:**\n" + ("\n".join(f"- {u}" for u in wiki_useful) if wiki_useful else "- None") + "\n\n")
            f.write("**Missing/Empty:**\n" + ("\n".join(f"- {m}" for m in wiki_missing) if wiki_missing else "- None") + "\n\n")
            
            # OpenStreetMap Section
            f.write("### 3. OpenStreetMap Infrastructure Data (3km radius)\n")
            f.write("```json\n" + json.dumps(osm_data, indent=2) + "\n```\n")
            osm_useful, osm_missing = analyze_data("OpenStreetMap", osm_data)
            f.write("**Useful Data:**\n" + ("\n".join(f"- {u}" for u in osm_useful) if osm_useful else "- None") + "\n\n")
            f.write("**Missing/Empty:**\n" + ("\n".join(f"- {m}" for m in osm_missing) if osm_missing else "- None") + "\n\n")
            
            # Numbeo Section
            numbeo_data = fetch_numbeo_data(location_name)
            f.write("### 4. Numbeo Quality of Life & Cost of Living Data\n")
            f.write("```json\n" + json.dumps(numbeo_data, indent=2) + "\n```\n")
            numbeo_useful, numbeo_missing = analyze_data("Numbeo", numbeo_data)
            f.write("**Useful Data:**\n" + ("\n".join(f"- {u}" for u in numbeo_useful) if numbeo_useful else "- None") + "\n\n")
            f.write("**Missing/Empty:**\n" + ("\n".join(f"- {m}" for m in numbeo_missing) if numbeo_missing else "- None") + "\n\n")
            
            f.write("---\n\n")
            
    print(f"\nReport successfully generated at: {report_path}")

if __name__ == "__main__":
    run_tests()
