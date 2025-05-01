import uuid
from unittest.mock import MagicMock, patch

from sqlmodel import Session

from app.core.models import (
    Conversation,
    ConversationCreate,
    Message,
    MessageCreate,
    User,
    UserCreate,
)
from app.db.crud import (
    check_conversation_exists,
    check_user_exists,
    create_conversation,
    create_message,
    create_user,
    get_conversation_by_id,
    get_conversations_by_user_id,
)


class TestCRUD:
    """
    Test CRUD operations for User, Conversation, and Message models.
    """

    def setup_method(self):
        """Setup common test resources."""
        self.mock_session = MagicMock(spec=Session)
        self.user_id = uuid.uuid4()
        self.conversation_id = uuid.uuid4()

    def teardown_method(self):
        """Clean up resources after each test."""
        self.mock_session.close()
        self.mock_session = None
        print("Test resources cleaned up.")

    def test_create_user(self):
        """Test creating a user."""
        # Arrange
        mock_user = MagicMock(spec=User)
        self.mock_session.add.return_value = None
        self.mock_session.commit.return_value = None
        self.mock_session.refresh.return_value = None

        with patch("app.core.models.User.model_validate", return_value=mock_user):
            with patch(
                "app.core.security.get_password_hash", return_value="hashed_password"
            ):
                # Act
                user_create = UserCreate(
                    username="testuser", email="test@example.com", password="password"
                )
                result = create_user(session=self.mock_session, user_create=user_create)

                # Assert
                self.mock_session.add.assert_called_once()
                self.mock_session.commit.assert_called_once()
                self.mock_session.refresh.assert_called_once()
                assert result == mock_user
        print("Test passed: User created successfully.")

    def test_create_message(self):
        """Test creating a message."""
        # Arrange
        mock_message = MagicMock(spec=Message)
        self.mock_session.add.return_value = None
        self.mock_session.commit.return_value = None
        self.mock_session.refresh.return_value = None

        with patch("app.core.models.Message.model_validate", return_value=mock_message):
            # Act
            message_create = MessageCreate(content="Hello", role="user")
            result = create_message(
                session=self.mock_session,
                message_create=message_create,
                conversation_id=self.conversation_id,
            )

            # Assert
            self.mock_session.add.assert_called_once()
            self.mock_session.commit.assert_called_once()
            self.mock_session.refresh.assert_called_once()
            assert result == mock_message
            print("Test passed: Message created successfully.")

    def test_create_conversation(self):
        """Test creating a conversation."""
        # Arrange
        mock_conversation = MagicMock(spec=Conversation)
        self.mock_session.add.return_value = None
        self.mock_session.commit.return_value = None
        self.mock_session.refresh.return_value = None

        with patch(
            "app.core.models.Conversation.model_validate",
            return_value=mock_conversation,
        ):
            # Act
            conversation_create = ConversationCreate(title="Test Conversation")
            result = create_conversation(
                session=self.mock_session,
                conversation_create=conversation_create,
                user_id=self.user_id,
            )

            # Assert
            self.mock_session.add.assert_called_once()
            self.mock_session.commit.assert_called_once()
            self.mock_session.refresh.assert_called_once()
            assert result == mock_conversation
            print("Test passed: User created successfully.")

    def test_get_conversation_by_id(self):
        """Test getting a conversation by ID."""
        # Arrange
        mock_conversation = MagicMock(spec=Conversation)
        self.mock_session.exec.return_value.first.return_value = mock_conversation

        # Act
        result = get_conversation_by_id(
            session=self.mock_session, conversation_id=self.conversation_id
        )

        # Assert
        self.mock_session.exec.assert_called_once()
        assert result == mock_conversation
        print("Test passed: Conversation retrieved successfully.")

    def test_get_conversation_by_id_none(self):
        """Test getting a conversation by ID when it doesn't exist."""
        # Arrange
        mock_result = MagicMock()
        mock_result.first.return_value = None
        self.mock_session.exec.return_value = mock_result

        # Act
        result = get_conversation_by_id(
            session=self.mock_session, conversation_id=self.conversation_id
        )

        # Assert
        self.mock_session.exec.assert_called_once()
        assert result is None
        print("Test passed: No conversation found with the given ID.")

    def test_get_conversations_by_user_id(self):
        """Test getting conversations by user ID."""
        # Arrange
        mock_conversation = MagicMock(spec=Conversation)
        self.mock_session.exec.return_value.all.return_value = [mock_conversation]

        # Act
        result = get_conversations_by_user_id(
            session=self.mock_session, user_id=self.user_id
        )

        # Assert
        self.mock_session.exec.assert_called_once()
        assert result == [mock_conversation]
        print("Test passed: Conversations retrieved successfully.")

    def test_get_conversations_by_user_id_none(self):
        """Test getting conversations for a user with no conversations."""
        # Arrange
        mock_result = MagicMock()
        mock_result.all.return_value = []
        self.mock_session.exec.return_value = mock_result

        # Act
        result = get_conversations_by_user_id(
            session=self.mock_session, user_id=self.user_id
        )

        # Assert
        self.mock_session.exec.assert_called_once()
        assert result == []
        print("Test passed: No conversations found for user.")

    def test_check_conversation_exists(self):
        """Test checking if a conversation exists."""
        # Arrange
        self.mock_session.exec.return_value.first.return_value = True

        # Act
        result = check_conversation_exists(
            session=self.mock_session, conversation_id=self.conversation_id
        )

        # Assert
        self.mock_session.exec.assert_called_once()
        assert result is True
        print("Test passed: Conversation existence checked successfully.")

    def test_check_conversation_exists_false(self):
        """Test checking if a conversation exists when it doesn't."""
        # Arrange
        mock_result = MagicMock()
        mock_result.first.return_value = None
        self.mock_session.exec.return_value = mock_result

        # Act
        result = check_conversation_exists(
            session=self.mock_session, conversation_id=self.conversation_id
        )

        # Assert
        self.mock_session.exec.assert_called_once()
        assert result is False
        print("Test passed: Conversation existence checked successfully.")

    def test_check_user_exists(self):
        """Test checking if a user exists."""
        # Arrange
        self.mock_session.exec.return_value.first.return_value = True

        # Act
        result = check_user_exists(session=self.mock_session, user_id=self.user_id)

        # Assert
        self.mock_session.exec.assert_called_once()
        assert result is True
        print("Test passed: User existence checked successfully.")

    def test_check_user_exists_false(self):
        """Test checking if a user exists when they don't."""
        # Arrange
        mock_result = MagicMock()
        mock_result.first.return_value = None
        self.mock_session.exec.return_value = mock_result

        # Act
        result = check_user_exists(session=self.mock_session, user_id=self.user_id)

        # Assert
        self.mock_session.exec.assert_called_once()
        assert result is False
        print("Test passed: User existence checked successfully.")
