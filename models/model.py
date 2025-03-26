from pydantic import BaseModel, Field
from typing import Optional

class HealthQuery(BaseModel):
    symptoms: str = Field(..., description="Description of symptoms")
    user_context: Optional[str] = Field(None, description="Additional context about health situation")
    
    class Config:
        schema_extra = {
            "example": {
                "symptoms": "I've been experiencing headaches and dizziness",
                "user_context": "I have a history of migraines"
            }
        }

class HealthResponse(BaseModel):
    response: str = Field(..., description="LLM-generated response")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error description")