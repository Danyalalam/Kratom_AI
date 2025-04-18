from services.ai_service import GeminiAIService
from services.recommendation import RecommendationService

# Create singleton instances
ai_service = GeminiAIService()
recommendation_service = RecommendationService(ai_service)

def get_recommendation_service() -> RecommendationService:
    return recommendation_service