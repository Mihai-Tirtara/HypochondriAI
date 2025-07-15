import asyncio
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
    graph: Any | None = None
    checkpointer = None
    model: Any | None = None
    db_pool: AsyncConnectionPool | None = None
    model_id: str | None = None
    model_provider: str | None = None
    initialized: bool = False
    instance: Optional["LangchainService"] = None
    creation_lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, model_id: str | None = None, model_provider: str | None = None):
        # Initialize instance variables if not already done
        if not hasattr(self, "initialized"):
            self.graph = None
            self.checkpointer = None
            self._model = None
            self.db_pool = None
            self.initialized = False
        LangchainService.initialize_bedrock_client()

    @classmethod
    async def get_instance(cls):
        """Get the singleton instance with proper initialization."""
        instance = cls()
        await instance.ensure_initialized()
        return instance

    async def ensure_initialized(self):
        """Ensure the singleton instance is properly initialized with thread safety."""
        if not self.initialized:
            async with self.creation_lock:
                if not self.initialized:  # Double-check locking
                    await self.initialize_all_resources()
                    self.initialized = True

    async def conversation(
        self, conversation_id: str, user_input: str, user_context: str | None = None
    ):
        # Ensure singleton is initialized
        await self.ensure_initialized()

        if not self.initialized or self.graph is None:
            raise Exception("Graph not initialized. Call initialize_graph() first.")

        # Check if checkpointer exists and log its type for debugging
        if self.checkpointer:
            logger.debug(f"Using checkpointer: {type(self.checkpointer)}")
        else:
            logger.error("Checkpointer is None during conversation call.")
            raise Exception("Checkpointer not available.")

        config = {"configurable": {"thread_id": conversation_id}}
        input_messages = [HumanMessage(content=user_input)]
        response = await self.graph.ainvoke(
            {"messages": input_messages, "user_context": user_context}, config=config
        )
        return response["messages"][-1]

    async def initialize_all_resources(self):
        try:
            self.initialize_model()
            await self.initialize_pool()
            await self.initialize_checkpointer()
            self.initialize_graph()
        except Exception as e:
            logger.error(f"Error initializing Langchain components: {e!s}")
            raise
        logger.info("Langchain components initialized successfully.")

    def initialize_model(
        self, model_id: str | None = None, model_provider: str | None = None
    ):
        self.model_id = model_id or settings.MODEL_ID
        self.model_provider = model_provider or settings.MODEL_PROVIDER
        try:
            self.initialize_bedrock_client()
            self._model = init_chat_model(
                model=self.model_id, model_provider=self.model_provider
            )
            logger.info(
                f"Model initialized: {self.model_id} with provider: {self.model_provider}"
            )
        except Exception as e:
            logger.error(f"Error initializing model: {e!s}")
            raise

    async def initialize_pool(self):
        if self.db_pool is None:
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
                self.db_pool = AsyncConnectionPool(
                    conninfo=conninfo_str,
                    max_size=20,
                    max_idle=60,
                    open=False,
                    kwargs=connection_kwargs,
                )
                await self.db_pool.open()
                logger.info("Database pool initialized.")
            except Exception as e:
                logger.error(f"Error initializing database pool: {e!s}")
                self.db_pool = None
                raise

    async def close_pool(self):
        if self.db_pool:
            try:
                await self.db_pool.close()
                self.db_pool = None
                logger.info("Database pool closed.")
            except Exception as e:
                logger.error(f"Error closing database pool: {e!s}")
        else:
            logger.info("No database pool to close.")

    async def initialize_checkpointer(self):
        if self.checkpointer is None and self.db_pool is not None:
            logger.info("Initializing checkpointer...")
            try:
                self.checkpointer = AsyncPostgresSaver(self.db_pool)
                await self.checkpointer.setup()
                logger.info("Checkpointer initialized.")
            except Exception as e:
                logger.error(f"Error initializing checkpointer: {e!s}")
                self.checkpointer = None
                raise

    def initialize_graph(self):
        """Initialize graph for singleton instance."""
        if self.graph is None:
            logger.info("Initializing graph...")
            workflow = StateGraph(state_schema=State)
            workflow.add_edge(START, "model")
            workflow.add_node("model", self.call_model)
            workflow.add_edge("model", END)
            self.graph = workflow.compile(checkpointer=self.checkpointer)
            logger.info("Graph initialized.")
        else:
            logger.info("Graph already initialized.")

    def call_model(self, state: State):
        """Call the model with the current state."""
        messages = state["messages"]
        user_context = state.get("user_context", None)
        prompt_template = generate_health_anxiety_prompt(user_context)

        # Invoke the prompt template with the state to get a formatted prompt
        formatted_prompt = prompt_template.invoke({"messages": messages})

        # Now pass the formatted prompt to the model
        response = self._model.invoke(formatted_prompt)
        logger.info(f"Model response: {response}")
        return {"messages": [response]}

    @staticmethod
    def initialize_bedrock_client():
        try:
            boto3.setup_default_session(
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
        except Exception as e:
            logging.error(f"Error initializing Bedrock client: {e!s}")
            raise
