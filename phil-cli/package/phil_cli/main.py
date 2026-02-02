import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.spinner import Spinner
from .config import save_config, load_config
from .api import send_chat
import shutil
import os

app = typer.Typer(help="Phil AI CLI - Trợ lý Lập trình Ảo")
console = Console()

@app.command()
def login(key: str, server: str = typer.Option(None, help="Custom Server URL")):
    """Đăng nhập bằng API Key"""
    save_config(api_key=key, server_url=server)
    console.print(f"[green]✅ Đăng nhập thành công! Key đã được lưu.[/green]")

@app.command()
def chat():
    """Bắt đầu phiên chat với Phil"""
    console.print("[bold cyan]🤖 PHIL AI AGENT - Sẵn sàng phục vụ[/bold cyan]")
    console.print("[dim]Gõ 'exit' để thoát.[/dim]\n")
    
    while True:
        user_input = Prompt.ask("[bold yellow]You[/bold yellow]")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        with console.status("[cyan]Phil đang suy nghĩ...[/cyan]", spinner="dots"):
            response = send_chat(user_input)
            
        if "error" in response:
            console.print(f"[red]❌ {response['error']}[/red]")
        else:
            # Hiển thị Markdown đẹp mắt
            console.print(Markdown(response.get("response", "")))
            console.print("-" * 50)

@app.command()
def fix(folder_path: str = ".", instruction: str = "Tìm lỗi và sửa giúp tôi"):
    """Gửi project (folder hiện tại) lên để Phil sửa"""
    if not os.path.exists(folder_path):
        console.print("[red]Thư mục không tồn tại![/red]")
        return

    # Nén folder thành zip
    with console.status("[yellow]Đang nén project...[/yellow]"):
        shutil.make_archive("temp_project", 'zip', folder_path)
        
    with console.status("[cyan]Đang gửi lên Server để phân tích...[/cyan]"):
        response = send_chat(instruction, project_zip_path="temp_project.zip")
        
    # Xóa file tạm
    os.remove("temp_project.zip")
    
    if "error" in response:
        console.print(f"[red]❌ {response['error']}[/red]")
    else:
        console.print(Markdown(response.get("response", "")))
        if "download_url" in response:
             console.print(f"[green]📦 Tải project đã sửa tại: {response['download_url']}[/green]")

def main():
    app()

if __name__ == "__main__":
    main()