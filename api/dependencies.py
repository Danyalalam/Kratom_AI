from services.ai_service import OpenAIService # Import OpenAIService
from services.recommendation import RecommendationService
from services.email_service import EmailService
from services.scheduler import SchedulerService
from config import get_settings
from fastapi import Request

# Create singleton instances using the new service with settings
settings = get_settings()

# Initialize services
scheduler_service = SchedulerService()
scheduler_service.start()  # Start the scheduler

ai_service = OpenAIService()
email_service = EmailService(scheduler=scheduler_service)  # Pass scheduler to email service
recommendation_service = RecommendationService(ai_service)

async def cleanup_ai_service():
    """Cleanup OpenAI service resources"""
    await ai_service.close()

def get_recommendation_service() -> RecommendationService:
    return recommendation_service

def get_email_service() -> EmailService:
    return email_service

def get_scheduler_service() -> SchedulerService:
    return scheduler_service