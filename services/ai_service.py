from openai import AsyncOpenAI, OpenAIError
from typing import Dict, Any
import asyncio
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        # Configure the OpenAI API client
        self.api_key = settings.OPENAI_API_KEY
        self.model_name = settings.OPENAI_MODEL
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the OpenAI async client"""
        if not self.api_key:
            logger.error("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
            self.client = None
            return
            
        try:
            # Use AsyncOpenAI for async operations
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info(f"OpenAI client initialized successfully for model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            self.client = None

    async def enhance_recommendation(self, base_recommendation: str, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Use OpenAI GPT to enhance recommendation with additional context"""
        if not self.client:
            logger.warning("OpenAI client not initialized, returning default recommendation")
            return {
                "additional_info": "Start with a lower dose if you're new to Kratom.",
                "ai_insights": None
            }

        # Create a prompt for OpenAI
        prompt_content = self._create_prompt(base_recommendation, user_data)

        try:
            # Make the API call using the async client
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant providing concise advice about Kratom usage based on a user profile and a base recommendation. Respond in two distinct paragraphs as requested."},
                    {"role": "user", "content": prompt_content}
                ],
                temperature=0.7 # Adjust for creativity vs consistency
            )

            # Extract the response text
            response_text = response.choices[0].message.content.strip()

            # Split response into sections (expecting two paragraphs separated by double newline)
            sections = response_text.split("\n\n", 1)

            if len(sections) >= 2:
                additional_info = sections[0].strip()
                ai_insights = sections[1].strip()
            else:
                # Fallback if the format isn't exactly two paragraphs
                additional_info = response_text
                ai_insights = "AI insights could not be separated."
                logger.warning("OpenAI response format unexpected. Could not split into two paragraphs.")

            return {
                "additional_info": additional_info,
                "ai_insights": ai_insights
            }

        except OpenAIError as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return {
                "additional_info": "Start with a lower dose if you're new to Kratom. Stay hydrated.",
                "ai_insights": f"AI Error: {str(e)}" # Provide error context if needed
            }
        except Exception as e:
            logger.error(f"An unexpected error occurred during OpenAI call: {str(e)}")
            return {
                "additional_info": "Start with a lower dose if you're new to Kratom. Stay hydrated.",
                "ai_insights": "An unexpected error occurred."
            }

    def _create_prompt(self, base_recommendation: str, user_data: Dict[str, Any]) -> str:
        """Create a prompt for the OpenAI API"""
        # Keep the prompt structure similar, as it clearly defines the task
        return f"""
        A user with the following profile needs kratom recommendations:
        
        User Profile:
        - Age: {user_data['age']} years
        - Weight: {user_data['weight']} kg
        - Pain level: {user_data['pain_level']}/10
        - Body type: {user_data['body_type']}
        
        Base recommendation: {base_recommendation}
        
        Provide your response in two concise paragraphs, separated by a double newline:
        
        Paragraph 1: Practical usage advice (e.g., time of day, with/without food, hydration). Keep it under 3 sentences.
        
        Paragraph 2: Safety considerations and potential interactions to be aware of. Keep it under 3 sentences.
        """