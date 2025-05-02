import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.api.utils import (
    cleanup_conversation,
    create_title,
    get_and_save_ai_response,
    save_conversation,
    save_message,
)
from app.core.dependencies import get_langchain_service, get_session
from app.core.models import ConversationPublic, MessageCreate, MessageRole
from app.db.crud import (
    check_conversation_exists,
    check_user_exists,
    get_conversation_by_id,
    get_conversations_by_user_id,
)
from app.services.llm import LangchainService

router = APIRouter(prefix="/v1", tags=["llm"])

logger = logging.getLogger(__name__)


@router.post("/new", response_model=ConversationPublic)
async def start_conversation(
    query: MessageCreate,
    user_id: UUID = Query(...),
    db: Session = Depends(get_session),
    langchain_service: LangchainService = Depends(get_langchain_service),
):
    """Start a new conversation with the AI.

    Args:
        query (MessageCreate): The message to send to the AI.
        user_id (UUID): The ID of the user.
        db (Session): The SQLModel session.
        langchain_service (LangchainService): The Langchain service instance.

    Returns:
        ConversationPublic: The created conversation object.
    """
    if not check_user_exists(session=db, user_id=user_id):
        raise HTTPException(status_code=404, detail="User not found")

    new_conversation = save_conversation(
        db=db, user_id=user_id, title=create_title(query.content)
    )

    user_message = save_message(
        db=db,
        conversation_id=new_conversation.id,
        content=query.content,
        role=MessageRole.user,
        message_data=None,
    )

    try:
        await get_and_save_ai_response(
            conversation_id=str(new_conversation.id),
            user_content=user_message.content,
            service=langchain_service,
            db=db,
        )
    except HTTPException as e:
        cleanup_conversation(db=db, conversation_id=new_conversation.id)
        raise e

    # Return the newly created conversation with the messages
    conversation = get_conversation_by_id(
        session=db, conversation_id=new_conversation.id
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    logger.info(f"Retrieved conversation with ID: {conversation.id} and messages")
    return conversation


@router.post("/conversations", response_model=ConversationPublic)
async def continue_conversation(
    query: MessageCreate,
    conversation_id: UUID = Query(...),
    db: Session = Depends(get_session),
    langchain_service: LangchainService = Depends(get_langchain_service),
):
    """Continue an existing conversation by conversation ID.

    Args:
        query (MessageCreate): The message to send to the AI.
        conversation_id (UUID): The ID of the conversation.
        db (Session): The SQLModel session.
        langchain_service (LangchainService): The Langchain service instance.

    Returns:
        ConversationPublic: The updated conversation object.
    """
    if not check_conversation_exists(session=db, conversation_id=conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")

    user_message = save_message(
        db=db,
        conversation_id=conversation_id,
        content=query.content,
        role=MessageRole.user,
        message_data=None,
    )

    try:
        await get_and_save_ai_response(
            conversation_id=str(conversation_id),
            user_content=user_message.content,
            service=langchain_service,
            db=db,
        )
    except HTTPException as e:
        raise e

    conversation = get_conversation_by_id(session=db, conversation_id=conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    logger.info(f"Retrieved conversation with ID: {conversation.id} and messages")
    return conversation


@router.get("/conversations", response_model=list[ConversationPublic])
async def get_conversations(
    user_id: UUID = Query(...), db: Session = Depends(get_session)
):
    """Get all conversations for a user by user ID.

    Args:
        user_id (UUID): The ID of the user.
        db (Session): The SQLModel session.

    Returns:
        List[ConversationPublic]: A list of conversations for the user.
    """
    if not check_user_exists(session=db, user_id=user_id):
        raise HTTPException(status_code=404, detail="User not found")

    conversations = get_conversations_by_user_id(session=db, user_id=user_id)

    if not conversations:
        raise HTTPException(status_code=404, detail="No conversations found")

    logger.info(f"Retrieved {len(conversations)} conversations for user ID: {user_id}")
    return conversations
