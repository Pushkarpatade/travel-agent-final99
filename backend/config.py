import os
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "TravelPilot Multi-Agent API"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"

    # API Keys
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = ""
    WEATHER_API_KEY: str = ""
    RESEND_API_KEY: str = ""

    # LangSmith Tracing & Observability
    LANGSMITH_TRACING: bool = True
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "travelpilot-multiagent"

    # Models & Config
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'travelpilot.db').replace('\\', '/')}"

    # Auth
    JWT_SECRET: str = "travelpilot-secret-jwt-key-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Automatically configure LangSmith environment variables for LangChain/LangGraph
if settings.LANGSMITH_API_KEY and settings.LANGSMITH_API_KEY.strip():
    os.environ["LANGCHAIN_TRACING_V2"] = "true" if settings.LANGSMITH_TRACING else "false"
    os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
    os.environ["LANGSMITH_TRACING"] = "true" if settings.LANGSMITH_TRACING else "false"
    os.environ["LANGSMITH_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
    os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
    os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT

def validate_api_keys():
    """Check API key presence and log clean status without exposing key values."""
    status = {
        "gemini": bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip()),
        "groq": bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip()),
        "tavily": bool(settings.TAVILY_API_KEY and settings.TAVILY_API_KEY.strip()),
        "langsmith": bool(settings.LANGSMITH_API_KEY and settings.LANGSMITH_API_KEY.strip()),
        "google_maps": bool(settings.GOOGLE_MAPS_API_KEY and settings.GOOGLE_MAPS_API_KEY.strip()),
        "weather": bool(settings.WEATHER_API_KEY and settings.WEATHER_API_KEY.strip()),
    }
    return status

def require_gemini_key():
    if not settings.GEMINI_API_KEY or not settings.GEMINI_API_KEY.strip():
        raise ValueError(
            "GEMINI_API_KEY is missing in your .env file! "
            "Please paste your Gemini API key in .env to use AI features."
        )

def require_tavily_key():
    if not settings.TAVILY_API_KEY or not settings.TAVILY_API_KEY.strip():
        raise ValueError(
            "TAVILY_API_KEY is missing in your .env file! "
            "Please paste your Tavily API key in .env to enable web search."
        )
