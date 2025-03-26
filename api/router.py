from fastapi import APIRouter, HTTPException, Depends
from api.models import HealthQuery, HealthResponse, ErrorResponse
from services.bedrock import get_bedrock_response
from prompts.prompt_utils import generate_health_anxiety_prompt
import logging

router = APIRouter(
    prefix="/v1",
    tags=["llm"]
)

logger = logging.getLogger(__name__)

@router.post("/analyse-symptoms", response_model=HealthResponse)
async def analyze_symptoms(query: HealthQuery):
    try:
        prompt = generate_health_anxiety_prompt(query.symptoms, query.user_context)
        generated_text = get_bedrock_response(prompt)
        return HealthResponse(response=generated_text)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")