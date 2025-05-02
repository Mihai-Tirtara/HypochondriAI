import uuid

# Removed unused import of List from typing
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.core.models import (
    Conversation,
    ConversationCreate,
    Message,
    MessageCreate,
    User,
    UserCreate,
)
from app.core.security import get_password_hash


def create_user(*, session: Session, user_create: UserCreate) -> User:
    user_db = User.model_validate(
        user_create, update={"password_hash": get_password_hash(user_create.password)}
    )
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


def create_conversation(
    *, session: Session, conversation_create: ConversationCreate, user_id: uuid.UUID
) -> Conversation:
    conversation_db = Conversation.model_validate(
        conversation_create, update={"user_id": user_id}
    )
    session.add(conversation_db)
    session.commit()
    session.refresh(conversation_db)
    return conversation_db


def create_message(
    *, session: Session, message_create: MessageCreate, conversation_id: uuid.UUID
) -> Message:
    message_db = Message.model_validate(
        message_create, update={"conversation_id": conversation_id}
    )
    print("THis is how the message lookg before being saved in the database")
    print(message_db)
    session.add(message_db)
    session.commit()
    session.refresh(message_db)
    return message_db


def get_conversation_by_id(
    *, session: Session, conversation_id: uuid.UUID
) -> Conversation:
    statement = (
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )
    conversation = session.exec(statement).first()
    return conversation


def get_conversations_by_user_id(
    *, session: Session, user_id: uuid.UUID
) -> list[Conversation]:
    """Get all conversations for a user by user ID."""
    statement = select(Conversation).where(Conversation.user_id == user_id)
    conversations = session.exec(statement).all()
    return conversations


def check_conversation_exists(*, session: Session, conversation_id: uuid.UUID) -> bool:
    """Check if a conversation exists by its ID."""
    statement = select(Conversation).where(Conversation.id == conversation_id)
    return session.exec(statement).first() is not None


def check_user_exists(*, session: Session, user_id: uuid.UUID) -> bool:
    """Check if a user exists by its ID."""
    statement = select(User).where(User.id == user_id)
    return session.exec(statement).first() is not None
