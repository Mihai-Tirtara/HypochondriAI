from fastapi import APIRouter, HTTPException, Depends
from api.models import HealthQuery, HealthResponse, ErrorResponse
from services.bedrock import BedrockService
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
        service = BedrockService("anthropic.claude-3-5-sonnet-20240620-v1:0")
        prompt = generate_health_anxiety_prompt(query.symptoms, query.user_context)
        serviceResponse = service.get_response(prompt)
        return HealthResponse(response=serviceResponse)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")