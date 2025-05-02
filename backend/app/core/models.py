import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional  # Use standard typing

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB  # Keep this for JSONB type
from sqlmodel import Column, Field, Relationship, SQLModel


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)


class UserCreate(UserBase):
    password: str  # Receive plain password for creation


class UserPublic(UserBase):
    id: uuid.UUID


class User(UserBase, table=True):
    __tablename__ = "users"  # Optional, SQLModel infers if class name matches

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: str = Field(max_length=128)  # Specify max_length if desired
    created_at: datetime = Field(
        default_factory=datetime.utcnow,  # Use default_factory for non-SQL defaults
        sa_column_kwargs={
            "server_default": func.now()
        },  # Keep server_default via sa_column_kwargs
    )

    conversations: list["Conversation"] = Relationship(back_populates="user")


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"  # Add more roles as needed

    def __str__(self):
        return self.value


class MessageBase(SQLModel):
    content: str = Field()
    role: MessageRole = Field(
        sa_column=Column(SQLAlchemyEnum(MessageRole), nullable=False)
    )


class MessageCreate(MessageBase):
    message_data: dict[str, Any] | None = None


class MessagePublic(MessageBase):
    id: uuid.UUID
    created_at: datetime


class Message(MessageBase, table=True):
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", index=True)
    message_data: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,  # Use default_factory for non-SQL defaults
        sa_column_kwargs={
            "server_default": func.now()
        },  # Keep server_default via sa_column_kwargs
    )

    conversation: "Conversation" = Relationship(back_populates="messages")


class ConversationBase(SQLModel):
    title: str | None = Field(default=None, max_length=100)


class ConversationCreate(ConversationBase):
    pass


class ConversationPublic(ConversationBase):
    id: uuid.UUID
    created_at: datetime
    user_id: uuid.UUID
    messages: list[MessagePublic] = []  # Include messages in the public representation


class Conversation(ConversationBase, table=True):
    __tablename__ = "conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,  # Use default_factory for non-SQL defaults
        sa_column_kwargs={
            "server_default": func.now()
        },  # Keep server_default via sa_column_kwargs
    )
    user: User = Relationship(back_populates="conversations")
    messages: list[Message] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )  # Cascade delete for messages
