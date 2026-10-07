from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY : str
    ALGORITHM : str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES : int = 30
    REFRESH_TOKEN_EXPIRE_DAYS : int = 7
    FRONT_END_URL : str = "http://localhost:5173"
    FRED_API_KEY : str = ""
    NEWS_API_KEY: str = ""
    OLLAMA_URL: str = "http://ollama:11434"
    MLFLOW_TRACKING_URI: str = "http://mlflow:5000"
    DATABASE_URL: str
    COOKIE_SECURE: bool = False

    class Config:
        env_file = ".env"

settings = Settings()

