import logging
from sqlmodel import Session
from uuid import UUID
from typing import Optional, Dict, Any
from app.core.models import Conversation, Message, MessageCreate, ConversationCreate, MessageRole
from app.db.crud import create_conversation,create_message
from fastapi import HTTPException

logger = logging.getLogger(__name__)


def saveConversation(db:Session, user_id:UUID, title:Optional[str]) -> Conversation : 
    """
    Create the conversation object and save it to the database
    
    Args:
        db (Session): The SQLModel session.
        user_id (UUID): The ID of the user.
        title (Optional[str]): The title of the conversation.

    Returns:
        Conversation: The saved conversation object.
    """
    
    conversation = ConversationCreate(title=title)
    db_conversation = create_conversation(session=db, conversation_create=conversation, user_id=user_id)
    if not db_conversation:
        raise HTTPException(status_code=500, detail="Failed to create conversation") 
    logger.info(f"Created new conversation with ID: {db_conversation.id}")
    
    return db_conversation

def saveMessage(db:Session, conversation_id:UUID, content:str, role:MessageRole, message_data:Optional[Dict[str, Any]] = None) -> Message:
    """
    Create the message object and save it to the database
    
    Args:
        db (Session): The SQLModel session.
        conversation_id (UUID): The ID of the conversation.
        content (str): The content of the message.
        role (str): The role of the message (e.g., 'user', 'assistant').
        message_data (Optional[Dict[str, Any]]): The full messaged data .

    Returns:
        Message: The saved message object.
    """
    if content is None or content == "":
        raise HTTPException(status_code=400, detail="Message content cannot be empty")
    
    message_create = MessageCreate(
        content=content,
        role=role,
        message_data=message_data
    )
    
    db_message = create_message(session=db, message_create=message_create, conversation_id=conversation_id)
    if not db_message:
        raise HTTPException(status_code=500, detail="Failed to create message")
    
    logger.info(f"Created new message with ID: {db_message.id} in conversation ID: {conversation_id}")
    
    return db_message

def serialise_message_data(aiResponse:Any) -> Optional[Dict[str, Any]]:
    """
    Serializes the AI response message data into a dictionary format.
    
    Args:
        aiResponse (Any): The AI response object.

    Returns:
        Optional[Dict[str, Any]]: The serialized message data as a dictionary.
    """
    
    message_data_dict = None
    try:
        if hasattr(aiResponse, 'model_dump'):
            message_data_dict = aiResponse.model_dump()
        elif hasattr(aiResponse, 'dict'):
            message_data_dict = aiResponse.dict()
        else:
            message_data_dict = {"error": "Serialization failed", "content": aiResponse.content}
    except Exception as e:
        logger.error(f"Error serializing AI message object: {e}", exc_info=True)
        message_data_dict = {"error": f"Serialization failed: {e}", "content": aiResponse.content}
    
    return message_data_dict