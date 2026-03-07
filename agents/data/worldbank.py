import requests

def fetch_worldbank_data(country_name: str) -> dict:
    # 1. Fetch all countries and find the match for country_name
    search_url = "https://api.worldbank.org/v2/country?per_page=300&format=json"
    search_resp = requests.get(search_url)
    search_data = search_resp.json()

    if len(search_data) < 2 or not search_data[1]:
        return {"error": "Could not fetch country list from World Bank"}
    
    country_code = None
    country_exact_name = None
    for c in search_data[1]:
        if c.get("name", "").lower() == country_name.lower():
            country_code = c.get("iso2Code")
            country_exact_name = c.get("name")
            break
            
    if not country_code:
        return {"error": f"Could not find country code for '{country_name}'"}

    # 2. Fetch the indicators using mrv=5 (most recent 5 years of data, to ensure we get a non-null if latest is missing)
    indicators = {
        "gdp_growth": "NY.GDP.MKTP.KD.ZG",
        "urban_pop_growth": "SP.URB.GROW",
        "population_total": "SP.POP.TOTL",
        "inflation_rate": "FP.CPI.TOTL.ZG",
        "net_migration": "SM.POP.NETM",
        "unemployment_rate": "SL.UEM.TOTL.ZS",
        "gdp_per_capita": "NY.GDP.PCAP.CD",
        "population_density": "EN.POP.DNST",
        "labour_force_participation_rate": "SL.TLF.CACT.ZS",
        "urban_population_percentage": "SP.URB.TOTL.IN.ZS"
    }

    results = {}

    for label, indicator in indicators.items():
        url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json&mrv=5"
        resp = requests.get(url)
        data = resp.json()

        # Check if we got valid data
        if len(data) >= 2 and data[1]:
            # Take the most recent non-null value
            recent_record = next((item for item in data[1] if item['value'] is not None), None)
            if recent_record:
                results[label] = {
                    "value": recent_record['value'],
                    "year": recent_record['date']
                }
            else:
                results[label] = "No recent data available"
        else:
            results[label] = "No data available"

    return {
        "country": country_exact_name,
        "country_code": country_code,
        "metrics": results
    }
