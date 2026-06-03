from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    APP_ENV: str = "development"
    MONGODB_URL: str = os.getenv("MONGODB_URL", "")
    DB_NAME: str = "deepfake_db"
    MAX_IMAGE_SIZE_MB: int = 10
    MAX_VIDEO_SIZE_MB: int = 100
    UPLOAD_DIR: str = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        ),
        "uploads"
    )

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()