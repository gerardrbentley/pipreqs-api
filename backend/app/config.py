import functools
import logging
import os

from pydantic import BaseSettings


@functools.lru_cache()
def get_logger():
    return logging.getLogger("uvicorn")


log = get_logger()


class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "dev")
    testing: bool = os.getenv("TESTING", 0)


@functools.lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()
