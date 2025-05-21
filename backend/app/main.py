import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.api.router_test import router_test
from app.config.config import settings
from app.db.initial_setup import init_db
from app.services.llm import LangchainService

logging.basicConfig(
    level=settings.LOG_LEVEL.upper(),  # Use level from your config
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # You can also configure handlers, e.g., log to a file
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
        logger.info("DB initialization complete.")
    except Exception as e:
        logger.error(f"Error during database initilizations  {e}")
        raise

    try:
        await LangchainService.initialize_langchain_components()
        logger.info("Langchain components initialized successfully.")
    except Exception as e:
        logger.error(f"Error during Langchain initialization: {e}")
        LangchainService._initialized = False
        raise

    yield
    await LangchainService.close_pool()


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include the router
app.include_router(router)
app.include_router(router_test)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
