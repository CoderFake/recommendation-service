import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseSettings, PostgresDsn, validator, Field


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Song Recommendation API"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # Environment
    ENVIRONMENT: str = Field("dev", env="ENVIRONMENT")

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @property
    def ENABLE_DOCS(self) -> bool:
        return self.ENVIRONMENT.lower() == "dev"

    # Database Configuration
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    SQLALCHEMY_ASYNC_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    @validator("SQLALCHEMY_ASYNC_DATABASE_URI", pre=True)
    def assemble_async_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        postgres_dsn = PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
        return str(postgres_dsn).replace("postgresql://", "postgresql+asyncpg://")

    # Database pool configuration
    DB_ECHO_LOG: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Firebase Authentication
    FIREBASE_AUTH_ENABLED: bool = True

    FIREBASE_SERVICE_ACCOUNT_KEY: Optional[str] = None

    FIREBASE_PROJECT_ID: str = "music-app-8d65c"
    FIREBASE_PRIVATE_KEY_ID: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    FIREBASE_CLIENT_EMAIL: str = ""
    FIREBASE_CLIENT_ID: str = ""
    FIREBASE_CLIENT_CERT_URL: str = ""

    # Firebase Web App Config
    FIREBASE_API_KEY: str = ""
    FIREBASE_AUTH_DOMAIN: str = ""
    FIREBASE_STORAGE_BUCKET: str = ""
    FIREBASE_MESSAGING_SENDER_ID: str = ""
    FIREBASE_APP_ID: str = ""

    # SoundCloud API
    SOUNDCLOUD_CLIENT_ID: str
    SOUNDCLOUD_API_BASE_URL: str = "https://api.soundcloud.com"

    # Recommendation System
    DEFAULT_NUM_RECOMMENDATIONS: int = 10
    COLLABORATIVE_WEIGHT: float = 0.7
    CONTENT_BASED_WEIGHT: float = 0.3
    REAL_TIME_BOOST_FACTOR: float = 1.2

    # Model training and update
    MODEL_TRAINING_FREQUENCY_HOURS: int = 24
    INCREMENTAL_LEARNING_ENABLED: bool = True
    MIN_INTERACTIONS_FOR_TRAINING: int = 100

    class Config:
        case_sensitive = True

        @classmethod
        def customise_sources(
                cls,
                init_settings,
                env_settings,
                file_secret_settings,
        ):
            app_env = os.environ.get("APP_ENV", "dev")
            env_file = f".env.{app_env}"

            print(f"Loading environment from {env_file}")

            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )

        env_file = ".env.dev"


app_env = os.environ.get("APP_ENV", "dev")
env_file = f".env.{app_env}"
os.environ["PYDANTIC_ENV_FILE"] = env_file
settings = Settings()