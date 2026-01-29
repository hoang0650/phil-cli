import os
import sys
import json
import asyncio
from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from .config import Config
from .sandbox import Sandbox
from .mcp_client import MCPClient

console = Console()

class SentinelAgent:
    def __init__(self):
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.sandbox = Sandbox()
        self.mcp = MCPClient()
        self.history = []
        self.system_prompt = """Bạn là Sentinel, một AI Agent mạnh mẽ và bảo mật chạy trên Terminal.
Nhiệm vụ của bạn là giúp người dùng thực hiện các tác vụ từ lập trình đến quản lý hệ thống.
Bạn có quyền truy cập vào một sandbox an toàn để thực thi lệnh shell.

QUY TẮC BẢO MẬT:
1. Luôn thực thi code trong sandbox.
2. Nếu người dùng yêu cầu lệnh nguy hiểm (xóa file hệ thống, v.v.), hãy cảnh báo và yêu cầu xác nhận.
3. Giữ cho phản hồi ngắn gọn và tập trung vào kết quả.
"""

    def is_dangerous(self, command):
        dangerous_patterns = ["rm -rf", "sudo", "> /dev/sda", "mkfs", "dd if="]
        return any(pattern in command for pattern in dangerous_patterns)

    def run_shell(self, command):
        if self.is_dangerous(command):
            console.print(f"[bold yellow]CẢNH BÁO:[/bold yellow] Lệnh này có thể gây nguy hiểm: [bold red]{command}[/bold red]")
            confirm = console.input("Bạn có chắc chắn muốn chạy không? (y/n): ")
            if confirm.lower() != 'y':
                return "Lệnh đã bị hủy bởi người dùng."

        console.print(f"[bold blue]Executing:[/bold blue] {command}")
        output, exit_code = self.sandbox.execute(command)
        return f"Exit Code: {exit_code}\nOutput:\n{output}"

    def chat(self, user_input):
        self.history.append({"role": "user", "content": user_input})
        
        # Base tools
        tools = [
            {
                "name": "run_shell",
                "description": "Thực thi lệnh shell trong môi trường sandbox an toàn.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Lệnh shell cần chạy"}
                    },
                    "required": ["command"]
                }
            }
        ]
        
        # Add MCP tools if any
        tools.extend(self.mcp.get_tools_for_anthropic())

        while True:
            response = self.client.messages.create(
                model=Config.DEFAULT_MODEL,
                max_tokens=4096,
                system=self.system_prompt,
                messages=self.history,
                tools=tools
            )

            has_tool_use = False
            for content in response.content:
                if content.type == "text":
                    console.print(Markdown(content.text))
                    self.history.append({"role": "assistant", "content": content.text})
                
                if content.type == "tool_use":
                    has_tool_use = True
                    tool_name = content.name
                    tool_input = content.input
                    tool_use_id = content.id
                    
                    if tool_name == "run_shell":
                        result = self.run_shell(tool_input["command"])
                    elif "__" in tool_name:
                        # MCP Tool handling (simplified)
                        result = f"MCP Tool {tool_name} called with {tool_input}. (MCP execution requires active server connection)"
                    else:
                        result = "Unknown tool"
                        
                    self.history.append({
                        "role": "assistant",
                        "content": [content]
                    })
                    self.history.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": result
                            }
                        ]
                    })
            
            if not has_tool_use:
                break

def main():
    valid, msg = Config.validate()
    if not valid:
        console.print(f"[bold red]Error:[/bold red] {msg}")
        return

    agent = SentinelAgent()
    console.print(Panel("[bold green]Sentinel-CLI is ready.[/bold green]\nType 'exit' to quit.", title="Sentinel Agent"))
    
    while True:
        try:
            user_input = console.input("[bold cyan]>>> [/bold cyan]")
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                break
            agent.chat(user_input)
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")

if __name__ == "__main__":
    main()
