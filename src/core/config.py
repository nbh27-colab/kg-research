import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class AppSettings:
    """Application settings and constants."""
    
    # Default directories
    DEFAULT_EXTRACTED_DIR = "data/extracted"
    DEFAULT_MERGED_DIR = "data/merged"
    DEFAULT_VISUALIZATION_DIR = "data/visualizations"
    DEFAULT_URLS_DIR = "data/urls"
    
    # HTTP settings
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    DEFAULT_REQUEST_TIMEOUT = 30
    
    # Visualization settings
    DEFAULT_VIZ_HEIGHT = "750px"
    DEFAULT_VIZ_WIDTH = "100%"
    DEFAULT_PHYSICS_ENABLED = True
    
    # Logging settings
    DEFAULT_LOG_LEVEL = "INFO"
    LOG_FILE = None  # Set to path if you want file logging
    

class Config:
    """Configuration for OpenAI and LLM settings."""
    
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    LLM_MODEL_NAME_ANALYSIS: str = os.getenv("LLM_MODEL_NAME_ANALYSIS", "gpt-4o-mini")

    def __init__(self):
        self._validate_config()

    def _validate_config(self):
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables.")
        if not self.LLM_MODEL_NAME_ANALYSIS:
            raise ValueError("LLM_MODEL_NAME_ANALYSIS is not set in environment variables.")


# Singleton instances
app_config = Config()
app_settings = AppSettings()