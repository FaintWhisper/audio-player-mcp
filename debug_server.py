import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions

# Redirect all stdout buffering
sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')
# Force stderr for logging
sys.stderr.reconfigure(encoding='utf-8')

async def main():
    server = Server("test")
    
    async with stdio_server() as (read, write):
        await server.run(
            read,
            write,
            InitializationOptions(
                server_name="test",
                server_version="1.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())