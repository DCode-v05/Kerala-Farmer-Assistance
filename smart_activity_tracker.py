"""
Smart Activity Tracking System for Kerala Farmer Assistance Platform
Provides intelligent activity logging, suggestions, and learning capabilities
"""

import json
import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging
from enum import Enum

class ActivityType(Enum):
    """Standardized activity types for farming operations"""
    LAND_PREPARATION = "land_preparation"
    SOWING = "sowing"
    FERTILIZATION = "fertilization"
    IRRIGATION = "irrigation"
    PEST_CONTROL = "pest_control"
    DISEASE_MANAGEMENT = "disease_management"
    WEEDING = "weeding"
    HARVESTING = "harvesting"
    POST_HARVEST = "post_harvest"
    MARKETING = "marketing"
    MAINTENANCE = "maintenance"
    MONITORING = "monitoring"
    OTHER = "other"

class ActivityStatus(Enum):
    """Activity status tracking"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"

class SmartActivityTracker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Activity templates with Malayalam translations
        self.activity_templates = {
            ActivityType.LAND_PREPARATION: {
                "name": "Land Preparation",
                "malayalam": "നിലം തയ്യാറാക്കൽ",
                "sub_activities": [
                    {"name": "Ploughing", "malayalam": "ഉഴവ്", "duration": "1-2 days"},
                    {"name": "Harrowing", "malayalam": "കിളയൽ", "duration": "1 day"},
                    {"name": "Leveling", "malayalam": "നിരപ്പാക്കൽ", "duration": "1 day"},
                    {"name": "Manure Application", "malayalam": "വളം ഇടൽ", "duration": "1 day"}
                ],
                "optimal_conditions": ["Dry weather", "Soil moisture 15-20%"],
                "tools_required": ["Tractor/Bullocks", "Plough", "Harrow"]
            },
            ActivityType.SOWING: {
                "name": "Sowing/Planting",
                "malayalam": "വിത്ത് വിതയ്ക്കൽ/നടീൽ",
                "sub_activities": [
                    {"name": "Seed Selection", "malayalam": "വിത്ത് തിരഞ്ഞെടുക്കൽ", "duration": "Half day"},
                    {"name": "Seed Treatment", "malayalam": "വിത്ത് സംസ്കാരം", "duration": "1 day"},
                    {"name": "Sowing", "malayalam": "വിതയ്ക്കൽ", "duration": "1-2 days"},
                    {"name": "Covering/Mulching", "malayalam": "മൂടൽ", "duration": "Half day"}
                ],
                "optimal_conditions": ["Post-monsoon", "Good soil moisture", "Temperature 20-30°C"],
                "tools_required": ["Seed drill/Dibbler", "Seeds", "Organic mulch"]
            },
            ActivityType.FERTILIZATION: {
                "name": "Fertilization",
                "malayalam": "വളം നൽകൽ",
                "sub_activities": [
                    {"name": "Soil Testing", "malayalam": "മണ്ണ് പരിശോധന", "duration": "1 day"},
                    {"name": "Fertilizer Selection", "malayalam": "വളം തിരഞ്ഞെടുക്കൽ", "duration": "Half day"},
                    {"name": "Application", "malayalam": "പ്രയോഗം", "duration": "1 day"},
                    {"name": "Incorporation", "malayalam": "മണ്ണിൽ കലർത്തൽ", "duration": "Half day"}
                ],
                "optimal_conditions": ["Before rain", "Active growth stage", "Early morning application"],
                "tools_required": ["Fertilizer spreader", "Measuring tools", "Protective gear"]
            },
            ActivityType.PEST_CONTROL: {
                "name": "Pest Control",
                "malayalam": "കീട നിയന്ത്രണം",
                "sub_activities": [
                    {"name": "Pest Scouting", "malayalam": "കീട നിരീക്ഷണം", "duration": "Half day"},
                    {"name": "Identification", "malayalam": "തിരിച്ചറിയൽ", "duration": "Half day"},
                    {"name": "Treatment Selection", "malayalam": "ചികിത്സ തിരഞ്ഞെടുക്കൽ", "duration": "Half day"},
                    {"name": "Application", "malayalam": "പ്രയോഗം", "duration": "1 day"}
                ],
                "optimal_conditions": ["Early morning/evening", "No wind", "No rain for 24 hours"],
                "tools_required": ["Sprayer", "Pesticides/Bio-agents", "Protective gear"]
            },
            ActivityType.IRRIGATION: {
                "name": "Irrigation",
                "malayalam": "നീരൊഴുക്ക്",
                "sub_activities": [
                    {"name": "Soil Moisture Check", "malayalam": "മണ്ണിലെ ഈർപ്പം പരിശോധന", "duration": "30 minutes"},
                    {"name": "Water Source Check", "malayalam": "ജല സ്രോത പരിശോധന", "duration": "30 minutes"},
                    {"name": "Irrigation", "malayalam": "നീരൊഴുക്ക്", "duration": "2-4 hours"},
                    {"name": "System Maintenance", "malayalam": "സിസ്റ്റം പരിപാലനം", "duration": "1 hour"}
                ],
                "optimal_conditions": ["Early morning", "Soil moisture below 70%", "No recent rain"],
                "tools_required": ["Irrigation system", "Water pump", "Pipes/Channels"]
            },
            ActivityType.HARVESTING: {
                "name": "Harvesting",
                "malayalam": "വിളവെടുപ്പ്",
                "sub_activities": [
                    {"name": "Maturity Assessment", "malayalam": "പക്വത വിലയിരുത്തൽ", "duration": "1 hour"},
                    {"name": "Weather Check", "malayalam": "കാലാവസ്ഥ പരിശോധന", "duration": "30 minutes"},
                    {"name": "Harvesting", "malayalam": "വിളവെടുപ്പ്", "duration": "2-5 days"},
                    {"name": "Initial Processing", "malayalam": "പ്രാഥമിക സംസ്കരണം", "duration": "1-2 days"}
                ],
                "optimal_conditions": ["Dry weather", "Early morning harvest", "Full maturity"],
                "tools_required": ["Harvesting tools", "Collection containers", "Transportation"]
            }
        }
        
        # Crop-specific activity calendars
        self.crop_calendars = {
            "rice": {
                "kharif": {
                    "land_preparation": {"start_month": 5, "end_month": 6},
                    "sowing": {"start_month": 6, "end_month": 7},
                    "fertilization": {"start_month": 7, "end_month": 9},
                    "pest_control": {"start_month": 8, "end_month": 10},
                    "harvesting": {"start_month": 10, "end_month": 11}
                },
                "rabi": {
                    "land_preparation": {"start_month": 11, "end_month": 12},
                    "sowing": {"start_month": 12, "end_month": 1},
                    "fertilization": {"start_month": 1, "end_month": 3},
                    "pest_control": {"start_month": 2, "end_month": 4},
                    "harvesting": {"start_month": 4, "end_month": 5}
                }
            },
            "coconut": {
                "year_round": {
                    "fertilization": {"frequency": "quarterly", "months": [3, 6, 9, 12]},
                    "pest_control": {"frequency": "monthly", "peak_months": [4, 5, 9, 10]},
                    "harvesting": {"frequency": "monthly", "optimal_months": [1, 2, 11, 12]},
                    "maintenance": {"frequency": "bi_annual", "months": [6, 12]}
                }
            },
            "vegetables": {
                "continuous": {
                    "land_preparation": {"frequency": "seasonal", "months": [3, 6, 10]},
                    "sowing": {"frequency": "seasonal", "months": [4, 7, 11]},
                    "fertilization": {"frequency": "weekly_biweekly"},
                    "pest_control": {"frequency": "weekly"},
                    "harvesting": {"frequency": "continuous", "start_after_days": 45}
                }
            }
        }
    
    def log_activity(self, farmer_id: str, activity_data: Dict) -> Dict:
        """Log a farming activity with intelligent enhancements"""
        
        # Extract and validate activity data
        activity_type = self._parse_activity_type(activity_data.get("activity_type", "other"))
        
        # Create enhanced activity record
        enhanced_activity = {
            "id": self._generate_activity_id(),
            "farmer_id": farmer_id,
            "activity_type": activity_type.value,
            "activity_name": activity_data.get("name", activity_type.value.replace("_", " ").title()),
            "description": activity_data.get("description", ""),
            "notes": activity_data.get("notes", ""),
            "status": activity_data.get("status", ActivityStatus.COMPLETED.value),
            "date_planned": activity_data.get("date_planned"),
            "date_started": activity_data.get("date_started"),
            "date_completed": activity_data.get("date_completed", datetime.datetime.now().isoformat()),
            "duration_hours": activity_data.get("duration_hours"),
            "cost": activity_data.get("cost", 0),
            "crop": activity_data.get("crop"),
            "area_covered": activity_data.get("area_covered"),
            "weather_conditions": activity_data.get("weather_conditions"),
            "materials_used": activity_data.get("materials_used", []),
            "tools_used": activity_data.get("tools_used", []),
            "results": activity_data.get("results", {}),
            "created_at": datetime.datetime.now().isoformat(),
            
            # AI-enhanced fields
            "ai_suggestions": self._generate_activity_suggestions(farmer_id, activity_type, activity_data),
            "next_recommended_activities": self._suggest_next_activities(farmer_id, activity_type, activity_data),
            "lessons_learned": self._extract_lessons(activity_data),
            "improvement_suggestions": self._suggest_improvements(activity_data),
            "seasonal_context": self._get_seasonal_context(activity_type, activity_data.get("crop"))
        }
        
        return enhanced_activity
    
    def get_upcoming_activities(self, farmer_id: str, farmer_profile: Dict, days_ahead: int = 30) -> List[Dict]:
        """Get upcoming recommended activities based on farmer profile and season"""
        
        upcoming = []
        current_date = datetime.datetime.now()
        
        # Get farmer's crops and current season
        crops = farmer_profile.get("farm_details", {}).get("crops", [])
        current_month = current_date.month
        
        for crop_data in crops:
            crop_name = self._normalize_crop_name(crop_data.get("crop", ""))
            
            if crop_name in self.crop_calendars:
                crop_calendar = self.crop_calendars[crop_name]
                
                # Check each season/pattern
                for season, activities in crop_calendar.items():
                    for activity_type, timing in activities.items():
                        activity_recommendations = self._check_activity_timing(
                            activity_type, timing, current_month, crop_data
                        )
                        
                        if activity_recommendations:
                            for rec in activity_recommendations:
                                rec.update({
                                    "farmer_id": farmer_id,
                                    "crop": crop_data.get("crop"),
                                    "crop_area": crop_data.get("area_acres", 0),
                                    "priority": self._calculate_activity_priority(activity_type, timing, current_month),
                                    "estimated_cost": self._estimate_activity_cost(activity_type, crop_data),
                                    "weather_dependency": self._check_weather_dependency(activity_type)
                                })
                                upcoming.append(rec)
        
        # Sort by priority and date
        upcoming.sort(key=lambda x: (x.get("priority", 5), x.get("recommended_date", "")))
        
        return upcoming[:10]  # Return top 10 recommendations
    
    def analyze_farmer_patterns(self, farmer_id: str, activities: List[Dict]) -> Dict:
        """Analyze farmer's activity patterns for insights and recommendations"""
        
        if not activities:
            return {"error": "No activities to analyze"}
        
        analysis = {
            "activity_frequency": {},
            "seasonal_patterns": {},
            "crop_wise_activities": {},
            "cost_analysis": {},
            "timing_analysis": {},
            "success_patterns": {},
            "recommendations": []
        }
        
        # Analyze activity frequency
        for activity in activities:
            activity_type = activity.get("activity_type", "other")
            analysis["activity_frequency"][activity_type] = analysis["activity_frequency"].get(activity_type, 0) + 1
        
        # Analyze seasonal patterns
        for activity in activities:
            date_str = activity.get("date_completed") or activity.get("created_at")
            if date_str:
                try:
                    date = datetime.datetime.fromisoformat(date_str.replace("Z", ""))
                    month = date.month
                    season = self._get_season_from_month(month)
                    
                    if season not in analysis["seasonal_patterns"]:
                        analysis["seasonal_patterns"][season] = {}
                    
                    activity_type = activity.get("activity_type", "other")
                    analysis["seasonal_patterns"][season][activity_type] = (
                        analysis["seasonal_patterns"][season].get(activity_type, 0) + 1
                    )
                except:
                    continue
        
        # Analyze crop-wise activities
        for activity in activities:
            crop = activity.get("crop", "unknown")
            if crop not in analysis["crop_wise_activities"]:
                analysis["crop_wise_activities"][crop] = {}
            
            activity_type = activity.get("activity_type", "other")
            analysis["crop_wise_activities"][crop][activity_type] = (
                analysis["crop_wise_activities"][crop].get(activity_type, 0) + 1
            )
        
        # Analyze costs
        total_cost = sum(activity.get("cost", 0) for activity in activities)
        analysis["cost_analysis"] = {
            "total_cost": total_cost,
            "average_cost_per_activity": total_cost / len(activities) if activities else 0,
            "cost_by_type": {}
        }
        
        for activity in activities:
            activity_type = activity.get("activity_type", "other")
            cost = activity.get("cost", 0)
            if activity_type not in analysis["cost_analysis"]["cost_by_type"]:
                analysis["cost_analysis"]["cost_by_type"][activity_type] = {"total": 0, "count": 0}
            
            analysis["cost_analysis"]["cost_by_type"][activity_type]["total"] += cost
            analysis["cost_analysis"]["cost_by_type"][activity_type]["count"] += 1
        
        # Generate recommendations based on analysis
        analysis["recommendations"] = self._generate_pattern_based_recommendations(analysis)
        
        return analysis
    
    def get_activity_suggestions(self, farmer_id: str, farmer_profile: Dict, current_weather: Dict = None) -> List[Dict]:
        """Get intelligent activity suggestions based on current context"""
        
        suggestions = []
        current_date = datetime.datetime.now()
        current_month = current_date.month
        
        # Weather-based suggestions
        if current_weather:
            weather_suggestions = self._get_weather_based_suggestions(current_weather, farmer_profile)
            suggestions.extend(weather_suggestions)
        
        # Season-based suggestions
        seasonal_suggestions = self._get_seasonal_suggestions(current_month, farmer_profile)
        suggestions.extend(seasonal_suggestions)
        
        # Crop stage-based suggestions
        crop_suggestions = self._get_crop_stage_suggestions(farmer_profile)
        suggestions.extend(crop_suggestions)
        
        # Remove duplicates and prioritize
        unique_suggestions = self._deduplicate_suggestions(suggestions)
        prioritized_suggestions = sorted(unique_suggestions, 
                                       key=lambda x: x.get("priority_score", 0), 
                                       reverse=True)
        
        return prioritized_suggestions[:8]  # Return top 8 suggestions
    
    def create_activity_plan(self, farmer_id: str, farmer_profile: Dict, planning_horizon_days: int = 90) -> Dict:
        """Create a comprehensive activity plan for the farmer"""
        
        plan = {
            "farmer_id": farmer_id,
            "plan_start_date": datetime.datetime.now().isoformat(),
            "plan_end_date": (datetime.datetime.now() + datetime.timedelta(days=planning_horizon_days)).isoformat(),
            "planning_horizon_days": planning_horizon_days,
            "activities": [],
            "milestones": [],
            "resource_requirements": {},
            "cost_estimation": {},
            "risk_factors": [],
            "success_metrics": []
        }
        
        # Generate activities for each crop
        crops = farmer_profile.get("farm_details", {}).get("crops", [])
        
        for crop_data in crops:
            crop_activities = self._generate_crop_activity_plan(
                crop_data, planning_horizon_days, farmer_profile
            )
            plan["activities"].extend(crop_activities)
        
        # Add general farm activities
        general_activities = self._generate_general_activity_plan(
            farmer_profile, planning_horizon_days
        )
        plan["activities"].extend(general_activities)
        
        # Calculate resource requirements and costs
        plan["resource_requirements"] = self._calculate_resource_requirements(plan["activities"])
        plan["cost_estimation"] = self._calculate_plan_costs(plan["activities"])
        
        # Identify risk factors
        plan["risk_factors"] = self._identify_plan_risks(plan["activities"], farmer_profile)
        
        # Define success metrics
        plan["success_metrics"] = self._define_success_metrics(plan["activities"], farmer_profile)
        
        return plan
    
    def track_activity_outcomes(self, activity_id: str, outcome_data: Dict) -> Dict:
        """Track and analyze activity outcomes for learning"""
        
        outcome = {
            "activity_id": activity_id,
            "outcome_date": datetime.datetime.now().isoformat(),
            "success_level": outcome_data.get("success_level", "medium"),  # high, medium, low
            "yield_achieved": outcome_data.get("yield_achieved"),
            "quality_rating": outcome_data.get("quality_rating"),
            "cost_effectiveness": outcome_data.get("cost_effectiveness"),
            "time_efficiency": outcome_data.get("time_efficiency"),
            "challenges_faced": outcome_data.get("challenges_faced", []),
            "what_worked_well": outcome_data.get("what_worked_well", []),
            "improvements_for_next_time": outcome_data.get("improvements_for_next_time", []),
            "farmer_satisfaction": outcome_data.get("farmer_satisfaction"),
            "would_repeat": outcome_data.get("would_repeat", True),
            
            # AI analysis
            "success_factors": self._analyze_success_factors(outcome_data),
            "learning_points": self._extract_learning_points(outcome_data),
            "recommendations_for_similar_activities": self._generate_outcome_based_recommendations(outcome_data)
        }
        
        return outcome
    
    # Helper methods
    def _parse_activity_type(self, activity_type_str: str) -> ActivityType:
        """Parse activity type from string"""
        try:
            return ActivityType(activity_type_str.lower())
        except ValueError:
            return ActivityType.OTHER
    
    def _generate_activity_id(self) -> str:
        """Generate unique activity ID"""
        return f"ACT_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _generate_activity_suggestions(self, farmer_id: str, activity_type: ActivityType, activity_data: Dict) -> List[Dict]:
        """Generate AI-powered suggestions for the activity"""
        suggestions = []
        
        template = self.activity_templates.get(activity_type, {})
        
        # Add template-based suggestions
        if template:
            suggestions.append({
                "type": "best_practice",
                "message": f"For optimal {template['name'].lower()}, consider: {', '.join(template.get('optimal_conditions', []))}",
                "malayalam": f"ഉത്തമമായ {template.get('malayalam', '')} എന്നതിനായി പരിഗണിക്കുക"
            })
        
        # Add contextual suggestions based on data
        crop = activity_data.get("crop")
        if crop and activity_type == ActivityType.PEST_CONTROL:
            suggestions.append({
                "type": "crop_specific",
                "message": f"For {crop}, monitor for common pests during this season",
                "malayalam": f"{crop} വിളയിൽ ഈ സീസണിൽ പൊതുവായുള്ള കീടങ്ങൾക്കായി നിരീക്ഷിക്കുക"
            })
        
        return suggestions
    
    def _suggest_next_activities(self, farmer_id: str, completed_activity: ActivityType, activity_data: Dict) -> List[Dict]:
        """Suggest logical next activities"""
        next_activities = []
        
        # Activity sequence mapping
        activity_sequences = {
            ActivityType.LAND_PREPARATION: [ActivityType.SOWING],
            ActivityType.SOWING: [ActivityType.IRRIGATION, ActivityType.FERTILIZATION],
            ActivityType.FERTILIZATION: [ActivityType.MONITORING],
            ActivityType.PEST_CONTROL: [ActivityType.MONITORING],
            ActivityType.MONITORING: [ActivityType.IRRIGATION, ActivityType.PEST_CONTROL, ActivityType.HARVESTING],
            ActivityType.HARVESTING: [ActivityType.POST_HARVEST, ActivityType.MARKETING]
        }
        
        suggested_types = activity_sequences.get(completed_activity, [])
        
        for activity_type in suggested_types:
            template = self.activity_templates.get(activity_type, {})
            next_activities.append({
                "activity_type": activity_type.value,
                "name": template.get("name", activity_type.value),
                "malayalam": template.get("malayalam", ""),
                "recommended_timing": "Within 1-7 days",
                "priority": "medium"
            })
        
        return next_activities
    
    def _extract_lessons(self, activity_data: Dict) -> List[str]:
        """Extract lessons learned from activity data"""
        lessons = []
        
        # Extract from notes if available
        notes = activity_data.get("notes", "")
        if "learned" in notes.lower() or "lesson" in notes.lower():
            lessons.append("Review detailed notes for specific learnings")
        
        # Extract from results
        results = activity_data.get("results", {})
        if results.get("success_level") == "high":
            lessons.append("Document successful practices for replication")
        elif results.get("success_level") == "low":
            lessons.append("Analyze challenges for improvement opportunities")
        
        return lessons
    
    def _suggest_improvements(self, activity_data: Dict) -> List[str]:
        """Suggest improvements for future similar activities"""
        improvements = []
        
        # Cost-based improvements
        cost = activity_data.get("cost", 0)
        if cost > 0:
            improvements.append("Consider cost optimization strategies")
        
        # Duration-based improvements
        duration = activity_data.get("duration_hours", 0)
        if duration > 8:  # If activity took more than 8 hours
            improvements.append("Explore time-saving techniques or tools")
        
        # Weather-based improvements
        weather = activity_data.get("weather_conditions", {})
        if weather.get("condition") == "rainy":
            improvements.append("Plan weather-dependent activities more carefully")
        
        return improvements
    
    def _get_seasonal_context(self, activity_type: ActivityType, crop: str = None) -> Dict:
        """Get seasonal context for the activity"""
        current_month = datetime.datetime.now().month
        season = self._get_season_from_month(current_month)
        
        context = {
            "current_season": season,
            "current_month": current_month,
            "seasonal_suitability": "medium"  # Default
        }
        
        # Crop and activity specific context
        if crop and crop in self.crop_calendars:
            crop_calendar = self.crop_calendars[crop]
            for season_key, activities in crop_calendar.items():
                if activity_type.value in activities:
                    timing = activities[activity_type.value]
                    if self._is_optimal_timing(timing, current_month):
                        context["seasonal_suitability"] = "high"
                        context["timing_message"] = "Optimal timing for this activity"
                    break
        
        return context
    
    def _get_season_from_month(self, month: int) -> str:
        """Get season from month number"""
        if month in [6, 7, 8, 9]:
            return "monsoon"
        elif month in [10, 11, 12, 1]:
            return "post_monsoon"
        elif month in [2, 3, 4, 5]:
            return "summer"
        else:
            return "unknown"
    
    def _normalize_crop_name(self, crop_name: str) -> str:
        """Normalize crop name to match calendar keys"""
        crop_lower = crop_name.lower()
        
        if "rice" in crop_lower or "paddy" in crop_lower:
            return "rice"
        elif "coconut" in crop_lower:
            return "coconut"
        elif "vegetable" in crop_lower or any(veg in crop_lower for veg in ["tomato", "okra", "brinjal"]):
            return "vegetables"
        else:
            return crop_lower
    
    def _check_activity_timing(self, activity_type: str, timing: Dict, current_month: int, crop_data: Dict) -> List[Dict]:
        """Check if it's the right time for an activity"""
        recommendations = []
        
        if "start_month" in timing and "end_month" in timing:
            start_month = timing["start_month"]
            end_month = timing["end_month"]
            
            if self._is_month_in_range(current_month, start_month, end_month):
                recommendations.append({
                    "activity_type": activity_type,
                    "recommended_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "urgency": "high" if current_month == end_month else "medium",
                    "timing_reason": f"Optimal season for {activity_type.replace('_', ' ')}"
                })
        
        elif "months" in timing:  # For quarterly/specific month activities
            if current_month in timing["months"]:
                recommendations.append({
                    "activity_type": activity_type,
                    "recommended_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "urgency": "high",
                    "timing_reason": f"Scheduled month for {activity_type.replace('_', ' ')}"
                })
        
        return recommendations
    
    def _is_month_in_range(self, month: int, start_month: int, end_month: int) -> bool:
        """Check if month is in range, handling year wrap-around"""
        if start_month <= end_month:
            return start_month <= month <= end_month
        else:  # Range crosses year boundary
            return month >= start_month or month <= end_month
    
    def _calculate_activity_priority(self, activity_type: str, timing: Dict, current_month: int) -> int:
        """Calculate priority score (1-5, 1 being highest priority)"""
        
        # Time-sensitive activities get higher priority
        if "end_month" in timing and current_month == timing["end_month"]:
            return 1
        elif activity_type in ["pest_control", "irrigation"]:
            return 2
        elif activity_type in ["fertilization", "harvesting"]:
            return 3
        else:
            return 4
    
    def _estimate_activity_cost(self, activity_type: str, crop_data: Dict) -> float:
        """Estimate cost for an activity"""
        area = crop_data.get("area_acres", 1)
        
        # Base cost per acre for different activities
        cost_per_acre = {
            "land_preparation": 2000,
            "sowing": 1500,
            "fertilization": 3000,
            "irrigation": 500,
            "pest_control": 1000,
            "harvesting": 2500,
            "weeding": 800
        }
        
        return cost_per_acre.get(activity_type, 1000) * area
    
    def _check_weather_dependency(self, activity_type: str) -> str:
        """Check weather dependency level for activity"""
        high_dependency = ["sowing", "harvesting", "pest_control"]
        medium_dependency = ["fertilization", "irrigation"]
        
        if activity_type in high_dependency:
            return "high"
        elif activity_type in medium_dependency:
            return "medium"
        else:
            return "low"
    
    def _generate_pattern_based_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate recommendations based on activity pattern analysis"""
        recommendations = []
        
        # Check for missing critical activities
        critical_activities = ["fertilization", "pest_control", "irrigation"]
        activity_freq = analysis.get("activity_frequency", {})
        
        for critical in critical_activities:
            if activity_freq.get(critical, 0) < 2:  # Less than 2 times
                recommendations.append({
                    "type": "missing_activity",
                    "priority": "high",
                    "message": f"Consider increasing frequency of {critical.replace('_', ' ')}",
                    "malayalam": f"{critical.replace('_', ' ')} കൂടുതൽ തവണ നടത്താൻ പരിഗണിക്കുക"
                })
        
        # Cost optimization recommendations
        cost_analysis = analysis.get("cost_analysis", {})
        avg_cost = cost_analysis.get("average_cost_per_activity", 0)
        
        if avg_cost > 2000:  # If average cost is high
            recommendations.append({
                "type": "cost_optimization",
                "priority": "medium",
                "message": "Look for cost-effective alternatives for expensive activities",
                "malayalam": "ചെലവേറിയ പ്രവർത്തനങ്ങൾക്ക് ചെലവ് കുറഞ്ഞ ബദലുകൾ തേടുക"
            })
        
        return recommendations
    
    def _get_weather_based_suggestions(self, current_weather: Dict, farmer_profile: Dict) -> List[Dict]:
        """Get activity suggestions based on current weather"""
        suggestions = []
        
        condition = current_weather.get("condition", "").lower()
        temperature = current_weather.get("temperature", 25)
        humidity = current_weather.get("humidity", 70)
        
        # Rainy weather suggestions
        if "rain" in condition:
            suggestions.append({
                "activity_type": "monitoring",
                "message": "Good time for field monitoring and planning",
                "malayalam": "വയൽ നിരീക്ഷണത്തിനും ആസൂത്രണത്തിനും നല്ല സമയം",
                "priority_score": 7,
                "weather_context": "Rainy weather - indoor/covered activities recommended"
            })
        
        # Sunny weather suggestions
        elif "sunny" in condition or "clear" in condition:
            suggestions.append({
                "activity_type": "harvesting",
                "message": "Excellent weather for harvesting and drying activities",
                "malayalam": "വിളവെടുപ്പിനും ഉണക്കുന്നതിനും മികച്ച കാലാവസ്ഥ",
                "priority_score": 9,
                "weather_context": "Sunny weather - optimal for outdoor activities"
            })
            
            suggestions.append({
                "activity_type": "pest_control",
                "message": "Good conditions for spraying (if no wind)",
                "malayalam": "സ്പ്രേ ചെയ്യുന്നതിന് നല്ല സാഹചര്യങ്ങൾ (കാറ്റില്ലെങ്കിൽ)",
                "priority_score": 8,
                "weather_context": "Sunny weather - good for treatments"
            })
        
        return suggestions
    
    def _get_seasonal_suggestions(self, current_month: int, farmer_profile: Dict) -> List[Dict]:
        """Get activity suggestions based on current season"""
        suggestions = []
        season = self._get_season_from_month(current_month)
        
        if season == "monsoon":
            suggestions.append({
                "activity_type": "sowing",
                "message": "Optimal time for kharif crop sowing",
                "malayalam": "ഖരീഫ് വിള വിതയ്ക്കുന്നതിന് അനുയോജ്യമായ സമയം",
                "priority_score": 9,
                "seasonal_context": "Monsoon season - water abundant"
            })
        
        elif season == "post_monsoon":
            suggestions.append({
                "activity_type": "harvesting",
                "message": "Time for kharif crop harvesting",
                "malayalam": "ഖരീഫ് വിള വിളവെടുപ്പിന്റെ സമയം",
                "priority_score": 9,
                "seasonal_context": "Post-monsoon - harvesting season"
            })
        
        elif season == "summer":
            suggestions.append({
                "activity_type": "irrigation",
                "message": "Regular irrigation critical during summer",
                "malayalam": "വേനൽക്കാലത്ത് പതിവ് നീരൊഴുക്ക് അത്യാവശ്യം",
                "priority_score": 9,
                "seasonal_context": "Summer season - water management crucial"
            })
        
        return suggestions
    
    def _get_crop_stage_suggestions(self, farmer_profile: Dict) -> List[Dict]:
        """Get suggestions based on crop growth stages"""
        suggestions = []
        
        # This would be enhanced with actual crop stage tracking
        # For now, providing general suggestions
        
        crops = farmer_profile.get("farm_details", {}).get("crops", [])
        
        for crop_data in crops:
            crop_name = crop_data.get("crop", "").lower()
            
            if "rice" in crop_name or "paddy" in crop_name:
                suggestions.append({
                    "activity_type": "monitoring",
                    "message": "Monitor rice crop for pests and diseases",
                    "malayalam": "നെല്ല് വിളയെ കീടങ്ങൾക്കും രോഗങ്ങൾക്കുമായി നിരീക്ഷിക്കുക",
                    "priority_score": 7,
                    "crop_context": f"Rice crop management"
                })
            
            elif "coconut" in crop_name:
                suggestions.append({
                    "activity_type": "maintenance",
                    "message": "Check coconut palms for crown cleaning needs",
                    "malayalam": "തേങ്ങാ മരങ്ങളുടെ കിരീടം വൃത്തിയാക്കേണ്ടതുണ്ടോ എന്ന് പരിശോധിക്കുക",
                    "priority_score": 6,
                    "crop_context": "Coconut palm maintenance"
                })
        
        return suggestions
    
    def _deduplicate_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """Remove duplicate suggestions based on activity type"""
        seen_types = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            activity_type = suggestion.get("activity_type")
            if activity_type not in seen_types:
                seen_types.add(activity_type)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions
    
    def _is_optimal_timing(self, timing: Dict, current_month: int) -> bool:
        """Check if current timing is optimal for the activity"""
        if "start_month" in timing and "end_month" in timing:
            return self._is_month_in_range(current_month, timing["start_month"], timing["end_month"])
        elif "months" in timing:
            return current_month in timing["months"]
        else:
            return False