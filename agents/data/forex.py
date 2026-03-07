import requests

COUNTRY_CURRENCY_MAP = {
    "india": "INR",
    "united arab emirates": "AED",
    "uae": "AED",
    "singapore": "SGD",
    "uk": "GBP",
    "united kingdom": "GBP",
    "japan": "JPY",
    "united states": "USD",
    "usa": "USD",
    "us": "USD",
    "australia": "AUD",
    "canada": "CAD",
    "germany": "EUR",
    "france": "EUR",
    "italy": "EUR",
    "spain": "EUR",
    "netherlands": "EUR"
}

def get_currency_code(country_name: str) -> str:
    country_lower = country_name.lower().strip()
    if country_lower in COUNTRY_CURRENCY_MAP:
        return COUNTRY_CURRENCY_MAP[country_lower]
        
    try:
        # Fallback to RestCountries API to automatically resolve almost any country
        url = f"https://restcountries.com/v3.1/name/{country_name}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data and "currencies" in data[0]:
                return list(data[0]["currencies"].keys())[0]
    except Exception:
        pass
        
    return None

def fetch_forex_data(country_name: str) -> dict:
    if not country_name:
        return {"error": "Country name not provided"}
        
    currency_code = get_currency_code(country_name)
    if not currency_code:
        return {"error": f"Could not determine currency for '{country_name}'"}
        
    try:
        # Public Open Exchange Rates endpoint (base=USD)
        url = "https://open.er-api.com/v6/latest/USD"
        resp = requests.get(url, timeout=10)
        
        if resp.status_code != 200:
            return {"error": f"Forex API error: {resp.status_code}"}
            
        data = resp.json()
        rates = data.get("rates", {})
        
        if currency_code not in rates:
            return {"error": f"Currency {currency_code} not found in exchange rates"}
            
        # All rates are based on 1 USD
        usd_to_local = rates[currency_code]
        usd_to_eur = rates.get("EUR", 1.0)
        usd_to_gbp = rates.get("GBP", 1.0)
        
        # Calculate cross rates
        # If 1 USD = X Local, and 1 USD = Y EUR => 1 EUR = X/Y Local
        eur_to_local = usd_to_local / usd_to_eur if usd_to_eur else 0
        gbp_to_local = usd_to_local / usd_to_gbp if usd_to_gbp else 0
        
        return {
            "currency_code": currency_code,
            "rate_vs_usd": round(usd_to_local, 4),
            "rate_vs_eur": round(eur_to_local, 4),
            "rate_vs_gbp": round(gbp_to_local, 4),
            "summary": f"1 USD = {round(usd_to_local, 2)} {currency_code}"
        }
        
    except Exception as e:
        return {"error": f"Forex internal error: {str(e)}"}
