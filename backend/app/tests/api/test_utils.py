import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status
from sqlmodel import Session

from app.api.utils import (
    cleanup_conversation,
    create_title,
    get_and_save_ai_response,
    save_conversation,
    save_message,
    serialise_message_data,
)
from app.core.models import Conversation, Message, MessageRole
from app.services.llm import LangchainService


class TestUtils:
    """Test utility functions."""

    def setup_method(self):
        """Setup common test resources."""
        self.mock_db = MagicMock(spec=Session)
        self.user_id = uuid.uuid4()
        self.conversation_id = uuid.uuid4()
        self.message_content = "Test message content"

    def teardown_method(self):
        """Clean up resources after each test."""
        self.mock_db.close()
        self.mock_db = None
        print("Test resources cleaned up.")

    def test_create_title(self):
        """Test the create_title function."""
        # Test with short content
        title_length = 20
        short_content = "Short message"
        assert create_title(short_content) == short_content

        # Test with long content (more than 20 chars)
        long_content = "This is a very long message that should be truncated"
        assert create_title(long_content) == "This is a very long "
        assert len(create_title(long_content)) == title_length

    def test_save_conversation_success(self):
        """Test saveConversation with valid inputs."""
        # Arrange
        title = "Test Conversation"
        mock_conversation = MagicMock(spec=Conversation)
        mock_conversation.id = self.conversation_id
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        self.mock_db.refresh.return_value = None

        with patch(
            "app.api.utils.create_conversation", return_value=mock_conversation
        ) as mock_create:
            # Act
            result = save_conversation(
                db=self.mock_db, user_id=self.user_id, title=title
            )

            # Assert
            mock_create.assert_called_once()
            assert result.id == self.conversation_id

    def test_save_conversation_failure(self):
        """Test saveConversation when create_conversation fails."""
        # Arrange
        title = "Test Conversation"

        with patch("app.api.utils.create_conversation", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                save_conversation(db=self.mock_db, user_id=self.user_id, title=title)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to create conversation" in str(exc_info.value.detail)

    def test_save_message_success(self):
        """Test saveMessage with valid inputs."""
        # Arrange
        content = "Test message"
        role = MessageRole.user
        mock_message = MagicMock(spec=Message)
        mock_message.id = uuid.uuid4()

        with patch(
            "app.api.utils.create_message", return_value=mock_message
        ) as mock_create:
            # Act
            result = save_message(
                db=self.mock_db,
                conversation_id=self.conversation_id,
                content=content,
                role=role,
            )

            # Assert
            mock_create.assert_called_once()
            assert result == mock_message

    def test_save_message_empty_content(self):
        """Test saveMessage with empty content."""
        # Arrange
        content = ""
        role = MessageRole.user

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            save_message(
                db=self.mock_db,
                conversation_id=self.conversation_id,
                content=content,
                role=role,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Message content cannot be empty" in str(exc_info.value.detail)

    def test_save_message_creation_fails(self):
        """Test saveMessage when create_message fails."""
        # Arrange
        content = "Test message"
        role = MessageRole.user

        with patch("app.api.utils.create_message", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                save_message(
                    db=self.mock_db,
                    conversation_id=self.conversation_id,
                    content=content,
                    role=role,
                )

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to create message" in str(exc_info.value.detail)

    def test_serialise_message_data_with_model_dump(self):
        """Test serialising message data with model_dump method."""
        # Arrange
        mock_response = MagicMock()
        expected_data = {"content": "Test content", "type": "ai"}

        # Explicitly set hasattr to return True for model_dump
        with patch("app.api.utils.hasattr", lambda obj, attr: attr == "model_dump"):
            mock_response.model_dump.return_value = expected_data

        # Act
        result = serialise_message_data(mock_response)

        # Assert
        assert result == expected_data
        mock_response.model_dump.assert_called_once()

    def test_serialise_message_data_with_dict(self):
        """Test serialising message data with dict method."""
        # Arrange
        mock_response = MagicMock()
        expected_data = {"content": "Test content", "type": "ai"}

        # Explicitly set hasattr to return True only for dict, not for model_dump
        with patch("app.api.utils.hasattr", lambda obj, attr: attr == "dict"):
            mock_response.dict.return_value = expected_data

            # Act
            result = serialise_message_data(mock_response)

            # Assert
            assert result == expected_data
            mock_response.dict.assert_called_once()

    def test_serialise_message_data_fallback(self):
        """Test serialising message data fallback when no methods available."""
        # Arrange
        mock_response = MagicMock()
        mock_response.content = "Test content"

        # Explicitly set hasattr to always return False
        with patch("app.api.utils.hasattr", lambda obj, attr: False):
            # Act
            result = serialise_message_data(mock_response)

            # Assert
            assert result["error"] == "Serialization failed"
            assert result["content"] == "Test content"

    def test_cleanup_conversation_success(self):
        """Test successful conversation cleanup."""
        # Arrange
        mock_conversation = MagicMock(spec=Conversation)
        self.mock_db.get.return_value = mock_conversation

        # Act
        cleanup_conversation(db=self.mock_db, conversation_id=self.conversation_id)

        # Assert
        self.mock_db.get.assert_called_once_with(Conversation, self.conversation_id)
        self.mock_db.delete.assert_called_once_with(mock_conversation)
        self.mock_db.commit.assert_called_once()

    def test_cleanup_conversation_not_found(self):
        """Test cleanup when conversation is not found."""
        # Arrange
        self.mock_db.get.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            cleanup_conversation(db=self.mock_db, conversation_id=self.conversation_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Conversation not found" in str(exc_info.value.detail)

    def test_cleanup_conversation_exception(self):
        """Test cleanup with database exception."""
        # Arrange
        mock_conversation = MagicMock(spec=Conversation)
        self.mock_db.get.return_value = mock_conversation
        self.mock_db.delete.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            cleanup_conversation(db=self.mock_db, conversation_id=self.conversation_id)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to delete conversation" in str(exc_info.value.detail)
        self.mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_and_save_ai_response_success(self):
        """Test successful AI response generation and saving."""
        # Arrange
        mock_service = AsyncMock(spec=LangchainService)
        mock_response = MagicMock()
        mock_response.content = "AI generated response"
        mock_service.conversation.return_value = mock_response
        mock_message = MagicMock(spec=Message)

        with patch(
            "app.api.utils.serialise_message_data",
            return_value={"content": "AI generated response"},
        ) as mock_serialize:
            with patch(
                "app.api.utils.save_message", return_value=mock_message
            ) as mock_save:
                # Act
                result = await get_and_save_ai_response(
                    conversation_id=self.conversation_id,
                    user_content=self.message_content,
                    service=mock_service,
                    db=self.mock_db,
                )

                # Assert
                mock_service.conversation.assert_awaited_once_with(
                    str(self.conversation_id), self.message_content
                )
                mock_serialize.assert_called_once_with(mock_response)
                mock_save.assert_called_once()
                assert result == mock_message

    @pytest.mark.asyncio
    async def test_get_and_save_ai_response_empty_response(self):
        """Test AI response handling when empty response is returned."""
        # Arrange
        mock_service = AsyncMock(spec=LangchainService)
        mock_service.conversation.return_value = None

        # Act
        with pytest.raises(HTTPException) as exc_info:
            await get_and_save_ai_response(
                conversation_id=self.conversation_id,
                user_content=self.message_content,
                service=mock_service,
                db=self.mock_db,
            )

        # Assert
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Error getting AI response" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_and_save_ai_response_service_exception(self):
        """Test AI response handling when service raises an exception."""
        # Arrange
        mock_service = AsyncMock(spec=LangchainService)
        mock_service.conversation.side_effect = Exception("Service error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_and_save_ai_response(
                conversation_id=self.conversation_id,
                user_content=self.message_content,
                service=mock_service,
                db=self.mock_db,
            )

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Error getting AI response" in str(exc_info.value.detail)
        assert "Service error" in str(exc_info.value.detail)
