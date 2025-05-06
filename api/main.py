from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from api.models import RecommendationRequest, RecommendationResponse
from api.dependencies import get_recommendation_service, get_email_service, cleanup_ai_service
from api.database import Database, UserData, LocationData
from services.recommendation import RecommendationService
from services.email_service import EmailService
from config import settings
import logging
from datetime import datetime
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to see all log levels
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
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

@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup"""
    await Database.connect_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    await Database.close_db()
    await cleanup_ai_service()

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendation(
    request: RecommendationRequest,
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
    email_service: EmailService = Depends(get_email_service)
):
    """Get a personalized Kratom dosage recommendation"""
    try:
        logger.info(f"Recommendation request received for age: {request.age}, weight: {request.weight}")
        
        # Convert location data to the correct format
        location_data = None
        if request.location_data:
            location_data = LocationData(**request.location_data.dict())
        
        # Check if user already exists
        existing_user = await Database.get_user_by_email(request.email)
        
        # Save user data to MongoDB
        user_data = UserData(
            age=request.age,
            height=request.height,
            weight={"kg": request.weight, "lbs": request.weight * 2.20462},  # Convert kg to lbs
            body_type=request.body_type,
            sex=request.sex,  # Changed from sex_type to sex
            blood_type=request.blood_type,
            pain_level=request.pain_level,
            email=request.email,
            newsletter=request.newsletter,
            location=location_data.dict() if location_data else None,  # Convert to dict
            created_at=datetime.utcnow() if not existing_user else None  # Set created_at only for new users
        )
        
        try:
            await Database.save_user_data(user_data)
            logger.info("User data saved/updated in MongoDB")
            
            # Send welcome email only for new users
            if not existing_user:
                await email_service.send_welcome_email(user_data.model_dump())
            
            # Schedule follow-up email if user subscribed to newsletter
            if user_data.newsletter:
                await email_service.schedule_followup_email(user_data.model_dump())
                
        except Exception as db_error:
            logger.error(f"Error saving to MongoDB or sending email: {str(db_error)}")
            # Continue with recommendation even if DB save or email fails
        
        # Get recommendation
        recommendation = await recommendation_service.get_recommendation(request)
        logger.info(f"Recommendation generated: {recommendation.dosage}")
        return recommendation
        
    except Exception as e:
        logger.error(f"Error in recommendation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news")
async def get_news():
    """Fetch kratom-related news articles"""
    try:
        url = f"https://newsapi.org/v2/everything?q=kratom&language=en&sortBy=publishedAt&apiKey={settings.NEWS_API_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Failed to fetch news")
                data = await response.json()
                return data
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch news")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Kratom AI API server")
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)