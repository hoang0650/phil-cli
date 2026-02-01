import os
import sys
import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.live import Live
from rich.spinner import Spinner

# Load environment & config
load_dotenv()
sys.path.append(os.getcwd())

from src.agent_graph import app_graph
from src.tools_audio import speak_text

console = Console()

def print_banner():
    console.print(Panel.fit(
        "[bold cyan]PHIL AI AGENT 1 (CLI EDITION)[/bold cyan]\n"
        "[dim]Sovereign Multimodal Intelligence System[/dim]",
        border_style="blue"
    ))

def process_input(user_input, iterations=0):
    inputs = {
        "user_input_vn": user_input,
        "image_url": None, # CLI cơ bản chưa hỗ trợ upload ảnh trực tiếp
        "iterations": iterations,
        "technical_plan": "", "code": "", "exec_result": ""
    }
    
    # Chạy Graph
    try:
        final_state = app_graph.invoke(inputs)
        return final_state['final_response_vn']
    except Exception as e:
        return f"System Error: {str(e)}"

def main():
    print_banner()
    console.print("[green]System initialized. Ready to serve.[/green]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold yellow]You[/bold yellow]")
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                console.print("[bold red]Shutting down systems... Goodbye![/bold red]")
                break
                
            if not user_input.strip():
                continue

            # Hiển thị trạng thái đang suy nghĩ
            with Live(Spinner("dots", text="[cyan]Phil is thinking & coding...[/cyan]"), refresh_per_second=10, transient=True):
                response = process_input(user_input)

            # In câu trả lời
            console.print(Panel(Markdown(response), title="[bold cyan]Phil AI[/bold cyan]", border_style="cyan"))
            
            # (Tùy chọn) Phát âm thanh nếu muốn CLI nói chuyện
            # audio_path = speak_text(response)
            # if audio_path:
            #     os.system(f"aplay {audio_path}" if sys.platform == "linux" else f"start {audio_path}")

        except KeyboardInterrupt:
            console.print("\n[bold red]Force Interrupted.[/bold red]")
            break

if __name__ == "__main__":
    main()