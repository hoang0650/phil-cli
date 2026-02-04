import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.spinner import Spinner
from .config import save_config, load_config
from .api import send_chat
import shutil
import os

app = typer.Typer(
    help="Phil AI CLI - Hệ thống AI Tự chủ Đa phương thức cho Doanh nghiệp",
    rich_markup_mode="rich"
)
console = Console()

@app.command()
def login(key: str = typer.Argument(..., help="API Key được cấp từ Dashboard"), 
          server: str = typer.Option("http://localhost:8080", help="URL của Phil Server")):
    """
    🔐 Đăng nhập vào hệ thống Phil AI.
    """
    try:
        save_config(api_key=key, server_url=server)
        console.print(f"[bold green]✅ Đăng nhập thành công![/bold green]")
        console.print(f"[dim]Server:[/dim] [cyan]{server}[/cyan]")
        console.print(f"[dim]Cấu hình đã được lưu tại ~/.phil_cli/config.json[/dim]")
    except Exception as e:
        console.print(f"[bold red]❌ Lỗi khi lưu cấu hình: {e}[/bold red]")

@app.command()
def status():
    """
    📊 Kiểm tra trạng thái kết nối và thông tin hệ thống.
    """
    config = load_config()
    if not config.get("api_key"):
        console.print("[yellow]⚠️ Bạn chưa đăng nhập. Hãy dùng lệnh `phil-cli login <key>`[/yellow]")
        return

    console.print("[bold cyan]🖥️ PHIL AI SYSTEM STATUS[/bold cyan]")
    console.print(f"• [bold]Server URL:[/bold] {config.get('server_url')}")
    console.print(f"• [bold]API Key:[/bold] {'*' * 10}{config.get('api_key')[-4:]}")
    
    with console.status("[yellow]Đang kiểm tra kết nối tới server...[/yellow]"):
        # Giả sử có endpoint /health
        try:
            import requests
            resp = requests.get(f"{config.get('server_url')}/v1/chat", timeout=5) # Thử gọi chat hoặc health
            if resp.status_code in [200, 405]: # 405 vì GET vào POST endpoint
                console.print("• [bold]Kết nối:[/bold] [green]Online[/green] ✅")
            else:
                console.print(f"• [bold]Kết nối:[/bold] [red]Lỗi ({resp.status_code})[/red] ❌")
        except Exception:
            console.print("• [bold]Kết nối:[/bold] [red]Offline[/red] ❌")

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