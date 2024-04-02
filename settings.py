from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./icodes.db"
    OPENAI_API_KEY: str = ""


settings = Settings()
