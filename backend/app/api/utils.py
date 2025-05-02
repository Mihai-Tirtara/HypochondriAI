import logging
from typing import Any, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.core.models import (
    Conversation,
    ConversationCreate,
    Message,
    MessageCreate,
    MessageRole,
)
from app.db.crud import create_conversation, create_message
from app.services.llm import LangchainService

logger = logging.getLogger(__name__)


def save_conversation(db: Session, user_id: UUID, title: str | None) -> Conversation:
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
    db_conversation = create_conversation(
        session=db, conversation_create=conversation, user_id=user_id
    )
    if not db_conversation:
        raise HTTPException(status_code=500, detail="Failed to create conversation")
    logger.info(f"Created new conversation with ID: {db_conversation.id}")

    return db_conversation


def save_message(
    db: Session,
    conversation_id: UUID,
    content: str,
    role: MessageRole,
    message_data: dict[str, Any] | None = None,
) -> Message:
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
        content=content, role=role, message_data=message_data
    )

    db_message = create_message(
        session=db, message_create=message_create, conversation_id=conversation_id
    )
    if not db_message:
        raise HTTPException(status_code=500, detail="Failed to create message")

    logger.info(
        f"Created new message with ID: {db_message.id} in conversation ID: {conversation_id}"
    )

    return db_message


def serialise_message_data(ai_response: Any) -> dict[str, Any] | None:
    """
    Serializes the AI response message data into a dictionary format.
    Args:
        aiResponse (Any): The AI response object.
    Returns:
        Optional[Dict[str, Any]]: The serialized message data as a dictionary.
    """

    message_data_dict = None
    try:
        if hasattr(ai_response, "model_dump"):
            message_data_dict = ai_response.model_dump()
        elif hasattr(ai_response, "dict"):
            message_data_dict = ai_response.dict()
        else:
            message_data_dict = {
                "error": "Serialization failed",
                "content": ai_response.content,
            }
    except Exception as e:
        logger.error(f"Error serializing AI message object: {e}", exc_info=True)
        message_data_dict = {
            "error": f"Serialization failed: {e}",
            "content": ai_response.content,
        }

    return message_data_dict


def create_title(content: str) -> str:
    """
    Create a title for the conversation based on the content.
    At the moment just save the title of the conversation as the first 20 characters of the query content
    In the future, we can use the query content to generate a more meaningful title
    Args:
    content (str): The content of the message.

    Returns:
    str: The generated title.
    """
    title = content[:20] if len(content) > 20 else content  # noqa: PLR2004
    return title


def cleanup_conversation(db: Session, conversation_id: UUID) -> None:
    """
    Clean up the conversation by deleting it from the database.

    Args:
        db (Session): The SQLModel session.
        conversation (Conversation): The conversation object to be deleted.
    """
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        logger.error(f"Conversation with ID {conversation_id} not found")
        raise HTTPException(status_code=404, detail="Conversation not found")
    try:
        db.delete(conversation)
        db.commit()
        logger.info(f"Deleted conversation with ID: {conversation_id}")
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to delete conversation"
        ) from e


async def get_and_save_ai_response(
    conversation_id: UUID, user_content: str, service: LangchainService, db: Session
) -> Message:
    """
    Get the AI response and save it to the database.

    Args:
        conversation_id (UUID): The ID of the conversation.
        user_content (str): The content of the user's message.
        service (LangchainService): The Langchain service instance.
        db (Session): The SQLModel session.

    Returns:
        Message: The saved AI response message object.
    """
    try:
        ai_response = await service.conversation(str(conversation_id), user_content)
        if not ai_response:
            raise ValueError("Langchain service returned None or empty response")
        logger.info(f"Received AI response: {ai_response}")
        ai_response_metadata = serialise_message_data(ai_response)
        ai_message = save_message(
            db=db,
            conversation_id=conversation_id,
            content=ai_response.content,
            role=MessageRole.assistant,
            message_data=ai_response_metadata,
        )
        return ai_message
    except Exception as e:
        logger.error(f"Langchain service error: {e!s}")
        raise HTTPException(
            status_code=500, detail=f"Error getting AI response: {e!s}"
        ) from e
