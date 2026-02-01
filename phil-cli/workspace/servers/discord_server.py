import os
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Discord Bot")
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
BASE_URL = "https://discord.com/api/v10"

headers = {
    "Authorization": f"Bot {TOKEN}",
    "Content-Type": "application/json"
}

@mcp.tool()
def send_discord_message(channel_id: str, content: str) -> str:
    """Gửi tin nhắn vào kênh Discord."""
    if not TOKEN: return "Error: Missing DISCORD_BOT_TOKEN"
    
    url = f"{BASE_URL}/channels/{channel_id}/messages"
    payload = {"content": content}
    
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code in [200, 201]:
        return "Message sent successfully."
    return f"Error {res.status_code}: {res.text}"

@mcp.tool()
def read_discord_channel(channel_id: str, limit: int = 5) -> str:
    """Đọc tin nhắn gần nhất từ kênh."""
    if not TOKEN: return "Error: Missing DISCORD_BOT_TOKEN"
    
    url = f"{BASE_URL}/channels/{channel_id}/messages?limit={limit}"
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        msgs = res.json()
        result = []
        for m in msgs:
            result.append(f"[{m['author']['username']}]: {m['content']}")
        return "\n".join(result[::-1]) # Đảo ngược để xếp theo thời gian
    return f"Error: {res.text}"

if __name__ == "__main__":
    mcp.run()