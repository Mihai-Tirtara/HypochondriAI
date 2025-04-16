
from fastapi import APIRouter, HTTPException, Depends, Query
from core.models import ConversationPublic, MessageCreate, ConversationCreate
from core.session import get_session
from core.crud import create_conversation, create_message, get_conversation_by_id, get_conversations_by_user_id
from core.dependencies import get_langchain_service 
from services.llm import LangchainService
from services.bedrock import BedrockService
from prompts.prompt_utils import generate_health_anxiety_prompt
import logging
from sqlmodel import Session
from uuid import UUID


router = APIRouter(
    prefix="/v1",
    tags=["llm"]
)

logger = logging.getLogger(__name__)


@router.post("/analyse-symptoms", response_model=ConversationPublic)
async def analyze_symptoms(query: MessageCreate, userId:UUID = Query(...), db: Session = Depends(get_session), langchain_service: LangchainService = Depends(get_langchain_service)):
    
    conversation = ConversationCreate(title=query.content[:20])
    new_conversation = create_conversation(session=db, conversation_create=conversation, user_id=userId)
    if not new_conversation:
        raise HTTPException(status_code=500, detail="Failed to create conversation") 
    logger.info(f"Created new conversation with ID: {new_conversation.id}")
    
    user_message = create_message(session=db, message_create=query, conversation_id=new_conversation.id)
    if not user_message:
        raise HTTPException(status_code=500, detail="Failed to create message")
    logger.info(f"Created new message with ID: {user_message.id} in conversation ID: {new_conversation.id}")
    
    ai_response = await langchain_service.conversation(str(new_conversation.id), user_message.content)
    if not ai_response:
        raise HTTPException(status_code=500, detail="Failed to get AI response")
    logger.info(f"Received AI response: {ai_response}")
    
    # --- Serialize and store the full message data ---
    message_data_dict = None
    try:
        if hasattr(ai_response, 'model_dump'):
            message_data_dict = ai_response.model_dump()
        elif hasattr(ai_response, 'dict'):
            message_data_dict = ai_response.dict()
        else:
            message_data_dict = {"error": "Serialization failed", "content": ai_response_message.content}
    except Exception as e:
        logger.error(f"Error serializing AI message object: {e}", exc_info=True)
        message_data_dict = {"error": f"Serialization failed: {e}", "content": ai_response_message.content}
        
    ai_message = MessageCreate(
        content=ai_response.content,
        role="assistant",
        message_data=message_data_dict
    )
    ai_message_db = create_message(session=db, message_create=ai_message, conversation_id=new_conversation.id)
    if not ai_message_db:
        raise HTTPException(status_code=500, detail="Failed to create AI message")
    logger.info(f"Created AI message with ID: {ai_message_db.id} in conversation ID: {new_conversation.id}")
    
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