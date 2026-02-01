import asyncio
import os
import sys
from mcp.server.fastmcp import FastMCP
from telegram import Bot

# Khởi tạo MCP Server
mcp = FastMCP("Telegram Bot")
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

@mcp.tool()
async def send_telegram_message(chat_id: str, text: str) -> str:
    """Gửi tin nhắn Telegram đến một Chat ID cụ thể."""
    if not TOKEN: return "Error: Missing TELEGRAM_BOT_TOKEN"
    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(chat_id=chat_id, text=text)
        return f"Sent to {chat_id}: {text}"
    except Exception as e:
        return f"Error sending telegram: {e}"

@mcp.tool()
async def get_telegram_updates() -> str:
    """Kiểm tra tin nhắn mới nhất (cơ chế polling đơn giản)."""
    if not TOKEN: return "Error: Missing TELEGRAM_BOT_TOKEN"
    try:
        bot = Bot(token=TOKEN)
        updates = await bot.get_updates(limit=5)
        if not updates: return "No new messages."
        
        result = []
        for u in updates:
            if u.message:
                result.append(f"[From {u.message.chat.id} - {u.message.chat.first_name}]: {u.message.text}")
        return "\n".join(result)
    except Exception as e:
        return f"Error reading updates: {e}"

if __name__ == "__main__":
    mcp.run()