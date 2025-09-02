from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 7861
    SPACE_ID: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()