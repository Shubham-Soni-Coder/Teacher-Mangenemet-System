from dotenv import load_dotenv
import os

from app.utils.json_loader import load_json

load_dotenv()


class Settings:
    # On Render, these values are read directly from the environment
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-secret-key-for-local-dev")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")

    @classmethod
    def validate_config(cls):
        """Simple check to alert you if keys are missing in production."""
        if os.getenv("RENDER") and not os.getenv("SECRET_KEY"):
            print("WARNING: SECRET_KEY is not set in Render environment!")

    # load the data
    JSON_DATA: dict = load_json()


settings = Settings()
