from pydantic_settings import BaseSettings
from typing import Optional
from pydantic_core import MultiHostUrl
from typing_extensions import Self
from pydantic import PostgresDsn, computed_field


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Health Anxiety LLM Service"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "API for interacting with Amazon Bedrock for health anxiety responses"

    # API settings
    API_PREFIX: str = "/api/v1"
    API_HOST:str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Langsmith settings 
    #LANGSMITH_TRACING = "true"
    #LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"
    #LANGSMITH_API_KEY = "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"
    #LANGSMITH_PROJECT ="HyphochondriAI"
    
    # AWS settings
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "eu-central-1"
    
    # Bedrock settings
    MODEL_ID: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    MODEL_PROVIDER: str = "bedrock_converse"
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.3
    TOP_P: float = 0.4
    
    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USERNAME:  Optional[str] = None
    DB_PASSWORD:  Optional[str] = None
    DB_NAME: str = "health_anxiety"
    DB_SUPERUSER_USERNAME: Optional[str] = None
    DB_SUPERUSER_PASSWORD: Optional[str] = None
    DB_SUPERUSER_EMAIL: Optional[str] = None
        
    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql",
            username=self.DB_USERNAME,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        )
        params = {
        "pool_size": "20",
        "pool_pre_ping": "true",
        "connect_timeout": "10"
        }
        # Join parameters into a query string
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}?{query_string}"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()