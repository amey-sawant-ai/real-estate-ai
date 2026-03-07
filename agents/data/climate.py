import requests

def fetch_climate_data(lat: float, lng: float) -> dict:
    try:
        # 1. Forecast for today
        forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto&forecast_days=1"
        forecast_resp = requests.get(forecast_url, timeout=10)
        forecast_data = forecast_resp.json()
        
        # 2. Archive for averages (2020-2023)
        archive_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lng}&start_date=2020-01-01&end_date=2023-12-31&daily=precipitation_sum,temperature_2m_max,temperature_2m_min&timezone=auto"
        archive_resp = requests.get(archive_url, timeout=15)
        archive_data = archive_resp.json()
        
        if "daily" not in archive_data:
            return {"error": "Climate data not found for these coordinates"}
            
        daily = archive_data["daily"]
        precip = [p for p in daily.get("precipitation_sum", []) if p is not None]
        max_temps = [t for t in daily.get("temperature_2m_max", []) if t is not None]
        min_temps = [t for t in daily.get("temperature_2m_min", []) if t is not None]
        
        if not precip or not max_temps or not min_temps:
            return {"error": "Insufficient climate data"}
            
        # Yearly rainfall = total over 4 years / 4
        avg_annual_rainfall = sum(precip) / 4.0
        avg_max_temp = sum(max_temps) / len(max_temps)
        avg_min_temp = sum(min_temps) / len(min_temps)
        
        # Calculate maximum historical temperature for heat risk
        abs_max_temp = max(max_temps)
        
        if avg_annual_rainfall > 2000:
            flood_risk = "High"
        elif 1000 <= avg_annual_rainfall <= 2000:
            flood_risk = "Medium"
        else:
            flood_risk = "Low"
            
        if abs_max_temp > 40:
            heat_risk = "High"
        elif 30 <= abs_max_temp <= 40:
            heat_risk = "Medium"
        else:
            heat_risk = "Low"
            
        current_forecast = {}
        if "daily" in forecast_data and forecast_data["daily"].get("temperature_2m_max"):
            current_forecast = {
                "max_temp": forecast_data["daily"]["temperature_2m_max"][0],
                "min_temp": forecast_data["daily"]["temperature_2m_min"][0],
                "precipitation": forecast_data["daily"]["precipitation_sum"][0]
            }

        return {
            "average_annual_rainfall_mm": round(avg_annual_rainfall, 2),
            "average_max_temperature_celsius": round(avg_max_temp, 2),
            "average_min_temperature_celsius": round(avg_min_temp, 2),
            "absolute_max_temperature_celsius": round(abs_max_temp, 2),
            "flood_risk": flood_risk,
            "heat_risk": heat_risk,
            "current_forecast": current_forecast
        }
        
    except Exception as e:
        return {"error": f"Climate API internal error: {str(e)}"}
