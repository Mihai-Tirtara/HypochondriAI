from fastapi import FastAPI
#from api.router import router
from config.config import settings
from core.db import init_db
import logging

logging.basicConfig(
    level=settings.LOG_LEVEL.upper(), # Use level from your config
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    # You can also configure handlers, e.g., log to a file
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Include the router
#app.include_router(router)

@app.on_event("startup")
def on_startup():
    logger.info("Running DB initialization...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"Error during DB initialization: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)