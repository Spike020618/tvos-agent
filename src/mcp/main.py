import os
import sys
import json
import argparse
import asyncio
import logging
from typing import Dict, Any, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mcp.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("mcp.main")

async def start_client(host: str = "localhost", port: int = 8080):
    """启动MCP客户端服务"""
    from client import MCPClient
    client = MCPClient(host=host, port=port)
    await client.start()
    return client

async def start_server(host: str = "localhost", port: int = 8081, client_url: str = None):
    """启动MCP服务器"""
    from server import MCPServer
    server = MCPServer(host=host, port=port, client_url=client_url)
    await server.start()
    return server

async def main():
    parser = argparse.ArgumentParser(description='MCP Service')
    parser.add_argument('--host', type=str, default='localhost', help='Client host address')
    parser.add_argument('--port', type=int, default=8080, help='Client port')
    parser.add_argument('--server-host', type=str, default='localhost', help='Server host address')
    parser.add_argument('--server-port', type=int, default=8081, help='Server port')
    parser.add_argument('--embedded-server', action='store_true', help='Start embedded server')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    
    args = parser.parse_args()
    
    # 加载配置文件（如果提供）
    config = {}
    if args.config and os.path.exists(args.config):
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {args.config}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
    
    # 合并命令行参数和配置文件
    client_host = args.host or config.get("client_host", "localhost")
    client_port = args.port or config.get("client_port", 8080)
    server_host = args.server_host or config.get("server_host", "localhost")
    server_port = args.server_port or config.get("server_port", 8081)
    embedded_server = args.embedded_server or config.get("embedded_server", False)
    
    # 启动MCP客户端服务
    logger.info(f"Starting MCP Client on {client_host}:{client_port}")
    client = await start_client(host=client_host, port=client_port)
    
    # 启动嵌入式服务器（如果需要）
    server = None
    if embedded_server:
        client_url = f"http://{client_host}:{client_port}"
        logger.info(f"Starting embedded MCP Server on {server_host}:{server_port}, registering with {client_url}")
        server = await start_server(
            host=server_host,
            port=server_port,
            client_url=client_url
        )
    
    # 保持运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down MCP service...")
        if server:
            await server.stop()
        await client.stop()
        logger.info("MCP service stopped")

if __name__ == "__main__":
    asyncio.run(main())
