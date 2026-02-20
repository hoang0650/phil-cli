import typer
from rich.console import Console
from rich.table import Table
from rich.json import JSON
from typing import Optional, List
import json
import httpx
from pathlib import Path
from .config import load_config

app = typer.Typer(help="MCP (Model Context Protocol) management commands")
console = Console()

@app.command("list")
def list_mcp_servers(
    server_name: Optional[str] = typer.Argument(None, help="Tên server MCP cụ thể"),
    schema: bool = typer.Option(False, "--schema", "-s", help="Hiển thị schema của server")
):
    """Liệt kê các MCP servers đã cấu hình"""
    config = load_config()
    
    try:
        # Gọi API để lấy danh sách MCP servers
        response = httpx.get(
            f"{config['server_url']}/v1/mcp/servers",
            headers={"X-API-Key": config["api_key"]},
            timeout=10
        )
        
        if response.status_code != 200:
            console.print(f"[red]Lỗi khi lấy danh sách MCP servers: {response.status_code}[/red]")
            return
            
        servers = response.json()
        
        if server_name:
            # Hiển thị thông tin chi tiết của server cụ thể
            server = next((s for s in servers if s["name"] == server_name), None)
            if not server:
                console.print(f"[red]Không tìm thấy MCP server: {server_name}[/red]")
                return
                
            if schema:
                # Lấy schema của server
                schema_response = httpx.get(
                    f"{config['server_url']}/v1/mcp/servers/{server_name}/schema",
                    headers={"X-API-Key": config["api_key"]},
                    timeout=10
                )
                if schema_response.status_code == 200:
                    console.print(JSON.from_data(schema_response.json()))
                else:
                    console.print(f"[red]Không thể lấy schema: {schema_response.status_code}[/red]")
            else:
                console.print(JSON.from_data(server))
        else:
            # Hiển thị bảng tất cả servers
            table = Table(title="MCP Servers")
            table.add_column("Tên", style="cyan")
            table.add_column("Trạng thái", style="green")
            table.add_column("Loại", style="yellow")
            table.add_column("Mô tả", style="white")
            
            for server in servers:
                status = "🟢 Hoạt động" if server.get("connected") else "🔴 Ngắt kết nối"
                table.add_row(
                    server["name"],
                    status,
                    server.get("type", "stdio"),
                    server.get("description", "Không có mô tả")
                )
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[red]Lỗi: {str(e)}[/red]")

@app.command("call")
def call_mcp_tool(
    tool_selector: str = typer.Argument(..., help="Server.tool hoặc URL đầy đủ"),
    args: Optional[str] = typer.Argument(None, help="Arguments dạng key=value hoặc JSON"),
    args_file: Optional[Path] = typer.Option(None, "--args-file", help="File JSON chứa arguments"),
    stdio: bool = typer.Option(False, "--stdio", help="Sử dụng stdio transport"),
    command: Optional[str] = typer.Option(None, "--cmd", help="Lệnh cho stdio server")
):
    """Gọi một MCP tool"""
    config = load_config()
    
    # Parse arguments
    tool_args = {}
    if args_file:
        tool_args = json.loads(args_file.read_text())
    elif args:
        # Parse key=value format
        for arg in args.split():
            if "=" in arg:
                key, value = arg.split("=", 1)
                # Try to convert to appropriate type
                if value.lower() in ["true", "false"]:
                    tool_args[key] = value.lower() == "true"
                elif value.isdigit():
                    tool_args[key] = int(value)
                elif "." in value and value.replace(".", "").isdigit():
                    tool_args[key] = float(value)
                else:
                    tool_args[key] = value
    
    try:
        payload = {
            "tool": tool_selector,
            "arguments": tool_args,
            "stdio": stdio,
            "command": command
        }
        
        response = httpx.post(
            f"{config['server_url']}/v1/mcp/tools/call",
            headers={"X-API-Key": config["api_key"]},
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                console.print(JSON.from_data(result.get("result", {})))
            else:
                console.print(f"[red]Tool execution failed: {result.get('error', 'Unknown error')}[/red]")
        else:
            console.print(f"[red]HTTP Error: {response.status_code} - {response.text}[/red]")
            
    except Exception as e:
        console.print(f"[red]Lỗi khi gọi tool: {str(e)}[/red]")

@app.command("auth")
def auth_mcp_server(
    server_name: str = typer.Argument(..., help="Tên server hoặc URL"),
    reset: bool = typer.Option(False, "--reset", help="Reset authentication")
):
    """Xác thực với MCP server (OAuth/API Key)"""
    config = load_config()
    
    try:
        response = httpx.post(
            f"{config['server_url']}/v1/mcp/servers/{server_name}/auth",
            headers={"X-API-Key": config["api_key"]},
            json={"reset": reset},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                console.print(f"[green]✅ Xác thực thành công với {server_name}[/green]")
                if result.get("auth_url"):
                    console.print(f"Vui lòng truy cập: {result['auth_url']}")
            else:
                console.print(f"[red]❌ Xác thực thất bại: {result.get('error', 'Unknown error')}[/red]")
        else:
            console.print(f"[red]HTTP Error: {response.status_code}[/red]")
            
    except Exception as e:
        console.print(f"[red]Lỗi: {str(e)}[/red]")

@app.command("config")
def manage_mcp_config(
    action: str = typer.Argument(..., help="list|get|add|remove|import|login|logout"),
    server_name: Optional[str] = typer.Argument(None, help="Tên server (cho get/add/remove)"),
    config_file: Optional[Path] = typer.Option(None, "--file", help="File config để import"),
    server_type: str = typer.Option("stdio", "--type", help="Loại server: stdio|http|websocket"),
    command: Optional[str] = typer.Option(None, "--cmd", help="Lệnh khởi chạy (stdio)"),
    url: Optional[str] = typer.Option(None, "--url", help="URL endpoint (http/websocket)"),
    env_vars: Optional[str] = typer.Option(None, "--env", help="Biến môi trường: KEY1=val1,KEY2=val2")
):
    """Quản lý cấu hình MCP servers"""
    config = load_config()
    
    try:
        if action == "list":
            response = httpx.get(
                f"{config['server_url']}/v1/mcp/config",
                headers={"X-API-Key": config["api_key"]},
                timeout=10
            )
            if response.status_code == 200:
                console.print(JSON.from_data(response.json()))
        
        elif action == "get" and server_name:
            response = httpx.get(
                f"{config['server_url']}/v1/mcp/config/{server_name}",
                headers={"X-API-Key": config["api_key"]},
                timeout=10
            )
            if response.status_code == 200:
                console.print(JSON.from_data(response.json()))
        
        elif action == "add" and server_name:
            payload = {
                "name": server_name,
                "type": server_type,
                "command": command,
                "url": url,
                "env": {}
            }
            
            if env_vars:
                for env_pair in env_vars.split(","):
                    if "=" in env_pair:
                        key, value = env_pair.split("=", 1)
                        payload["env"][key] = value
            
            response = httpx.post(
                f"{config['server_url']}/v1/mcp/config",
                headers={"X-API-Key": config["api_key"]},
                json=payload,
                timeout=10
            )
            
            if response.status_code == 201:
                console.print(f"[green]✅ Đã thêm MCP server: {server_name}[/green]")
            else:
                console.print(f"[red]❌ Lỗi: {response.status_code} - {response.text}[/red]")
        
        elif action == "remove" and server_name:
            response = httpx.delete(
                f"{config['server_url']}/v1/mcp/config/{server_name}",
                headers={"X-API-Key": config["api_key"]},
                timeout=10
            )
            if response.status_code == 204:
                console.print(f"[green]✅ Đã xóa MCP server: {server_name}[/green]")
        
        elif action == "import" and config_file:
            config_data = json.loads(config_file.read_text())
            response = httpx.post(
                f"{config['server_url']}/v1/mcp/config/import",
                headers={"X-API-Key": config["api_key"]},
                json=config_data,
                timeout=10
            )
            if response.status_code == 201:
                console.print("[green]✅ Đã import cấu hình MCP[/green]")
        
        else:
            console.print("[red]Thiếu tham số. Xem --help để biết cách dùng.[/red]")
            
    except Exception as e:
        console.print(f"[red]Lỗi: {str(e)}[/red]")

@app.command("daemon")
def manage_mcp_daemon(
    action: str = typer.Argument(..., help="start|stop|restart|status"),
    port: int = typer.Option(8000, "--port", "-p", help="Port cho daemon"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="File config daemon")
):
    """Quản lý MCP daemon"""
    config = load_config()
    
    try:
        if action == "status":
            response = httpx.get(
                f"{config['server_url']}/v1/mcp/daemon/status",
                headers={"X-API-Key": config["api_key"]},
                timeout=10
            )
            if response.status_code == 200:
                status = response.json()
                console.print(f"[green]🟢 Daemon đang chạy[/green]" if status.get("running") else "[red]🔴 Daemon đã dừng[/red]")
                console.print(JSON.from_data(status))
        else:
            payload = {"action": action, "port": port}
            if config_file:
                payload["config"] = json.loads(config_file.read_text())
            
            response = httpx.post(
                f"{config['server_url']}/v1/mcp/daemon/{action}",
                headers={"X-API-Key": config["api_key"]},
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                console.print(f"[green]✅ Daemon {action} thành công[/green]")
            else:
                console.print(f"[red]❌ Lỗi: {response.status_code}[/red]")
                
    except Exception as e:
        console.print(f"[red]Lỗi: {str(e)}[/red]")

if __name__ == "__main__":
    app()