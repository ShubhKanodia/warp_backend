import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")  # Added for Sarvam.ai integration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///agentswarm.db")
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

# Agent Configuration
AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", "30"))  # seconds
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Sarvam.ai Configuration
SARVAM_MODEL = os.getenv("SARVAM_MODEL", "merchant-assistant")  # Default model for merchant operations
SARVAM_CONTEXT_WINDOW = int(os.getenv("SARVAM_CONTEXT_WINDOW", "4096"))
SARVAM_TEMPERATURE = float(os.getenv("SARVAM_TEMPERATURE", "0.7"))

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Test Configuration
TEST_MODE = os.getenv("TEST_MODE", "False").lower() == "true"
MOCK_GROQ = os.getenv("MOCK_GROQ", "False").lower() == "true"
MOCK_SARVAM = os.getenv("MOCK_SARVAM", "False").lower() == "true"  # Added for testing 