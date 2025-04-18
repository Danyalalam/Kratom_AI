from pydantic import BaseModel, Field, field_validator
from typing import Optional

class RecommendationRequest(BaseModel):
    age: int = Field(..., ge=18, description="User age (must be 18+)")
    weight: float = Field(..., gt=0, description="User weight in kg")
    pain_level: int = Field(..., ge=1, le=10, description="Pain level from 1-10")
    body_type: str = Field(..., description="User's body type")
    
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