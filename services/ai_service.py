import google.generativeai as genai
from typing import Dict, Any
import asyncio
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiAIService:
    def __init__(self):
        # Configure the Gemini API
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Gemini model"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info("Gemini AI model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI model: {str(e)}")
            self.model = None
    
    async def enhance_recommendation(self, base_recommendation: str, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Use Gemini AI to enhance recommendation with additional context"""
        if not self.model:
            logger.warning("Gemini AI model not initialized, returning default recommendation")
            return {
                "additional_info": "Start with a lower dose if you're new to Kratom.",
                "ai_insights": None
            }
        
        # Create a prompt for Gemini
        prompt = self._create_prompt(base_recommendation, user_data)
        
        try:
            # Run the Gemini API call in a separate thread to not block the event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(prompt)
            )
            
            # Parse the response
            response_text = response.text
            
            # Split response into sections (we expect two sections)
            sections = response_text.split("\n\n", 1)
            
            if len(sections) >= 2:
                additional_info = sections[0].strip()
                ai_insights = sections[1].strip()
            else:
                additional_info = response_text
                ai_insights = None
                
            return {
                "additional_info": additional_info,
                "ai_insights": ai_insights
            }
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            return {
                "additional_info": "Start with a lower dose if you're new to Kratom. Stay hydrated.",
                "ai_insights": None
            }
    
    def _create_prompt(self, base_recommendation: str, user_data: Dict[str, Any]) -> str:
        """Create a prompt for the Gemini API"""
        return f"""
        You are a Kratom dosage expert assistant. A user with the following profile needs kratom recommendations:
        
        User Profile:
        - Age: {user_data['age']} years
        - Weight: {user_data['weight']} kg
        - Pain level: {user_data['pain_level']}/10
        - Body type: {user_data['body_type']}
        
        Base recommendation: {base_recommendation}
        
        Provide your response in two concise paragraphs:
        
        Paragraph 1: Practical usage advice (time of day, with/without food, hydration, etc.)
        
        Paragraph 2: Safety considerations and potential interactions to be aware of.

        Keep each paragraph under 3 sentences and focused on practical advice.
        """