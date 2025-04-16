import logging
from fastapi import Depends, HTTPException
from services.llm import LangchainService # Import the service class

logger = logging.getLogger(__name__)

def get_langchain_service() -> LangchainService:
    """
    Dependency function that provides an instance of LangchainService.
    Checks if the service was successfully initialized during startup.
    """
    # Crucial check: Ensure the class-level initialization succeeded
    if not LangchainService._initialized:
        logger.error("Attempted to use LangchainService, but it failed to initialize.")
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail="Chat service is currently unavailable due to an initialization error."
        )
    # Return a new, lightweight instance. It uses the shared class resources.
    return LangchainService()