import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env (nếu có)
load_dotenv()

class Config:
    CODER_API_BASE = os.getenv("CODER_API_BASE", "http://llm-coder:8000/v1")
    VN_API_BASE = os.getenv("VN_API_BASE", "http://llm-vietnamese:8001/v1")
    VISION_API_BASE = os.getenv("VISION_API_BASE", "http://llm-vision:8002/v1")
    STT_API_URL = os.getenv("STT_API_URL", "http://stt-engine:8000/v1/audio/transcriptions")
    TTS_API_URL = os.getenv("TTS_API_URL", "http://tts-engine:8004/tts/to_audio")   
    API_KEY = os.getenv("API_KEY", "EMPTY")

    @staticmethod
    def validate():
        missing = []
        if not Config.CODER_API_BASE: missing.append("CODER_API_BASE")
        if not Config.VN_API_BASE: missing.append("VN_API_BASE")
        
        if missing:
            return False, f"Thiếu cấu hình môi trường quan trọng: {', '.join(missing)}"
        return True, "Cấu hình hợp lệ."

CODER_API_BASE = Config.CODER_API_BASE
VN_API_BASE = Config.VN_API_BASE
VISION_API_BASE = Config.VISION_API_BASE
STT_API_URL = Config.STT_API_URL
TTS_API_URL = Config.TTS_API_URL
API_KEY = Config.API_KEY

is_valid, msg = Config.validate()
if not is_valid:
    print(f"⚠️ CẢNH BÁO CONFIG: {msg}")
else:
    print(f"✅ Config Loaded. Brain Code connected to: {CODER_API_BASE}")