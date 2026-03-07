from data.worldbank import fetch_worldbank_data
from data.wikipedia import fetch_wikipedia_data
from data.openstreetmap import fetch_osm_data
from data.numbeo import fetch_numbeo_data

def fetch_all_data(query: str, location: str, country: str) -> dict:
    # 1. World Bank Data
    try:
        # Pass the country name to worldbank
        wb_data = fetch_worldbank_data(country)
    except Exception as e:
        wb_data = {"error": f"World Bank internal error: {str(e)}"}

    # 2. Wikipedia Data
    try:
        # Pass the location name to wikipedia
        wiki_data = fetch_wikipedia_data(location)
    except Exception as e:
        wiki_data = {"error": f"Wikipedia internal error: {str(e)}"}

    # 3. OpenStreetMap Data
    try:
        # Pass the location name to openstreetmap
        osm_data = fetch_osm_data(location)
    except Exception as e:
        osm_data = {"error": f"OpenStreetMap internal error: {str(e)}"}

    # 4. Numbeo Data
    try:
        import os
        from utils.groq_client import groq_manager
        
        prompt = f'Extract exactly the primary city name from this location string: "{location}". Return ONLY the city name in plain text, do not add quotes, explanation, or punctuation.'
        response = groq_manager.safe_call(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        city_name = response.strip()
        numbeo_data = fetch_numbeo_data(city_name)
    except Exception as e:
        numbeo_data = {"error": f"Numbeo internal error: {str(e)}"}

    # 5. Climate Data
    try:
        if isinstance(osm_data, dict) and "coordinates" in osm_data and "lat" in osm_data["coordinates"]:
            from data.climate import fetch_climate_data
            lat = float(osm_data["coordinates"]["lat"])
            lng = float(osm_data["coordinates"]["lng"])
            climate_data = fetch_climate_data(lat, lng)
        else:
            climate_data = {"error": "Skipped climate data because OSM coordinates were not found"}
    except Exception as e:
        climate_data = {"error": f"Climate internal error: {str(e)}"}

    # 6. Forex Data
    try:
        from data.forex import fetch_forex_data
        if country:
            forex_data = fetch_forex_data(country)
        else:
            forex_data = {"error": "Skipped forex data because country was not found"}
    except Exception as e:
        forex_data = {"error": f"Forex internal error: {str(e)}"}

    # 7. News Data
    try:
        from data.news import fetch_news_data
        news_data = fetch_news_data(location)
    except Exception as e:
        news_data = {"error": f"News internal error: {str(e)}"}

    # 8. Country Legal/Info Data
    try:
        from data.restcountries import fetch_country_legal_data
        if country:
            country_info = fetch_country_legal_data(country)
        else:
            country_info = {"error": "Skipped country legal data because country was not found"}
    except Exception as e:
        country_info = {"error": f"REST Countries internal error: {str(e)}"}

    # Combine results
    return {
        "location": location,
        "country": country,
        "worldbank": wb_data,
        "wikipedia": wiki_data,
        "osm": osm_data,
        "numbeo": numbeo_data,
        "climate": climate_data,
        "forex": forex_data,
        "news": news_data,
        "country_data": country_info
    }