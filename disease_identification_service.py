"""
Disease Identification Service for Kerala Farmer Assistance
Provides AI-powered plant disease identification using Gemini API
"""

import os
import base64
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import google.generativeai as genai
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")

class DiseaseIdentificationService:
    """Service for plant disease identification and recommendations"""
    
    def __init__(self):
        """Initialize the disease identification service"""
        self.initialize_gemini()
        
    def initialize_gemini(self):
        """Initialize Gemini AI model"""
        try:
            if not GEMINI_API_KEY:
                raise ValueError("Gemini API key not found")
            
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("✅ Gemini AI initialized successfully for disease identification")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini AI: {e}")
            self.model = None

    def analyze_plant_disease(self, image_data: bytes, crop_type: str = "Unknown", 
                            language: str = "English") -> Dict[str, Any]:
        """
        Analyze plant image for disease identification
        
        Args:
            image_data: Raw image bytes
            crop_type: Type of crop (Rice, Coconut, etc.)
            language: Language for response (English/Malayalam)
            
        Returns:
            Dictionary containing disease analysis results
        """
        try:
            if not self.model:
                return self._generate_fallback_analysis(crop_type, language)
            
            # Convert image to base64 for Gemini
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create comprehensive prompt for disease analysis
            prompt = self._create_disease_analysis_prompt(crop_type, language)
            
            # Analyze image with Gemini
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": image_b64
                }
            ])
            
            # Parse and structure the response
            analysis_result = self._parse_gemini_response(response.text, language)
            
            # Add metadata
            analysis_result.update({
                "crop_type": crop_type,
                "language": language,
                "analyzed_at": datetime.now().isoformat(),
                "analysis_method": "AI-Powered (Gemini)",
                "confidence": "high"
            })
            
            logger.info(f"✅ Disease analysis completed for {crop_type}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Error in disease analysis: {e}")
            return self._generate_fallback_analysis(crop_type, language)

    def _create_disease_analysis_prompt(self, crop_type: str, language: str) -> str:
        """Create comprehensive prompt for disease analysis"""
        
        lang_instruction = "Provide response in Malayalam language" if language == "Malayalam" else "Provide response in English language"
        
        prompt = f"""
You are an expert plant pathologist specializing in {crop_type} diseases in Kerala, India. 
Analyze this plant image and provide comprehensive disease identification and treatment recommendations.

{lang_instruction}

Please provide a detailed analysis in the following JSON format:

{{
    "disease_identification": {{
        "primary_disease": "Name of the most likely disease",
        "confidence_level": "High/Medium/Low",
        "alternative_diseases": ["List of other possible diseases"],
        "disease_category": "Fungal/Bacterial/Viral/Nutritional/Pest"
    }},
    "disease_details": {{
        "symptoms_observed": ["List of visible symptoms"],
        "disease_description": "Detailed description of the disease",
        "causes": ["Primary causes of this disease"],
        "severity_level": "Mild/Moderate/Severe",
        "affected_parts": ["Leaves/Stems/Fruits/Roots"]
    }},
    "treatment_recommendations": {{
        "immediate_actions": ["Urgent steps to take"],
        "pesticide_recommendations": [
            {{
                "name": "Pesticide name",
                "type": "Fungicide/Bactericide/Insecticide",
                "dosage": "Application rate",
                "frequency": "How often to apply",
                "safety_precautions": "Safety measures"
            }}
        ],
        "organic_alternatives": ["Natural treatment options"],
        "cultural_practices": ["Preventive farming practices"]
    }},
    "prevention_measures": {{
        "field_hygiene": ["Cleanliness practices"],
        "crop_management": ["Cultivation practices"],
        "environmental_control": ["Climate management"],
        "monitoring_schedule": "How often to check plants"
    }},
    "prognosis": {{
        "recovery_timeline": "Expected recovery time",
        "yield_impact": "Expected impact on harvest",
        "spread_risk": "Risk of disease spreading",
        "follow_up_actions": ["What to do after treatment"]
    }}
}}

Focus on Kerala's climate conditions and commonly available treatments. 
Prioritize safe, effective, and locally available solutions.
If the image shows a healthy plant, indicate that in your analysis.
"""
        return prompt

    def _parse_gemini_response(self, response_text: str, language: str) -> Dict[str, Any]:
        """Parse Gemini response into structured data"""
        try:
            # Try to parse as JSON first
            if '{' in response_text and '}' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            
        except json.JSONDecodeError:
            pass
        
        # Fallback: create structured response from text
        return {
            "disease_identification": {
                "primary_disease": "Analysis Available",
                "confidence_level": "Medium",
                "alternative_diseases": [],
                "disease_category": "Analysis in Progress"
            },
            "disease_details": {
                "symptoms_observed": ["AI analysis completed"],
                "disease_description": response_text[:500] + "...",
                "causes": ["See detailed analysis"],
                "severity_level": "To be determined",
                "affected_parts": ["Under analysis"]
            },
            "treatment_recommendations": {
                "immediate_actions": ["Consult local agricultural officer"],
                "pesticide_recommendations": [],
                "organic_alternatives": ["Neem oil application"],
                "cultural_practices": ["Maintain field hygiene"]
            },
            "ai_analysis_text": response_text
        }

    def _generate_fallback_analysis(self, crop_type: str, language: str) -> Dict[str, Any]:
        """Generate fallback analysis when AI is unavailable"""
        
        fallback_data = {
            "English": {
                "primary_disease": "Analysis Unavailable",
                "description": "AI analysis temporarily unavailable. Please consult local agricultural officer.",
                "immediate_actions": [
                    "Take clear photos of affected plants",
                    "Contact local Krishi Bhavan",
                    "Isolate affected plants if possible",
                    "Monitor spread to other plants"
                ],
                "general_pesticides": [
                    {
                        "name": "Copper Hydroxide",
                        "type": "Fungicide",
                        "dosage": "2-3g per liter",
                        "frequency": "Weekly application"
                    },
                    {
                        "name": "Neem Oil",
                        "type": "Organic",
                        "dosage": "5ml per liter",
                        "frequency": "Twice a week"
                    }
                ]
            },
            "Malayalam": {
                "primary_disease": "വിശകലനം ലഭ്യമല്ല",
                "description": "AI വിശകലനം താൽക്കാലികമായി ലഭ്യമല്ല. ദയവായി പ്രാദേശിക കൃഷി ഉദ്യോഗസ്ഥനെ സമീപിക്കുക.",
                "immediate_actions": [
                    "രോഗബാധിത ചെടികളുടെ വ്യക്തമായ ചിത്രങ്ങൾ എടുക്കുക",
                    "പ്രാദേശിക കൃഷി ഭവനുമായി ബന്ധപ്പെടുക",
                    "സാധ്യമെങ്കിൽ രോഗബാധിത ചെടികളെ വേർതിരിക്കുക",
                    "മറ്റ് ചെടികളിലേക്ക് പടരുന്നത് നിരീക്ഷിക്കുക"
                ],
                "general_pesticides": [
                    {
                        "name": "കോപ്പർ ഹൈഡ്രോക്സൈഡ്",
                        "type": "കുമിൾനാശിനി",
                        "dosage": "ഒരു ലിറ്ററിന് 2-3 ഗ്രാം",
                        "frequency": "ആഴ്ചയിൽ ഒരിക്കൽ"
                    }
                ]
            }
        }
        
        lang_data = fallback_data.get(language, fallback_data["English"])
        
        return {
            "disease_identification": {
                "primary_disease": lang_data["primary_disease"],
                "confidence_level": "Low",
                "alternative_diseases": [],
                "disease_category": "Requires Expert Analysis"
            },
            "disease_details": {
                "symptoms_observed": ["Image analysis needed"],
                "disease_description": lang_data["description"],
                "causes": ["Multiple possible causes"],
                "severity_level": "Unknown",
                "affected_parts": ["To be determined"]
            },
            "treatment_recommendations": {
                "immediate_actions": lang_data["immediate_actions"],
                "pesticide_recommendations": lang_data["general_pesticides"],
                "organic_alternatives": ["Neem oil", "Turmeric paste"],
                "cultural_practices": ["Proper drainage", "Regular monitoring"]
            },
            "crop_type": crop_type,
            "language": language,
            "analyzed_at": datetime.now().isoformat(),
            "analysis_method": "Fallback Analysis",
            "confidence": "low",
            "note": "AI analysis temporarily unavailable"
        }

    def generate_pdf_report(self, analysis_data: Dict[str, Any], 
                          farmer_info: Optional[Dict[str, Any]] = None) -> bytes:
        """
        Generate PDF report of disease analysis
        
        Args:
            analysis_data: Disease analysis results
            farmer_info: Optional farmer information
            
        Returns:
            PDF report as bytes
        """
        try:
            # Create PDF buffer
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                textColor=colors.darkgreen
            )
            
            # Build document content
            content = []
            
            # Title
            language = analysis_data.get('language', 'English')
            title_text = "Plant Disease Analysis Report" if language == 'English' else "സസ്യ രോഗ വിശകലന റിപ്പോർട്ട്"
            content.append(Paragraph(title_text, title_style))
            content.append(Spacer(1, 12))
            
            # Report details
            report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            content.append(Paragraph(f"Report Date: {report_date}", styles['Normal']))
            content.append(Paragraph(f"Crop Type: {analysis_data.get('crop_type', 'Unknown')}", styles['Normal']))
            content.append(Paragraph(f"Analysis Method: {analysis_data.get('analysis_method', 'AI-Powered')}", styles['Normal']))
            content.append(Spacer(1, 12))
            
            # Farmer information if provided
            if farmer_info:
                content.append(Paragraph("Farmer Information", styles['Heading2']))
                content.append(Paragraph(f"Name: {farmer_info.get('name', 'N/A')}", styles['Normal']))
                content.append(Paragraph(f"Location: {farmer_info.get('address', 'N/A')}", styles['Normal']))
                content.append(Paragraph(f"Mobile: {farmer_info.get('mobile_no', 'N/A')}", styles['Normal']))
                content.append(Spacer(1, 12))
            
            # Disease identification
            disease_id = analysis_data.get('disease_identification', {})
            content.append(Paragraph("Disease Identification", styles['Heading2']))
            content.append(Paragraph(f"Primary Disease: {disease_id.get('primary_disease', 'Unknown')}", styles['Normal']))
            content.append(Paragraph(f"Confidence Level: {disease_id.get('confidence_level', 'Medium')}", styles['Normal']))
            content.append(Paragraph(f"Disease Category: {disease_id.get('disease_category', 'Unknown')}", styles['Normal']))
            content.append(Spacer(1, 12))
            
            # Disease details
            disease_details = analysis_data.get('disease_details', {})
            content.append(Paragraph("Disease Details", styles['Heading2']))
            content.append(Paragraph(f"Description: {disease_details.get('disease_description', 'N/A')}", styles['Normal']))
            content.append(Paragraph(f"Severity: {disease_details.get('severity_level', 'Unknown')}", styles['Normal']))
            content.append(Spacer(1, 12))
            
            # Treatment recommendations
            treatment = analysis_data.get('treatment_recommendations', {})
            content.append(Paragraph("Treatment Recommendations", styles['Heading2']))
            
            # Immediate actions
            immediate_actions = treatment.get('immediate_actions', [])
            if immediate_actions:
                content.append(Paragraph("Immediate Actions:", styles['Heading3']))
                for action in immediate_actions:
                    content.append(Paragraph(f"• {action}", styles['Normal']))
                content.append(Spacer(1, 6))
            
            # Pesticide recommendations
            pesticides = treatment.get('pesticide_recommendations', [])
            if pesticides:
                content.append(Paragraph("Pesticide Recommendations:", styles['Heading3']))
                
                # Create table for pesticides
                pesticide_data = [['Name', 'Type', 'Dosage', 'Frequency']]
                for pesticide in pesticides:
                    pesticide_data.append([
                        pesticide.get('name', 'N/A'),
                        pesticide.get('type', 'N/A'),
                        pesticide.get('dosage', 'N/A'),
                        pesticide.get('frequency', 'N/A')
                    ])
                
                pesticide_table = Table(pesticide_data)
                pesticide_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                content.append(pesticide_table)
                content.append(Spacer(1, 12))
            
            # Organic alternatives
            organic_alternatives = treatment.get('organic_alternatives', [])
            if organic_alternatives:
                content.append(Paragraph("Organic Alternatives:", styles['Heading3']))
                for alternative in organic_alternatives:
                    content.append(Paragraph(f"• {alternative}", styles['Normal']))
                content.append(Spacer(1, 12))
            
            # Prevention measures
            prevention = analysis_data.get('prevention_measures', {})
            if prevention:
                content.append(Paragraph("Prevention Measures", styles['Heading2']))
                for key, value in prevention.items():
                    if isinstance(value, list):
                        content.append(Paragraph(f"{key.replace('_', ' ').title()}:", styles['Heading3']))
                        for item in value:
                            content.append(Paragraph(f"• {item}", styles['Normal']))
                    else:
                        content.append(Paragraph(f"{key.replace('_', ' ').title()}: {value}", styles['Normal']))
                content.append(Spacer(1, 12))
            
            # Footer
            content.append(Spacer(1, 24))
            footer_text = "Kerala Farmer Assistance - AI-Powered Agriculture Solutions" if language == 'English' else "കേരള കർഷക സഹായം - AI-കാർഷിക പരിഹാരങ്ങൾ"
            content.append(Paragraph(footer_text, styles['Normal']))
            
            # Build PDF
            doc.build(content)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info("✅ PDF report generated successfully")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"❌ Error generating PDF report: {e}")
            # Return a simple error PDF
            return self._generate_error_pdf(str(e))

    def _generate_error_pdf(self, error_message: str) -> bytes:
        """Generate a simple error PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        content = [
            Paragraph("Disease Analysis Report - Error", styles['Title']),
            Spacer(1, 12),
            Paragraph(f"Error generating report: {error_message}", styles['Normal']),
            Spacer(1, 12),
            Paragraph("Please try again or contact support.", styles['Normal'])
        ]
        
        doc.build(content)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    def get_common_diseases_by_crop(self, crop_type: str, language: str = "English") -> List[Dict[str, Any]]:
        """
        Get common diseases for a specific crop type
        
        Args:
            crop_type: Type of crop
            language: Language for response
            
        Returns:
            List of common diseases with basic information
        """
        
        diseases_db = {
            "Rice": [
                {
                    "name": "Rice Blast" if language == "English" else "നെൽ ബ്ലാസ്റ്റ്",
                    "symptoms": ["Brown spots on leaves", "Diamond-shaped lesions"] if language == "English" else ["ഇലകളിൽ തവിട്ട് പാടുകൾ", "വജ്രാകൃതിയിലുള്ള മുറിവുകൾ"],
                    "treatment": "Copper fungicide" if language == "English" else "കോപ്പർ കുമിൾനാശിനി"
                },
                {
                    "name": "Bacterial Blight" if language == "English" else "ബാക്ടീരിയൽ ബ്ലൈറ്റ്",
                    "symptoms": ["Water-soaked lesions", "Yellow halos"] if language == "English" else ["ജലം കുതിർന്ന മുറിവുകൾ", "മഞ്ഞ വളയങ്ങൾ"],
                    "treatment": "Copper bactericide" if language == "English" else "കോപ്പർ ബാക്ടീരിയനാശിനി"
                }
            ],
            "Coconut": [
                {
                    "name": "Coconut Leaf Blight" if language == "English" else "തെങ്ങിന്റെ ഇല പുരട്",
                    "symptoms": ["Brown patches on leaves", "Leaf yellowing"] if language == "English" else ["ഇലകളിൽ തവിട്ട് പാടുകൾ", "ഇല മഞ്ഞയാകൽ"],
                    "treatment": "Bordeaux mixture" if language == "English" else "ബോർഡോ മിശ്രിതം"
                }
            ],
            "Pepper": [
                {
                    "name": "Pepper Anthracnose" if language == "English" else "കുരുമുളക് ആന്ത്രാക്നോസ്",
                    "symptoms": ["Dark spots on fruits", "Leaf drop"] if language == "English" else ["കായകളിൽ ഇരുണ്ട പാടുകൾ", "ഇല കൊഴിയൽ"],
                    "treatment": "Mancozeb" if language == "English" else "മാൻകോസെബ്"
                }
            ]
        }
        
        return diseases_db.get(crop_type, [])


# Global service instance
disease_service = DiseaseIdentificationService()


def analyze_plant_disease_image(image_data: bytes, crop_type: str = "Unknown", 
                              language: str = "English") -> Dict[str, Any]:
    """
    Convenience function for disease analysis
    
    Args:
        image_data: Raw image bytes
        crop_type: Type of crop
        language: Language for response (English/Malayalam)
        
    Returns:
        Disease analysis results
    """
    return disease_service.analyze_plant_disease(image_data, crop_type, language)


def generate_disease_report_pdf(analysis_data: Dict[str, Any], 
                              farmer_info: Optional[Dict[str, Any]] = None) -> bytes:
    """
    Convenience function for PDF report generation
    
    Args:
        analysis_data: Disease analysis results
        farmer_info: Optional farmer information
        
    Returns:
        PDF report as bytes
    """
    return disease_service.generate_pdf_report(analysis_data, farmer_info)


def get_crop_diseases(crop_type: str, language: str = "English") -> List[Dict[str, Any]]:
    """
    Convenience function to get common diseases for a crop
    
    Args:
        crop_type: Type of crop
        language: Language for response
        
    Returns:
        List of common diseases
    """
    return disease_service.get_common_diseases_by_crop(crop_type, language)


if __name__ == "__main__":
    # Test the service
    print("🧪 Testing Disease Identification Service...")
    
    # Test common diseases lookup
    rice_diseases = get_crop_diseases("Rice", "English")
    print(f"✅ Rice diseases: {len(rice_diseases)} found")
    
    # Test fallback analysis
    fallback_result = disease_service._generate_fallback_analysis("Rice", "English")
    print(f"✅ Fallback analysis: {fallback_result['disease_identification']['primary_disease']}")
    
    print("🎉 Disease Identification Service test completed!")