import uuid
from typing import Any,List

from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from core.security import get_password_hash, verify_password
from core.models import User, UserCreate, UserPublic, Conversation, ConversationCreate, Message, MessageCreate

def create_user(*, session: Session, user_create: UserCreate) -> User:
    user_db = User.model_validate(user_create, update={"password_hash": get_password_hash(user_create.password)} )
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db

def create_conversation(*, session: Session, conversation_create: ConversationCreate, user_id: uuid.UUID) -> Conversation:
    conversation_db = Conversation.model_validate(conversation_create, update={"user_id": user_id})
    session.add(conversation_db)
    session.commit()
    session.refresh(conversation_db)
    return conversation_db

def create_message(*, session: Session, message_create: MessageCreate, conversation_id: uuid.UUID) -> Message:
    message_db = Message.model_validate(message_create, update={"conversation_id": conversation_id})
    session.add(message_db)
    session.commit()
    session.refresh(message_db)
    return message_db

def get_conversation_by_id(*, session: Session, conversation_id: uuid.UUID) -> Conversation:
    statement = select(Conversation).where(Conversation.id == conversation_id).options(selectinload(Conversation.messages))
    conversation = session.exec(statement).first()
    return conversation

def get_conversations_by_user_id(*, session: Session, user_id: uuid.UUID) -> List[Conversation]:
    """Get all conversations for a user by user ID."""
    statement = select(Conversation).where(Conversation.user_id == user_id)
    conversations = session.exec(statement).all()
    return conversations
