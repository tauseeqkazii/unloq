
import os
try:
    from pydantic.v1 import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "UnloqAI Backend"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./dev.db"
    )
    API_KEY: str = os.getenv("API_KEY", "default_insecure_key_for_dev")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    LLM_PROVIDER: str = "ollama" # gemini | ollama
    LLM_MODEL: str = "qwen:0.5b" # Default model

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
