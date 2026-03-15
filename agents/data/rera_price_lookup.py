import pandas as pd
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

CSV_PATH = os.path.join(os.path.dirname(__file__), "rera_data.csv")

def load_rera_data():
    try:
        # Check if file exists
        if not os.path.exists(CSV_PATH):
             logger.error(f"RERA CSV not found at {CSV_PATH}")
             return None
        df = pd.read_csv(CSV_PATH)
        return df
    except Exception as e:
        logger.error(f"Failed to load RERA data: {e}")
        return None

def fetch_rera_project_data(location: str) -> Dict[str, Any]:
    df = load_rera_data()
    
    if df is None:
        return {
            "source": "RERA Maharashtra",
            "data_available": False,
            "message": "RERA dataset not loaded"
        }
    
    location_lower = location.lower()
    
    # Search across all text columns for location match
    mask = df.apply(
        lambda row: row.astype(str).str.lower().str.contains(
            location_lower, na=False
        ).any(), 
        axis=1
    )
    matches = df[mask]
    
    if len(matches) == 0:
        # Try with just first word of location
        words = location_lower.split()
        if words:
            first_word = words[0]
            mask2 = df.apply(
                lambda row: row.astype(str).str.lower().str.contains(
                    first_word, na=False
                ).any(),
                axis=1
            )
            matches = df[mask2]
    
    if len(matches) == 0:
        return {
            "source": "RERA Maharashtra",
            "data_available": False,
            "location": location,
            "message": "No RERA registered projects found for this location"
        }
    
    # Return summary of found projects (limited to 5 for context window)
    return {
        "source": "RERA Maharashtra (Government Registered Data)",
        "data_available": True,
        "location": location,
        "total_projects_found": len(matches),
        "projects": matches.head(5).to_dict(orient="records"),
        "disclaimer": "RERA project registration data. Prices are developer registered values."
    }
