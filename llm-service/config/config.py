from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Health Anxiety LLM Service"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "API for interacting with Amazon Bedrock for health anxiety responses"

    # API settings
    API_PREFIX: str = "/api/v1"
    API_HOST:str = "0.0.0.0"
    API_PORT: int = 8000
           
    # AWS settings
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "eu-central-1"
    
    # Bedrock settings
    MODEL_ID: str = "eu.meta.llama3-2-1b-instruct-v1:0"
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.3
    TOP_P: float = 0.4
    
    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USERNAME:  Optional[str] = None
    DB_PASSWORD:  Optional[str] = None
    DB_NAME: str = "health_anxiety"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()