from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class LocationData(BaseModel):
    ip: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None

class RecommendationRequest(BaseModel):
    age: int = Field(..., ge=18, description="User age (must be 18+)")
    weight: float = Field(..., gt=0, description="User weight in kg")
    pain_level: int = Field(..., ge=1, le=10, description="Pain level from 1-10")
    body_type: str = Field(..., description="User's body type")
    email: str = Field(..., description="User's email address")  # New field
    sex: str = Field(..., description="User's sex type")  
    height: dict = Field(..., description="User's height in feet and inches")  # New field
    blood_type: str = Field(..., description="User's blood type")  # New field
    newsletter: bool = Field(False, description="Newsletter subscription status")  # New field
    location_data: Optional[LocationData] = None  # New field
    
    @field_validator('body_type')
    @classmethod
    def validate_body_type(cls, v):
        valid_types = ["ectomorph", "mesomorph", "endomorph", "average"]
        if v.lower() not in valid_types:
            raise ValueError(f"Body type must be one of {valid_types}")
        return v.lower()

class RecommendationResponse(BaseModel):
    dosage: str
    additional_info: Optional[str] = None
    ai_insights: Optional[str] = None
    sponsored_info: Optional[dict] = Field(
        None,
        description="Information about sponsored strain vendors",
        example={"vendor": "Vendor X", "url": "https://example.com", "description": "Premium Red Bali"}
    )