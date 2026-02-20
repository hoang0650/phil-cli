#!/usr/bin/env python3
"""
Phil-CLI Server Runner
Chạy FastAPI server cho Phil-CLI
"""

import uvicorn
from api_server import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)