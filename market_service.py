from typing import Any, Dict, List, Optional
import os
import re
import requests
from datetime import datetime, timedelta
import logging
import random
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Optional pandas import
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    PANDAS_AVAILABLE = False
    logging.warning("Pandas not available. Some advanced market analysis features may be limited.")

logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
    logger.warning("BeautifulSoup not available. HTML scraping will be disabled.")

# Load environment variables
DATA_GOV_API_URL = "https://api.data.gov.in/resource/{resource_id}"
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
DATA_GOV_RESOURCE_ID = os.getenv("DATA_GOV_RESOURCE_ID", "")
DATA_GOV_RESOURCE_ID_CURRENT = os.getenv("DATA_GOV_RESOURCE_ID_CURRENT", "")
DATA_GOV_RESOURCE_ID_HISTORY = os.getenv("DATA_GOV_RESOURCE_ID_HISTORY", "")

# Legacy HTML scraping fallback
AGMARKNET_KERALA_URL = (
    "https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity=0&Tx_State=KL&Tx_District=0&Tx_Market=0&DateFrom=0&DateTo=0&Fr_Date=0&To_Date=0&Tx_Trend=0&Tx_CommodityHead=--Select--&Tx_StateHead=Kerala&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select--"
)

def safe_get(url, params=None, timeout=20):
    """Safe HTTP GET request with error handling"""
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response
    except Exception as e:
        logger.error(f"HTTP request failed: {e}")
        return None

def _to_float(text: str) -> float:
    """Convert text to float, handling various formats"""
    cleaned = re.sub(r"[^0-9.]+", "", text or "")
    try:
        return float(cleaned) if cleaned else 0.0
    except Exception:
        return 0.0

def fetch_data_from_resource(resource_id: str, filters: Dict[str, Any], limit: int = 200) -> List[Dict[str, Any]]:
    """Generic function to fetch data from any data.gov.in resource."""
    if not (DATA_GOV_API_KEY and resource_id):
        return []
    
    url = DATA_GOV_API_URL.format(resource_id=resource_id)
    params = {
        "api-key": DATA_GOV_API_KEY,
        "format": "json",
        "limit": limit
    }
    params.update(filters)
    
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        
        data = resp.json()
        records = data.get("records", [])
        
        # Convert to standardized format
        results: List[Dict[str, Any]] = []
        for r in records:
            # Handle different field name formats
            commodity = r.get("commodity", r.get("Commodity", ""))
            market = r.get("market", r.get("market_center", r.get("Market", "")))
            min_price = r.get("min_price", r.get("min_price_(rs/quintal)", r.get("Min_Price", "")))
            max_price = r.get("max_price", r.get("max_price_(rs/quintal)", r.get("Max_Price", "")))
            modal_price = r.get("modal_price", r.get("modal_price_(rs/quintal)", r.get("Modal_Price", "")))
            date = r.get("arrival_date", r.get("date", r.get("Arrival_Date", "")))
            district = r.get("district", r.get("District", ""))
            state = r.get("state", r.get("State", "Kerala"))
            
            # Only include records from Kerala
            if state.lower() == "kerala" or state.lower() == "kl":
                results.append({
                    "commodity": commodity,
                    "market": market,
                    "min_price": _to_float(str(min_price)),
                    "max_price": _to_float(str(max_price)),
                    "modal_price": _to_float(str(modal_price)),
                    "date": date,
                    "district": district,
                    "state": "Kerala",
                })
        
        return results
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API Request failed for resource {resource_id}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error for resource {resource_id}: {e}")
        return []

def fetch_current_prices(crop_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch current/latest daily market prices."""
    logger.info(f"Fetching current prices for {crop_name or 'all crops'}...")
    
    filters = {"filters[state]": "Kerala"}
    if crop_name:
        filters["filters[commodity]"] = crop_name
    
    # Try current dataset first
    if DATA_GOV_RESOURCE_ID_CURRENT:
        records = fetch_data_from_resource(DATA_GOV_RESOURCE_ID_CURRENT, filters, limit=200)
        if records:
            logger.info(f"Current dataset: {len(records)} records")
            return records
    
    # Fallback to legacy dataset
    if DATA_GOV_RESOURCE_ID:
        records = fetch_data_from_resource(DATA_GOV_RESOURCE_ID, filters, limit=200)
        if records:
            logger.info(f"Legacy dataset: {len(records)} records")
            return records
    
    logger.warning("No current data available")
    return []

def fetch_history_prices(crop_name: Optional[str] = None, days: int = 7) -> List[Dict[str, Any]]:
    """Fetch historical variety-wise daily market prices."""
    logger.info(f"Fetching {days}-day history for {crop_name or 'all crops'}...")
    
    if not DATA_GOV_RESOURCE_ID_HISTORY or not DATA_GOV_API_KEY:
        logger.error("History Resource ID or API key not configured")
        return []
    
    all_records = []
    today = datetime.now().date()
    
    # Fetch data day by day
    for i in range(days):
        target_date = today - timedelta(days=i)
        date_str = target_date.strftime("%d-%m-%Y")  # Use dd-MM-yyyy format
        
        params = {
            "api-key": DATA_GOV_API_KEY,
            "format": "json",
            "limit": 100,
            "filters[State]": "Kerala",
            "filters[Commodity]": crop_name or "Banana",
            "filters[Arrival_Date]": date_str
        }
        
        try:
            url = f"https://api.data.gov.in/resource/{DATA_GOV_RESOURCE_ID_HISTORY}"
            resp = requests.get(url, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            records = data.get("records", [])
            
            if records:
                logger.info(f"Day {i+1} ({date_str}): {len(records)} records")
                # Convert to standard format
                for r in records:
                    all_records.append({
                        "commodity": r.get("Commodity", ""),
                        "market": r.get("Market", ""),
                        "min_price": float(r.get("Min_Price", 0)),
                        "max_price": float(r.get("Max_Price", 0)),
                        "modal_price": float(r.get("Modal_Price", 0)),
                        "date": r.get("Arrival_Date", ""),
                        "district": r.get("District", ""),
                        "state": r.get("State", "Kerala")
                    })
            else:
                logger.info(f"Day {i+1} ({date_str}): No data")
                
        except Exception as e:
            logger.error(f"Day {i+1} ({date_str}): Error - {e}")
    
    logger.info(f"Total historical records: {len(all_records)}")
    return all_records

def fetch_combined_prices(crop_name: Optional[str] = None, days: int = 7) -> List[Dict[str, Any]]:
    """Fetch combined current + historical prices for comprehensive coverage."""
    logger.info(f"Fetching combined prices for {crop_name or 'all crops'}...")
    
    # Get current prices (latest snapshot)
    current_records = fetch_current_prices(crop_name)
    
    # Get historical prices (past N days)
    history_records = fetch_history_prices(crop_name, days)
    
    # Merge while avoiding duplicates
    seen = set()
    merged = []
    
    # Add historical records first (older data)
    for record in history_records:
        key = (record.get("commodity"), record.get("market"), record.get("date"))
        if key not in seen:
            seen.add(key)
            merged.append(record)
    
    # Add current records (newer data, may override historical)
    for record in current_records:
        key = (record.get("commodity"), record.get("market"), record.get("date"))
        if key not in seen:
            seen.add(key)
            merged.append(record)
    
    logger.info(f"Combined data: {len(merged)} unique records")
    return merged

def get_kerala_market_prices(crop_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Get Kerala market prices with fallback to mock data"""
    
    # Try to fetch real data first
    if DATA_GOV_API_KEY and (DATA_GOV_RESOURCE_ID_CURRENT or DATA_GOV_RESOURCE_ID_HISTORY):
        try:
            real_data = fetch_combined_prices(crop_name, days=5)
            if real_data:
                return real_data[:limit]
        except Exception as e:
            logger.error(f"Failed to fetch real market data: {e}")
    
    # Fallback to mock data for demonstration
    logger.info("Using mock market data")
    mock_crops = [
        "Paddy (Uma)", "Coconut", "Rubber", "Black Pepper", "Cardamom",
        "Banana (Nendran)", "Ginger", "Turmeric", "Cashew", "Coffee"
    ]
    
    markets = [
        "Kochi Spice Market", "Alappuzha Mandi", "Kottayam Market",
        "Thrissur Agricultural Market", "Kozhikode Spice Bazaar"
    ]
    
    districts = ["Ernakulam", "Alappuzha", "Kottayam", "Thrissur", "Kozhikode"]
    
    mock_data = []
    crops_to_use = [crop_name] if crop_name else mock_crops[:10]
    
    for crop in crops_to_use:
        for i in range(min(3, limit // len(crops_to_use))):  # 3 entries per crop
            market = random.choice(markets)
            district = random.choice(districts)
            
            # Generate realistic price ranges for different crops
            base_prices = {
                "Paddy (Uma)": (2200, 2400),
                "Coconut": (30, 35),
                "Rubber": (180, 200),
                "Black Pepper": (550, 600),
                "Cardamom": (1500, 1800),
                "Banana (Nendran)": (35, 45),
                "Ginger": (60, 80),
                "Turmeric": (90, 120),
                "Cashew": (800, 900),
                "Coffee": (150, 180)
            }
            
            min_price, max_price = base_prices.get(crop, (50, 100))
            modal_price = (min_price + max_price) / 2
            
            # Add some variation
            variation = random.uniform(0.9, 1.1)
            min_price = round(min_price * variation, 2)
            max_price = round(max_price * variation, 2)
            modal_price = round(modal_price * variation, 2)
            
            mock_data.append({
                "commodity": crop,
                "market": market,
                "min_price": min_price,
                "max_price": max_price,
                "modal_price": modal_price,
                "date": (datetime.now() - timedelta(days=random.randint(0, 5))).strftime("%d-%m-%Y"),
                "district": district,
                "state": "Kerala"
            })
    
    return mock_data[:limit]

def get_price_trends(crop_name: str, days: int = 7) -> Dict[str, Any]:
    """Get price trends for a specific crop"""
    try:
        # Try to get real data
        historical_data = fetch_history_prices(crop_name, days)
        
        if not historical_data:
            # Generate mock trend data
            logger.info(f"Generating mock price trend for {crop_name}")
            historical_data = []
            base_price = random.uniform(50, 200)
            
            for i in range(days):
                date = (datetime.now() - timedelta(days=days-i-1)).strftime("%d-%m-%Y")
                # Add trend and random variation
                trend_factor = 1 + (i * 0.02)  # Slight upward trend
                price = base_price * trend_factor * random.uniform(0.95, 1.05)
                
                historical_data.append({
                    "commodity": crop_name,
                    "market": "Kerala Average",
                    "modal_price": round(price, 2),
                    "date": date,
                    "district": "All",
                    "state": "Kerala"
                })
        
        # Calculate trend analysis
        prices = [item.get("modal_price", 0) for item in historical_data if item.get("modal_price", 0) > 0]
        
        if len(prices) < 2:
            return {
                "crop": crop_name,
                "trend": "insufficient_data",
                "data": historical_data,
                "analysis": "Insufficient data for trend analysis"
            }
        
        # Calculate trend
        price_change = prices[-1] - prices[0]
        percent_change = (price_change / prices[0]) * 100 if prices[0] > 0 else 0
        
        if percent_change > 5:
            trend = "increasing"
        elif percent_change < -5:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "crop": crop_name,
            "trend": trend,
            "percent_change": round(percent_change, 2),
            "current_price": prices[-1] if prices else 0,
            "price_range": {
                "min": min(prices),
                "max": max(prices),
                "avg": round(sum(prices) / len(prices), 2)
            },
            "data": historical_data,
            "analysis": f"Price trend is {trend} with {abs(percent_change):.1f}% change over {days} days"
        }
        
    except Exception as e:
        logger.error(f"Error getting price trends: {e}")
        return {
            "crop": crop_name,
            "trend": "error",
            "data": [],
            "analysis": "Unable to fetch price trend data"
        }

def get_market_advisory(price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate market advisory based on price data"""
    if not price_data:
        return {
            "advisory": "No market data available for advisory",
            "recommendations": [],
            "priority": "low"
        }
    
    advisories = []
    recommendations = []
    
    # Analyze price patterns
    crops_analyzed = {}
    for item in price_data:
        crop = item.get("commodity", "")
        price = item.get("modal_price", 0)
        
        if crop and price > 0:
            if crop not in crops_analyzed:
                crops_analyzed[crop] = []
            crops_analyzed[crop].append(price)
    
    # Generate recommendations
    for crop, prices in crops_analyzed.items():
        avg_price = sum(prices) / len(prices)
        max_price = max(prices)
        min_price = min(prices)
        
        price_variance = (max_price - min_price) / avg_price * 100 if avg_price > 0 else 0
        
        if price_variance > 20:
            advisories.append(f"High price volatility observed for {crop}")
            recommendations.append(f"Monitor {crop} prices closely before selling")
        
        if len(prices) > 1:
            recent_price = prices[-1]
            older_price = prices[0]
            change = (recent_price - older_price) / older_price * 100 if older_price > 0 else 0
            
            if change > 10:
                advisories.append(f"{crop} prices are trending upward (+{change:.1f}%)")
                recommendations.append(f"Good time to sell {crop}")
            elif change < -10:
                advisories.append(f"{crop} prices are declining ({change:.1f}%)")
                recommendations.append(f"Consider holding {crop} for better prices")
    
    # Default advisory
    if not advisories:
        advisories.append("Market conditions are stable")
        recommendations.append("Continue with normal trading activities")
    
    # Seasonal advisories
    current_month = datetime.now().month
    if current_month in [10, 11, 12]:  # Post-harvest season
        advisories.append("Post-harvest season: Expect lower prices for major crops")
        recommendations.append("Consider value addition or storage for better prices")
    elif current_month in [4, 5, 6]:  # Pre-monsoon
        advisories.append("Pre-monsoon period: Good time for selling stored produce")
    
    priority = "high" if len(advisories) > 2 else "medium"
    
    return {
        "advisory": "; ".join(advisories),
        "recommendations": recommendations,
        "priority": priority,
        "generated_at": datetime.now().isoformat(),
        "crops_analyzed": list(crops_analyzed.keys())
    }


def get_market_advisory(crop_name: str, farmer_location: Optional[str] = None) -> Dict[str, Any]:
    """Generate AI-powered market advisory using Gemini - main function used by app.py"""
    try:
        logger.info(f"🔄 Generating market advisory for {crop_name}")
        
        # Get current market data
        market_prices = get_kerala_market_prices(crop_name=crop_name, limit=10)
        price_trends = get_price_trends(crop_name, days=7)
        
        # Initialize Gemini AI
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Prepare comprehensive prompt for market analysis
        prompt = f"""
As an agricultural market expert for Kerala, India, provide comprehensive market advisory for {crop_name}.

Current Market Data:
{json.dumps(market_prices[:5], indent=2)}

Price Trends (Last 7 days):
{json.dumps(price_trends, indent=2)}

Farmer Location: {farmer_location or "Kerala"}

Please provide a detailed market advisory in JSON format with these sections:

1. **current_situation**: Brief overview of current market conditions
2. **price_analysis**: 
   - current_price_range: [min, max] in Rs/Quintal
   - trend_assessment: "rising/falling/stable/volatile"
   - market_strength: "strong/moderate/weak"
3. **selling_recommendations**:
   - best_markets: List of top 3 markets with reasons
   - optimal_timing: When to sell (immediate/wait/seasonal advice)
   - quality_focus: What quality aspects to emphasize
4. **market_insights**:
   - demand_factors: What's driving current demand
   - supply_situation: Current supply conditions
   - seasonal_outlook: Expected changes in coming weeks
5. **actionable_advice**:
   - immediate_actions: What farmer should do now
   - preparation_tips: How to prepare crop for best prices
   - market_monitoring: What indicators to watch
6. **risk_assessment**:
   - price_volatility: Risk level (high/medium/low)
   - market_risks: Potential challenges
   - mitigation_strategies: How to reduce risks

Focus on practical, actionable advice for Kerala farmers. Consider local market dynamics, transportation costs, and seasonal patterns.
Provide specific recommendations based on the actual price data and trends shown above.
"""

        # Generate AI advisory
        response = model.generate_content(prompt)
        ai_analysis = response.text
        
        # Try to parse as JSON, fallback to structured text
        try:
            advisory_data = json.loads(ai_analysis)
        except json.JSONDecodeError:
            # If not valid JSON, create structured response from text
            advisory_data = {
                "current_situation": "Market analysis generated",
                "price_analysis": {
                    "current_price_range": [
                        min([p.get("min_price", 0) for p in market_prices if p.get("min_price")], default=0),
                        max([p.get("max_price", 0) for p in market_prices if p.get("max_price")], default=0)
                    ],
                    "trend_assessment": price_trends.get("summary", {}).get("trend_direction", "stable"),
                    "market_strength": "moderate"
                },
                "ai_analysis_text": ai_analysis
            }
        
        # Add metadata
        advisory_data.update({
            "crop": crop_name,
            "location": farmer_location or "Kerala",
            "generated_at": datetime.now().isoformat(),
            "data_sources": ["Kerala Market Prices", "Price Trend Analysis"],
            "advisory_type": "AI-Powered Market Analysis",
            "confidence": "high" if len(market_prices) >= 3 else "medium"
        })
        
        logger.info(f"✅ Market advisory generated for {crop_name}")
        return advisory_data
        
    except Exception as e:
        logger.error(f"❌ Error generating market advisory: {e}")
        # Return fallback advisory
        return generate_fallback_market_advisory(crop_name, farmer_location)


def generate_fallback_market_advisory(crop_name: str, farmer_location: Optional[str] = None) -> Dict[str, Any]:
    """Generate fallback market advisory when AI service is unavailable"""
    market_prices = get_kerala_market_prices(crop_name=crop_name, limit=5)
    
    if market_prices:
        avg_price = sum(p.get("modal_price", 0) for p in market_prices) / len(market_prices)
        price_range = [
            min(p.get("min_price", 0) for p in market_prices if p.get("min_price")),
            max(p.get("max_price", 0) for p in market_prices if p.get("max_price"))
        ]
    else:
        avg_price = 0
        price_range = [0, 0]
    
    return {
        "crop": crop_name,
        "location": farmer_location or "Kerala",
        "current_situation": f"Current market data shows {crop_name} trading at ₹{avg_price:.0f}/quintal average",
        "price_analysis": {
            "current_price_range": price_range,
            "trend_assessment": "stable",
            "market_strength": "moderate",
            "average_price": round(avg_price, 2)
        },
        "selling_recommendations": {
            "best_markets": ["Kochi", "Kozhikode", "Thrissur"],
            "optimal_timing": "Monitor daily prices for best timing",
            "quality_focus": "Ensure good quality and proper grading"
        },
        "actionable_advice": {
            "immediate_actions": [
                "Check current market prices daily",
                "Ensure proper post-harvest handling",
                "Consider local demand patterns"
            ],
            "preparation_tips": [
                "Grade your produce properly",
                "Package according to market standards",
                "Plan transportation efficiently"
            ]
        },
        "generated_at": datetime.now().isoformat(),
        "advisory_type": "Basic Market Analysis",
        "confidence": "medium",
        "note": "Enhanced AI analysis temporarily unavailable"
    }


def get_kerala_market_prices(crop_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Get current market prices for Kerala - main function used by app.py"""
    try:
        # Try to get from API first
        if DATA_GOV_API_KEY and DATA_GOV_RESOURCE_ID:
            prices = fetch_kerala_prices_data_gov(limit=limit, crop_name=crop_name)
            if prices:
                logger.info(f"✅ API returned {len(prices)} market records")
                return format_market_prices_for_display(prices)
        
        # Fallback to mock data for demonstration
        logger.info("⚠️ Using mock market data (API not configured)")
        return generate_mock_kerala_prices(crop_name, limit)
        
    except Exception as e:
        logger.error(f"Error fetching Kerala market prices: {e}")
        return generate_mock_kerala_prices(crop_name, limit)


def format_market_prices_for_display(raw_prices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format raw price data for frontend display"""
    formatted_prices = []
    
    for price in raw_prices:
        formatted_price = {
            "crop": price.get("commodity", "Unknown"),
            "market": price.get("market", "Unknown"),
            "district": price.get("district", "Kerala"),
            "min_price": price.get("min_price", 0),
            "max_price": price.get("max_price", 0),
            "modal_price": price.get("modal_price", 0),
            "date": price.get("date", datetime.now().strftime("%Y-%m-%d")),
            "price_unit": "₹/Quintal",
            "trend": calculate_price_trend(price),
            "quality": "Good"  # Default quality
        }
        formatted_prices.append(formatted_price)
    
    return formatted_prices


def calculate_price_trend(price_data: Dict[str, Any]) -> str:
    """Calculate price trend based on historical comparison"""
    modal_price = price_data.get("modal_price", 0)
    min_price = price_data.get("min_price", 0)
    max_price = price_data.get("max_price", 0)
    
    if modal_price == 0:
        return "stable"
    
    # Simple trend calculation based on price range
    price_range = max_price - min_price
    if price_range > modal_price * 0.2:  # High volatility
        return "volatile"
    elif modal_price > (min_price + max_price) / 2:
        return "rising"
    elif modal_price < (min_price + max_price) / 2:
        return "falling"
    else:
        return "stable"


def generate_mock_kerala_prices(crop_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Generate mock market prices for testing when API is not available"""
    kerala_crops = [
        "Rice", "Coconut", "Pepper", "Cardamom", "Rubber", "Tea", "Coffee", "Banana", 
        "Ginger", "Turmeric", "Arecanut", "Cashew", "Vanilla", "Cinnamon"
    ]
    
    kerala_markets = [
        "Kochi", "Kozhikode", "Thrissur", "Palakkad", "Alappuzha", "Kollam", 
        "Kottayam", "Ernakulam", "Kannur", "Kasaragod"
    ]
    
    mock_prices = []
    crops_to_use = [crop_name] if crop_name else kerala_crops[:limit//2]
    
    for crop in crops_to_use:
        for i, market in enumerate(kerala_markets[:min(3, limit//len(crops_to_use)+1)]):
            base_price = random.uniform(1000, 5000)  # Base price in Rs/Quintal
            min_price = base_price * random.uniform(0.9, 1.0)
            max_price = base_price * random.uniform(1.0, 1.2)
            modal_price = (min_price + max_price) / 2
            
            mock_prices.append({
                "crop": crop,
                "market": market,
                "district": market,  # Simplified for mock data
                "min_price": round(min_price, 2),
                "max_price": round(max_price, 2),
                "modal_price": round(modal_price, 2),
                "date": (datetime.now() - timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d"),
                "price_unit": "₹/Quintal",
                "trend": random.choice(["rising", "falling", "stable", "volatile"]),
                "quality": random.choice(["Good", "Fair", "FAQ"])
            })
    
    return mock_prices[:limit]


def get_price_trends(crop_name: str, days: int = 7) -> Dict[str, Any]:
    """Get price trends for a specific crop over specified days"""
    try:
        # Try to get real trend data
        if DATA_GOV_API_KEY:
            trend_data = fetch_combined_prices(crop_name, days)
            if trend_data:
                return process_trend_data(trend_data, crop_name, days)
        
        # Fallback to mock trend data
        logger.info(f"⚠️ Using mock trend data for {crop_name}")
        return generate_mock_price_trends(crop_name, days)
        
    except Exception as e:
        logger.error(f"Error fetching price trends: {e}")
        return generate_mock_price_trends(crop_name, days)


def process_trend_data(raw_data: List[Dict[str, Any]], crop_name: str, days: int) -> Dict[str, Any]:
    """Process raw trend data into formatted response"""
    # Group by date and calculate averages
    date_prices = {}
    for record in raw_data:
        date = record.get("date", "")
        modal_price = record.get("modal_price", 0)
        if date and modal_price > 0:
            if date not in date_prices:
                date_prices[date] = []
            date_prices[date].append(modal_price)
    
    # Calculate daily averages
    trend_points = []
    for date, prices in sorted(date_prices.items()):
        avg_price = sum(prices) / len(prices)
        trend_points.append({
            "date": date,
            "price": round(avg_price, 2),
            "market_count": len(prices)
        })
    
    # Calculate trend metrics
    if len(trend_points) >= 2:
        first_price = trend_points[0]["price"]
        last_price = trend_points[-1]["price"]
        change_percent = ((last_price - first_price) / first_price) * 100
        trend_direction = "rising" if change_percent > 2 else "falling" if change_percent < -2 else "stable"
    else:
        change_percent = 0
        trend_direction = "stable"
    
    return {
        "crop": crop_name,
        "period_days": days,
        "trend_points": trend_points,
        "summary": {
            "trend_direction": trend_direction,
            "change_percent": round(change_percent, 2),
            "current_price": trend_points[-1]["price"] if trend_points else 0,
            "average_price": round(sum(p["price"] for p in trend_points) / len(trend_points), 2) if trend_points else 0
        }
    }


def generate_mock_price_trends(crop_name: str, days: int = 7) -> Dict[str, Any]:
    """Generate mock price trend data for testing"""
    base_price = random.uniform(2000, 4000)
    trend_direction = random.choice(["rising", "falling", "stable"])
    
    trend_points = []
    current_price = base_price
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i-1)).strftime("%Y-%m-%d")
        
        # Apply trend
        if trend_direction == "rising":
            current_price *= random.uniform(1.01, 1.05)
        elif trend_direction == "falling":
            current_price *= random.uniform(0.95, 0.99)
        else:  # stable
            current_price *= random.uniform(0.98, 1.02)
        
        trend_points.append({
            "date": date,
            "price": round(current_price, 2),
            "market_count": random.randint(3, 8)
        })
    
    change_percent = ((current_price - base_price) / base_price) * 100
    
    return {
        "crop": crop_name,
        "period_days": days,
        "trend_points": trend_points,
        "summary": {
            "trend_direction": trend_direction,
            "change_percent": round(change_percent, 2),
            "current_price": round(current_price, 2),
            "average_price": round(sum(p["price"] for p in trend_points) / len(trend_points), 2)
        }
    }


def fetch_kerala_prices_data_gov(limit: int = 50, crop_name: Optional[str] = None, 
                                date_from: Optional[str] = None, date_to: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch market prices from data.gov.in API - enhanced version"""
    logger.info(f"🔄 Fetching Kerala market prices from API...")
    
    # Check API configuration
    if not DATA_GOV_API_KEY or DATA_GOV_API_KEY == "your_api_key_here":
        logger.warning("⚠️ DATA_GOV_API_KEY not configured")
        return []
    
    if not DATA_GOV_RESOURCE_ID or DATA_GOV_RESOURCE_ID == "your_resource_id_here":
        logger.warning("⚠️ DATA_GOV_RESOURCE_ID not configured")
        return []
    
    try:
        # Try combined approach first
        if DATA_GOV_RESOURCE_ID_CURRENT or DATA_GOV_RESOURCE_ID_HISTORY:
            records = fetch_combined_prices(crop_name, days=7)
            if records:
                logger.info(f"✅ Combined API: {len(records)} records")
                return records[:limit]
        
        # Fallback to single resource
        url = DATA_GOV_API_URL.format(resource_id=DATA_GOV_RESOURCE_ID)
        params = {
            "api-key": DATA_GOV_API_KEY,
            "format": "json",
            "limit": limit,
            "filters[state]": "Kerala",
        }
        
        if crop_name:
            params["filters[commodity]"] = crop_name
        if date_from:
            params["filters[arrival_date][gte]"] = date_from
        if date_to:
            params["filters[arrival_date][lte]"] = date_to
        
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        
        data = resp.json()
        records = data.get("records", [])
        
        # Format records
        results = []
        for r in records:
            results.append({
                "commodity": r.get("commodity", ""),
                "market": r.get("market", r.get("market_center", "")),
                "min_price": _to_float(str(r.get("min_price", r.get("min_price_(rs/quintal)", "")))),
                "max_price": _to_float(str(r.get("max_price", r.get("max_price_(rs/quintal)", "")))),
                "modal_price": _to_float(str(r.get("modal_price", r.get("modal_price_(rs/quintal)", "")))),
                "date": r.get("arrival_date", r.get("date", "")),
                "district": r.get("district", ""),
                "state": r.get("state", "Kerala"),
            })
        
        logger.info(f"✅ Single API: {len(results)} records")
        return results
        
    except Exception as e:
        logger.error(f"❌ API fetch failed: {e}")
        return []