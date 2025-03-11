import os
from typing import List
from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    # Thông tin cơ bản
    PROJECT_NAME: str = "Song Recommendation API"
    API_V1_STR: str = "/api"

    # Bảo mật
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "")
    OTP_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # Database chính (để đọc dữ liệu)
    MAIN_DB_HOST: str = os.getenv("MAIN_DB_HOST", "localhost")
    MAIN_DB_PORT: str = os.getenv("MAIN_DB_PORT", "5432")
    MAIN_DB_USER: str = os.getenv("MAIN_DB_USER", "postgres")
    MAIN_DB_PASS: str = os.getenv("MAIN_DB_PASS", "postgres")
    MAIN_DB_NAME: str = os.getenv("MAIN_DB_NAME", "music_service")
    MAIN_DB_URI: str = f"postgresql://{MAIN_DB_USER}:{MAIN_DB_PASS}@{MAIN_DB_HOST}:{MAIN_DB_PORT}/{MAIN_DB_NAME}"

    # Neo4j connection (dựa trên ERD và code base đã cung cấp)
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")

    # Database riêng cho service recommendation
    RECO_DB_HOST: str = os.getenv("RECO_DB_HOST", "localhost")
    RECO_DB_PORT: str = os.getenv("RECO_DB_PORT", "5432")
    RECO_DB_USER: str = os.getenv("RECO_DB_USER", "postgres")
    RECO_DB_PASS: str = os.getenv("RECO_DB_PASS", "postgres")
    RECO_DB_NAME: str = os.getenv("RECO_DB_NAME", "recommendation_service")
    RECO_DB_URI: str = f"postgresql://{RECO_DB_USER}:{RECO_DB_PASS}@{RECO_DB_HOST}:{RECO_DB_PORT}/{RECO_DB_NAME}"

    # Cấu hình đồng bộ dữ liệu
    SYNC_INTERVAL_MINUTES: int = 5
    REAL_TIME_SYNC_ENABLED: bool = True

    # Cấu hình thuật toán gợi ý
    DEFAULT_NUM_RECOMMENDATIONS: int = 10
    COLLABORATIVE_WEIGHT: float = 0.7
    CONTENT_BASED_WEIGHT: float = 0.3
    REAL_TIME_BOOST_FACTOR: float = 1.2

    # Cấu hình NCF và Incremental Learning
    USE_NCF: bool = os.getenv("USE_NCF", "true").lower() == "true"
    USE_INCREMENTAL_LEARNING: bool = os.getenv("USE_INCREMENTAL_LEARNING", "true").lower() == "true"
    MODEL_UPDATE_INTERVAL_MINUTES: int = int(os.getenv("MODEL_UPDATE_INTERVAL_MINUTES", "5"))
    BUFFER_SIZE: int = int(os.getenv("BUFFER_SIZE", "1000"))

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Kiểm tra thiếu cấu hình quan trọng
if not settings.API_SECRET_KEY:
    raise ValueError("API_SECRET_KEY phải được đặt trong biến môi trường")