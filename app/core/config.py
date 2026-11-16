from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "DataRakshak")
    environment: str = os.getenv("ENVIRONMENT", "development")

settings = Settings()
