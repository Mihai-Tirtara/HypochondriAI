import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
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
        # Initialize singleton instance
        await LangchainService.get_instance()
        logger.info("Langchain singleton initialized successfully.")
    except Exception as e:
        logger.error(f"Error during Langchain initialization: {e}")
        raise

    yield

    # Cleanup singleton resources
    try:
        instance = await LangchainService.get_instance()
        await instance.close_pool()
    except Exception as e:
        logger.error(f"Error during Langchain cleanup: {e}")


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# Parse CORS origins from settings (comma-separated)
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include the router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
