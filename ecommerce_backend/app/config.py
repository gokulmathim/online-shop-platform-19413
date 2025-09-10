import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


class Config:
    """Flask configuration loaded from environment variables."""

    # Core
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("FLASK_DEBUG", "0") in {"1", "true", "yes", "y", "on"}
    TESTING = os.getenv("FLASK_TESTING", "0") in {"1", "true", "yes", "y", "on"}

    # Secret key for session-related features (Flask & JWT)
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-env")

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # OpenAPI / Swagger via flask-smorest
    API_TITLE = os.getenv("API_TITLE", "E-commerce Backend API")
    API_VERSION = os.getenv("API_VERSION", "v1")
    OPENAPI_VERSION = os.getenv("OPENAPI_VERSION", "3.0.3")
    OPENAPI_URL_PREFIX = os.getenv("OPENAPI_URL_PREFIX", "/docs")
    OPENAPI_SWAGGER_UI_PATH = os.getenv("OPENAPI_SWAGGER_UI_PATH", "")
    OPENAPI_SWAGGER_UI_URL = os.getenv(
        "OPENAPI_SWAGGER_UI_URL",
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-env")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MIN", "60"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "7"))
    )
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_TYPE = os.getenv("JWT_HEADER_TYPE", "Bearer")

    # Database (from ecommerce_database)
    DATABASE_URL = os.getenv("DATABASE_URL")  # just for documentation

    # Payments (mock)
    PAYMENT_PROVIDER = os.getenv("PAYMENT_PROVIDER", "mock")
    PAYMENT_CURRENCY = os.getenv("PAYMENT_CURRENCY", "USD")
