import os
from typing import Optional

from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings

APP_ENV = os.getenv("APP_ENV", "dev")
env_file = ".env.test" if APP_ENV == "test" else ".env"
print(f"Using environment file: {env_file}")


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Health Anxiety LLM Service"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = (
        "API for interacting with Amazon Bedrock for health anxiety responses"
    )

    # API settings
    API_PREFIX: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # AWS settings
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
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
    DB_USERNAME: str | None = None
    DB_PASSWORD: str | None = None
    DB_NAME: str | None = None
    DB_SUPERUSER_USERNAME: str | None = None
    DB_SUPERUSER_PASSWORD: str | None = None
    DB_SUPERUSER_EMAIL: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:  # noqa: N802
        base_url = MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.DB_USERNAME,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        )
        # params = {"pool_pre_ping": "true", "connect_timeout": "10"}
        # Join parameters into a query string
        # query_string = "&".join(f"{k}={v}" for k, v in params.items())
        # return f"{base_url}?{query_string}"
        return base_url

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = env_file


settings = Settings()

print("-" * 20)
print(f"DEBUG (config.py): APP_ENV='{os.getenv('APP_ENV')}'")  # Check APP_ENV directly
print(
    f"DEBUG (config.py): Loading from env_file='{Settings.Config.env_file}'"
)  # Check which file it *thinks* it loaded
print(
    f"DEBUG (config.py): settings.DB_USERNAME = '{settings.DB_USERNAME}'"
)  # <-- Is this None?
print(
    f"DEBUG (config.py): settings.DB_PASSWORD = '{settings.DB_PASSWORD}'"
)  # <-- Is this None?
print(
    f"DEBUG (config.py): settings.SQLALCHEMY_DATABASE_URI = '{settings.SQLALCHEMY_DATABASE_URI}'"
)
print("-" * 20)
