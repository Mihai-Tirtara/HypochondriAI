from typing import Sequence, Optional,Any

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
from langchain.chat_models import init_chat_model
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.prompts.prompt_utils import generate_health_anxiety_prompt
from psycopg_pool import AsyncConnectionPool
import logging
import boto3
from app.config.config import settings
logger = logging.getLogger(__name__)


class State(TypedDict):
    """State for Langchain service"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_context: Optional[str]


class LangchainService:
    graph: Optional[Any] = None # Use Any or more specific type if available
    checkpointer = None # Union type for checkpointer
    model: Optional[Any] = None # Use Any or more specific ChatModel type
    db_pool: Optional[AsyncConnectionPool] = None # Store the pool instance
    _model_id: Optional[str] = None
    _model_provider: Optional[str] = None
    _initialized: bool = False
    
    def __init__(self, model_id: Optional[str] = None, model_provider: Optional[str] = None):
        """
        Initialize Langchain service with optional model and provider 

        Args:
            model_id: The model ID to use. If None, uses the default from settings.
            model_provider: The provider of the model. If None, uses the default from settings.
        """
        logger.debug("LangchainSerivice created")
        LangchainService.initialize_bedrock_client()
        
    @staticmethod
    def initialize_bedrock_client():
        """Create and return an Amazon Bedrock client"""
        try:
            boto3.setup_default_session(   
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        except Exception as e:
            logging.error(f"Error initializing Bedrock client: {str(e)}")
            raise    
        
    @staticmethod    
    def call_model(state:State):
        
            
        """
        Call the model with the given state.

        Args:
            state: The state to pass to the model.

        Returns:
            The response from the model.
            
        """
        
        # Get the components from the state
        messages = state["messages"]
        user_context = state.get("user_context", None)
        prompt_template = generate_health_anxiety_prompt(user_context)
        # Invoke the prompt template with the state to get a formatted prompt
        formatted_prompt = prompt_template.invoke({"messages": messages})
    
        # Now pass the formatted prompt to the model
        response = LangchainService.model.invoke(formatted_prompt)
        logger.info(f"Model response: {response}")
        return {"messages": [response]}
    
    @classmethod
    async def initialize_langchain_components(cls, model_id: Optional[str] = None, model_provider: Optional[str] = None):
        """
        Set up all the necessary componnents  for the Langchain service.
        
        Args:
            model_id: The model ID to use. If None, uses the default from settings.
            model_provider: The provider of the model. If None, uses the default from settings.
        """
        if cls._initialized:
            logger.info("Graph already initialized.")
            return cls.graph
        try:
            cls._initialize_model(model_id=model_id, model_provider=model_provider)
            await cls._initialize_pool()
            await cls._initialize_checkpointer()
            cls._initialize_graph()
        except Exception as e:
            logger.error(f"Error initializing Langchain components: {str(e)}")
            raise
        
    @classmethod
    def _initialize_model(cls, model_id: Optional[str] = None, model_provider: Optional[str] = None):
        """
        Initialize the model with the given ID and provider.

        Args:
            model_id: The ID of the model to use.
            model_provider: The provider of the model.

        Returns:
            The initialized model.
        """
        # Initialize the model
        cls._model_id = model_id or settings.MODEL_ID
        cls._model_provider = model_provider or settings.MODEL_PROVIDER 
        try:
            # Initialize the Bedrock client one extra time for safety
            # This is a bit redundant but ensures the client is set up before model initialization
            cls.initialize_bedrock_client()
            cls.model = init_chat_model(model=cls._model_id, model_provider=cls._model_provider)
            logger.info(f"Model initialized: {cls._model_id} with provider: {cls._model_provider}")
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            raise
            
    @classmethod
    async def _initialize_pool(cls):
        """
        Initialize the database pool 
        """
        if cls.db_pool is None:
            logger.info("Initializing database pool...")
            try:
                connection_kwargs = {
                    "autocommit": True,
                    "prepare_threshold": 0,
                }
                conninfo_str = (
                    f"dbname={settings.DB_NAME} "
                    f"user={settings.DB_USERNAME} "
                    f"password={settings.DB_PASSWORD} "
                    f"host={settings.DB_HOST} "
                    f"port={settings.DB_PORT}"
                )
                cls.db_pool = AsyncConnectionPool(conninfo=conninfo_str, max_size=20, max_idle=60, open=False, kwargs=connection_kwargs)
                await cls.db_pool.open()
                logger.info("Database pool initialized.")
            except Exception as e:
                logger.error(f"Error initializing database pool: {str(e)}")
                cls.db_pool = None
                raise   
            
    @classmethod 
    async def _initialize_checkpointer(cls):
        """
        Initialize the checkpointer for the graph.
        """
        if cls.checkpointer is None and cls.db_pool is not None:
            logger.info("Initializing checkpointer...")
            try:
                cls.checkpointer = AsyncPostgresSaver(cls.db_pool)
                await cls.checkpointer.setup()
                logger.info("Checkpointer initialized.")
            except Exception as e:
                logger.error(f"Error initializing checkpointer: {str(e)}")
                cls.checkpointer = None
                raise
            
    @classmethod    
    async def close_pool(cls):
        """
        Close the pool and any resources it holds.
        """
        if cls.db_pool:
            try:
                await cls.db_pool.close()
                cls.db_pool = None
                logger.info("Database pool closed.")
            except Exception as e:
                logger.error(f"Error closing database pool: {str(e)}")    
        else:
            logger.info("No database pool to close.")
            
    @classmethod
    def _initialize_graph(cls):
        """
        Initialize the graph with the model and checkpointer.
        """
        if cls.graph is None:
            logger.info("Initializing graph...")
            workflow = StateGraph(state_schema=State)
            workflow.add_edge(START, "model")
            workflow.add_node("model", cls.call_model)
            workflow.add_edge("model", END)
            cls.graph = workflow.compile(checkpointer=cls.checkpointer)
            cls._initialized = True
            logger.info("Graph initialized.")
        else:
            logger.info("Graph already initialized.")        

    async def conversation(self, conversation_id:str ,user_input: str, user_context: Optional[str] = None) :
        """
        Create a conversation with the chat model or continue an existing one.
        Args:
            conversation_id: The ID of the conversation.
            user_input: The user's query.
            user_context: Additional context provided by the user.

        Returns:
            The response from the AI model 
        """
        if not self.__class__._initialized or self.__class__.graph is None:
            raise Exception("Graph not initialized. Call initialize_graph() first.")
        
        # Check if checkpointer exists and maybe log its type for debugging
        if self.__class__.checkpointer:
            logger.debug(f"Using checkpointer: {type(self.__class__.checkpointer)}")
        else:
            logger.error("Checkpointer is None during conversation call.")
            raise Exception("Checkpointer not available.")    
            
        config = {"configurable": {"thread_id": conversation_id}}
        input_messages = [HumanMessage(content=user_input)]
        response = await self.__class__.graph.ainvoke({"messages":input_messages, "user_context": user_context}, config=config)
        return response["messages"][-1]  
    
    