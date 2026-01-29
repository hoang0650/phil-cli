import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEFAULT_MODEL = os.getenv("SENTINEL_MODEL", "claude-3-5-sonnet-20240620")
    WORKSPACE_DIR = os.getenv("SENTINEL_WORKSPACE", os.getcwd())
    
    @staticmethod
    def validate():
        if not Config.ANTHROPIC_API_KEY and not Config.OPENAI_API_KEY:
            return False, "Vui lòng cấu hình ANTHROPIC_API_KEY hoặc OPENAI_API_KEY trong file .env"
        return True, ""
