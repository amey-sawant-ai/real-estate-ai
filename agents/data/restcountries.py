import requests

def fetch_country_legal_data(country: str) -> dict:
    if not country:
        return {"error": "Country not provided"}
        
    try:
        url = f"https://restcountries.com/v3.1/name/{country}"
        resp = requests.get(url, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                country_info = data[0]
                
                # Extract currencies
                currencies = []
                if "currencies" in country_info:
                    for code, info in country_info["currencies"].items():
                        name = info.get("name", "")
                        currencies.append({"code": code, "name": name})
                        
                # Extract languages
                languages = []
                if "languages" in country_info:
                    for code, name in country_info["languages"].items():
                        languages.append(name)
                        
                return {
                    "full_name": country_info.get("name", {}).get("official", ""),
                    "capital_city": country_info.get("capital", [""])[0] if country_info.get("capital") else "",
                    "region": country_info.get("region", ""),
                    "subregion": country_info.get("subregion", ""),
                    "currencies": currencies,
                    "languages_spoken": languages,
                    "population": country_info.get("population", 0),
                    "area_km2": country_info.get("area", 0),
                    "timezones": country_info.get("timezones", []),
                    "un_member": country_info.get("unMember", False),
                    "bordering_countries": country_info.get("borders", [])
                }
                
        return {"error": f"Failed to fetch country data. Status code: {resp.status_code}"}
        
    except Exception as e:
        return {"error": f"REST Countries internal error: {str(e)}"}
