import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self):
        self.sessions = {}
        self.tools = []

    async def connect_to_server(self, server_name, command, args):
        try:
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=None
            )
            
            # Note: In a real app, we'd keep the context open. 
            # This is a simplified version for the agent loop.
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_response = await session.list_tools()
                    for tool in tools_response.tools:
                        self.tools.append({
                            "server": server_name,
                            "name": tool.name,
                            "description": tool.description,
                            "input_schema": tool.inputSchema
                        })
            return True
        except Exception as e:
            print(f"Error connecting to MCP server {server_name}: {e}")
            return False

    def get_tools_for_anthropic(self):
        anthropic_tools = []
        for t in self.tools:
            anthropic_tools.append({
                "name": f"{t['server']}__{t['name']}",
                "description": t['description'],
                "input_schema": t['input_schema']
            })
        return anthropic_tools
