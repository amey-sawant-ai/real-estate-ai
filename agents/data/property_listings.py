"""
99acres.com Property Listings Scraper

Fetches current property listings and prices from 99acres.com.
Implements web scraping with fallback to NHB RESIDEX data when scraping fails.
"""

import logging
import time
from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

logger = logging.getLogger(__name__)


def fetch_property_listings(location: str, budget: str = None) -> Dict[str, Any]:
    """
    Fetch current property listings from 99acres.com.
    
    Scrapes the website for listings in a given location and extracts:
    - Price per sqft
    - Total price
    - Area in sqft
    - Property type (1BHK/2BHK/3BHK)
    - Locality name
    
    Falls back to NHB RESIDEX data if scraping fails.
    
    Args:
        location: Location/city name (e.g., "Jogeshwari Mumbai", "Bangalore")
        budget: Optional budget constraint (e.g., "1 crore", "50 lakh")
        
    Returns:
        Dict with listings data structure or fallback data
        
    Example:
        {
            "location": "Jogeshwari Mumbai",
            "listings_found": 3,
            "average_price_per_sqft": 18500,
            "price_range": {
                "min_per_sqft": 14000,
                "max_per_sqft": 23000
            },
            "sample_listings": [
                {
                    "title": "2BHK in Jogeshwari West",
                    "total_price": "95 Lac",
                    "area_sqft": 550,
                    "price_per_sqft": 17272,
                    "locality": "Jogeshwari West"
                }
            ],
            "data_source": "99acres.com",
            "scraped_at": "2026-03-15"
        }
    """
    try:
        logger.info(f"Fetching property listings for {location}")
        
        # Be polite - add delay before scraping
        time.sleep(2)
        
        # Construct search URL
        location_encoded = quote(location)
        url = f"https://www.99acres.com/search/property/buy/{location_encoded}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse listings
        listings = _parse_listings(response.content, location)
        
        if listings and len(listings["sample_listings"]) > 0:
            logger.info(f"Successfully fetched {len(listings['sample_listings'])} listings for {location}")
            listings["data_source"] = "99acres.com"
            return listings
        else:
            logger.warning(f"No listings found for {location}, falling back to RESIDEX data")
            return _get_fallback_from_residex(location)
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching listings for {location}: {e}")
        return _get_fallback_from_residex(location)
    except Exception as e:
        logger.error(f"Error fetching listings for {location}: {e}")
        return _get_fallback_from_residex(location)


def _parse_listings(content: bytes, location: str) -> Dict[str, Any]:
    """
    Parse property listings from 99acres HTML content.
    
    Args:
        content: HTML content from 99acres
        location: Location being searched
        
    Returns:
        Dict with parsed listings or None
    """
    try:
        soup = BeautifulSoup(content, "html.parser")
        listings = []
        prices_per_sqft = []
        
        # Look for listing cards - 99acres typically uses specific div classes
        # Try multiple selectors as page structure may change
        listing_cards = soup.find_all("div", class_=["property-card", "srp-item", "srp-item-card"])
        
        if not listing_cards:
            # Try alternative selectors
            listing_cards = soup.find_all("div", {"data-listing-id": True})
        
        if not listing_cards:
            # Try to find any article or li elements that might contain listings
            listing_cards = soup.find_all(["article", "li"], class_=["listing", "property"])
        
        # Extract up to 5 listings
        for card in listing_cards[:5]:
            try:
                listing = _extract_listing_data(card)
                if listing:
                    listings.append(listing)
                    if listing.get("price_per_sqft"):
                        prices_per_sqft.append(listing["price_per_sqft"])
            except Exception as e:
                logger.warning(f"Error parsing individual listing: {e}")
                continue
        
        if not listings:
            return None
        
        # Calculate statistics
        avg_price_per_sqft = (
            sum(prices_per_sqft) / len(prices_per_sqft)
            if prices_per_sqft else 0
        )
        min_price_per_sqft = min(prices_per_sqft) if prices_per_sqft else 0
        max_price_per_sqft = max(prices_per_sqft) if prices_per_sqft else 0
        
        return {
            "location": location,
            "listings_found": len(listings),
            "average_price_per_sqft": round(avg_price_per_sqft, 2),
            "price_range": {
                "min_per_sqft": round(min_price_per_sqft, 2),
                "max_per_sqft": round(max_price_per_sqft, 2),
            },
            "sample_listings": listings,
        }
        
    except Exception as e:
        logger.error(f"Error parsing listings page: {e}")
        return None


def _extract_listing_data(card) -> Dict[str, Any]:
    """
    Extract individual listing data from a card element.
    
    Args:
        card: BeautifulSoup element representing a listing card
        
    Returns:
        Dict with listing data or None
    """
    try:
        listing = {}
        
        # Extract title
        title_elem = card.find(["h2", "h3", "a"], class_=["title", "heading"])
        if not title_elem:
            title_elem = card.find("a")
        listing["title"] = title_elem.get_text(strip=True) if title_elem else "Unknown"
        
        # Extract price
        price_elem = card.find(["span", "div"], class_=["price", "amount", "mrp"])
        price_text = price_elem.get_text(strip=True) if price_elem else ""
        listing["total_price"] = price_text
        
        # Extract area/sqft
        area_elem = card.find(["span", "div"], class_=["area", "super-area", "size"])
        if not area_elem:
            area_elem = card.find(["span", "div"], string=lambda x: x and "sqft" in x.lower() if x else False)
        
        area_text = area_elem.get_text(strip=True) if area_elem else ""
        area_sqft = _parse_area(area_text)
        listing["area_sqft"] = area_sqft
        
        # Extract price per sqft
        price_per_sqft_elem = card.find(["span", "div"], string=lambda x: x and "per sqft" in x.lower() if x else False)
        if price_per_sqft_elem:
            listing["price_per_sqft"] = _parse_price(price_per_sqft_elem.get_text())
        elif area_sqft and price_text:
            price_numeric = _parse_price(price_text)
            if price_numeric and area_sqft:
                listing["price_per_sqft"] = round(price_numeric / area_sqft, 2)
        
        # Extract locality
        locality_elem = card.find(["span", "div"], class_=["locality", "location", "address"])
        if not locality_elem:
            locality_elem = card.find(["span", "div"], string=lambda x: x and any(
                city in x.lower() for city in ["mumbai", "delhi", "bangalore", "pune", "hyderabad", "chennai", "west", "east"]
            ) if x else False)
        listing["locality"] = locality_elem.get_text(strip=True) if locality_elem else "Unknown"
        
        return listing if listing.get("title") else None
        
    except Exception as e:
        logger.warning(f"Error extracting listing data: {e}")
        return None


def _parse_price(price_text: str) -> float:
    """
    Parse price from text (handles formats like "95 Lac", "1 Cr", "95,00,000").
    
    Args:
        price_text: Price text string
        
    Returns:
        Price in base units (rupees) or 0 if parsing fails
    """
    try:
        price_text = price_text.lower().strip()
        
        # Remove common words
        price_text = price_text.replace("price:", "").replace("₹", "").strip()
        
        # Handle Crore (Cr)
        if "cr" in price_text:
            value = float(price_text.replace("cr", "").replace("crore", "").strip())
            return value * 10000000  # 1 Crore = 1 Cr = 10 million
        
        # Handle Lakh (Lac)
        if "lac" in price_text or "lakh" in price_text:
            value = float(price_text.replace("lac", "").replace("lakh", "").strip())
            return value * 100000  # 1 Lakh = 1 Lac = 100 thousand
        
        # Handle direct numbers with commas
        price_text = price_text.replace(",", "")
        return float(price_text)
        
    except (ValueError, AttributeError):
        return 0


def _parse_area(area_text: str) -> float:
    """
    Parse area from text (handles formats like "550 sqft", "50 sq.ft", "550").
    
    Args:
        area_text: Area text string
        
    Returns:
        Area in sqft or 0 if parsing fails
    """
    try:
        area_text = area_text.lower().strip()
        
        # Remove sqft/sq.ft/sq ft variations
        area_text = area_text.replace("sqft", "").replace("sq.ft", "").replace("sq ft", "").strip()
        
        # Remove commas and parse
        area_text = area_text.replace(",", "")
        return float(area_text)
        
    except (ValueError, AttributeError):
        return 0


def _get_fallback_from_residex(location: str) -> Dict[str, Any]:
    """
    Fallback to NHB RESIDEX data when listings scraping fails.
    
    Args:
        location: Location being searched
        
    Returns:
        Dict with fallback data structure
    """
    try:
        from data.nhb_residex import fetch_residex_data
        
        # Extract city name from location (e.g., "Jogeshwari Mumbai" -> "Mumbai")
        parts = location.split()
        city = parts[-1] if parts else location
        
        residex_data = fetch_residex_data(city)
        
        if "error" in residex_data:
            return {
                "location": location,
                "listings_found": 0,
                "average_price_per_sqft": 0,
                "price_range": {"min_per_sqft": 0, "max_per_sqft": 0},
                "sample_listings": [],
                "data_source": "99acres.com (unavailable) / RESIDEX fallback (failed)",
                "error": "Unable to fetch listings or fallback data",
            }
        
        # Format residex data as listings response
        avg_price = residex_data.get("price_range_inr_per_sqft", {}).get("average", 0)
        min_price = residex_data.get("price_range_inr_per_sqft", {}).get("min", 0)
        max_price = residex_data.get("price_range_inr_per_sqft", {}).get("max", 0)
        
        return {
            "location": location,
            "listings_found": 0,
            "average_price_per_sqft": avg_price,
            "price_range": {
                "min_per_sqft": min_price,
                "max_per_sqft": max_price,
            },
            "sample_listings": [],
            "data_source": "99acres.com (unavailable) / NHB RESIDEX fallback",
            "notes": f"Live listings unavailable; using RESIDEX index data for {city}",
        }
        
    except Exception as e:
        logger.error(f"Error creating fallback from RESIDEX: {e}")
        return {
            "location": location,
            "listings_found": 0,
            "average_price_per_sqft": 0,
            "price_range": {"min_per_sqft": 0, "max_per_sqft": 0},
            "sample_listings": [],
            "data_source": "99acres.com (unavailable)",
            "error": f"Failed to fetch data: {str(e)}",
        }
