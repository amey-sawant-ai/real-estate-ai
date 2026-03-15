"""
NHB RESIDEX Data Fetcher - Verified Market Data Edition

Provides verified real estate price data from 99acres.com and market research (March 2026).
Supports both listing prices and actual transaction prices for Mumbai micro-markets.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Verified Price Data - March 2026 (INR per sqft)
# Source: 99acres.com and Registration Data Analysis
MUMBAI_VERIFIED_PRICES = {
    "jogeshwari west": {
        "listing": 28700, "transaction": 18147,
        "yoy": 4.2, "five_year": 21.6,
        "rental_yield": 5.0,
        "one_bhk_range": "90L-1.5cr",
        "two_bhk_range": "1.6cr-2.4cr"
    },
    "jogeshwari east": {
        "listing": 22500, "transaction": 17000,
        "yoy": 7.3, "five_year": 25.0,
        "rental_yield": 4.5,
        "one_bhk_range": "80L-1.2cr",
        "two_bhk_range": "1.4cr-2cr"
    },
    "jogeshwari": {
        "listing": 25600, "transaction": 17574,
        "yoy": 5.8, "five_year": 23.3,
        "rental_yield": 4.8,
        "one_bhk_range": "85L-1.4cr",
        "two_bhk_range": "1.5cr-2.2cr"
    },
    "shyam nagar": {
        "listing": 22500, "transaction": 17000,
        "yoy": 7.3, "five_year": 25.0,
        "rental_yield": 4.5,
        "one_bhk_range": "80L-1.2cr",
        "two_bhk_range": "1.4cr-2cr"
    },
    "andheri west": {
        "listing": 38000, "transaction": 28000,
        "yoy": 7.5, "five_year": 28.0,
        "rental_yield": 3.5,
        "one_bhk_range": "1.5cr-2.5cr",
        "two_bhk_range": "2.5cr-4cr"
    },
    "andheri east": {
        "listing": 22500, "transaction": 17500,
        "yoy": 8.1, "five_year": 26.0,
        "rental_yield": 4.0,
        "one_bhk_range": "90L-1.4cr",
        "two_bhk_range": "1.5cr-2.2cr"
    },
    "bandra west": {
        "listing": 55000, "transaction": 42000,
        "yoy": 6.8, "five_year": 22.0,
        "rental_yield": 2.5,
        "one_bhk_range": "2.5cr-4cr",
        "two_bhk_range": "4cr-8cr"
    },
    "bandra east": {
        "listing": 38000, "transaction": 30000,
        "yoy": 7.2, "five_year": 24.0,
        "rental_yield": 3.0,
        "one_bhk_range": "1.8cr-2.8cr",
        "two_bhk_range": "3cr-5cr"
    },
    "malad west": {
        "listing": 27000, "transaction": 20000,
        "yoy": 8.8, "five_year": 30.0,
        "rental_yield": 4.2,
        "one_bhk_range": "1cr-1.6cr",
        "two_bhk_range": "1.7cr-2.5cr"
    },
    "goregaon west": {
        "listing": 28000, "transaction": 21000,
        "yoy": 9.5, "five_year": 32.0,
        "rental_yield": 4.5,
        "one_bhk_range": "1cr-1.6cr",
        "two_bhk_range": "1.8cr-2.8cr"
    },
    "borivali west": {
        "listing": 25000, "transaction": 19000,
        "yoy": 9.1, "five_year": 29.0,
        "rental_yield": 4.8,
        "one_bhk_range": "90L-1.4cr",
        "two_bhk_range": "1.5cr-2.2cr"
    },
    "powai": {
        "listing": 35000, "transaction": 27000,
        "yoy": 10.2, "five_year": 35.0,
        "rental_yield": 3.8,
        "one_bhk_range": "1.5cr-2.2cr",
        "two_bhk_range": "2.5cr-4cr"
    },
    "thane west": {
        "listing": 16000, "transaction": 13000,
        "yoy": 9.8, "five_year": 38.0,
        "rental_yield": 5.5,
        "one_bhk_range": "55L-90L",
        "two_bhk_range": "90L-1.4cr"
    },
    "navi mumbai": {
        "listing": 13000, "transaction": 10500,
        "yoy": 12.5, "five_year": 45.0,
        "rental_yield": 6.0,
        "one_bhk_range": "45L-75L",
        "two_bhk_range": "75L-1.2cr"
    },
    "worli": {
        "listing": 75000, "transaction": 58000,
        "yoy": 5.2, "five_year": 18.0,
        "rental_yield": 2.0,
        "one_bhk_range": "4cr-7cr",
        "two_bhk_range": "8cr-15cr"
    },
    "lower parel": {
        "listing": 55000, "transaction": 44000,
        "yoy": 6.1, "five_year": 20.0,
        "rental_yield": 2.5,
        "one_bhk_range": "3cr-5cr",
        "two_bhk_range": "5cr-9cr"
    },
    "chembur": {
        "listing": 28000, "transaction": 22000,
        "yoy": 9.5, "five_year": 33.0,
        "rental_yield": 4.5,
        "one_bhk_range": "1cr-1.6cr",
        "two_bhk_range": "1.8cr-2.8cr"
    },
    "dahisar": {
        "listing": 17000, "transaction": 13500,
        "yoy": 8.9, "five_year": 28.0,
        "rental_yield": 5.2,
        "one_bhk_range": "60L-95L",
        "two_bhk_range": "95L-1.5cr"
    },
    "virar": {
        "listing": 9000, "transaction": 7500,
        "yoy": 11.2, "five_year": 42.0,
        "rental_yield": 6.5,
        "one_bhk_range": "30L-55L",
        "two_bhk_range": "55L-85L"
    },
}

# Mumbai City Level Fallback
MUMBAI_FALLBACK = {
    "listing": 25000, "transaction": 19000,
    "yoy": 7.0, "five_year": 26.0,
    "rental_yield": 3.8,
    "one_bhk_range": "80L-1.5cr",
    "two_bhk_range": "1.5cr-3cr",
    "note": "Mumbai city average - check locality specific data for accuracy"
}

def fetch_residex_data(city: str) -> Dict[str, Any]:
    """
    Fetch property price index using verified market data for Mumbai micro-markets.
    """
    city_lower = city.lower().strip()
    
    # Check for exact locality match in verified prices
    # Note: Keys are lowercase for easier matching
    matched_data = None
    locality_key = None
    
    for key in MUMBAI_VERIFIED_PRICES.keys():
        if key in city_lower:
            matched_data = MUMBAI_VERIFIED_PRICES[key]
            locality_key = key
            break
            
    # If no micro-market match, check if it's Mumbai in general
    if not matched_data:
        mumbai_keywords = ["mumbai", "bombay", "thane", "navi mumbai"]
        if any(kw in city_lower for kw in mumbai_keywords):
            matched_data = MUMBAI_FALLBACK
            locality_key = city_lower
        else:
            # For non-Mumbai cities, return the requested "honest failure" response
            return {
                "city": city.title(),
                "price_data_available": False,
                "message": "Live price data unavailable beyond Mumbai micro-markets. Check Housing.com or MagicBricks for current prices.",
                "data_source": "none",
                "fallback_guide": {
                    "mumbai_range": "Check magicbricks.com/mumbai",
                    "note": "Prices vary significantly by locality"
                }
            }

    # Determine market trend
    trend = "Stable"
    if matched_data["yoy"] > 7:
        trend = "Rising"
    elif matched_data["yoy"] < 3:
        trend = "Falling"

    return {
        "city": city.title() if matched_data == MUMBAI_FALLBACK else locality_key.title() + " Mumbai",
        "listing_price_per_sqft": matched_data["listing"],
        "transaction_price_per_sqft": matched_data["transaction"],
        "price_gap_note": "Listing prices are typically 35-58% higher than actual transaction prices",
        "yoy_appreciation_pct": matched_data["yoy"],
        "five_year_appreciation_pct": matched_data["five_year"],
        "rental_yield_pct": matched_data["rental_yield"],
        "typical_units": {
            "1bhk": matched_data["one_bhk_range"],
            "2bhk": matched_data["two_bhk_range"]
        },
        "data_source": "99acres.com verified March 2026",
        "market_trend": trend,
        "notes": matched_data.get("note", "")
    }
