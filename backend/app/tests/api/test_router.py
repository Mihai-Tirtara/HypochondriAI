import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from unittest.mock import AsyncMock, MagicMock

# Import your models and schemas
from app.core.models import User, Conversation, Message, MessageCreate
from app.services.llm import LangchainService

def test_start_conversation(client: TestClient, session: Session, mock_langchain_service: MagicMock, test_user: User):
    
    #Arrange
    
    user_id = test_user.id  # Assuming you have a test user created in your fixtures
    user_content = "Hello, how are you?"
    user_role = "user"
    request_data = { "content": user_content, "role": user_role}
    expected_AI_response = { "content": f"AI response to:{user_content}", "role": "assistant", "message_data": "mock_data"}
    
    #Act 
    response = client.post("/v1/new", json=request_data, params={"user_id": user_id})
    
    #Assert
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    response_data = response.json()
    
    # Assert the response structure
    assert "id" in response_data
    assert response_data["user_id"] == str(user_id), f"Expected user_id {user_id}, got {response_data['user_id']}"
    assert response_data["title"] == request_data["content"][:20], f"Expected title {request_data['content'][:20]}, got {response_data['title']}"
    assert "messages" in response_data, "Expected messages in response"
    assert len(response_data["messages"]) == 2, f"Expected 2 messages, got {len(response_data['messages'])}"
    
    # Check user message details
    assert response_data["messages"][0]["role"] == "user", "Expected user message role"
    assert response_data["messages"][0]["content"] == request_data["content"], f"Expected user message content {request_data['content']}, got {response_data['messages'][0]['content']}"
    
    #Check AI message details
    assert response_data["messages"][1]["role"] == "assistant", "Expected assistant message role"
    assert response_data["messages"][1]["content"] == expected_AI_response["content"], f"Expected assistant message content {expected_AI_response['content']}, got {response_data['messages'][1]['content']}"
    
    mock_langchain_service.conversation.assert_awaited_once()
    call_args  = mock_langchain_service.conversation.call_args
    assert call_args[0][0] == str(response_data["id"]), f"Expected conversation ID {response_data['id']}, got {call_args[0][0]}"
    assert call_args[0][1] == request_data["content"], f"Expected user input {request_data['content']}, got {call_args[0][1]}"
    assert "user_context" not in call_args.kwargs, f"Expected the keyword argument 'user_context' to be not present if passed with None, got {call_args.kwargs}"
        
    db_conversation = session.get(Conversation, response_data["id"])
    assert db_conversation is not None, "Expected conversation to be saved in the database"
    assert db_conversation.user_id == user_id, f"Expected conversation user ID {user_id}, got {db_conversation.user_id}"
    assert db_conversation.title == request_data["content"][:20], f"Expected conversation title {request_data['content'][:20]}, got {db_conversation.title}"
    assert len(db_conversation.messages) == 2, f"Expected 2 messages in conversation, got {len(db_conversation.messages)}"
    assert db_conversation.messages[0].role == "user", "Expected user message role in conversation"
    assert db_conversation.messages[0].content == request_data["content"], f"Expected user message content {request_data['content']}, got {db_conversation.messages[0].content}"
    assert db_conversation.messages[1].role == "assistant", "Expected assistant message role in conversation"
    assert db_conversation.messages[1].content == expected_AI_response["content"], f"Expected assistant message content {expected_AI_response['content']}, got {db_conversation.messages[1].content}"
    #assert db_conversation.messages[1].message_data == expected_AI_response["message_data"], f"Expected assistant message data {expected_AI_response['message_data']}, got {db_conversation.messages[1].message_data}"
    print("Test passed: Response contains the expected conversation")
    
def test_start_conversation_missing_user_id(client: TestClient, session: Session, mock_langchain_service: MagicMock):
    """
    Test the /v1/new endpoint with a missing user_id parameter.
    """
    # Arrange
    user_content = "Hello, I have no user_ID"
    user_role = "user"
    request_data = { "content": user_content, "role": user_role}
    
    # Act
    response = client.post("/v1/new", json=request_data)
    
    #Assert
    assert response.status_code == 422, f"Expected status code 422, got {response.status_code}"
    # Get the JSON response
    response_data = response.json()
    
    # Assert the error structure
    assert 'detail' in response_data, "Response missing 'detail' field"
    assert isinstance(response_data['detail'], list), "'detail' is not a list"
    assert len(response_data['detail']) > 0, "'detail' list is empty"
    
    # Find the specific user_id error
    user_id_error = None
    for error in response_data['detail']:
        if error.get('loc') == ['query', 'user_id']:
            user_id_error = error
            break
    
    # Assert that we found the user_id error
    assert user_id_error is not None, "user_id error not found in response"
    
    # Verify each component of the error
    assert user_id_error['type'] == 'missing', f"Expected 'missing', got '{user_id_error['type']}'"
    assert user_id_error['msg'] == 'Field required', f"Expected 'Field required', got '{user_id_error['msg']}'"
    assert user_id_error['input'] is None, f"Expected None, got {user_id_error['input']}"
    
    print("Test passed: Response contains the expected 'missing user_id' error")
    
def test_start_conversation_invalid_user_id(client: TestClient, session: Session, mock_langchain_service: MagicMock):
    """
    Test the /v1/new endpoint with an invalid user_id parameter.
    """
    # Arrange
    invalid_user_id = str(uuid.uuid4())  # Generate a random UUID that doesn't exist in the database
    user_content = "Hello, I have an invalid user_ID"
    user_role = "user"
    request_data = { "content": user_content, "role": user_role}    
    # Act
    response = client.post("/v1/new", json=request_data, params={"user_id": invalid_user_id})
    
    #Assert
    assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"
    
    # Get the JSON response
    response_data = response.json()
    
    # Assert the error structure
    assert 'detail' in response_data, "Response missing 'detail' field"
    
    # Assert the error message
    assert response_data['detail'] == "User not found", f"Expected 'User not found', got '{response_data['detail']}'"
    
    print("Test passed: Response contains the expected 'user not found' error")
    
        