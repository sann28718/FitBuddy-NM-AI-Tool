from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    app_name: str = "FitBuddy"

    database_url: str = "sqlite:///./fitbuddy.db"

    gemini_api_key: str = ""

    workout_model: str = "gemini-3.8-flash"

    nutrition_model: str = "gemini-3.8-flash"

    admin_token: str = "change-this-token"


@lru_cache
def get_settings() -> Settings:

    return Settings(
        app_name=os.getenv(
            "APP_NAME",
            "FitBuddy"
        ),

        database_url=os.getenv(
            "DATABASE_URL",
            "sqlite:///./fitbuddy.db"
        ),

        gemini_api_key=os.getenv(
            "GEMINI_API_KEY",
            ""
        ),

        workout_model=os.getenv(
            "GEMINI_WORKOUT_MODEL",
            "gemini-3.8-flash"
        ),

        nutrition_model=os.getenv(
            "GEMINI_NUTRITION_MODEL",
            "gemini-3.8-flash"
        ),

        admin_token=os.getenv(
            "ADMIN_TOKEN",
            "change-this-token"
        ),
    )