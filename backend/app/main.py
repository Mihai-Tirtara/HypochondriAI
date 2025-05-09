import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.api.router_test import router_test
from app.config.config import settings
from app.services.llm import LangchainService

logging.basicConfig(
    level=settings.LOG_LEVEL.upper(),  # Use level from your config
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # You can also configure handlers, e.g., log to a file
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    logger.info("Running DB initialization...")
    try:
        # init_db()
        logger.info("DB initialization complete.")
    except Exception as e:
        logger.error(f"Error during database initilizations  {e}")

    logger.info("Initializing Langchain componenents...")
    try:
        await LangchainService.initialize_langchain_components()
        logger.info("Langchain components initialized successfully.")
    except Exception as e:
        logger.error(f"Error during Langchain initialization: {e}")
        # Set the class-level flag to indicate failure
        LangchainService._initialized = False


# Add or ensure the shutdown handler exists
@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Running application shutdown procedures...")
    # Close the LangchainService resources (specifically the pool)
    await LangchainService.close_pool()
    logger.info("Application shutdown complete.")


# Include the router
app.include_router(router)
app.include_router(router_test)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
