from fastapi import FastAPI
#from api.router import router
from config.config import settings
from core.db import create_db_and_tables

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Include the router
#app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    create_db_and_tables()
    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)