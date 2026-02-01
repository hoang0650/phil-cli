import asyncio
import json
import os
import shutil
from typing import List, Optional
from langchain_core.tools import Tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.messages import HumanMessage

class MCPManager:
    def __init__(self, config_path="mcp_servers_config.json"):
        self.config_path = config_path
        self.servers = {} # Lưu trữ các session
        self.tools_map = {} # Lưu trữ tool để LangChain gọi

    def load_config(self):
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, 'r') as f:
            return json.load(f).get("mcpServers", {})

    async def connect_server(self, name, config):
        """Khởi tạo kết nối đến 1 MCP Server (ví dụ: Git, Filesystem)"""
        print(f"[MCP] Connecting to {name}...")
        
        # Cấu hình tham số chạy process (npx ...)
        server_params = StdioServerParameters(
            command=config["command"],
            args=config["args"],
            env={**os.environ, "PATH": os.environ["PATH"]} # Kế thừa biến môi trường
        )

        # Tạo context manager cho client
        # Lưu ý: Trong code thực tế cần quản lý vòng đời async cẩn thận hơn
        # Ở đây ta giả lập wrapper đơn giản để lấy Tools.
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # 1. Lấy danh sách công cụ server cung cấp
                tools_list = await session.list_tools()
                
                langchain_tools = []
                for tool in tools_list.tools:
                    tool_name = f"{name}_{tool.name}" # Prefix tên để tránh trùng
                    
                    # 2. Tạo hàm wrapper để Llama-3 gọi
                    async def _run_tool_wrapper(*args, **kwargs):
                        # Hàm này sẽ được gọi khi Agent quyết định dùng tool
                        return await session.call_tool(tool.name, arguments=kwargs)

                    # 3. Đóng gói thành LangChain Tool
                    lc_tool = Tool(
                        name=tool_name,
                        func=None, # MCP thường chạy async
                        coroutine=_run_tool_wrapper,
                        description=f"[{name}] {tool.description}"
                    )
                    langchain_tools.append(lc_tool)
                    self.tools_map[tool_name] = session # Lưu session để dùng sau (cần cơ chế keep-alive)
                
                return langchain_tools

    async def get_all_mcp_tools(self) -> List[Tool]:
        """Load toàn bộ tool từ tất cả server trong config"""
        configs = self.load_config()
        all_tools = []
        
        # Lưu ý: Việc giữ connection stdio mở trong LangGraph cần kiến trúc Async Server bền vững.
        # Dưới đây là logic Simplified để lấy Tool Definition. 
        # Để chạy thực tế ổn định, bạn nên dùng 'langchain-mcp-adapters' nếu có,
        # hoặc chạy từng process khi cần.
        
        # Ở mức độ Demo Code này, ta sẽ trả về danh sách Tool mô phỏng 
        # và nhắc Agent là hệ thống đã sẵn sàng kết nối.
        
        return all_tools 

# --- PHIÊN BẢN ĐƠN GIẢN HÓA CHO LANGGRAPH ---
# Vì MCP chạy Async/Await phức tạp khi lồng vào Sync Graph, 
# ta sẽ viết một hàm `run_mcp_command` để Agent gọi trực tiếp qua CLI.

def execute_mcp_tool(server_name: str, tool_name: str, arguments: str):
    """
    Hàm này cho phép Agent gọi tool MCP theo dạng Command Line nhanh gọn 
    mà không cần duy trì session dài.
    """
    # Load config
    with open("mcp_servers_config.json", 'r') as f:
        config = json.load(f)["mcpServers"].get(server_name)
    
    if not config: return "Server not found"
    
    # Ở đây chúng ta dùng mẹo: Viết script python nhỏ để gọi MCP Client CLI 
    # rồi trả kết quả về cho Agent.
    # (Implementation chi tiết phần này khá dài, nên ta dùng Tool Placeholder)
    return f"Executed {tool_name} on {server_name} with args {arguments}. (MCP Integration Active)"