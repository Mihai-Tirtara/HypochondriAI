
from fastapi import APIRouter, HTTPException, Depends, Query
from app.core.models import ConversationPublic, MessageCreate, ConversationCreate, Conversation
from app.db.crud import create_conversation, create_message, get_conversation_by_id, get_conversations_by_user_id,check_conversation_exists, check_user_exists
from app.core.dependencies import get_langchain_service,get_session
from app.services.llm import LangchainService
import logging
from sqlmodel import Session
from uuid import UUID
from app.api.utils import saveConversation,saveMessage, serialise_message_data
from typing import List


router = APIRouter(
    prefix="/v1",
    tags=["llm"]
)

logger = logging.getLogger(__name__)


@router.post("/new", response_model=ConversationPublic)
async def start_conversation(query: MessageCreate, user_id:UUID = Query(...), db: Session = Depends(get_session), langchain_service: LangchainService = Depends(get_langchain_service)):
    
    """
    Start a new conversation with the AI.
        
    Args:
        query (MessageCreate): The message to send to the AI.
        user_id (UUID): The ID of the user.
        db (Session): The SQLModel session.
        langchain_service (LangchainService): The Langchain service instance.
    Returns:
        ConversationPublic: The created conversation object.    
    """
    if check_user_exists(session=db, user_id=user_id) == False:
        raise HTTPException(status_code=404, detail="User not found")
    
    # At the moment just save the title of the conversation as the first 20 characters of the query content
    # In the future, we can use the query content to generate a more meaningful title
    new_conversation = saveConversation(db=db, user_id = user_id, title=query.content[:20])
    user_message = saveMessage(db=db, conversation_id=new_conversation.id, content=query.content, role="user", message_data=None)
    ai_response = await langchain_service.conversation(str(new_conversation.id), user_message.content)
    if not ai_response:
        raise HTTPException(status_code=500, detail="Failed to get AI response")
    logger.info(f"Received AI response: {ai_response}")
    ai_response_metadata = serialise_message_data(ai_response)
    ai_message = saveMessage(db=db, conversation_id=new_conversation.id, content=ai_response.content, role="assistant", message_data=ai_response_metadata)
    #Return the newly created conversation with the messages
    conversation = get_conversation_by_id(session=db, conversation_id=new_conversation.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    logger.info(f"Retrieved conversation with ID: {conversation.id} and messages")
    return conversation
    
@router.post("/conversations", response_model=ConversationPublic)
async def continue_conversation(query: MessageCreate, conversation_id:UUID = Query(...), db: Session = Depends(get_session), langchain_service: LangchainService = Depends(get_langchain_service) ):
    """
    Continue an existing conversation by conversation ID.
    
    Args:
        query (MessageCreate): The message to send to the AI.
        conversation_id (UUID): The ID of the conversation.
        db (Session): The SQLModel session.
        langchain_service (LangchainService): The Langchain service instance.
        
    Returns:
        ConversationPublic: The updated conversation object.
    """
    if(check_conversation_exists(session=db, conversation_id=conversation_id) == False):
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    user_message = saveMessage(db=db, conversation_id=conversation_id, content=query.content, role="user", message_data=None)
    ai_response = await langchain_service.conversation(str(conversation_id), user_message.content)
    if not ai_response:
        raise HTTPException(status_code=500, detail="Failed to get AI response")
    logger.info(f"Received AI response: {ai_response}")
    ai_response_metadata = serialise_message_data(ai_response)
    ai_message = saveMessage(db=db, conversation_id=conversation_id, content=ai_response.content, role="assistant", message_data=ai_response_metadata)
    conversation = get_conversation_by_id(session=db, conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    logger.info(f"Retrieved conversation with ID: {conversation.id} and messages")
    return conversation      

@router.get("/conversations", response_model=List[ConversationPublic])
async def get_conversations(user_id: UUID = Query(...), db: Session = Depends(get_session)):
    """
    Get all conversations for a user by user ID.
    
    Args:
        user_id (UUID): The ID of the user.
        db (Session): The SQLModel session.

    Returns:
        List[ConversationPublic]: A list of conversations for the user.
    """
    if check_user_exists(session=db, user_id=user_id) == False:
        raise HTTPException(status_code=404, detail="User not found")
    
    conversations = get_conversations_by_user_id(session=db, user_id=user_id)
    if not conversations:
        raise HTTPException(status_code=404, detail="No conversations found")
    logger.info(f"Retrieved {len(conversations)} conversations for user ID: {user_id}")
    return conversations