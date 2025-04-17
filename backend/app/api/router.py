
from fastapi import APIRouter, HTTPException, Depends, Query
from core.models import ConversationPublic, MessageCreate, ConversationCreate, Conversation
from db.crud import create_conversation, create_message, get_conversation_by_id, get_conversations_by_user_id
from core.dependencies import get_langchain_service,get_session
from services.llm import LangchainService
import logging
from sqlmodel import Session
from uuid import UUID
from utils import saveConversation,saveMessage, serialise_message_data


router = APIRouter(
    prefix="/v1",
    tags=["llm"]
)

logger = logging.getLogger(__name__)


@router.post("/analyse-symptoms", response_model=ConversationPublic)
async def analyze_symptoms(query: MessageCreate, userId:UUID = Query(...), db: Session = Depends(get_session), langchain_service: LangchainService = Depends(get_langchain_service)):
    
    # At the moment just save the title of the conversation as the first 20 characters of the query content
    # In the future, we can use the query content to generate a more meaningful title
    new_conversation = saveConversation(db=db, user_id = userId, title=query.content[:20])
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
    
    
    """   
@router.post("/conversations{conversation_Id}", response_model=ConversationPublic)
async def conversation(query: MessageCreate, conversation_id:UUID ):  
    - create message with the conversation_id and the MessageCreate object from the front-end in the database 
    - Call the langchain_service with the conversation_id and the messageCreate object
    - With the response from the langchain_service, create a new messsage with the conversation_id and the response from the langchain_service in the database      
    - Return the conversation with the messages from the database
    """        