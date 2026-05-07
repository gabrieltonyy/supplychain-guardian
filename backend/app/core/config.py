from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.
    Loads values from environment variables and .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # =========================================
    # APPLICATION
    # =========================================
    APP_NAME: str = "SupplyChain Guardian"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str

    # =========================================
    # SERVER
    # =========================================
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # =========================================
    # DATABASE
    # =========================================
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    DATABASE_URL: str

    # =========================================
    # REDIS
    # =========================================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str

    # =========================================
    # QDRANT
    # =========================================
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "supplier_profiles"

    # =========================================
    # LLM CONFIG
    # =========================================
    LLM_PROVIDER: str = "ollama"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"

    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # =========================================
    # EXTERNAL DATA SOURCES
    # =========================================
    OPEN_METEO_BASE_URL: str

    GDELT_BASE_URL: str

    FINNHUB_API_KEY: str | None = None
    FINNHUB_BASE_URL: str

    SHIPBOB_API_KEY: str | None = None
    SHIPBOB_BASE_URL: str

    WITS_BASE_URL: str

    # =========================================
    # SENDGRID
    # =========================================
    SENDGRID_API_KEY: str | None = None
    SENDGRID_FROM_EMAIL: str = "procurement@scg.internal"

    # =========================================
    # SLACK
    # =========================================
    SLACK_BOT_TOKEN: str | None = None
    SLACK_APPROVAL_CHANNEL: str = "#procurement-approvals"

    # =========================================
    # APPROVAL THRESHOLDS
    # =========================================
    AUTO_APPROVAL_MAX_COST_DELTA: float = 25.0
    AUTO_APPROVAL_MIN_CONFIDENCE: float = 0.60
    AUTO_APPROVAL_MAX_RESIDUAL_RISK: float = 49.0
    AUTO_APPROVAL_MAX_ONBOARDING_WEEKS: int = 2

    # =========================================
    # CACHE TTLs
    # =========================================
    WEATHER_CACHE_TTL: int = 600
    FINANCIAL_CACHE_TTL: int = 14400
    LOGISTICS_CACHE_TTL: int = 1800
    GEOPOLITICAL_CACHE_TTL: int = 3600
    TARIFF_CACHE_TTL: int = 86400

    # =========================================
    # FEATURE FLAGS
    # =========================================
    MVP_MODE: bool = True
    ENABLE_EMAIL_DISPATCH: bool = False
    ENABLE_BACKGROUND_JOBS: bool = True
    ENABLE_VECTOR_SEARCH: bool = True

    # =========================================
    # LOGGING
    # =========================================
    LOG_LEVEL: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.
    Prevents reloading .env repeatedly.
    """
    return Settings()


settings = get_settings()