import sys
import requests
import json
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

# Cấu hình Client (Người dùng sẽ trỏ về Server của bạn)
# Nếu bạn deploy server lên IP 1.2.3.4, thì thay localhost bằng IP đó
SERVER_URL = "http://localhost:8080/v1/chat" 
API_KEY = "phil_secret_key_123"

console = Console()

def main():
    console.print("[bold cyan]PHIL AI - REMOTE CLI[/bold cyan]")
    user_id = Prompt.ask("Enter your User ID", default="guest")

    while True:
        user_input = Prompt.ask(f"[green]{user_id}[/green]")
        if user_input.lower() in ['exit', 'quit']: break

        # Gửi request lên Server (Không xử lý tại máy này)
        try:
            with console.status("[bold green]Sending to Brain Cluster...[/bold green]"):
                payload = {
                    "user_input": user_input,
                    "user_id": user_id
                }
                headers = {"x-api-key": API_KEY}
                
                resp = requests.post(SERVER_URL, json=payload, headers=headers)
                
                if resp.status_code == 200:
                    data = resp.json()
                    console.print(Markdown(data['response']))
                else:
                    console.print(f"[red]Error {resp.status_code}: {resp.text}[/red]")
                    
        except Exception as e:
            console.print(f"[red]Connection failed: {e}[/red]")

if __name__ == "__main__":
    main()