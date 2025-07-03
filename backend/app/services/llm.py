import logging
from collections.abc import Sequence
from typing import Annotated, Any, Optional

import boto3
from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from psycopg_pool import AsyncConnectionPool
from typing_extensions import TypedDict

from app.config.config import settings
from app.prompts.prompt_utils import generate_health_anxiety_prompt

logger = logging.getLogger(__name__)


class State(TypedDict):
    """State for Langchain service"""

    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_context: str | None


class LangchainService:
    graph: Any | None = None  # Use Any or more specific type if available
    checkpointer = None  # Union type for checkpointer
    model: Any | None = None  # Use Any or more specific ChatModel type
    db_pool: AsyncConnectionPool | None = None  # Store the pool instance
    _model_id: str | None = None
    _model_provider: str | None = None
    _initialized: bool = False

    def __init__(self, model_id: str | None = None, model_provider: str | None = None):
        LangchainService.initialize_bedrock_client()

    async def conversation(
        self, conversation_id: str, user_input: str, user_context: str | None = None
    ):

        if not self.__class__._initialized or self.__class__.graph is None:
            raise Exception("Graph not initialized. Call initialize_graph() first.")

        # Check if checkpointer exists and log its type for debugging
        if self.__class__.checkpointer:
            logger.debug(f"Using checkpointer: {type(self.__class__.checkpointer)}")
        else:
            logger.error("Checkpointer is None during conversation call.")
            raise Exception("Checkpointer not available.")

        config = {"configurable": {"thread_id": conversation_id}}
        input_messages = [HumanMessage(content=user_input)]
        response = await self.__class__.graph.ainvoke(
            {"messages": input_messages, "user_context": user_context}, config=config
        )
        return response["messages"][-1]

    @classmethod
    async def initialize_langchain_components(
        cls, model_id: str | None = None, model_provider: str | None = None
    ):

        if cls._initialized:
            logger.info("Graph already initialized.")
            return cls.graph
        try:
            cls._initialize_model(model_id=model_id, model_provider=model_provider)
            await cls._initialize_pool()
            await cls._initialize_checkpointer()
            cls._initialize_graph()
        except Exception as e:
            logger.error(f"Error initializing Langchain components: {e!s}")
            raise
        logger.info("Langchain components initialized successfully.")

    @classmethod
    def _initialize_graph(cls):
        """
        model and checkpointer need to be initialized before this method is called.
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

    @classmethod
    async def _initialize_checkpointer(cls):
        if cls.checkpointer is None and cls.db_pool is not None:
            logger.info("Initializing checkpointer...")
            try:
                cls.checkpointer = AsyncPostgresSaver(cls.db_pool)
                await cls.checkpointer.setup()
                logger.info("Checkpointer initialized.")
            except Exception as e:
                logger.error(f"Error initializing checkpointer: {e!s}")
                cls.checkpointer = None
                raise

    @classmethod
    async def _initialize_pool(cls):
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
                cls.db_pool = AsyncConnectionPool(
                    conninfo=conninfo_str,
                    max_size=20,
                    max_idle=60,
                    open=False,
                    kwargs=connection_kwargs,
                )
                await cls.db_pool.open()
                logger.info("Database pool initialized.")
            except Exception as e:
                logger.error(f"Error initializing database pool: {e!s}")
                cls.db_pool = None
                raise

    @classmethod
    async def close_pool(cls):
        if cls.db_pool:
            try:
                await cls.db_pool.close()
                cls.db_pool = None
                logger.info("Database pool closed.")
            except Exception as e:
                logger.error(f"Error closing database pool: {e!s}")
        else:
            logger.info("No database pool to close.")

    @staticmethod
    def call_model(state: State):

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
    def _initialize_model(
        cls, model_id: str | None = None, model_provider: str | None = None
    ):

        cls._model_id = model_id or settings.MODEL_ID
        cls._model_provider = model_provider or settings.MODEL_PROVIDER
        try:
            # Initialize the Bedrock client one extra time for safety
            # This is a bit redundant but ensures the client is set up before model initialization
            cls.initialize_bedrock_client()
            cls.model = init_chat_model(
                model=cls._model_id, model_provider=cls._model_provider
            )
            logger.info(
                f"Model initialized: {cls._model_id} with provider: {cls._model_provider}"
            )
        except Exception as e:
            logger.error(f"Error initializing model: {e!s}")
            raise

    @staticmethod
    def initialize_bedrock_client():
        """Create and return an Amazon Bedrock client"""
        try:
            boto3.setup_default_session(
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
        except Exception as e:
            logging.error(f"Error initializing Bedrock client: {e!s}")
            raise
