import json
import os
from datetime import datetime

class SessionMemory:
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def _get_session_path(self, session_id: str):
        return os.path.join(self.storage_dir, f"{session_id}.json")

    def save_context(self, session_id: str, context: dict):
        path = self._get_session_path(session_id)
        data = self.load_context(session_id)
        data.append({
            "timestamp": datetime.now().isoformat(),
            "context": context
        })
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    def load_context(self, session_id: str) -> list:
        path = self._get_session_path(session_id)
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return []

    def clear_session(self, session_id: str):
        path = self._get_session_path(session_id)
        if os.path.exists(path):
            os.remove(path)

# Ví dụ sử dụng
# memory = SessionMemory("./workspace/sessions")