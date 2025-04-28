from services.ai_service import OpenAIService # Import OpenAIService
from services.recommendation import RecommendationService

# Create singleton instances using the new service
ai_service = OpenAIService()
recommendation_service = RecommendationService(ai_service)

def get_recommendation_service() -> RecommendationService:
    return recommendation_service