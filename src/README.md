
需要安装npm环境运行前端，python环境运行后端，redis作为数据缓存支持后端运行

MCP服务
cd mcp
python main.py --host localhost --port 9000 --server-host localhost --server-port 9001 --embedded-server

Redis服务启动
redis-server

backend启动
cd backend
Python manage.py runserver 0.0.0.0:8000

frontend开发模式启动
cd frontend
npm run dev