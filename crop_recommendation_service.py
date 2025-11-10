"""
Crop Recommendation Service for Kerala Farmer Assistance
Integrates crop recommendation models for optimal crop selection
"""

import os
import pickle
import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CropRecommendationService:
    """Service for crop recommendation based on soil and climate parameters"""
    
    def __init__(self):
        """Initialize the crop recommendation service"""
        self.model = None
        self.model_loaded = False
        self.load_model()
        
    def load_model(self):
        """Load crop recommendation model"""
        try:
            # Try to load models in order of preference
            model_paths = [
                'crop_model_new.pkl',
                'crop_model_joblib.pkl', 
                'recommender.pkl',
                'recommender_joblib.pkl'
            ]
            
            for model_path in model_paths:
                if os.path.exists(model_path):
                    try:
                        with open(model_path, 'rb') as file:
                            self.model = pickle.load(file)
                        self.model_loaded = True
                        logger.info(f"✅ Crop recommendation model loaded from: {model_path}")
                        return
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to load model from {model_path}: {e}")
                        continue
            
            logger.warning("⚠️ No compatible model found, using rule-based recommendations")
            self.model_loaded = False
            
        except Exception as e:
            logger.error(f"❌ Error loading crop recommendation model: {e}")
            self.model_loaded = False

    def get_crop_recommendations(self, soil_params: Dict[str, float], 
                               climate_params: Dict[str, float],
                               location: str = "Kerala") -> Dict[str, Any]:
        """
        Get crop recommendations based on soil and climate parameters
        
        Args:
            soil_params: Dict with keys: nitrogen, phosphorus, potassium, ph
            climate_params: Dict with keys: temperature, humidity, rainfall
            location: Location for regional considerations
            
        Returns:
            Dictionary containing crop recommendations
        """
        try:
            # Extract parameters
            nitrogen = soil_params.get('nitrogen', 50)
            phosphorus = soil_params.get('phosphorus', 50) 
            potassium = soil_params.get('potassium', 50)
            ph = soil_params.get('ph', 6.5)
            temperature = climate_params.get('temperature', 25)
            humidity = climate_params.get('humidity', 80)
            rainfall = climate_params.get('rainfall', 200)
            
            if self.model_loaded and self.model:
                return self._get_ml_recommendations(
                    nitrogen, phosphorus, potassium, ph,
                    temperature, humidity, rainfall, location
                )
            else:
                return self._get_rule_based_recommendations(
                    nitrogen, phosphorus, potassium, ph,
                    temperature, humidity, rainfall, location
                )
                
        except Exception as e:
            logger.error(f"❌ Error getting crop recommendations: {e}")
            return self._get_fallback_recommendations(location)

    def _get_ml_recommendations(self, n: float, p: float, k: float, ph: float,
                              temp: float, humidity: float, rainfall: float,
                              location: str) -> Dict[str, Any]:
        """Get recommendations using ML model"""
        try:
            # Prepare input data
            input_data = np.array([[n, p, k, temp, humidity, ph, rainfall]])
            
            # Make prediction
            prediction = self.model.predict(input_data)[0]
            
            # Get probabilities if available
            try:
                probabilities = self.model.predict_proba(input_data)[0]
                # Get top 5 recommendations
                top_indices = np.argsort(probabilities)[-5:][::-1]
                top_probs = probabilities[top_indices]
            except:
                top_indices = [prediction]
                top_probs = [1.0]
            
            # Map predictions to crop names
            recommendations = []
            for idx, prob in zip(top_indices, top_probs):
                crop_name = self._get_crop_name(idx)
                suitability_score = int(prob * 100)
                
                recommendations.append({
                    "crop": crop_name,
                    "suitability_score": suitability_score,
                    "confidence": "high" if prob > 0.7 else "medium" if prob > 0.4 else "low",
                    "recommendation_reason": self._get_crop_reason(crop_name, n, p, k, ph, temp, humidity, rainfall)
                })
            
            return {
                "recommendations": recommendations,
                "input_parameters": {
                    "nitrogen": n, "phosphorus": p, "potassium": k, "ph": ph,
                    "temperature": temp, "humidity": humidity, "rainfall": rainfall
                },
                "location": location,
                "analysis_method": "Machine Learning Model",
                "confidence": "high",
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ ML prediction error: {e}")
            return self._get_rule_based_recommendations(n, p, k, ph, temp, humidity, rainfall, location)

    def _get_rule_based_recommendations(self, n: float, p: float, k: float, ph: float,
                                      temp: float, humidity: float, rainfall: float,
                                      location: str) -> Dict[str, Any]:
        """Get recommendations using rule-based approach"""
        
        recommendations = []
        
        # Rice recommendation
        rice_score = self._calculate_rice_suitability(n, p, k, ph, temp, humidity, rainfall)
        if rice_score > 0:
            recommendations.append({
                "crop": "Rice",
                "suitability_score": min(100, rice_score),
                "confidence": "high" if rice_score > 70 else "medium",
                "recommendation_reason": "Suitable soil nutrients and climate for rice cultivation"
            })
        
        # Wheat recommendation  
        wheat_score = self._calculate_wheat_suitability(n, p, k, ph, temp, humidity, rainfall)
        if wheat_score > 0:
            recommendations.append({
                "crop": "Wheat",
                "suitability_score": min(100, wheat_score),
                "confidence": "medium" if wheat_score > 50 else "low",
                "recommendation_reason": "Moderate suitability for wheat based on climate conditions"
            })
        
        # Maize recommendation
        maize_score = self._calculate_maize_suitability(n, p, k, ph, temp, humidity, rainfall)
        if maize_score > 0:
            recommendations.append({
                "crop": "Maize",
                "suitability_score": min(100, maize_score),
                "confidence": "high" if maize_score > 60 else "medium",
                "recommendation_reason": "Good soil and climate conditions for maize"
            })
        
        # Cotton recommendation
        cotton_score = self._calculate_cotton_suitability(n, p, k, ph, temp, humidity, rainfall)
        if cotton_score > 0:
            recommendations.append({
                "crop": "Cotton",
                "suitability_score": min(100, cotton_score),
                "confidence": "medium",
                "recommendation_reason": "Suitable for cotton with proper water management"
            })
        
        # Kerala-specific crops
        if location.lower() in ['kerala', 'kochi', 'thrissur', 'kozhikode']:
            kerala_crops = self._get_kerala_specific_crops(n, p, k, ph, temp, humidity, rainfall)
            recommendations.extend(kerala_crops)
        
        # Sort by suitability score
        recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return {
            "recommendations": recommendations[:5],  # Top 5 recommendations
            "input_parameters": {
                "nitrogen": n, "phosphorus": p, "potassium": k, "ph": ph,
                "temperature": temp, "humidity": humidity, "rainfall": rainfall
            },
            "location": location,
            "analysis_method": "Rule-Based Analysis",
            "confidence": "medium",
            "generated_at": datetime.now().isoformat()
        }

    def _calculate_rice_suitability(self, n: float, p: float, k: float, ph: float,
                                  temp: float, humidity: float, rainfall: float) -> int:
        """Calculate rice suitability score"""
        score = 0
        
        # Soil parameters (40% weight)
        if 80 <= n <= 120: score += 15
        elif 60 <= n <= 140: score += 10
        
        if 40 <= p <= 60: score += 10
        elif 30 <= p <= 70: score += 6
        
        if 40 <= k <= 60: score += 10
        elif 30 <= k <= 70: score += 6
        
        if 5.5 <= ph <= 7.0: score += 15
        elif 5.0 <= ph <= 7.5: score += 10
        
        # Climate parameters (60% weight)
        if 20 <= temp <= 35: score += 20
        elif 18 <= temp <= 38: score += 15
        
        if humidity >= 80: score += 20
        elif humidity >= 70: score += 15
        
        if rainfall >= 150: score += 20
        elif rainfall >= 100: score += 15
        
        return score

    def _calculate_wheat_suitability(self, n: float, p: float, k: float, ph: float,
                                   temp: float, humidity: float, rainfall: float) -> int:
        """Calculate wheat suitability score"""
        score = 0
        
        # Soil parameters
        if 50 <= n <= 80: score += 15
        if 30 <= p <= 50: score += 10
        if 30 <= k <= 50: score += 10
        if 6.0 <= ph <= 7.5: score += 15
        
        # Climate parameters (wheat prefers cooler, drier conditions)
        if 15 <= temp <= 25: score += 25
        elif 10 <= temp <= 30: score += 15
        
        if 50 <= humidity <= 70: score += 15
        elif 40 <= humidity <= 80: score += 10
        
        if 50 <= rainfall <= 100: score += 20
        elif 30 <= rainfall <= 150: score += 10
        
        return score

    def _calculate_maize_suitability(self, n: float, p: float, k: float, ph: float,
                                   temp: float, humidity: float, rainfall: float) -> int:
        """Calculate maize suitability score"""
        score = 0
        
        # Soil parameters
        if 75 <= n <= 100: score += 15
        if 50 <= p <= 75: score += 10
        if 75 <= k <= 100: score += 10
        if 5.8 <= ph <= 7.0: score += 15
        
        # Climate parameters
        if 21 <= temp <= 27: score += 20
        elif 18 <= temp <= 30: score += 15
        
        if 60 <= humidity <= 70: score += 15
        
        if 50 <= rainfall <= 100: score += 20
        elif 40 <= rainfall <= 120: score += 15
        
        return score

    def _calculate_cotton_suitability(self, n: float, p: float, k: float, ph: float,
                                    temp: float, humidity: float, rainfall: float) -> int:
        """Calculate cotton suitability score"""
        score = 0
        
        # Soil parameters
        if 60 <= n <= 90: score += 10
        if 30 <= p <= 50: score += 10
        if 50 <= k <= 80: score += 10
        if 5.8 <= ph <= 8.0: score += 15
        
        # Climate parameters
        if 21 <= temp <= 30: score += 20
        elif 18 <= temp <= 35: score += 15
        
        if 50 <= humidity <= 80: score += 15
        
        if 50 <= rainfall <= 100: score += 20
        elif 40 <= rainfall <= 120: score += 15
        
        return score

    def _get_kerala_specific_crops(self, n: float, p: float, k: float, ph: float,
                                 temp: float, humidity: float, rainfall: float) -> List[Dict[str, Any]]:
        """Get Kerala-specific crop recommendations"""
        kerala_crops = []
        
        # Coconut
        if humidity >= 75 and rainfall >= 150 and temp >= 24:
            coconut_score = 60
            if ph >= 5.5 and ph <= 7.5: coconut_score += 20
            if rainfall >= 200: coconut_score += 15
            
            kerala_crops.append({
                "crop": "Coconut",
                "suitability_score": min(100, coconut_score),
                "confidence": "high",
                "recommendation_reason": "Excellent climate conditions for coconut cultivation in Kerala"
            })
        
        # Pepper
        if temp >= 20 and temp <= 30 and humidity >= 75 and rainfall >= 125:
            pepper_score = 65
            if 5.5 <= ph <= 6.5: pepper_score += 15
            if rainfall >= 200: pepper_score += 10
            
            kerala_crops.append({
                "crop": "Pepper",
                "suitability_score": min(100, pepper_score),
                "confidence": "high", 
                "recommendation_reason": "Ideal Kerala climate for spice cultivation"
            })
        
        # Cardamom (hill crop)
        if temp >= 18 and temp <= 25 and humidity >= 80 and rainfall >= 200:
            cardamom_score = 70
            if 5.0 <= ph <= 6.5: cardamom_score += 15
            
            kerala_crops.append({
                "crop": "Cardamom",
                "suitability_score": min(100, cardamom_score),
                "confidence": "high",
                "recommendation_reason": "Perfect hill station climate for cardamom"
            })
        
        # Banana
        if temp >= 26 and temp <= 30 and humidity >= 75 and rainfall >= 100:
            banana_score = 60
            if k >= 40: banana_score += 15
            if rainfall >= 150: banana_score += 10
            
            kerala_crops.append({
                "crop": "Banana",
                "suitability_score": min(100, banana_score),
                "confidence": "medium",
                "recommendation_reason": "Good tropical conditions for banana cultivation"
            })
        
        return kerala_crops

    def _get_crop_name(self, crop_index: int) -> str:
        """Map crop index to crop name"""
        crop_mapping = {
            0: "Rice", 1: "Wheat", 2: "Maize", 3: "Cotton", 4: "Pigeon Peas",
            5: "Moth Beans", 6: "Mung Bean", 7: "Black Gram", 8: "Lentil", 9: "Pomegranate",
            10: "Banana", 11: "Mango", 12: "Grapes", 13: "Watermelon", 14: "Muskmelon",
            15: "Apple", 16: "Orange", 17: "Papaya", 18: "Coconut", 19: "Cotton",
            20: "Jute", 21: "Coffee"
        }
        return crop_mapping.get(crop_index, f"Crop {crop_index}")

    def _get_crop_reason(self, crop_name: str, n: float, p: float, k: float, ph: float,
                        temp: float, humidity: float, rainfall: float) -> str:
        """Get explanation for crop recommendation"""
        reasons = []
        
        if crop_name == "Rice":
            if humidity >= 80: reasons.append("high humidity suitable")
            if rainfall >= 150: reasons.append("adequate rainfall")
            if 5.5 <= ph <= 7.0: reasons.append("optimal soil pH")
        
        elif crop_name == "Wheat":
            if 15 <= temp <= 25: reasons.append("cool climate preferred")
            if 50 <= rainfall <= 100: reasons.append("moderate rainfall needed")
            if 6.0 <= ph <= 7.5: reasons.append("suitable soil pH")
        
        elif crop_name == "Maize":
            if 21 <= temp <= 27: reasons.append("optimal temperature range")
            if 75 <= n <= 100: reasons.append("good nitrogen levels")
            if 5.8 <= ph <= 7.0: reasons.append("suitable soil pH")
        
        elif crop_name == "Cotton":
            if 21 <= temp <= 30: reasons.append("warm climate suitable")
            if 50 <= humidity <= 80: reasons.append("moderate humidity")
            if 5.8 <= ph <= 8.0: reasons.append("tolerant pH range")
        
        if not reasons:
            reasons.append("based on overall parameter compatibility")
        
        return f"Recommended due to {', '.join(reasons)}"

    def _get_fallback_recommendations(self, location: str) -> Dict[str, Any]:
        """Get fallback recommendations when analysis fails"""
        
        fallback_crops = [
            {
                "crop": "Rice",
                "suitability_score": 75,
                "confidence": "medium",
                "recommendation_reason": "Common staple crop suitable for Kerala climate"
            },
            {
                "crop": "Coconut", 
                "suitability_score": 80,
                "confidence": "high",
                "recommendation_reason": "Traditional Kerala crop with good market demand"
            },
            {
                "crop": "Banana",
                "suitability_score": 70,
                "confidence": "medium", 
                "recommendation_reason": "Year-round cultivation possible in tropical climate"
            }
        ]
        
        return {
            "recommendations": fallback_crops,
            "input_parameters": {},
            "location": location,
            "analysis_method": "Fallback Recommendations",
            "confidence": "low",
            "generated_at": datetime.now().isoformat(),
            "note": "Default recommendations - please provide soil and climate data for accurate analysis"
        }

    def get_crop_requirements(self, crop_name: str) -> Dict[str, Any]:
        """Get specific requirements for a crop"""
        
        crop_requirements = {
            "Rice": {
                "soil": {"nitrogen": "80-120", "phosphorus": "40-60", "potassium": "40-60", "ph": "5.5-7.0"},
                "climate": {"temperature": "20-35°C", "humidity": ">80%", "rainfall": ">150mm"},
                "season": "Kharif (June-Oct) and Rabi (Nov-Mar)",
                "growth_period": "120-150 days"
            },
            "Wheat": {
                "soil": {"nitrogen": "50-80", "phosphorus": "30-50", "potassium": "30-50", "ph": "6.0-7.5"},
                "climate": {"temperature": "15-25°C", "humidity": "50-70%", "rainfall": "50-100mm"},
                "season": "Rabi (Nov-Mar)",
                "growth_period": "120-140 days"
            },
            "Coconut": {
                "soil": {"nitrogen": "Variable", "phosphorus": "Medium", "potassium": "High", "ph": "5.5-7.5"},
                "climate": {"temperature": ">24°C", "humidity": ">75%", "rainfall": ">150mm"},
                "season": "Year-round",
                "growth_period": "5-6 years to bearing"
            }
        }
        
        return crop_requirements.get(crop_name, {
            "note": f"Specific requirements for {crop_name} not available in database"
        })


# Global service instance
crop_recommendation_service = CropRecommendationService()


def get_crop_recommendations(soil_params: Dict[str, float], 
                           climate_params: Dict[str, float],
                           location: str = "Kerala") -> Dict[str, Any]:
    """
    Convenience function for crop recommendations
    
    Args:
        soil_params: Dict with nitrogen, phosphorus, potassium, ph
        climate_params: Dict with temperature, humidity, rainfall
        location: Location for regional considerations
        
    Returns:
        Crop recommendations with suitability scores
    """
    return crop_recommendation_service.get_crop_recommendations(soil_params, climate_params, location)


def get_crop_requirements(crop_name: str) -> Dict[str, Any]:
    """
    Convenience function to get crop requirements
    
    Args:
        crop_name: Name of the crop
        
    Returns:
        Crop requirements and growing conditions
    """
    return crop_recommendation_service.get_crop_requirements(crop_name)


if __name__ == "__main__":
    # Test the service
    print("🧪 Testing Crop Recommendation Service...")
    
    # Test with sample parameters
    soil_params = {
        "nitrogen": 90,
        "phosphorus": 45,
        "potassium": 50,
        "ph": 6.2
    }
    
    climate_params = {
        "temperature": 28,
        "humidity": 85,
        "rainfall": 180
    }
    
    recommendations = get_crop_recommendations(soil_params, climate_params, "Kerala")
    print(f"✅ Got {len(recommendations['recommendations'])} crop recommendations")
    
    for rec in recommendations['recommendations'][:3]:
        print(f"   - {rec['crop']}: {rec['suitability_score']}% ({rec['confidence']})")
    
    print("🎉 Crop Recommendation Service test completed!")