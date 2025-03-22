import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file if it exists
load_dotenv()

class Settings:
    # Basic application settings
    APP_NAME = "AI EVM Agent"
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./evm_agent.db")
    DATABASE_DIR = os.getenv("DATABASE_DIR", "./data")
    DATABASE_FILENAME = os.getenv("DATABASE_FILENAME", "evm_agent.db")
    
    # API settings
    API_PREFIX = "/api/v1"
    
    # EVM settings
    EVM_DEFAULT_THRESHOLD = float(os.getenv("EVM_DEFAULT_THRESHOLD", "0.1"))  # 10% threshold for variances
    
    # AI/ML settings
    MODEL_PATH = os.getenv("MODEL_PATH", "./models")
    
    # Integration settings
    JIRA_URL = os.getenv("JIRA_URL", "")
    JIRA_USERNAME = os.getenv("JIRA_USERNAME", "")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
    
    MS_PROJECT_INTEGRATION = os.getenv("MS_PROJECT_INTEGRATION", "False").lower() in ("true", "1", "t")
    SAP_INTEGRATION = os.getenv("SAP_INTEGRATION", "False").lower() in ("true", "1", "t")
    
    # Data ingestion settings
    DATA_IMPORT_BATCH_SIZE = int(os.getenv("DATA_IMPORT_BATCH_SIZE", "100"))
    
    # NLG settings
    NLG_DEFAULT_CONFIDENCE_THRESHOLD = float(os.getenv("NLG_CONFIDENCE_THRESHOLD", "0.7"))

# Create settings instance
settings = Settings()
