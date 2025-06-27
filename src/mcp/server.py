import json
import asyncio
import aiohttp
import argparse
import time
import pandas as pd
from typing import Dict, Any, List, Optional, Callable
from utils import get_logger, generate_request_id, validate_mcp_request, format_message_for_logging

logger = get_logger("mcp.server")

class MCPServer:
    """MCP服务器实现，负责执行具体工具"""
    
    def __init__(self, host: str = "localhost", port: int = 8081, client_url: str = None):
        self.host = host
        self.port = port
        self.client_url = client_url
        self.tools = {}
        self.running = False
        self.app = None
        self.runner = None
        self.site = None
        
        # 注册内置工具
        self.register_tool("search_movies", self.search_movies)
        self.register_tool("calculate", self.calculate)
    
    def register_tool(self, name: str, func: Callable):
        """注册工具函数"""
        self.tools[name] = func
        logger.info(f"Tool registered: {name}")
    
    async def search_movies(self, query: str) -> List[Dict[str, Any]]:
        excel_file = pd.ExcelFile('movie.xlsx')
        # 获取指定工作表中的数据
        df = excel_file.parse('Sheet1')

        # 将票房列转换为数值类型
        df['票房数值'] = df['票房'].str.extract(r'(\d+\.?\d*)').astype(float)

        # 按照票房数值降序排序
        sorted_df = df.sort_values(by='票房数值', ascending=False)

        # 获取前 top_n 个影片
        top_n = 10
        top_movies = sorted_df.head(top_n)

        result = []
        for index, row in top_movies.iterrows():
            movie_info = {
                "id": index + 1,
                "title": row['title'],
                "票房": row['票房']
            }
            result.append(movie_info)

        return result
    
    async def calculate(self, expression: str) -> float:
        """模拟计算工具"""
        try:
            # 注意：实际应用中不应该直接使用eval，这里仅作演示
            return eval(expression)
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """执行工具并返回结果"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
        
        logger.info(f"Executing tool: {tool_name}, parameters: {format_message_for_logging(parameters)}")
        
        # 执行工具
        try:
            result = await self.tools[tool_name](**parameters)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def health_check(self, request):
        """健康检查端点"""
        return aiohttp.web.json_response({"status": "ok"})
    
    async def execute_handler(self, request):
        """处理工具执行请求"""
        try:
            data = await request.json()
            logger.info(f"Received execute request: {format_message_for_logging(data)}")
            
            # 验证请求格式
            validation = validate_mcp_request(data)
            if not validation["valid"]:
                return aiohttp.web.json_response(
                    {"status": "error", "message": validation["error"]},
                    status=400
                )
            
            tool_name = data.get("tool_name")
            parameters = data.get("parameters", {})
            # 关键：强制parameters为字典类型
            if not isinstance(parameters, dict):
                try:
                    parameters = json.loads(parameters)
                except (json.JSONDecodeError, TypeError):
                    logger.error(f"Invalid parameters type: {type(parameters)}")
                    return aiohttp.web.json_response(
                        {"status": "error", "message": "parameters must be a JSON object"},
                        status=400
                    )
            print(tool_name, parameters)
            
            # 执行工具
            result = await self.execute_tool(tool_name, parameters)
            
            # 构建大模型友好的响应格式
            response_data = {
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result.get("result", None),
                "success": result.get("success", False),
                "error": result.get("error", None)
            }
            
            # 使用SSE格式返回结果
            response = aiohttp.web.StreamResponse(
                status=200,
                reason='OK',
                headers={
                    'Content-Type': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                }
            )
            
            await response.prepare(request)
            
            # 发送结果
            await response.write(f"data: {json.dumps(response_data)}\n\n".encode())
            await response.write("data: {\"type\": \"done\"}\n\n".encode())
            
            await response.write_eof()
            return response
            
        except Exception as e:
            logger.error(f"Error handling execute request: {str(e)}")
            return aiohttp.web.json_response(
                {"status": "error", "message": str(e)},
                status=500
            )
    
    async def register_with_client(self):
        """向MCP Client注册此服务器"""
        if not self.client_url:
            logger.warning("No client URL provided, skipping registration")
            return
        
        try:
            tool_info = [{"name": name, "parameters": {} } for name in self.tools.keys()]
            server_info = {
                "id": f"{self.host}:{self.port}",
                "host": self.host,
                "port": self.port,
                "tools": tool_info,
                "status": "online",
                "last_heartbeat": time.time()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.client_url}/register", json=server_info) as response:
                    if response.status == 200:
                        logger.info("Successfully registered with MCP Client")
                    else:
                        logger.error(f"Failed to register with MCP Client: {response.status}")
        except Exception as e:
            logger.error(f"Error registering with MCP Client: {str(e)}")
    
    async def setup(self):
        """设置服务器"""
        self.running = True
        
        # 创建Web应用
        self.app = aiohttp.web.Application()
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/execute', self.execute_handler)
    
    async def start(self):
        """启动MCP服务器"""
        await self.setup()
        
        # 启动服务器
        self.runner = aiohttp.web.AppRunner(self.app)
        await self.runner.setup()
        self.site = aiohttp.web.TCPSite(runner=self.runner, host=self.host, port=self.port)
        await self.site.start()
        
        logger.info(f"MCP Server started on http://{self.host}:{self.port}")
        
        # 向Client注册
        await self.register_with_client()
    
    async def stop(self):
        """停止MCP服务器"""
        self.running = False
        if self.runner:
            await self.runner.cleanup()
        logger.info("MCP Server stopped")

async def main():
    parser = argparse.ArgumentParser(description='MCP Server')
    parser.add_argument('--host', type=str, default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8081, help='Server port')
    parser.add_argument('--client-url', type=str, help='MCP Client URL')
    
    args = parser.parse_args()
    
    server = MCPServer(
        host=args.host,
        port=args.port,
        client_url=args.client_url
    )
    
    await server.start()
    
    # 保持运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
