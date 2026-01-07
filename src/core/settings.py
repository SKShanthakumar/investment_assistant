from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    GROQ_API_KEY: str
    GOOGLE_API_KEY: str
    TAVILY_API_KEY: str
    DB_URI: str
    DB_URI_CHECKPOINTER: str

    class Config:
        env_file = ".env"

settings = Settings()
