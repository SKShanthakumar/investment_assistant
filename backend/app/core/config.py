from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    GROQ_API_KEY: str
    GOOGLE_API_KEY: str
    TAVILY_API_KEY: str
    DB_URI: str
    DB_URI_CHECKPOINTER: str
    MONGODB_URI: str
    MONGODB_DB_NAME: str
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_BASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
