import uuid
from typing import List, Optional, Dict, Any # Use standard typing
from datetime import datetime
from sqlalchemy import func # Import func for SQLAlchemy functions
from sqlalchemy.dialects.postgresql import JSONB # Keep this for JSONB type

from sqlmodel import Field, Relationship, SQLModel, Column
from pydantic import BaseModel

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    
class UserCreate(UserBase):
    password: str # Receive plain password for creation

class UserPublic(UserBase):
    id: uuid.UUID

class User(UserBase, table=True):
    __tablename__ = 'users' # Optional, SQLModel infers if class name matches

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: str = Field(max_length=128) # Specify max_length if desired
    created_at: datetime = Field(
        default_factory=datetime.utcnow, # Use default_factory for non-SQL defaults
        sa_column_kwargs={"server_default": func.now()} # Keep server_default via sa_column_kwargs
    )

    conversations: List["Conversation"] = Relationship(back_populates="user")
    

class MessageBase(SQLModel):
    content: str = Field(max_length=2000) # Adjust max_length as needed
    role: str = Field(max_length=50) # e.g., 'user', 'assistant'
    
class MessageCreate(MessageBase):
    pass

class MessagePublic(MessageBase):
    id: uuid.UUID
    created_at: datetime  
    
class Message(MessageBase, table=True):
    __tablename__ = 'messages'

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id",index=True)
    message_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    created_at: datetime = Field(
        default_factory=datetime.utcnow, # Use default_factory for non-SQL defaults
        sa_column_kwargs={"server_default": func.now()} # Keep server_default via sa_column_kwargs
    ) 

    conversation: "Conversation" = Relationship(back_populates="messages")    
    
    
class ConversationBase(SQLModel):
    title: Optional[str] = Field(default=None, max_length=100)    

class ConversationCreate(ConversationBase):
    pass    
        
class ConversationPublic(ConversationBase):
    id:uuid.UUID 
    created_at: datetime 
    userId: uuid.UUID   
    messages: List[MessagePublic] = [] # Include messages in the public representation
        
class Conversation(ConversationBase, table=True):
    __tablename__ = 'conversations'

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id",index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, # Use default_factory for non-SQL defaults
        sa_column_kwargs={"server_default": func.now()} # Keep server_default via sa_column_kwargs
    )
    user: User = Relationship(back_populates="conversations")
    messages: List[Message] = Relationship(back_populates="conversation", sa_relationship_kwargs={"cascade": "all, delete-orphan"}) # Cascade delete for messages
    

class HealthQuery(BaseModel):
    symptoms: str = Field(..., description="Description of symptoms")
    user_context: Optional[str] = Field(None, description="Additional context about health situation")        
    
    class Config:
        schema_extra = {
            "example": {
                "symptoms": "I've been experiencing headaches and dizziness",
                "user_context": "I have a history of migraines"
            }
        }
        
        