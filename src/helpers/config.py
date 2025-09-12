from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: str

    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int 
    FILE_MAX_CHUNK_SIZE: int

    MONGODB_URI: str
    MONGODB_DB_NAME: str

    
    class Config:
        env_file = ".env"

def get_settings():
    return Settings()