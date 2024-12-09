"""
App settings module
"""

import pathlib

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """
    Simplifies work with environment
    """

    APP_VERSION: str = "local"

    CONFIG_PATH: str = str(
        pathlib.Path(__file__).parent.parent.absolute() / "config.yml"
    )

    REDIS_ENDPOINT: str = "redis://:password@localhost:6379/0"

    BIND_HOST: str = "localhost"
    BIND_PORT: int = 8000

    DEBUG: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
