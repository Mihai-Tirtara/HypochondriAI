import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.core.models import User, UserCreate, UserPublic, Conversation, ConversationCreate, Message, MessageCreate

def create_user(*, session: Session, user_create: UserCreate) -> User:
    user_db = User.model_validate(user_create, update={"hashed_password": get_password_hash(user_create.password)} )
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
