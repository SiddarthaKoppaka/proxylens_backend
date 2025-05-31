import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Configuration settings for the application.
    """
    
    PROJECT_NAME: str = "RAG Backend"
    ENVIRONMENT: str = "development"

    # Add Tavily API Key to the settings model
    TAVILY_API_KEY: str

    # Enable .env file loading
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

# Initialize settings
settings = Settings()
