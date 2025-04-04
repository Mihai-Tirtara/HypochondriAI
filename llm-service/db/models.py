from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    """User model for storing user information."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
    
    class Conversation(Base):
        """Conversation model for storing conversation threads."""
        __tablename__ = 'conversations'

        id = Column(Integer, primary_key=True, autoincrement=True)
        user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
        title = Column(String(100), nullable=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        
        user = relationship("User")
        messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

        def __repr__(self):
            return f"<Conversation(id={self.id}, title={self.title})>"
        
    class Message(Base):
        """Message model for storing conversation messages."""
        __tablename__ = 'messages'

        id = Column(Integer, primary_key=True, autoincrement=True)
        conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
        content = Column(Text, nullable=False)
        role = Column(String(50), nullable=False) # e.g., 'user', 'assistant'
        message_data = Column(JSONB, nullable=True) # For storing the complete message data in JSON format
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        
        conversation = relationship("Conversation", back_populates="messages")
        
        def __repr__(self):
            return f"<Message(id={self.id}, role={self.role}, content={self.content[:20]})>"