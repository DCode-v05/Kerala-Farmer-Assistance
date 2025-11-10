"""
Enhanced Farm Profile Service for Kerala Farmer Assistance Platform
Provides comprehensive farmer and farm profiling with AI context
"""

import json
import datetime
from typing import Dict, List, Optional, Any
import logging

# Kerala-specific farm data
KERALA_DISTRICTS = [
    "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha", "Kottayam", 
    "Idukki", "Ernakulam", "Thrissur", "Palakkad", "Malappuram", 
    "Kozhikode", "Wayanad", "Kannur", "Kasaragod"
]

KERALA_CROPS = {
    "rice": {
        "name": "Paddy/Rice",
        "malayalam": "നെല്ല്",
        "varieties": ["Uma", "Jyothi", "Athira", "Ptb-39", "Prathyasha"],
        "seasons": ["Kharif", "Rabi"],
        "soil_types": ["Clay", "Clay Loam", "Alluvial"],
        "water_requirement": "High",
        "growth_duration": "120-130 days"
    },
    "coconut": {
        "name": "Coconut",
        "malayalam": "തേങ്ങ",
        "varieties": ["West Coast Tall", "Laccadive Ordinary", "Chandra Laksha", "Malayan Dwarf"],
        "seasons": ["Year Round"],
        "soil_types": ["Sandy Loam", "Red Laterite", "Coastal Sand"],
        "water_requirement": "Medium",
        "growth_duration": "5-6 years (to bearing)"
    },
    "rubber": {
        "name": "Rubber",
        "malayalam": "റബ്ബർ",
        "varieties": ["RRII 105", "RRII 118", "GT 1", "PB 217"],
        "seasons": ["April-May planting"],
        "soil_types": ["Red Laterite", "Hill Soil"],
        "water_requirement": "High",
        "growth_duration": "6-7 years (to tapping)"
    },
    "spices": {
        "name": "Spices",
        "malayalam": "സുഗന്ധവർഗ്ഗങ്ങൾ",
        "varieties": ["Black Pepper", "Cardamom", "Ginger", "Turmeric", "Cinnamon"],
        "seasons": ["Monsoon dependent"],
        "soil_types": ["Hill Soil", "Forest Soil", "Well-drained Loam"],
        "water_requirement": "Medium to High",
        "growth_duration": "Varies (6 months - 3 years)"
    },
    "vegetables": {
        "name": "Vegetables",
        "malayalam": "പച്ചക്കറികൾ",
        "varieties": ["Amaranthus", "Okra", "Bitter Gourd", "Snake Gourd", "Cowpea"],
        "seasons": ["Year Round with season preferences"],
        "soil_types": ["Well-drained Loam", "Sandy Loam"],
        "water_requirement": "Medium",
        "growth_duration": "60-120 days"
    },
    "banana": {
        "name": "Banana",
        "malayalam": "വാഴ",
        "varieties": ["Nendran", "Robusta", "Red Banana", "Poovan", "Rasthali"],
        "seasons": ["Year Round"],
        "soil_types": ["Alluvial", "Rich Loam", "Well-drained"],
        "water_requirement": "High",
        "growth_duration": "12-15 months"
    }
}

SOIL_TYPES = {
    "red_laterite": {
        "name": "Red Laterite",
        "malayalam": "ചുവന്ന ലാറ്ററൈറ്റ്",
        "ph_range": "5.5-6.5",
        "characteristics": "Iron-rich, well-drained, low fertility",
        "suitable_crops": ["coconut", "rubber", "cashew"],
        "improvements": ["Organic matter addition", "Lime application", "Green manuring"]
    },
    "alluvial": {
        "name": "Alluvial Soil",
        "malayalam": "എക്കൽ മണ്ണ്",
        "ph_range": "6.0-7.5",
        "characteristics": "Fertile, well-drained, rich in nutrients",
        "suitable_crops": ["rice", "banana", "vegetables"],
        "improvements": ["Drainage management", "Organic matter maintenance"]
    },
    "coastal_sandy": {
        "name": "Coastal Sandy",
        "malayalam": "തീരദേശ മണൽ മണ്ണ്",
        "ph_range": "7.0-8.5",
        "characteristics": "Sandy, saline, low water retention",
        "suitable_crops": ["coconut", "salt-tolerant vegetables"],
        "improvements": ["Organic mulching", "Saline management", "Water conservation"]
    },
    "hill_soil": {
        "name": "Hill Soil",
        "malayalam": "മല മണ്ണ്",
        "ph_range": "5.0-6.5",
        "characteristics": "Acidic, organic-rich, prone to erosion",
        "suitable_crops": ["spices", "rubber", "tea", "coffee"],
        "improvements": ["Terracing", "Contour farming", "Lime application"]
    },
    "clay_loam": {
        "name": "Clay Loam",
        "malayalam": "കളിമണ് കലർന്ന മണ്ണ്",
        "ph_range": "6.0-7.0",
        "characteristics": "Good water retention, fertile, can be heavy",
        "suitable_crops": ["rice", "vegetables", "fruit trees"],
        "improvements": ["Drainage improvement", "Organic matter incorporation"]
    }
}

IRRIGATION_TYPES = {
    "drip": {
        "name": "Drip Irrigation",
        "malayalam": "തുള്ളി നീരൊഴുക്ക്",
        "efficiency": "90-95%",
        "suitable_crops": ["vegetables", "spices", "banana"],
        "investment": "High initial, low operational",
        "water_saving": "40-60%"
    },
    "sprinkler": {
        "name": "Sprinkler System",
        "malayalam": "സ്പ്രിങ്ക്ലർ സിസ്റ്റം",
        "efficiency": "75-85%",
        "suitable_crops": ["vegetables", "cereals", "fodder"],
        "investment": "Medium",
        "water_saving": "20-40%"
    },
    "flood": {
        "name": "Flood Irrigation",
        "malayalam": "നിർജ്ഞാത നീരൊഴുക്ക്",
        "efficiency": "45-60%",
        "suitable_crops": ["rice", "sugarcane"],
        "investment": "Low",
        "water_saving": "None"
    },
    "rainwater": {
        "name": "Rainwater Dependent",
        "malayalam": "മഴയെ ആശ്രയിച്ചുള്ള കൃഷി",
        "efficiency": "Variable",
        "suitable_crops": ["coconut", "rubber", "spices"],
        "investment": "None",
        "water_saving": "Natural"
    }
}

class FarmProfileService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_detailed_farmer_profile(self, farmer_data: Dict) -> Dict:
        """Enhance basic farmer data with detailed farm information"""
        enhanced_profile = {
            "basic_info": self._extract_basic_info(farmer_data),
            "farm_details": self._extract_farm_details(farmer_data),
            "location_context": self._get_location_context(farmer_data),
            "ai_context": self._generate_ai_context(farmer_data),
            "recommendations": self._generate_recommendations(farmer_data),
            "profile_completion": self._calculate_profile_completion(farmer_data)
        }
        
        return enhanced_profile
    
    def _extract_basic_info(self, farmer_data: Dict) -> Dict:
        """Extract and structure basic farmer information"""
        return {
            "farmer_id": farmer_data.get("id"),
            "name": farmer_data.get("name"),
            "mobile_no": farmer_data.get("mobile_no"),
            "gender": farmer_data.get("gender"),
            "age": self._calculate_age(farmer_data.get("dob")),
            "education_level": farmer_data.get("education_level"),
            "experience_years": farmer_data.get("farming_experience_years", "Not specified"),
            "primary_language": farmer_data.get("preferred_language", "Malayalam"),
            "registration_date": farmer_data.get("created_at")
        }
    
    def _extract_farm_details(self, farmer_data: Dict) -> Dict:
        """Extract comprehensive farm details with enhancements"""
        # Basic farm info
        farm_details = {
            "total_area_acres": farmer_data.get("area_acres", 0),
            "location": {
                "address": farmer_data.get("address"),
                "district": self._extract_district(farmer_data.get("address", "")),
                "pin_code": farmer_data.get("pin_code"),
                "coordinates": {
                    "lat": farmer_data.get("lat"),
                    "lon": farmer_data.get("lon")
                }
            }
        }
        
        # Enhanced farm characteristics
        farm_details.update({
            "crops": self._get_farmer_crops(farmer_data),
            "soil_type": self._determine_soil_type(farmer_data),
            "irrigation_type": self._determine_irrigation_type(farmer_data),
            "farm_type": self._classify_farm_type(farmer_data),
            "water_source": farmer_data.get("water_source", "Not specified"),
            "organic_status": farmer_data.get("organic_certified", False),
            "livestock": farmer_data.get("livestock_details", [])
        })
        
        return farm_details
    
    def _get_location_context(self, farmer_data: Dict) -> Dict:
        """Get location-specific agricultural context"""
        district = self._extract_district(farmer_data.get("address", ""))
        
        # District-specific information
        district_info = {
            "Thiruvananthapuram": {
                "climate": "Tropical coastal",
                "rainfall": "1500-3000mm",
                "major_crops": ["coconut", "rubber", "banana", "vegetables"],
                "soil_predominant": "coastal_sandy"
            },
            "Alappuzha": {
                "climate": "Tropical wet",
                "rainfall": "2000-3000mm", 
                "major_crops": ["rice", "coconut", "banana"],
                "soil_predominant": "alluvial"
            },
            "Wayanad": {
                "climate": "High rainfall hill station",
                "rainfall": "2000-4000mm",
                "major_crops": ["spices", "coffee", "banana"],
                "soil_predominant": "hill_soil"
            },
            "Palakkad": {
                "climate": "Semi-arid",
                "rainfall": "1200-2000mm",
                "major_crops": ["rice", "coconut", "vegetables"],
                "soil_predominant": "alluvial"
            }
        }
        
        return district_info.get(district, {
            "climate": "Tropical monsoon",
            "rainfall": "1500-3000mm",
            "major_crops": ["coconut", "rice", "spices"],
            "soil_predominant": "red_laterite"
        })
    
    def _generate_ai_context(self, farmer_data: Dict) -> Dict:
        """Generate AI context for personalized recommendations"""
        farm_details = self._extract_farm_details(farmer_data)
        location_context = self._get_location_context(farmer_data)
        
        ai_context = {
            "farmer_segment": self._classify_farmer_segment(farmer_data),
            "risk_profile": self._assess_risk_profile(farmer_data),
            "technology_readiness": self._assess_tech_readiness(farmer_data),
            "priority_areas": self._identify_priority_areas(farmer_data),
            "knowledge_gaps": self._identify_knowledge_gaps(farmer_data),
            "intervention_suggestions": self._suggest_interventions(farmer_data)
        }
        
        return ai_context
    
    def _generate_recommendations(self, farmer_data: Dict) -> Dict:
        """Generate personalized recommendations"""
        recommendations = {
            "immediate_actions": [],
            "seasonal_planning": [],
            "skill_development": [],
            "technology_adoption": [],
            "financial_planning": []
        }
        
        # Analyze current profile and generate specific recommendations
        area_acres = farmer_data.get("area_acres", 0)
        district = self._extract_district(farmer_data.get("address", ""))
        education = farmer_data.get("education_level", "")
        
        # Size-based recommendations
        if area_acres < 2:
            recommendations["immediate_actions"].append({
                "priority": "High",
                "action": "Focus on high-value crops like vegetables and spices",
                "malayalam": "പച്ചക്കറികളും സുഗന്ധവർഗ്ഗങ്ങളും പോലുള്ള ഉയർന്ന വിലയുള്ള വിളകളിൽ ശ്രദ്ധ കേന്ദ്രീകരിക്കുക"
            })
            recommendations["technology_adoption"].append({
                "priority": "Medium",
                "action": "Consider drip irrigation for water efficiency",
                "malayalam": "ജല സംരക്ഷണത്തിനായി തുള്ളി നീരൊഴുക്ക് പരിഗണിക്കുക"
            })
        elif area_acres >= 2 and area_acres < 5:
            recommendations["immediate_actions"].append({
                "priority": "High",
                "action": "Diversify crops with cereals and cash crops combination",
                "malayalam": "ധാന്യങ്ങളും നാണ്യവിളകളും കൂട്ടിച്ചേർത്ത് വിള വൈവിധ്യവൽക്കരണം നടത്തുക"
            })
        else:
            recommendations["immediate_actions"].append({
                "priority": "High", 
                "action": "Implement mechanization for efficient farming",
                "malayalam": "കാര്യക്ഷമമായ കൃഷിക്കായി യന്ത്രവൽക്കരണം നടപ്പിലാക്കുക"
            })
        
        # Education-based recommendations
        if education in ["Graduate", "Post Graduate"]:
            recommendations["technology_adoption"].append({
                "priority": "High",
                "action": "Explore precision farming and IoT applications",
                "malayalam": "കൃത്യമായ കൃഷിയും IoT ആപ്ലിക്കേഷനുകളും പര്യവേക്ഷണം ചെയ്യുക"
            })
        
        return recommendations
    
    def get_crop_recommendations(self, farmer_data: Dict, season: str = None) -> List[Dict]:
        """Get crop recommendations based on farmer profile"""
        district = self._extract_district(farmer_data.get("address", ""))
        area = farmer_data.get("area_acres", 0)
        soil_type = self._determine_soil_type(farmer_data)
        
        recommendations = []
        
        # Season-aware recommendations
        current_month = datetime.datetime.now().month
        if not season:
            if current_month in [6, 7, 8, 9]:  # Monsoon season
                season = "kharif"
            elif current_month in [10, 11, 12, 1]:  # Post-monsoon
                season = "rabi"
            else:  # Summer
                season = "summer"
        
        # Generate recommendations based on soil type and area
        soil_info = SOIL_TYPES.get(soil_type, {})
        suitable_crops = soil_info.get("suitable_crops", ["vegetables"])
        
        for crop_key in suitable_crops:
            if crop_key in KERALA_CROPS:
                crop_info = KERALA_CROPS[crop_key]
                recommendation = {
                    "crop": crop_info["name"],
                    "malayalam": crop_info["malayalam"],
                    "varieties": crop_info["varieties"][:3],  # Top 3 varieties
                    "season_suitability": self._check_season_suitability(crop_key, season),
                    "area_suitability": self._check_area_suitability(crop_key, area),
                    "expected_yield": self._estimate_yield(crop_key, area, soil_type),
                    "investment_required": self._estimate_investment(crop_key, area),
                    "market_potential": self._assess_market_potential(crop_key, district)
                }
                recommendations.append(recommendation)
        
        return sorted(recommendations, key=lambda x: x["season_suitability"], reverse=True)
    
    def _calculate_age(self, dob_str: str) -> Optional[int]:
        """Calculate age from date of birth string"""
        if not dob_str:
            return None
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            today = datetime.datetime.now()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except:
            return None
    
    def _extract_district(self, address: str) -> str:
        """Extract district from address string"""
        if not address:
            return "Unknown"
        
        address_lower = address.lower()
        for district in KERALA_DISTRICTS:
            if district.lower() in address_lower:
                return district
        
        # Try common variations
        district_variations = {
            "tvm": "Thiruvananthapuram",
            "kochi": "Ernakulam",
            "calicut": "Kozhikode"
        }
        
        for variation, district in district_variations.items():
            if variation in address_lower:
                return district
        
        return "Unknown"
    
    def _get_farmer_crops(self, farmer_data: Dict) -> List[Dict]:
        """Determine farmer's crops from available data"""
        # This could be enhanced with actual crop data from a crops table
        # For now, infer from address and area
        district = self._extract_district(farmer_data.get("address", ""))
        area = farmer_data.get("area_acres", 0)
        
        # Default crops based on district
        district_crops = {
            "Alappuzha": ["rice", "coconut"],
            "Wayanad": ["spices", "banana"],
            "Palakkad": ["rice", "vegetables"],
            "Idukki": ["spices", "rubber"]
        }
        
        crops = district_crops.get(district, ["coconut", "vegetables"])
        
        crop_details = []
        for crop_key in crops:
            if crop_key in KERALA_CROPS:
                crop_info = KERALA_CROPS[crop_key]
                crop_details.append({
                    "crop": crop_info["name"],
                    "malayalam": crop_info["malayalam"],
                    "area_acres": area / len(crops),  # Distribute area
                    "status": "Current",
                    "variety": crop_info["varieties"][0] if crop_info["varieties"] else "Unknown"
                })
        
        return crop_details
    
    def _determine_soil_type(self, farmer_data: Dict) -> str:
        """Determine soil type based on location and other factors"""
        district = self._extract_district(farmer_data.get("address", ""))
        address = farmer_data.get("address", "").lower()
        
        # District-based soil type mapping
        if district in ["Alappuzha", "Kuttanad"]:
            return "alluvial"
        elif district in ["Thiruvananthapuram", "Kollam"]:
            if "coast" in address or "beach" in address:
                return "coastal_sandy"
            return "red_laterite"
        elif district in ["Wayanad", "Idukki"]:
            return "hill_soil"
        elif district == "Palakkad":
            return "clay_loam"
        else:
            return "red_laterite"  # Most common in Kerala
    
    def _determine_irrigation_type(self, farmer_data: Dict) -> str:
        """Determine irrigation type based on crops and area"""
        crops = self._get_farmer_crops(farmer_data)
        area = farmer_data.get("area_acres", 0)
        
        # Check if rice is grown (flood irrigation)
        rice_grown = any(crop["crop"].lower() in ["paddy", "rice"] for crop in crops)
        if rice_grown:
            return "flood"
        
        # For smaller areas with vegetables, suggest drip
        if area < 2:
            vegetable_grown = any("vegetable" in crop["crop"].lower() for crop in crops)
            if vegetable_grown:
                return "drip"
        
        # Default based on area
        if area < 1:
            return "drip"
        elif area < 5:
            return "sprinkler"
        else:
            return "rainwater"
    
    def _classify_farm_type(self, farmer_data: Dict) -> str:
        """Classify farm type based on size and crops"""
        area = farmer_data.get("area_acres", 0)
        crops = self._get_farmer_crops(farmer_data)
        
        if area < 1:
            return "Kitchen Garden"
        elif area < 2.5:
            return "Small Farm"
        elif area < 5:
            return "Medium Farm"
        elif area < 10:
            return "Large Farm"
        else:
            return "Commercial Farm"
    
    def _classify_farmer_segment(self, farmer_data: Dict) -> str:
        """Classify farmer into segments for targeted advice"""
        area = farmer_data.get("area_acres", 0)
        education = farmer_data.get("education_level", "")
        age = self._calculate_age(farmer_data.get("dob"))
        
        if area < 2:
            if age and age < 40:
                return "Young Smallholder"
            else:
                return "Traditional Smallholder"
        elif area < 5:
            if education in ["Graduate", "Post Graduate"]:
                return "Progressive Mid-scale Farmer"
            else:
                return "Traditional Mid-scale Farmer"
        else:
            return "Commercial Farmer"
    
    def _assess_risk_profile(self, farmer_data: Dict) -> str:
        """Assess farmer's risk profile"""
        area = farmer_data.get("area_acres", 0)
        education = farmer_data.get("education_level", "")
        district = self._extract_district(farmer_data.get("address", ""))
        
        # High-risk areas (weather-dependent, single crop)
        high_risk_districts = ["Wayanad", "Idukki"]
        
        if district in high_risk_districts:
            return "High Risk"
        elif area < 1:
            return "High Risk"
        elif education in ["Graduate", "Post Graduate"] and area > 2:
            return "Low Risk"
        else:
            return "Medium Risk"
    
    def _assess_tech_readiness(self, farmer_data: Dict) -> str:
        """Assess farmer's technology adoption readiness"""
        education = farmer_data.get("education_level", "")
        age = self._calculate_age(farmer_data.get("dob"))
        
        if education in ["Graduate", "Post Graduate"] and age and age < 50:
            return "High"
        elif education == "Higher Secondary" and age and age < 40:
            return "Medium"
        else:
            return "Low"
    
    def _identify_priority_areas(self, farmer_data: Dict) -> List[str]:
        """Identify priority intervention areas"""
        priorities = []
        
        area = farmer_data.get("area_acres", 0)
        district = self._extract_district(farmer_data.get("address", ""))
        
        if area < 2:
            priorities.extend(["Crop intensification", "Value addition"])
        
        if district in ["Wayanad", "Idukki"]:
            priorities.append("Climate resilience")
        
        priorities.extend(["Market linkage", "Skill development"])
        
        return priorities[:3]  # Return top 3 priorities
    
    def _identify_knowledge_gaps(self, farmer_data: Dict) -> List[str]:
        """Identify potential knowledge gaps"""
        gaps = []
        
        education = farmer_data.get("education_level", "")
        age = self._calculate_age(farmer_data.get("dob"))
        
        if education in ["Primary", "Secondary"]:
            gaps.extend(["Modern farming techniques", "Financial planning"])
        
        if age and age > 50:
            gaps.append("Digital agriculture")
        
        gaps.extend(["Market intelligence", "Post-harvest management"])
        
        return gaps[:4]  # Return top 4 gaps
    
    def _suggest_interventions(self, farmer_data: Dict) -> List[Dict]:
        """Suggest specific interventions"""
        interventions = []
        
        area = farmer_data.get("area_acres", 0)
        tech_readiness = self._assess_tech_readiness(farmer_data)
        
        if area < 2 and tech_readiness == "High":
            interventions.append({
                "type": "Technology",
                "intervention": "Precision farming with IoT sensors",
                "priority": "Medium",
                "timeline": "6 months"
            })
        
        interventions.append({
            "type": "Training",
            "intervention": "Integrated pest management workshop",
            "priority": "High",
            "timeline": "1 month"
        })
        
        return interventions
    
    def _calculate_profile_completion(self, farmer_data: Dict) -> Dict:
        """Calculate profile completion percentage"""
        required_fields = [
            "name", "mobile_no", "address", "area_acres", "dob", 
            "education_level", "lat", "lon"
        ]
        
        optional_fields = [
            "water_source", "organic_certified", "farming_experience_years",
            "livestock_details", "bank_account_no"
        ]
        
        required_completed = sum(1 for field in required_fields if farmer_data.get(field))
        optional_completed = sum(1 for field in optional_fields if farmer_data.get(field))
        
        required_percentage = (required_completed / len(required_fields)) * 100
        overall_percentage = ((required_completed + optional_completed) / 
                            (len(required_fields) + len(optional_fields))) * 100
        
        return {
            "required_completion": required_percentage,
            "overall_completion": overall_percentage,
            "missing_required": [field for field in required_fields 
                               if not farmer_data.get(field)],
            "missing_optional": [field for field in optional_fields 
                               if not farmer_data.get(field)]
        }
    
    def _check_season_suitability(self, crop_key: str, season: str) -> float:
        """Check how suitable a crop is for the given season (0-1)"""
        crop_info = KERALA_CROPS.get(crop_key, {})
        crop_seasons = [s.lower() for s in crop_info.get("seasons", [])]
        
        if "year round" in crop_seasons:
            return 1.0
        elif season.lower() in crop_seasons:
            return 1.0
        elif "monsoon dependent" in crop_seasons and season == "kharif":
            return 0.8
        else:
            return 0.3
    
    def _check_area_suitability(self, crop_key: str, area: float) -> float:
        """Check how suitable a crop is for the given area (0-1)"""
        # Area suitability logic
        if crop_key == "rice" and area >= 1:
            return 1.0
        elif crop_key == "vegetables" and area <= 2:
            return 1.0
        elif crop_key == "coconut" and area >= 0.5:
            return 1.0
        elif crop_key == "spices" and area <= 1:
            return 1.0
        else:
            return 0.7  # Generally suitable
    
    def _estimate_yield(self, crop_key: str, area: float, soil_type: str) -> str:
        """Estimate yield for the crop"""
        base_yields = {
            "rice": "3-4 tons/hectare",
            "coconut": "80-120 nuts/palm/year",
            "rubber": "2000-3000 kg/hectare/year",
            "spices": "Varies by spice type",
            "vegetables": "15-25 tons/hectare",
            "banana": "40-60 tons/hectare"
        }
        return base_yields.get(crop_key, "Varies")
    
    def _estimate_investment(self, crop_key: str, area: float) -> str:
        """Estimate investment required"""
        base_investments = {
            "rice": f"₹{int(25000 * area)}-{int(35000 * area)}",
            "coconut": f"₹{int(50000 * area)}-{int(75000 * area)}",
            "rubber": f"₹{int(60000 * area)}-{int(80000 * area)}",
            "spices": f"₹{int(40000 * area)}-{int(60000 * area)}",
            "vegetables": f"₹{int(30000 * area)}-{int(50000 * area)}",
            "banana": f"₹{int(45000 * area)}-{int(65000 * area)}"
        }
        return base_investments.get(crop_key, f"₹{int(30000 * area)}-{int(50000 * area)}")
    
    def _assess_market_potential(self, crop_key: str, district: str) -> str:
        """Assess market potential for the crop in the district"""
        # District-wise market assessments
        if crop_key == "spices" and district in ["Wayanad", "Idukki"]:
            return "High - Premium spice markets"
        elif crop_key == "rice" and district in ["Alappuzha", "Palakkad"]:
            return "Good - Traditional rice regions"
        elif crop_key == "coconut":
            return "Good - State-wide demand"
        else:
            return "Medium - Local markets available"