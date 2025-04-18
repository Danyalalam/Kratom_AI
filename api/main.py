from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from api.models import RecommendationRequest, RecommendationResponse
from api.dependencies import get_recommendation_service
from services.recommendation import RecommendationService
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendation(
    request: RecommendationRequest,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """Get a personalized Kratom dosage recommendation"""
    try:
        logger.info(f"Recommendation request received for age: {request.age}, weight: {request.weight}")
        recommendation = await recommendation_service.get_recommendation(request)
        logger.info(f"Recommendation generated: {recommendation.dosage}")
        return recommendation
    except Exception as e:
        logger.error(f"Error in recommendation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Kratom AI API server")
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)