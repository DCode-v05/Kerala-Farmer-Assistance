"""
Authentication Service for Kerala Farmer Assistance
Provides user authentication based on AIMS database (farmers.json)
"""

import os
import json
import hashlib
import secrets
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
JWT_EXPIRATION_HOURS = 24

class AuthService:
    """Service for farmer authentication and session management"""
    
    def __init__(self, farmers_data_path: str = "data/farmers.json"):
        """Initialize the authentication service"""
        self.farmers_data_path = farmers_data_path
        self.farmers = self.load_farmers_data()
        self.active_sessions = {}
        
    def load_farmers_data(self) -> List[Dict[str, Any]]:
        """Load farmers data from JSON file"""
        try:
            if os.path.exists(self.farmers_data_path):
                with open(self.farmers_data_path, 'r', encoding='utf-8') as f:
                    farmers = json.load(f)
                logger.info(f"✅ Loaded {len(farmers)} farmers from database")
                return farmers
            else:
                logger.warning(f"⚠️ Farmers data file not found: {self.farmers_data_path}")
                return []
        except Exception as e:
            logger.error(f"❌ Failed to load farmers data: {e}")
            return []
    
    def authenticate_farmer(self, identifier: str, pin: str = None) -> Optional[Dict[str, Any]]:
        """
        Authenticate farmer using kerala_farmer_id, aadhaar_no, or mobile_no
        
        Args:
            identifier: Kerala Farmer ID, Aadhaar number, or mobile number
            pin: PIN/password (optional - for future implementation)
            
        Returns:
            Farmer data if authentication successful, None otherwise
        """
        try:
            # Search for farmer by multiple identifiers
            for farmer in self.farmers:
                if (farmer.get('kerala_farmer_id') == identifier or
                    farmer.get('aadhaar_no') == identifier or
                    farmer.get('mobile_no') == identifier or
                    farmer.get('id') == identifier):
                    
                    # For now, just return the farmer data
                    # In future, can add PIN verification here
                    logger.info(f"✅ Farmer authenticated: {farmer.get('name')} ({identifier})")
                    return self.sanitize_farmer_data(farmer)
            
            logger.warning(f"⚠️ Authentication failed for identifier: {identifier}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return None
    
    def sanitize_farmer_data(self, farmer: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from farmer record"""
        sensitive_fields = ['aadhaar_no', 'bank_account_no', 'ifsc']
        sanitized = farmer.copy()
        
        # Remove sensitive fields for client response
        for field in sensitive_fields:
            if field in sanitized:
                # Keep only partial data for identification
                if field == 'aadhaar_no':
                    sanitized[field] = sanitized[field][:4] + 'XXXX' + sanitized[field][-4:]
                elif field == 'bank_account_no':
                    sanitized[field] = 'XXXX' + sanitized[field][-4:] if len(sanitized[field]) > 4 else 'XXXX'
                else:
                    sanitized[field] = 'HIDDEN'
        
        return sanitized
    
    def generate_jwt_token(self, farmer_data: Dict[str, Any]) -> str:
        """Generate JWT token for authenticated farmer"""
        try:
            payload = {
                'farmer_id': farmer_data.get('id'),
                'kerala_farmer_id': farmer_data.get('kerala_farmer_id'),
                'name': farmer_data.get('name'),
                'mobile_no': farmer_data.get('mobile_no'),
                'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            logger.info(f"✅ JWT token generated for farmer: {farmer_data.get('name')}")
            return token
            
        except Exception as e:
            logger.error(f"❌ JWT token generation failed: {e}")
            return None
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return farmer data"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            
            # Get full farmer data
            farmer = self.get_farmer_by_id(payload.get('farmer_id'))
            if farmer:
                return self.sanitize_farmer_data(farmer)
            
            return None
            
        except jwt.ExpiredSignatureError:
            logger.warning("⚠️ JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("⚠️ Invalid JWT token")
            return None
        except Exception as e:
            logger.error(f"❌ JWT verification error: {e}")
            return None
    
    def get_farmer_by_id(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        """Get farmer data by ID"""
        try:
            for farmer in self.farmers:
                if farmer.get('id') == farmer_id:
                    return farmer
            return None
        except Exception as e:
            logger.error(f"❌ Error getting farmer by ID: {e}")
            return None
    
    def get_farmer_profile(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        """Get complete farmer profile with farm details"""
        try:
            farmer = self.get_farmer_by_id(farmer_id)
            if not farmer:
                return None
            
            # Add farm statistics
            profile = self.sanitize_farmer_data(farmer.copy())
            profile['farm_stats'] = {
                'total_area_acres': farmer.get('area_acres', 0),
                'location': {
                    'latitude': farmer.get('lat'),
                    'longitude': farmer.get('lon'),
                    'address': farmer.get('address'),
                    'post_office': farmer.get('post_office'),
                    'pin_code': farmer.get('pin_code')
                },
                'krishi_bhavan': farmer.get('farmhouse_krishibhavan'),
                'interests': {
                    'marketing': bool(farmer.get('marketing_interest', 0)),
                    'processing': bool(farmer.get('processing_interest', 0))
                }
            }
            
            return profile
            
        except Exception as e:
            logger.error(f"❌ Error getting farmer profile: {e}")
            return None
    
    def search_farmers(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search farmers by name, ID, or location"""
        try:
            results = []
            query_lower = query.lower()
            
            for farmer in self.farmers:
                if len(results) >= limit:
                    break
                
                # Search in various fields
                searchable_fields = [
                    farmer.get('name', '').lower(),
                    farmer.get('kerala_farmer_id', '').lower(),
                    farmer.get('id', '').lower(),
                    farmer.get('address', '').lower(),
                    farmer.get('post_office', '').lower()
                ]
                
                if any(query_lower in field for field in searchable_fields):
                    results.append(self.sanitize_farmer_data(farmer))
            
            logger.info(f"✅ Found {len(results)} farmers for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching farmers: {e}")
            return []
    
    def get_farmers_by_location(self, lat: float, lon: float, radius_km: float = 10) -> List[Dict[str, Any]]:
        """Get farmers within specified radius of location"""
        try:
            import math
            
            results = []
            
            for farmer in self.farmers:
                farmer_lat = farmer.get('lat')
                farmer_lon = farmer.get('lon')
                
                if farmer_lat and farmer_lon:
                    # Calculate distance using Haversine formula
                    distance = self.calculate_distance(lat, lon, farmer_lat, farmer_lon)
                    
                    if distance <= radius_km:
                        farmer_data = self.sanitize_farmer_data(farmer)
                        farmer_data['distance_km'] = round(distance, 2)
                        results.append(farmer_data)
            
            # Sort by distance
            results.sort(key=lambda x: x['distance_km'])
            
            logger.info(f"✅ Found {len(results)} farmers within {radius_km}km")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error getting farmers by location: {e}")
            return []
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        import math
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        
        return r * c
    
    def logout_farmer(self, token: str) -> bool:
        """Logout farmer by invalidating token"""
        try:
            # For JWT tokens, we could maintain a blacklist
            # For now, just log the logout
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            farmer_name = payload.get('name', 'Unknown')
            logger.info(f"✅ Farmer logged out: {farmer_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Logout error: {e}")
            return False


# Global service instance
auth_service = AuthService()

# Convenience functions for API endpoints
def authenticate_farmer(identifier: str, pin: str = None) -> Optional[Dict[str, Any]]:
    """Authenticate farmer and return farmer data"""
    return auth_service.authenticate_farmer(identifier, pin)

def generate_auth_token(farmer_data: Dict[str, Any]) -> str:
    """Generate authentication token"""
    return auth_service.generate_jwt_token(farmer_data)

def verify_auth_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify authentication token"""
    return auth_service.verify_jwt_token(token)

def get_farmer_profile(farmer_id: str) -> Optional[Dict[str, Any]]:
    """Get farmer profile"""
    return auth_service.get_farmer_profile(farmer_id)

def search_farmers(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search farmers"""
    return auth_service.search_farmers(query, limit)

def logout_farmer(token: str) -> bool:
    """Logout farmer"""
    return auth_service.logout_farmer(token)