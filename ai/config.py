import os
from dotenv import load_dotenv

load_dotenv()


class AIConfig:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    TOOL_CALL_MODEL = os.getenv("TOOL_CALL_MODEL", "llama-3.1-8b-instant")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    API_BASE_URL = os.getenv("API_BASE_URL", "")

    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 4096
    LLM_SUMMARY_MAX_TOKENS = 256
