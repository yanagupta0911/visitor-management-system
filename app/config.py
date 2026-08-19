import os
import secrets

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = "Visitor Management System"

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./visitor.db")

    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    CHECKIN_PHOTO_DIR = os.getenv("CHECKIN_PHOTO_DIR", "checkin_photos")
    CHECKOUT_PHOTO_DIR = os.getenv("CHECKOUT_PHOTO_DIR", "checkout_photos")
    MAX_PHOTO_SIZE_MB = int(os.getenv("MAX_PHOTO_SIZE_MB", "5"))
    ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

    ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
        ).split(",")
        if origin.strip()
    ]


settings = Settings()

if not os.getenv("SECRET_KEY"):
    print(
        "WARNING: SECRET_KEY is not set in the environment. Using a randomly "
        "generated key for this process only, so existing tokens will be "
        "invalidated on every restart. Set SECRET_KEY in a .env file "
        "(see .env.example) before deploying."
    )
