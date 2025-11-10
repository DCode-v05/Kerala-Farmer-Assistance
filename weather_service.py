from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import random
import os
import json
import requests
import logging

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def safe_get(url, params=None, timeout=10):
    """Safe HTTP GET request with error handling"""
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response
    except Exception as e:
        logger.error(f"HTTP request failed: {e}")
        return None

def json_or_none(response):
    """Parse JSON response or return None"""
    if not response:
        return None
    try:
        return response.json()
    except Exception as e:
        logger.error(f"JSON parsing failed: {e}")
        return None

def calculate_climate_summary(temperature: float, humidity: int, rainfall: float) -> Dict[str, Any]:
    """Calculate climate summary probabilities based on weather data."""
    # Calculate sunny probability
    sunny_prob = 0.0
    if temperature > 25 and rainfall == 0 and humidity < 70:
        sunny_prob = min(90, 20 + (temperature - 25) * 2 - (humidity - 50) * 0.5)
    elif temperature > 30 and rainfall == 0:
        sunny_prob = min(80, 30 + (temperature - 30) * 3)
    else:
        sunny_prob = max(0, 10 + (temperature - 20) * 1.5 - humidity * 0.3)
    
    # Calculate rainy probability
    rainy_prob = 0.0
    if rainfall > 0:
        rainy_prob = min(95, 50 + rainfall * 10)
    elif humidity > 80:
        rainy_prob = min(70, 30 + (humidity - 80) * 2)
    else:
        rainy_prob = max(0, humidity * 0.2)
    
    # Calculate cloudy probability
    cloudy_prob = 100 - sunny_prob - rainy_prob
    cloudy_prob = max(0, min(100, cloudy_prob))
    
    # Determine most likely climate
    probabilities = {
        "sunny": sunny_prob,
        "rainy": rainy_prob,
        "cloudy": cloudy_prob
    }
    most_likely = max(probabilities, key=probabilities.get)
    
    return {
        "sunny_probability": round(sunny_prob, 1),
        "rainy_probability": round(rainy_prob, 1),
        "cloudy_probability": round(cloudy_prob, 1),
        "most_likely_climate": most_likely
    }


def fetch_weather(latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(["temperature_2m", "relative_humidity_2m", "rain", "windspeed_10m"]),
        "timezone": "auto",
    }
    resp = safe_get(OPEN_METEO_URL, params=params)
    data = json_or_none(resp)
    if not data or "hourly" not in data:
        return None
    hourly = data["hourly"]
    # take the last available hour as current-ish snapshot
    idx = -1
    try:
        idx = len(hourly.get("time", [])) - 1
    except Exception:
        pass
    if idx < 0:
        return None
    def pick(key: str):
        arr = hourly.get(key)
        return arr[idx] if isinstance(arr, list) and len(arr) > idx else None

    return {
        "timestamp": hourly.get("time", [None])[idx],
        "temperature": pick("temperature_2m"),
        "humidity": pick("relative_humidity_2m"),
        "rainfall": pick("rain"),
        "windspeed": pick("windspeed_10m"),
        "raw": data,
    }


def get_current_weather() -> Dict[str, Any]:
    """Get current weather data for Kerala from Open-Meteo API."""
    # Kerala coordinates (Kochi as central point)
    kerala_lat = 9.9312
    kerala_lon = 76.2673
    
    try:
        weather_data = fetch_weather(kerala_lat, kerala_lon)
        if weather_data:
            temperature = round(weather_data.get("temperature", 25.0), 1)
            humidity = int(weather_data.get("humidity", 60))
            rainfall = round(weather_data.get("rainfall", 0.0), 1)
            windspeed = round(weather_data.get("windspeed", 0.0), 1)
            
            # Calculate climate summary
            climate_summary = calculate_climate_summary(temperature, humidity, rainfall)
            
            return {
                "temperature": temperature,
                "humidity": humidity,
                "rainfall": rainfall,
                "windspeed": windspeed,
                "timestamp": weather_data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
                "climate_summary": climate_summary,
                "location": "Kerala, India"
            }
    except Exception as e:
        logger.error(f"Weather API error: {e}")
    
    # Fallback to mock data if API fails
    temperature = round(random.uniform(25.0, 35.0), 1)
    humidity = random.randint(60, 90)
    rainfall = round(random.uniform(0.0, 5.0), 1)
    windspeed = round(random.uniform(0.0, 15.0), 1)
    
    # Calculate climate summary for fallback data
    climate_summary = calculate_climate_summary(temperature, humidity, rainfall)
    
    return {
        "temperature": temperature,
        "humidity": humidity,
        "rainfall": rainfall,
        "windspeed": windspeed,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "climate_summary": climate_summary,
        "location": "Kerala, India (Simulated)"
    }


def get_weather_forecast() -> Dict[str, Any]:
    """Get 7-day weather forecast for Kerala from Open-Meteo API."""
    # Kerala coordinates (Kochi as central point)
    kerala_lat = 9.9312
    kerala_lon = 76.2673
    
    try:
        # Fetch forecast data from Open-Meteo API
        params = {
            "latitude": kerala_lat,
            "longitude": kerala_lon,
            "daily": ",".join(["temperature_2m_max", "temperature_2m_min", "relative_humidity_2m", "rain_sum", "windspeed_10m_max"]),
            "timezone": "Asia/Kolkata",
            "forecast_days": 7
        }
        
        resp = safe_get(OPEN_METEO_URL, params=params)
        data = json_or_none(resp)
        
        if data and "daily" in data:
            daily = data["daily"]
            forecast = []
            
            for i in range(7):
                date = daily.get("time", [])[i] if i < len(daily.get("time", [])) else None
                if date:
                    # Calculate average temperature from max and min
                    temp_max = daily.get("temperature_2m_max", [0])[i] if i < len(daily.get("temperature_2m_max", [])) else 25
                    temp_min = daily.get("temperature_2m_min", [0])[i] if i < len(daily.get("temperature_2m_min", [])) else 25
                    avg_temp = (temp_max + temp_min) / 2
                    
                    humidity = daily.get("relative_humidity_2m", [60])[i] if i < len(daily.get("relative_humidity_2m", [])) else 60
                    rainfall = daily.get("rain_sum", [0])[i] if i < len(daily.get("rain_sum", [])) else 0
                    windspeed = daily.get("windspeed_10m_max", [0])[i] if i < len(daily.get("windspeed_10m_max", [])) else 0
                    
                    # Calculate climate summary for this day
                    climate_summary = calculate_climate_summary(avg_temp, int(humidity), rainfall)
                    
                    forecast.append({
                        "date": date,
                        "temperature": round(avg_temp, 1),
                        "temp_max": round(temp_max, 1),
                        "temp_min": round(temp_min, 1),
                        "humidity": int(humidity),
                        "rainfall": round(rainfall, 1),
                        "windspeed": round(windspeed, 1),
                        "climate_summary": climate_summary
                    })
            
            if forecast:
                return {
                    "forecast": forecast,
                    "total_days": len(forecast),
                    "location": "Kerala, India"
                }
    except Exception as e:
        logger.error(f"Weather forecast API error: {e}")
    
    # Fallback to mock data if API fails
    forecast = []
    today = datetime.now().date()
    
    for i in range(7):
        date = today + timedelta(days=i)
        temp_max = round(random.uniform(28.0, 36.0), 1)
        temp_min = round(random.uniform(20.0, 28.0), 1)
        avg_temp = (temp_max + temp_min) / 2
        humidity = random.randint(55, 95)
        rainfall = round(random.uniform(0.0, 8.0), 1)
        windspeed = round(random.uniform(0.0, 20.0), 1)
        
        # Calculate climate summary for this day
        climate_summary = calculate_climate_summary(avg_temp, humidity, rainfall)
        
        forecast.append({
            "date": date.strftime("%Y-%m-%d"),
            "temperature": round(avg_temp, 1),
            "temp_max": temp_max,
            "temp_min": temp_min,
            "humidity": humidity,
            "rainfall": rainfall,
            "windspeed": windspeed,
            "climate_summary": climate_summary
        })
    
    return {
        "forecast": forecast,
        "total_days": 7,
        "location": "Kerala, India (Simulated)"
    }


def get_weather_advisory(current_weather: Dict[str, Any], forecast: Dict[str, Any]) -> Dict[str, Any]:
    """Generate farming advisory based on weather conditions"""
    advisories = []
    
    # Current weather advisories
    temp = current_weather.get("temperature", 25)
    humidity = current_weather.get("humidity", 60)
    rainfall = current_weather.get("rainfall", 0)
    
    if temp > 35:
        advisories.append("High temperature warning: Provide shade for crops and increase irrigation frequency.")
    if humidity > 85:
        advisories.append("High humidity: Monitor for fungal diseases and ensure good air circulation.")
    if rainfall > 10:
        advisories.append("Heavy rainfall: Avoid field operations and ensure proper drainage.")
    
    # Forecast-based advisories
    forecast_data = forecast.get("forecast", [])
    if forecast_data:
        next_3_days = forecast_data[:3]
        total_rain = sum(day.get("rainfall", 0) for day in next_3_days)
        
        if total_rain > 20:
            advisories.append("Heavy rain expected in next 3 days: Postpone spraying and fertilizer application.")
        elif total_rain == 0:
            advisories.append("No rain expected: Plan irrigation schedule accordingly.")
        
        max_temps = [day.get("temp_max", 30) for day in next_3_days]
        if max(max_temps) > 38:
            advisories.append("Extreme heat expected: Provide crop protection and increase watering.")
    
    # Default advisory if no specific conditions
    if not advisories:
        advisories.append("Weather conditions are favorable for normal farming operations.")
    
    # Seasonal advisories for Kerala
    current_month = datetime.now().month
    if current_month in [6, 7, 8, 9]:  # Monsoon season
        advisories.append("Monsoon season: Focus on drainage management and disease prevention.")
    elif current_month in [12, 1, 2]:  # Winter season
        advisories.append("Winter season: Good time for land preparation and vegetable cultivation.")
    elif current_month in [3, 4, 5]:  # Summer season
        advisories.append("Summer season: Ensure adequate water supply and heat protection for crops.")
    
    return {
        "advisories": advisories,
        "priority": "high" if len(advisories) > 2 else "medium",
        "generated_at": datetime.now().isoformat()
    }