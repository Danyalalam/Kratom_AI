from typing import Dict, Any
from api.models import RecommendationRequest, RecommendationResponse
from services.ai_service import OpenAIService # Import the correct AI service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self, ai_service: OpenAIService): 
        self.ai_service = ai_service
        # Mapping of sponsored strains and their vendor information
        self.sponsored_strains = {
            "Red Maeng Da": {
                "vendor": "Premium Botanicals",
                "url": "https://premiumbotanicals.com/red-maeng-da",
                "description": "Premium Red Maeng Da - Lab Tested"
            },
            "Red Bali": {
                "vendor": "Kratom Masters",
                "url": "https://kratommasters.com/red-bali",
                "description": "Authentic Red Bali - Direct Import"
            },
            "Green Malay": {
                "vendor": "Nature's Remedy",
                "url": "https://naturesremedy.com/green-malay",
                "description": "Pure Green Malay - Ethically Sourced"
            },
            "White Thai": {
                "vendor": "Thai Botanicals",
                "url": "https://thaibotanicals.com/white-thai",
                "description": "Premium White Thai - Farm Direct"
            }
        }
    
    def _get_base_recommendation(self, age: int, weight: float, pain_level: int, body_type: str, sex: str) -> tuple[str, dict]:
        """Rule-based logic for Kratom dosage recommendation"""
        # Base dosage calculation based on weight
        base_dosage = weight * 0.03  # 0.03g per kg
        
        # Adjust for pain level
        if pain_level >= 8:
            dosage_multiplier = 1.5
            strain = "Red Maeng Da"
            doses_per_day = 3
        elif pain_level >= 5:
            dosage_multiplier = 1.2
            strain = "Red Bali"
            doses_per_day = 2
        elif pain_level >= 3:
            dosage_multiplier = 1.0
            strain = "Green Malay"
            doses_per_day = 2
        else:
            dosage_multiplier = 0.8
            strain = "White Thai"
            doses_per_day = 1
        
        # Adjust for body type
        if body_type == "ectomorph":
            body_multiplier = 0.9
        elif body_type == "mesomorph":
            body_multiplier = 1.0
        elif body_type == "endomorph":
            body_multiplier = 1.1
        else:  # average
            body_multiplier = 1.0
        
        # Adjust for age
        if age > 65:
            age_multiplier = 0.8
        elif age > 50:
            age_multiplier = 0.9
        else:
            age_multiplier = 1.0
            
        # Adjust for sex (females typically need slightly lower doses)
        sex_multiplier = 0.85 if sex.lower() == "female" else 1.0
        
        # Calculate final dosage
        final_dosage = round(base_dosage * dosage_multiplier * body_multiplier * age_multiplier * sex_multiplier, 1)
        
        # Safety cap
        if final_dosage > 5:
            final_dosage = 5.0
        
        # Get sponsored info if available
        sponsored_info = self.sponsored_strains.get(strain)
        
        # Format the recommendation with daily dosage info
        daily_dosage = round(final_dosage * doses_per_day, 1)
        recommendation = f"{final_dosage}g of {strain} Kratom per dose ({doses_per_day}x daily, total {daily_dosage}g/day)"
        
        return recommendation, sponsored_info
    
    async def get_recommendation(self, request_data: RecommendationRequest) -> RecommendationResponse:
        """Get a recommendation based on user data, enhanced by AI"""
        base_recommendation, sponsored_info = self._get_base_recommendation(
            request_data.age,
            request_data.weight,
            request_data.pain_level,
            request_data.body_type,
            request_data.sex
        )
        
        user_data = {
            "age": request_data.age,
            "weight": request_data.weight,
            "pain_level": request_data.pain_level,
            "body_type": request_data.body_type,
            "sex": request_data.sex,
            "height": {
                "feet": request_data.height['feet'],
                "inches": request_data.height['inches']
            },
            "blood_type": request_data.blood_type
        }
        
        try:
            # Get AI-enhanced information
            ai_response = await self.ai_service.enhance_recommendation(base_recommendation, user_data)
            
            return RecommendationResponse(
                dosage=base_recommendation,
                additional_info=ai_response["additional_info"],
                ai_insights=ai_response["ai_insights"],
                sponsored_info=sponsored_info
            )
        except Exception as e:
            logger.error(f"Error getting AI recommendation: {str(e)}")
            # Fall back to base recommendation if AI fails
            return RecommendationResponse(
                dosage=base_recommendation,
                additional_info="Start with a lower dose if you're new to Kratom.",
                sponsored_info=sponsored_info
            )