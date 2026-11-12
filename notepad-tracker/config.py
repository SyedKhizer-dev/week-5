import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY", "development-secret-key")

    PROJECT_ROOT = Path(__file__).resolve().parent

    AUTOSAVE_DELAY_MS = int(os.getenv("AUTOSAVE_DELAY_MS", 2000))

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
