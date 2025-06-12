import os
import json
import time
import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from aiohttp import web
from aiohttp.client import ClientSession, TCPConnector
from utils import validate_tool_request, format_message_for_logging
import argparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("mcp.client")

class MCPServerInfo:
    """MCP服务器信息类，存储服务器元数据和状态"""
    def __init__(self, server_data: Dict[str, Any]):
        self.id = server_data.get("id")
        self.host = server_data.get("host")
        self.port = server_data.get("port")
        self.tools = server_data.get("tools", [])
        self.status = server_data.get("status", "offline")
        self.last_heartbeat = server_data.get("last_heartbeat", 0)
        self.base_url = f"http://{self.host}:{self.port}"
    
    def has_tool(self, tool_name: str) -> bool:
        """检查服务器是否支持指定工具"""
        return any(tool.get("name") == tool_name for tool in self.tools)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，便于序列化"""
        return {
            "id": self.id,
            "host": self.host,
            "port": self.port,
            "tools": self.tools,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat
        }

class MCPClient:
    """MCP客户端服务，作为Agent与工具服务器的交互入口"""
    
    def __init__(self, host: str = "localhost", port: int = 9000):
        self.host = host
        self.port = port
        self.servers: Dict[str, MCPServerInfo] = {}
        self.running = False
        self.server = None
        self.session = None
        self.http_app = None
        self.health_check_task = None
        self.heartbeat_interval = 15  # 心跳检查间隔（秒）
        self.server_timeout = 45      # 服务器超时时间（秒）
        self.max_retries = 3          # 健康检查重试次数
    
    async def initialize(self):
        """初始化客户端资源，创建连接池和会话"""
        self.running = True
        # 配置连接池参数，防止资源耗尽
        connector = TCPConnector(
            limit=100,            # 最大连接数
            limit_per_host=20,      # 每个主机的最大连接数
            force_close=True,       # 请求后强制关闭连接
            enable_cleanup_closed=True  # 自动清理关闭的连接
        )
        self.session = ClientSession(connector=connector)
        logger.info(f"MCP Client initialized on http://{self.host}:{self.port}")
    
    async def close(self):
        """优雅关闭客户端资源，释放所有连接和任务"""
        self.running = False
        
        # 取消健康检查任务
        if self.health_check_task and not self.health_check_task.done():
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                logger.info("Health check task cancelled")
        
        # 关闭客户端会话
        if self.session:
            await self.session.close()
            self.session = None
        
        # 停止HTTP服务器
        if self.server:
            await self.server.stop()
            self.server = None
        
        # 清理HTTP应用
        if self.http_app:
            runner = self.http_app._runner
            if runner:
                await runner.cleanup()
            self.http_app = None
        
        logger.info("MCP Client resources closed")
    
    def register_server(self, server_data: Dict[str, Any]) -> bool:
        """注册工具服务器，记录基本信息并更新心跳"""
        server_id = server_data.get("id")
        if not server_id:
            logger.error("Server registration failed: missing server ID")
            return False
        
        server = MCPServerInfo(server_data)
        server.last_heartbeat = time.time()
        server.status = "online"
        self.servers[server_id] = server
        logger.info(f"Server registered: {server_id}, tools: {[t['name'] for t in server.tools]}")
        return True
    
    async def check_server_health(self):
        """检查所有服务器的健康状态，包含重试机制"""
        current_time = time.time()
        for server_id, server in list(self.servers.items()):
            # 检查超时
            if current_time - server.last_heartbeat > self.server_timeout:
                server.status = "offline"
                logger.warning(f"Server marked offline due to timeout: {server_id}")
                continue
            
            # 发送健康检查请求，包含重试逻辑
            success = False
            for retry in range(self.max_retries):
                try:
                    async with self.session.get(
                        f"{server.base_url}/health",
                        timeout=8,  # 适当延长超时时间
                        allow_redirects=False
                    ) as response:
                        if response.status == 200:
                            server.status = "online"
                            server.last_heartbeat = time.time()
                            success = True
                            break
                        else:
                            server.status = "offline"
                            logger.warning(f"Server health check failed (status {response.status}): {server_id}")
                except (asyncio.TimeoutError, ConnectionError) as e:
                    logger.warning(f"Health check retry {retry+1}/{self.max_retries} for {server_id}: {str(e)}")
                except Exception as e:
                    server.status = "offline"
                    logger.error(f"Unexpected error checking {server_id}: {str(e)}")
                    break
    
    async def periodic_health_check(self):
        """定期执行服务器健康检查的后台任务"""
        try:
            while self.running:
                await asyncio.sleep(self.heartbeat_interval)
                await self.check_server_health()
        except asyncio.CancelledError:
            logger.info("Periodic health check task cancelled")
        except Exception as e:
            logger.error(f"Health check task error: {str(e)}")
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取所有可用工具及其对应的服务器列表"""
        tools = {}
        for server in self.servers.values():
            if server.status != "online":
                continue
            for tool in server.tools:
                tool_name = tool.get("name")
                if tool_name:
                    if tool_name not in tools:
                        tools[tool_name] = {"name": tool_name, "servers": [server.id]}
                    else:
                        tools[tool_name]["servers"].append(server.id)
        return list(tools.values())
    
    def find_server_for_tool(self, tool_name: str) -> Optional[MCPServerInfo]:
        """根据工具名称查找可用的在线服务器"""
        for server in self.servers.values():
            if server.status == "online" and server.has_tool(tool_name):
                return server
        return None
    
    async def execute_tool(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具调用，转发请求到对应服务器并处理响应"""
        # 验证请求格式
        validation = validate_tool_request(request)
        if not validation["valid"]:
            return {
                "request_id": request.get("request_id", ""),
                "success": False,
                "error": validation["error"]
            }
        
        tool_name = request.get("tool_name")
        parameters = request.get("parameters", {})
        server = self.find_server_for_tool(tool_name)
        
        if not server:
            return {
                "request_id": request.get("request_id", ""),
                "success": False,
                "error": f"No online server available for tool: {tool_name}"
            }
        
        logger.info(f"Forwarding tool request to {server.id}: {tool_name}({parameters})")
        try:
            # 转发请求到服务器
            async with self.session.post(
                f"{server.base_url}/execute",
                json=request,
                timeout=60
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    return {
                        "request_id": request.get("request_id", ""),
                        "success": False,
                        "error": f"Server returned error ({response.status}): {error}"
                    }
                
                # 根据Content-Type处理响应
                content_type = response.headers.get('Content-Type', '')
                
                if 'text/event-stream' in content_type:
                    # 处理SSE格式响应
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data:'):
                            data = line[5:].strip()
                            try:
                                result = json.loads(data)
                                return result
                            except json.JSONDecodeError:
                                logger.error(f"Failed to parse SSE data: {data}")
                                return {
                                    "request_id": request.get("request_id", ""),
                                    "success": False,
                                    "error": "Failed to parse server response"
                                }
                    # 如果没有找到有效数据
                    return {
                        "request_id": request.get("request_id", ""),
                        "success": False,
                        "error": "Empty SSE response from server"
                    }
                else:
                    # 默认处理JSON响应
                    return await response.json()
                    
        except asyncio.TimeoutError:
            return {
                "request_id": request.get("request_id", ""),
                "success": False,
                "error": f"Tool execution timed out for {tool_name}"
            }
        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}", exc_info=True)
            return {
                "request_id": request.get("request_id", ""),
                "success": False,
                "error": str(e)
            }
    
    async def sse_response(self, request_id: str, data: Dict[str, Any]):
        """生成SSE格式的响应数据，返回字节数据"""
        sse_data = {"request_id": request_id, "data": data}
        return f"data: {json.dumps(sse_data)}\n\n".encode('utf-8')
    
    async def http_handler(self, request):
        """处理HTTP请求的入口函数，支持工具调用和服务器注册"""
        try:
            if request.method == 'POST' and request.path == '/execute':
                data = await request.json()
                logger.info(f"Received execute request: {format_message_for_logging(data)}")
                result = await self.execute_tool(data)
                response = web.StreamResponse(
                    status=200,
                    headers={"Content-Type": "text/event-stream", "Cache-Control": "no-cache"}
                )
                await response.prepare(request)
                await response.write(await self.sse_response(data.get("request_id"), result))
                await response.write_eof()
                return response
            
            elif request.method == 'POST' and request.path == '/register':
                server_data = await request.json()
                success = self.register_server(server_data)
                return web.json_response(
                    {"status": "success" if success else "error", 
                     "message": "Registration successful" if success else "Registration failed"}
                )
            
            elif request.method == 'GET' and request.path == '/health':
                return web.json_response({"status": "ok", "timestamp": time.time()})
            
            elif request.method == 'GET' and request.path == '/tools':
                return web.json_response(self.get_available_tools())
            
            elif request.method == 'GET' and request.path == '/servers':
                return web.json_response([s.to_dict() for s in self.servers.values()])
            
            return web.Response(text="Not Found", status=404)
        except Exception as e:
            logger.error(f"HTTP handler error: {str(e)}", exc_info=True)
            return web.json_response({"error": str(e)}, status=500)
    
    async def start(self):
        """启动客户端服务，包括HTTP服务器和后台任务"""
        await self.initialize()
        
        # 创建HTTP应用
        self.http_app = web.Application()
        self.http_app.router.add_route('*', '/{path:.*}', self.http_handler)
        
        # 启动HTTP服务器
        runner = web.AppRunner(self.http_app)
        await runner.setup()
        self.server = web.TCPSite(runner, self.host, self.port)
        await self.server.start()
        
        # 启动健康检查后台任务
        self.health_check_task = asyncio.create_task(self.periodic_health_check())
        
        logger.info(f"MCP Client started on http://{self.host}:{self.port}")
    
    async def stop(self):
        """优雅停止客户端服务，释放所有资源"""
        logger.info("Stopping MCP Client...")
        self.running = False
        await self.close()
        logger.info("MCP Client stopped")

# 主入口函数，支持命令行启动
async def main():
    parser = argparse.ArgumentParser(description='MCP Client Service')
    parser.add_argument('--host', type=str, default='localhost', help='Bind host')
    parser.add_argument('--port', type=int, default=9000, help='Bind port')
    args = parser.parse_args()
    
    client = MCPClient(host=args.host, port=args.port)
    try:
        await client.start()
        logger.info(f"Press Ctrl+C to stop the client")
        await asyncio.Future()  # 保持运行
    except KeyboardInterrupt:
        logger.info("Shutting down on user request")
    finally:
        await client.stop()

if __name__ == "__main__":
    asyncio.run(main())