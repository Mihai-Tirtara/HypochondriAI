import uuid

from sqlmodel import Field, Relationship, SQLModel

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    
class UserCreate(UserBase):
    password: str # Receive plain password for creation

class UserPublic(UserBase):
    id: int

class User(UserBase, table=True):
    __tablename__ = 'users' # Optional, SQLModel infers if class name matches

    id: Optional[int] = Field(default=None, primary_key=True)
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
    id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)    
    
class Message(MessageBase, table=True):
    __tablename__ = 'messages'

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id")
    message_data: Optional[dict] = Field(default=None) # For storing the complete message data in JSON format

    conversation: "Conversation" = Relationship(back_populates="messages")    
    
    
class ConversationBase(SQLModel):
    title: Optional[str] = None    
        
class ConversationPublic(ConversationBase):
    id: int
    created_at: datetime = Field(default_factory=datetime.utcnow) 
    userId: int   
    messages: List[MessagePublic] = [] # Include messages in the public representation
        
class Conversation(ConversationBase, table=True):
    __tablename__ = 'conversations'

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow) 

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
        
        