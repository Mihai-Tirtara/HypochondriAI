import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from unittest.mock import MagicMock, AsyncMock # Use AsyncMock for async methods
import os
import uuid
from typing import Optional

from app.main import app
from app.core.dependencies import get_session, get_langchain_service
from app.services.llm import LangchainService
from app.config.config import settings
from app.core.models import User, Conversation, Message,UserCreate
from app.db.crud import create_user
import logging

logger = logging.getLogger(__name__)

@pytest.fixture(name="session", scope="function")
def session_fixture():
    """Create a new database session for each test."""
    print("Datebase uri = " + str(settings.SQLALCHEMY_DATABASE_URI))
    engine = create_engine(
        str(settings.SQLALCHEMY_DATABASE_URI))
    SQLModel.metadata.create_all(engine)

    # Create a new session for each test
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)  # Clean up the database after tests 
    
@pytest.fixture(name="mock_langchain_service", scope="function")
def mock_langchain_service_fixture():
    """Mock the LangchainService for testing."""
    mock_service = MagicMock(spec=LangchainService)
    
    async def mock_conversation(conversation_id: str, user_input: str, user_context: Optional[str] = None):
        # Mock the conversation method to return a fixed response
        mock_response = MagicMock()
        mock_response.content = f"AI response to:{user_input}"
        mock_response.model_dump = MagicMock(return_value={"content": mock_response.content, "role": "assistant", "message_data": "mock_data"})
        return mock_response
    
    mock_service.conversation = AsyncMock(side_effect=mock_conversation)
    
    LangchainService._initialized = True  # Set the initialized flag to True
    
    yield mock_service
    
    LangchainService._initialized = False  # Reset the initialized flag after tests
    
@pytest.fixture(name="client", scope="function")
def client_fixture(session: Session, mock_langchain_service: LangchainService):
    """Create a TestClient for testing the FastAPI app."""
    # Override the dependencies for the test client
    # Dependency override for the database session
    def get_session_override():
        yield session

    # Dependency override for the langchain service
    def get_langchain_override():
        return mock_langchain_service
    
    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_langchain_service] = get_langchain_override
    
    with TestClient(app) as client:
        yield client
    
    # Clean up the overrides after tests
    app.dependency_overrides.clear()
    
@pytest.fixture(name="test_user", scope="function")
def test_user_fixture(session: Session):
    """Create a test user in the database."""
    test_user = UserCreate(
        username="testuser",
        email="test-email",
        password="hashedpassword",
    )
    print("We are in the fixture " + str(test_user))
    user = create_user(session=session, user_create=test_user)
    # Create a new user in the database
    return user   