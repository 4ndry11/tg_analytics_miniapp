from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # Bitrix24
    BITRIX24_DOMAIN: str
    BITRIX24_USER_ID: int
    BITRIX24_TOKEN_LEADS: str
    BITRIX24_TOKEN_USERS: str
    BITRIX24_TOKEN_STATUS: str
    BITRIX24_TOKEN_DEALS: str

    # Finmap
    FINMAP_API_KEY: str = ""
    FINMAP_COMPANY_ID: str = ""

    # Telegram
    TELEGRAM_BOT_TOKEN: str

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_CORS_ORIGINS: str = '["http://localhost:5173"]'

    # Redis (optional)
    REDIS_URL: str = ""

    # Environment
    ENVIRONMENT: str = "production"

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from JSON string"""
        try:
            return json.loads(self.API_CORS_ORIGINS)
        except:
            return ["http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
