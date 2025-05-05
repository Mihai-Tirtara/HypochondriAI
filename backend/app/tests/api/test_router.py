import uuid
from unittest.mock import MagicMock

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

# Import your models and schemas
from app.core.models import Conversation, Message, MessageRole, User


def test_start_conversation(
    client: TestClient,
    session: Session,
    mock_langchain_service: MagicMock,
    test_user: User,
):
    # Arrange
    user_id = test_user.id  # Assuming you have a test user created in your fixtures
    user_content = "Hello, how are you?"
    user_role = MessageRole.user
    request_data = {"content": user_content, "role": user_role}
    expected_ai_response = {
        "content": f"AI response to:{user_content}",
        "role": "assistant",
    }
    conversation_length = 2
    message_data = {
        "id": None,
        "name": None,
        "type": "ai",
        "content": f"AI response to:{user_content}",
        "example": False,
        "tool_calls": [],
        "usage_metadata": None,
        "additional_kwargs": {},
        "response_metadata": {},
        "invalid_tool_calls": [],
    }

    # Act
    response = client.post("/v1/new", json=request_data, params={"user_id": user_id})

    # Assert
    assert (
        response.status_code == status.HTTP_200_OK
    ), f"Expected status code status.HTTP_200_OK, got {response.status_code}"
    response_data = response.json()

    # Assert the response structure
    assert "id" in response_data
    assert response_data["user_id"] == str(
        user_id
    ), f"Expected user_id {user_id}, got {response_data['user_id']}"
    assert (
        response_data["title"] == request_data["content"][:20]
    ), f"Expected title {request_data['content'][:20]}, got {response_data['title']}"
    assert "messages" in response_data, "Expected messages in response"
    assert (
        len(response_data["messages"]) == conversation_length
    ), f"Expected 2 messages, got {len(response_data['messages'])}"

    # Check user message details
    assert response_data["messages"][0]["role"] == "user", "Expected user message role"
    assert (
        response_data["messages"][0]["content"] == request_data["content"]
    ), f"Expected user message content {request_data['content']}, got {response_data['messages'][0]['content']}"

    # Check AI message details
    assert (
        response_data["messages"][1]["role"] == "assistant"
    ), "Expected assistant message role"
    assert (
        response_data["messages"][1]["content"] == expected_ai_response["content"]
    ), f"Expected assistant message content {expected_ai_response['content']}, got {response_data['messages'][1]['content']}"

    mock_langchain_service.conversation.assert_awaited_once()
    call_args = mock_langchain_service.conversation.call_args
    assert call_args[0][0] == str(
        response_data["id"]
    ), f"Expected conversation ID {response_data['id']}, got {call_args[0][0]}"
    assert (
        call_args[0][1] == request_data["content"]
    ), f"Expected user input {request_data['content']}, got {call_args[0][1]}"
    assert (
        "user_context" not in call_args.kwargs
    ), f"Expected the keyword argument 'user_context' to be not present if passed with None, got {call_args.kwargs}"
    db_conversation = session.get(Conversation, response_data["id"])
    assert (
        db_conversation is not None
    ), "Expected conversation to be saved in the database"
    assert (
        db_conversation.user_id == user_id
    ), f"Expected conversation user ID {user_id}, got {db_conversation.user_id}"
    assert (
        db_conversation.title == request_data["content"][:20]
    ), f"Expected conversation title {request_data['content'][:20]}, got {db_conversation.title}"
    assert (
        len(db_conversation.messages) == conversation_length
    ), f"Expected 2 messages in conversation, got {len(db_conversation.messages)}"
    assert (
        db_conversation.messages[0].role == "user"
    ), "Expected user message role in conversation"
    assert (
        db_conversation.messages[0].content == request_data["content"]
    ), f"Expected user message content {request_data['content']}, got {db_conversation.messages[0].content}"
    assert (
        db_conversation.messages[1].role == "assistant"
    ), "Expected assistant message role in conversation"
    assert (
        db_conversation.messages[1].content == expected_ai_response["content"]
    ), f"Expected assistant message content {expected_ai_response['content']}, got {db_conversation.messages[1].content}"
    assert (
        db_conversation.messages[1].message_data == message_data
    ), f"Expected assistant message data {message_data}, got {db_conversation.messages[1].message_data}"
    print("Test passed: Response contains the expected conversation")


def test_start_conversation_missing_user_id(
    client: TestClient, session: Session, mock_langchain_service: MagicMock
):
    """
    Test the /v1/new endpoint with a missing user_id parameter.
    """
    # Arrange
    user_content = "Hello, I have no user_ID"
    user_role = MessageRole.user
    request_data = {"content": user_content, "role": user_role}

    # Act
    response = client.post("/v1/new", json=request_data)

    # Assert
    assert (
        response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    ), f"Expected status code status.HTTP_422_UNPROCESSABLE_ENTITY, got {response.status_code}"
    # Get the JSON response
    response_data = response.json()

    # Assert the error structure
    assert "detail" in response_data, "Response missing 'detail' field"
    assert isinstance(response_data["detail"], list), "'detail' is not a list"
    assert len(response_data["detail"]) > 0, "'detail' list is empty"

    # Find the specific user_id error
    user_id_error = None
    for error in response_data["detail"]:
        if error.get("loc") == ["query", "user_id"]:
            user_id_error = error
            break

    # Assert that we found the user_id error
    assert user_id_error is not None, "user_id error not found in response"

    # Verify each component of the error
    assert (
        user_id_error["type"] == "missing"
    ), f"Expected 'missing', got '{user_id_error['type']}'"
    assert (
        user_id_error["msg"] == "Field required"
    ), f"Expected 'Field required', got '{user_id_error['msg']}'"
    assert (
        user_id_error["input"] is None
    ), f"Expected None, got {user_id_error['input']}"

    print("Test passed: Response contains the expected 'missing user_id' error")


def test_start_conversation_invalid_user_id(
    client: TestClient, session: Session, mock_langchain_service: MagicMock
):
    """
    Test the /v1/new endpoint with an invalid user_id parameter.
    """
    # Arrange
    invalid_user_id = str(
        uuid.uuid4()
    )  # Generate a random UUID that doesn't exist in the database
    user_content = "Hello, I have an invalid user_ID"
    user_role = "user"
    request_data = {"content": user_content, "role": user_role}
    # Act
    response = client.post(
        "/v1/new", json=request_data, params={"user_id": invalid_user_id}
    )

    # Assert
    assert (
        response.status_code == status.HTTP_404_NOT_FOUND
    ), f"Expected status code status.HTTP_404_NOT_FOUND, got {response.status_code}"

    # Get the JSON response
    response_data = response.json()

    # Assert the error structure
    assert "detail" in response_data, "Response missing 'detail' field"

    # Assert the error message
    assert (
        response_data["detail"] == "User not found"
    ), f"Expected 'User not found', got '{response_data['detail']}'"

    print("Test passed: Response contains the expected 'user not found' error")


def test_continue_conversation(
    client: TestClient,
    session: Session,
    mock_langchain_service: MagicMock,
    test_user: User,
):
    """
    Test the /v1/conversations endpoint to continue an existing conversation.
    """
    # Arrange
    user_id = test_user.id  # Assuming you have a test user created in your fixtures
    # Create a conversation and a message in the database for the test
    conversation = Conversation(user_id=user_id, title="Test Conversation")
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    first_message = Message(
        conversation_id=conversation.id, content="Hello, how are you?", role="user"
    )
    session.add(first_message)
    session.commit()
    session.refresh(first_message)

    conversation_id = conversation.id
    user_content = "Hello, I want to continue the conversation."
    user_role = "user"
    request_data = {"content": user_content, "role": user_role}

    expected_ai_response = {
        "content": f"AI response to:{user_content}",
        "role": "assistant",
    }
    expected_ai_response_metadata = {
        "id": None,
        "name": None,
        "type": "ai",
        "content": f"AI response to:{user_content}",
        "example": False,
        "tool_calls": [],
        "usage_metadata": None,
        "additional_kwargs": {},
        "response_metadata": {},
        "invalid_tool_calls": [],
    }

    # Act
    response = client.post(
        "/v1/conversations",
        json=request_data,
        params={"conversation_id": conversation_id},
    )

    # Assert
    assert (
        response.status_code == status.HTTP_200_OK
    ), f"Expected status code status.HTTP_200_OK, got {response.status_code}"
    response_data = response.json()

    # Assert the response structure
    assert "id" in response_data
    assert response_data["user_id"] == str(
        user_id
    ), f"Expected user_id {user_id}, got {response_data['user_id']}"
    assert (
        response_data["title"] == conversation.title
    ), f"Expected title {conversation.title}, got {response_data['title']}"
    assert "messages" in response_data, "Expected messages in response"
    assert (
        len(response_data["messages"]) == 3  # noqa: PLR2004
    ), f"Expected 3 messages, got {len(response_data['messages'])}"

    # Check user message details
    assert response_data["messages"][1]["role"] == "user", "Expected user message role"
    assert (
        response_data["messages"][1]["content"] == request_data["content"]
    ), f"Expected user message content {request_data['content']}, got {response_data['messages'][2]['content']}"

    # Check AI message details
    assert (
        response_data["messages"][2]["role"] == "assistant"
    ), "Expected assistant message role"
    assert (
        response_data["messages"][2]["content"] == expected_ai_response["content"]
    ), f"Expected assistant message content {expected_ai_response['content']}, got {response_data['messages'][1]['content']}"

    mock_langchain_service.conversation.assert_awaited_once()
    call_args = mock_langchain_service.conversation.call_args
    assert call_args[0][0] == str(
        response_data["id"]
    ), f"Expected conversation ID {response_data['id']}, got {call_args[0][0]}"
    assert (
        call_args[0][1] == request_data["content"]
    ), f"Expected user input {request_data['content']}, got {call_args[0][1]}"
    assert (
        "user_context" not in call_args.kwargs
    ), f"Expected the keyword argument 'user_context' to be not present if passed with None, got {call_args.kwargs}"

    db_conversation = session.get(Conversation, response_data["id"])
    assert (
        db_conversation is not None
    ), "Expected conversation to be saved in the database"
    assert (
        db_conversation.user_id == user_id
    ), f"Expected conversation user ID {user_id}, got {db_conversation.user_id}"
    assert (
        db_conversation.title == conversation.title
    ), f"Expected conversation title {conversation.title}, got {db_conversation.title}"
    assert (
        len(db_conversation.messages) == 3  # noqa: PLR2004
    ), f"Expected 3 messages in conversation, got {len(db_conversation.messages)}"
    assert (
        db_conversation.messages[1].role == "user"
    ), "Expected user message role in conversation"
    assert (
        db_conversation.messages[1].content == request_data["content"]
    ), f"Expected user message content {request_data['content']}, got {db_conversation.messages[0].content}"
    assert (
        db_conversation.messages[1].message_data is None
    ), "Expected user message data to be None"
    assert (
        db_conversation.messages[2].role == "assistant"
    ), "Expected assistant message role in conversation"
    assert (
        db_conversation.messages[2].content == expected_ai_response["content"]
    ), f"Expected assistant message content {expected_ai_response['content']}, got {db_conversation.messages[1].content}"
    assert (
        db_conversation.messages[2].message_data == expected_ai_response_metadata
    ), f"Expected assistant message data {expected_ai_response_metadata}, got {db_conversation.messages[2].message_data}"
    print("Test passed: Response contains the expected conversation")


def test_continue_conversation_missing_conversation_id(
    client: TestClient,
    session: Session,
    mock_langchain_service: MagicMock,
    test_user: User,
):
    """
    Test the /v1/conversations endpoint with a missing conversation_id parameter.
    """
    # Arrange
    user_content = "Hello, I have no conversation_ID"
    user_role = "user"
    request_data = {"content": user_content, "role": user_role}

    # Act
    response = client.post("/v1/conversations", json=request_data)

    # Assert
    assert (
        response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    ), f"Expected status code status.HTTP_422_UNPROCESSABLE_ENTITY, got {response.status_code}"

    # Get the JSON response
    response_data = response.json()

    # Assert the error structure
    assert "detail" in response_data, "Response missing 'detail' field"
    assert isinstance(response_data["detail"], list), "'detail' is not a list"
    assert len(response_data["detail"]) > 0, "'detail' list is empty"

    # Find the specific conversation_id error
    conversation_id_error = None
    for error in response_data["detail"]:
        if error.get("loc") == ["query", "conversation_id"]:
            conversation_id_error = error
            break

    # Assert that we found the conversation_id error
    assert (
        conversation_id_error is not None
    ), "conversation_id error not found in response"
    assert (
        conversation_id_error["type"] == "missing"
    ), f"Expected 'missing', got '{conversation_id_error['type']}'"
    assert (
        conversation_id_error["msg"] == "Field required"
    ), f"Expected 'Field required', got '{conversation_id_error['msg']}'"
    assert (
        conversation_id_error["input"] is None
    ), f"Expected None, got {conversation_id_error['input']}"
    print("Test passed: Response contains the expected 'missing conversation_id' error")


def test_continue_conversation_invalid_conversation_id(
    client: TestClient,
    session: Session,
    mock_langchain_service: MagicMock,
    test_user: User,
):
    """
    Test the /v1/conversations endpoint with an invalid conversation_id parameter.
    """
    # Arrange
    invalid_conversation_id = str(
        uuid.uuid4()
    )  # Generate a random UUID that doesn't exist in the database
    user_content = "Hello, I have an invalid conversation_ID"
    user_role = "user"
    request_data = {"content": user_content, "role": user_role}

    # Act
    response = client.post(
        "/v1/conversations",
        json=request_data,
        params={"conversation_id": invalid_conversation_id},
    )

    # Assert
    assert (
        response.status_code == status.HTTP_404_NOT_FOUND
    ), f"Expected status code status.HTTP_404_NOT_FOUND, got {response.status_code}"

    # Get the JSON response
    response_data = response.json()

    # Assert the error structure
    assert "detail" in response_data, "Response missing 'detail' field"

    # Assert the error message
    assert (
        response_data["detail"] == "Conversation not found"
    ), f"Expected 'Conversation not found', got '{response_data['detail']}'"

    print("Test passed: Response contains the expected 'conversation not found' error")


def test_get_conversations(client: TestClient, session: Session, test_user: User):
    """
    Test the /v1/conversations endpoint to get all conversations for a user.
    """
    # Arrange
    user_id = test_user.id  # Assuming you have a test user created in your fixtures
    # Create a conversation and a message in the database for the test
    conversation = Conversation(user_id=user_id, title="Test Conversation")
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Act
    response = client.get("/v1/conversations", params={"user_id": user_id})

    # Assert
    assert (
        response.status_code == status.HTTP_200_OK
    ), f"Expected status code status.HTTP_200_OK, got {response.status_code}"

    # Get the JSON response
    response_data = response.json()

    # Assert the response structure
    assert isinstance(response_data, list), "Expected a list of conversations"

    # Check if the conversation is in the response
    assert len(response_data) == 1, f"Expected 1 conversation, got {len(response_data)}"

    # Check conversation details
    assert response_data[0]["id"] == str(
        conversation.id
    ), f"Expected conversation ID {conversation.id}, got {response_data[0]['id']}"
    assert response_data[0]["user_id"] == str(
        user_id
    ), f"Expected user ID {user_id}, got {response_data[0]['user_id']}"
    print("Test passed: Response contains the expected conversations")


def test_get_conversations_no_conversations(
    client: TestClient, session: Session, test_user: User
):
    """
    Test the /v1/conversations endpoint when there are no conversations for a user.
    """
    # Arrange
    user_id = test_user.id  # Assuming you have a test user created in your fixtures

    # Act
    response = client.get("/v1/conversations", params={"user_id": user_id})

    # Assert
    assert (
        response.status_code == status.HTTP_404_NOT_FOUND
    ), f"Expected status code status.HTTP_404_NOT_FOUND, got {response.status_code}"

    # Get the JSON response
    response_data = response.json()

    # Assert the error structure
    assert "detail" in response_data, "Response missing 'detail' field"

    # Assert the error message
    assert (
        response_data["detail"] == "No conversations found"
    ), f"Expected 'No conversations found', got '{response_data['detail']}'"

    print("Test passed: Response contains the expected 'no conversations found' error")


def test_get_conversations_missing_user_id(client: TestClient, session: Session):
    """
    Test the /v1/conversations endpoint with a missing user_id parameter.
    """
    # Arrange
    # Act
    response = client.get("/v1/conversations")

    # Assert
    assert (
        response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    ), f"Expected status code status.HTTP_422_UNPROCESSABLE_ENTITY, got {response.status_code}"

    # Get the JSON response
    response_data = response.json()

    # Assert the error structure
    assert "detail" in response_data, "Response missing 'detail' field"
    assert isinstance(response_data["detail"], list), "'detail' is not a list"
    assert len(response_data["detail"]) > 0, "'detail' list is empty"

    # Find the specific user_id error
    user_id_error = None
    for error in response_data["detail"]:
        if error.get("loc") == ["query", "user_id"]:
            user_id_error = error
            break

    # Assert that we found the user_id error
    assert user_id_error is not None, "user_id error not found in response"

    # Verify each component of the error
    assert (
        user_id_error["type"] == "missing"
    ), f"Expected 'missing', got '{user_id_error['type']}'"
    assert (
        user_id_error["msg"] == "Field required"
    ), f"Expected 'Field required', got '{user_id_error['msg']}'"
    assert (
        user_id_error["input"] is None
    ), f"Expected None, got {user_id_error['input']}"

    print("Test passed: Response contains the expected 'missing user_id' error")


def test_get_conversations_invalid_user_id(client: TestClient, session: Session):
    """
    Test the /v1/conversations endpoint with an invalid user_id parameter.
    """
    # Arrange
    invalid_user_id = str(
        uuid.uuid4()
    )  # Generate a random UUID that doesn't exist in the database

    # Act
    response = client.get("/v1/conversations", params={"user_id": invalid_user_id})

    # Assert
    assert (
        response.status_code == status.HTTP_404_NOT_FOUND
    ), f"Expected status code status.HTTP_404_NOT_FOUND, got {response.status_code}"

    # Get the JSON response
    response_data = response.json()
    # Assert the error structure
    assert "detail" in response_data, "Response missing 'detail' field"

    # Assert the error message
    assert (
        response_data["detail"] == "User not found"
    ), f"Expected 'User not found', got '{response_data['detail']}'"

    print("Test passed: Response contains the expected 'user not found' error")


def test_start_conversation_invalid_uuid(
    client: TestClient,
    session: Session,
    mock_langchain_service: MagicMock,
    test_user: User,
):
    """
    Test the /v1/new endpoint with a user_id in invalid format.
    """
    # Arrange
    invalid_user_id = "invalid-uuid"  # Invalid UUID format
    user_content = "Hello, I have an invalid user_ID"
    user_role = "user"
    request_data = {"content": user_content, "role": user_role}

    # Act
    response = client.post(
        "/v1/new", json=request_data, params={"user_id": invalid_user_id}
    )

    # Assert
    assert (
        response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    ), f"Expected status code status.HTTP_422_UNPROCESSABLE_ENTITY, got {response.status_code}"

    # Get the JSON response
    response_data = response.json()
    print(response_data)

    assert "detail" in response_data, "Response missing 'detail' field"
    assert isinstance(response_data["detail"], list), "'detail' is not a list"
    assert len(response_data["detail"]) > 0, "'detail' list is empty"

    # Find the specific user_id error
    user_id_error = None
    for error in response_data["detail"]:
        if error.get("loc") == ["query", "user_id"]:
            user_id_error = error
            break

    # Assert that we found the user_id error
    assert user_id_error is not None, "user_id error not found in response"

    # Verify each component of the error
    assert (
        user_id_error["type"] == "uuid_parsing"
    ), f"Expected 'uuid_parsing', got '{user_id_error['type']}'"
    assert (
        "Input should be a valid UUID, invalid character" in user_id_error["msg"]
    ), f"Expected 'Input should be a valid UUID, invalid character', got '{user_id_error['msg']}'"

    print("Test passed: Response contains the expected 'invalid UUID format' error")


def test_start_conversation_invalid_json_payload(
    client: TestClient,
    session: Session,
    mock_langchain_service: MagicMock,
    test_user: User,
):
    """
    Test the /v1/new endpoint with an invalid JSON payload.
    """
    # Arrange
    user_id = test_user.id  # Assuming you have a test user created in your fixtures
    invalid_payload = (
        "{ 'content': 'Hello, I have an invalid payload' }"  # Invalid JSON format
    )

    # Act
    response = client.post("/v1/new", json=invalid_payload, params={"user_id": user_id})

    # Assert
    assert (
        response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    ), f"Expected status code status.HTTP_422_UNPROCESSABLE_ENTITY, got {response.status_code}"

    # Get the JSON response
    response_data = response.json()

    # Find the specific json validation error
    json_error = None
    for error in response_data["detail"]:
        if error.get("loc") == ["body"]:
            json_error = error
            break

    # Assert that we found the json_error
    assert json_error is not None, "json_error not found in response"

    # Verify each component of the error
    assert (
        json_error["type"] == "model_attributes_type"
    ), f"Expected 'model_attributes_type', got '{json_error['type']}'"
    assert (
        "Input should be a valid dictionary" in json_error["msg"]
    ), f"Expected 'Input should be a valid dictionary', got '{json_error['msg']}'"

    print("Test passed: Response contains the expected 'invalid JSON format' error")


def test_continue_conversation_invalid_json_payload(
    client: TestClient,
    session: Session,
    mock_langchain_service: MagicMock,
    test_user: User,
):
    """
    Test the /v1/conversations endpoint with an invalid JSON payload.
    """
    # Arrange
    user_id = test_user.id  # Assuming you have a test user created in your fixtures
    conversation = Conversation(user_id=user_id, title="Test Conversation")
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    conversation_id = conversation.id
    invalid_payload = (
        "{ 'content': 'Hello, I have an invalid payload' }"  # Invalid JSON format
    )

    # Act
    response = client.post(
        "/v1/conversations",
        json=invalid_payload,
        params={"conversation_id": conversation_id},
    )

    # Assert
    assert (
        response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    ), f"Expected status code status.HTTP_422_UNPROCESSABLE_ENTITY, got {response.status_code}"

    # Get the JSON response
    response_data = response.json()

    # Find the specific json validation error
    json_error = None
    for error in response_data["detail"]:
        if error.get("loc") == ["body"]:
            json_error = error
            break

    # Assert that we found the json_error
    assert json_error is not None, "json_error not found in response"

    # Verify each component of the error
    assert (
        json_error["type"] == "model_attributes_type"
    ), f"Expected 'model_attributes_type', got '{json_error['type']}'"
    assert (
        "Input should be a valid dictionary" in json_error["msg"]
    ), f"Expected 'Input should be a valid dictionary', got '{json_error['msg']}'"

    print("Test passed: Response contains the expected 'invalid JSON format' error")


def test_start_conversation_empty_payload(
    client: TestClient,
    session: Session,
    mock_langchain_service: MagicMock,
    test_user: User,
):
    """
    Test the /v1/new endpoint with an empty payload.
    """
    # Arrange
    user_id = test_user.id  # Assuming you have a test user created in your fixtures
    empty_payload = {}  # Empty JSON payload

    # Act
    response = client.post("/v1/new", json=empty_payload, params={"user_id": user_id})

    # Assert
    assert (
        response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    ), f"Expected status code status.HTTP_422_UNPROCESSABLE_ENTITY, got {response.status_code}"

    # Get the JSON response
    response_data = response.json()
    # Find the specific json validation error
    json_error = None
    for error in response_data["detail"]:
        if error.get("loc") == ["body", "content"]:
            json_error = error
            break

    # Assert that we found the json_error
    assert json_error is not None, "json_error not found in response"

    # Verify each component of the error
    assert (
        json_error["type"] == "missing"
    ), f"Expected 'missing', got '{json_error['type']}'"
    assert (
        json_error["msg"] == "Field required"
    ), f"Expected 'Field required', got '{json_error['msg']}'"
    assert json_error["input"] == {}, f"Expected {{}}, got {json_error['input']}"

    print("Test passed: Response contains the expected 'empty payload' error")


def test_start_conversation_empty_content(
    client: TestClient,
    session: Session,
    mock_langchain_service: MagicMock,
    test_user: User,
):
    """
    Test the /v1/new endpoint with an empty content field.
    """
    # Arrange
    user_id = test_user.id  # Assuming you have a test user created in your fixtures
    empty_content_payload = {"content": "", "role": "user"}  # Empty content field

    # Act
    response = client.post(
        "/v1/new", json=empty_content_payload, params={"user_id": user_id}
    )

    # Assert
    assert (
        response.status_code == status.HTTP_400_BAD_REQUEST
    ), f"Expected status code status.HTTP_400_BAD_REQUEST, got {response.status_code}"
    # Get the JSON response
    response_data = response.json()
    # Assert the error structure
    assert "detail" in response_data, "Response missing 'detail' field"

    # Assert the error message
    assert (
        response_data["detail"] == "Message content cannot be empty"
    ), f"Expected 'Message content cannot be empty', got '{response_data['detail']}'"

    print("Test passed: Response contains the expected 'user not found' error")


def test_start_conversation_langchain_error(
    client: TestClient,
    session: Session,
    mock_langchain_service: MagicMock,
    test_user: User,
):
    """
    Test the /v1/new endpoint when the Langchain service raises an exception.
    """
    # Arrange
    user_id = test_user.id
    user_content = "Hello, how are you?"
    user_role = MessageRole.user
    request_data = {"content": user_content, "role": user_role}

    # For async methods, we need to make the side_effect an async function that raises an exception
    async def mock_async_error(*args, **kwargs):
        raise Exception("Langchain service error")

    # Configure mock to raise an exception
    mock_langchain_service.conversation.side_effect = mock_async_error

    # Act
    response = client.post("/v1/new", json=request_data, params={"user_id": user_id})

    # Assert
    assert (
        response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    ), f"Expected status code status.HTTP_500_INTERNAL_SERVER_ERROR, got {response.status_code}"
    response_data = response.json()

    # Assert the error structure
    assert "detail" in response_data, "Response missing 'detail' field"
    assert (
        "error" in response_data["detail"].lower()
    ), f"Expected error message, got '{response_data['detail']}'"

    # Verify the mock was called
    mock_langchain_service.conversation.assert_awaited_once()

    print("Test passed: Response contains the expected Langchain service error")


def test_start_conversation_langchain_not_initialized(
    client: TestClient,
    session: Session,
    mock_langchain_service: MagicMock,
    test_user: User,
):
    """
    Test the /v1/new endpoint when the Langchain service raises an exception.
    """
    # Arrange
    user_id = test_user.id
    user_content = "Hello, how are you?"
    user_role = MessageRole.user
    request_data = {"content": user_content, "role": user_role}

    # Configure mock to raise an exception
    mock_langchain_service.initialized = False
    mock_langchain_service.conversation.side_effect = Exception(
        "Langchain service not initialized"
    )

    # Act
    response = client.post("/v1/new", json=request_data, params={"user_id": user_id})

    # Assert
    assert (
        response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    ), f"Expected status code status.HTTP_500_INTERNAL_SERVER_ERROR, got {response.status_code}"
    response_data = response.json()

    # Assert the error structure
    assert "detail" in response_data, "Response missing 'detail' field"
    assert (
        "error" in response_data["detail"].lower()
    ), f"Expected error message, got '{response_data['detail']}'"

    print(
        "Test passed: Response contains the expected Langchain service error when not initialized"
    )
