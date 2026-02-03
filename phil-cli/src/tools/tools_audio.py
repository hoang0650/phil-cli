import requests
import os
from src.config import STT_API_URL, TTS_API_URL

def transcribe_audio(file_path):
    """Chuyển giọng nói thành văn bản (STT)"""
    if not os.path.exists(file_path): return ""
    try:
        files = {
            'file': (os.path.basename(file_path), open(file_path, 'rb'), 'audio/wav'),
            'model': (None, 'large-v3')
        }
        # whisper server format
        res = requests.post(STT_API_URL, files=files)
        return res.json().get('text', "")
    except Exception as e:
        return f"[Error STT]: {e}"

def speak_text(text, output_file="workspace/reply.wav"):
    """Chuyển văn bản thành giọng nói (TTS)"""
    try:
        # Clone giọng từ file mẫu
        ref_wav = "inputs/reference_voice.wav"
        if not os.path.exists(ref_wav):
            return None # Cần file mẫu để clone

        params = {
            "text": text,
            "speaker_wav": ref_wav,
            "language": "vi"
        }
        # Lưu ý: API XTTS Server có thể nhận GET hoặc POST tùy version
        # Đây là ví dụ request POST chuẩn
        res = requests.post(TTS_API_URL, json=params)
        
        if res.status_code == 200:
            with open(output_file, "wb") as f:
                f.write(res.content)
            return output_file
        return None
    except Exception as e:
        print(f"[Error TTS]: {e}")
        return None