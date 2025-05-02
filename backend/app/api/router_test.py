import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.api.utils import (
    cleanup_conversation,
    create_title,
    get_and_save_ai_response,
    save_conversation,
    save_message,
)
from app.core.dependencies import get_langchain_service, get_session
from app.core.models import (
    ConversationPublic,
    MessageCreate,
    MessageRole,
    User,
    UserCreate,
)
from app.db.crud import (
    create_user,
    get_conversation_by_id,
)
from app.services.llm import LangchainService

router_test = APIRouter(prefix="/test", tags=["llm"])

logger = logging.getLogger(__name__)


@router_test.post("/new", response_model=ConversationPublic)
async def start_conversation(
    query: MessageCreate,
    db: Session = Depends(get_session),
    langchain_service: LangchainService = Depends(get_langchain_service),
):
    """Test Starting a new conversation with the AI with a predefined user.
        Used at the moment for making the front-end functional
        Will be replaced once authenthication is implemented

    Args:
        query (MessageCreate): The message to send to the AI.
        db (Session): The SQLModel session.
        langchain_service (LangchainService): The Langchain service instance.

    Returns:
        ConversationPublic: The created conversation object.
    """
    test_user = create_test_user(db=db)
    new_conversation = save_conversation(
        db=db, user_id=test_user.id, title=create_title(query.content)
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


def create_test_user(db: Session) -> User:
    test_user = db.exec(select(User).where(User.email == "test@.com")).first()
    if not test_user:
        intial_user = UserCreate(
            username="test",
            password="test",
            email="test@.com",
        )
        test_user = create_user(session=db, user_create=intial_user)

    return test_user
