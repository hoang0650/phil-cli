import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".phil_config.json"

# URL Server mặc định (Thay bằng IP/Domain Server của bạn)
DEFAULT_SERVER_URL = "https://api.phil-ai.com" 

def load_config():
    if not CONFIG_PATH.exists():
        return {"server_url": DEFAULT_SERVER_URL, "api_key": None}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(api_key=None, server_url=None):
    config = load_config()
    if api_key: config["api_key"] = api_key
    if server_url: config["server_url"] = server_url
    
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)
    return config