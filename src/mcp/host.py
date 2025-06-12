import os
import json
import time
import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from aiohttp import web

# 配置日志
logger = logging.getLogger("mcp.host")

class MCPHost:
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.servers: Dict[str, Dict[str, Any]] = {}  # 服务器ID -> 服务器信息
        self.tools: Dict[str, Dict[str, Any]] = {}    # 工具名称 -> 工具信息
        self.app = web.Application()
        self.runner = None
        self.site = None
        
        # 设置路由
        self.setup_routes()
        
    def setup_routes(self):
        """设置HTTP路由"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/tools', self.list_tools)
        self.app.router.add_post('/register', self.register_server)
        self.app.router.add_post('/execute', self.execute_tool)
        
    async def health_check(self, request):
        """健康检查端点"""
        return web.json_response({"status": "ok", "server_count": len(self.servers)})
    
    async def list_tools(self, request):
        """列出所有可用工具"""
        return web.json_response({
            "status": "success",
            "tools": list(self.tools.values())
        })
    
    async def register_server(self, request):
        """注册服务器和其提供的工具"""
        try:
            data = await request.json()
            server_id = data.get("server_id")
            server_url = data.get("url")
            server_tools = data.get("tools", [])
            
            if not server_id or not server_url:
                return web.json_response({"status": "error", "message": "Missing server_id or url"}, status=400)
            
            # 保存服务器信息
            self.servers[server_id] = {
                "id": server_id,
                "url": server_url,
                "last_seen": time.time(),
                "tools": set()
            }
            
            # 注册工具
            for tool in server_tools:
                tool_name = tool.get("name")
                if not tool_name:
                    continue
                
                self.tools[tool_name] = tool
                self.servers[server_id]["tools"].add(tool_name)
            
            logger.info(f"Server registered: {server_id}, tools: {list(self.servers[server_id]['tools'])}")
            return web.json_response({"status": "success"})
            
        except Exception as e:
            logger.error(f"Error registering server: {str(e)}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)
    
    async def execute_tool(self, request):
        """执行工具并返回SSE流"""
        try:
            data = await request.json()
            tool_name = data.get("tool_name")
            parameters = data.get("parameters", {})
            
            if not tool_name:
                return web.json_response({"status": "error", "message": "Missing tool_name"}, status=400)
            
            # 检查工具是否存在
            if tool_name not in self.tools:
                return web.json_response({"status": "error", "message": f"Tool not found: {tool_name}"}, status=404)
            
            # 查找提供此工具的服务器
            server_id = None
            for sid, server in self.servers.items():
                if tool_name in server["tools"]:
                    server_id = sid
                    break
            
            if not server_id:
                return web.json_response({"status": "error", "message": f"No server available for tool: {tool_name}"}, status=503)
            
            server_url = self.servers[server_id]["url"]
            logger.info(f"Executing tool {tool_name} on server {server_id}")
            
            # 转发请求到服务器并流式返回结果
            async def generate():
                try:
                    async with web.ClientSession() as session:
                        async with session.post(
                            f"{server_url}/execute",
                            json={"tool_name": tool_name, "parameters": parameters}
                        ) as response:
                            if response.status != 200:
                                error_data = await response.json()
                                yield f"data: {json.dumps({'type': 'error', 'content': error_data.get('message', 'Unknown error')})}\n\n"
                                return
                            
                            # 流式读取服务器响应并转发
                            async for line in response.content:
                                line = line.decode('utf-8').strip()
                                if line.startswith('data:'):
                                    data_str = line[5:].strip()
                                    yield f"data: {data_str}\n\n"
                    
                    # 发送完成信号
                    yield "data: {\"type\": \"done\"}\n\n"
                    
                except Exception as e:
                    logger.error(f"Error executing tool: {str(e)}")
                    yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            
            return web.Response(
                body=generate(),
                content_type='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Transfer-Encoding': 'chunked'
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling execute request: {str(e)}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)
    
    async def start(self):
        """启动MCP主机服务"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        logger.info(f"MCP Host started on {self.host}:{self.port}")
        
        # 启动定期检查服务器健康状态的任务
        asyncio.create_task(self.check_servers_health())
    
    async def stop(self):
        """停止MCP主机服务"""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("MCP Host stopped")
    
    async def check_servers_health(self):
        """定期检查服务器健康状态"""
        while True:
            await asyncio.sleep(30)  # 每30秒检查一次
            
            current_time = time.time()
            servers_to_remove = []
            
            for server_id, server in self.servers.items():
                # 如果服务器超过60秒未响应，标记为需要移除
                if current_time - server["last_seen"] > 60:
                    servers_to_remove.append(server_id)
            
            # 移除离线服务器
            for server_id in servers_to_remove:
                logger.warning(f"Removing offline server: {server_id}")
                
                # 移除服务器提供的工具
                for tool_name in self.servers[server_id]["tools"]:
                    if tool_name in self.tools:
                        del self.tools[tool_name]
                
                # 移除服务器
                del self.servers[server_id]