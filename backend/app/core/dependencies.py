import logging
from collections.abc import Generator

from fastapi import HTTPException
from sqlmodel import Session, create_engine

from app.config.config import settings
from app.services.llm import LangchainService  # Import the service class

logger = logging.getLogger(__name__)


async def get_langchain_service() -> LangchainService:
    """
    Dependency function that provides the singleton LangchainService instance.
    Ensures the service is properly initialized before returning.
    """
    try:
        return await LangchainService.get_instance()
    except Exception as e:
        logger.error(f"Failed to get LangchainService instance: {e}")
        raise HTTPException(
            status_code=503,  # Service Unavailable
            detail="Chat service is currently unavailable due to an initialization error.",
        ) from e


# Use the database URL from your settings
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), pool_pre_ping=True)


# Create a configured "Session" class
# Dependency function to get a DB session
def get_session() -> Generator[Session, None, None]:
    """
    Dependency function that yields a SQLModel session.
    Ensures the session is closed afterwards.
    """
    with Session(engine) as session:
        try:
            yield session
        finally:
            pass
