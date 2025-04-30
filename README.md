# tvos agent

1. 安装本地Python环境和npm环境，请根据项目的依赖信息安装react等package。

2. 安装本地reids环境并启动redis数据库。

   ```
   redis-server
   ```

   默认启动端口为6379，使用数据库id为0

3. 启动后端

   ```shell
   cd backend
   Python manage.py runserver 0.0.0.0:8000
   ```

   请开放本机8000端口给外部服务，启动0.0.0.0:8000即是为了外部局域网移动端可访问后端资源。

   视频播放文件请放在backend/media目录下并命名为test.mp4

4. 启动前端

   ```shell
   cd frontend
   npm run dev
   ```

   
