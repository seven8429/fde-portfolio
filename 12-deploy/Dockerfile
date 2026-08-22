FROM python:3.13-slim
WORKDIR /app

# 1) 先装依赖（放前面，依赖不变时 Docker 直接命中缓存层，不用重装）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) 再放应用代码
COPY d1_agent_api.py .

# 3) 声明容器监听的端口
EXPOSE 8000

# 4) 启动：host 必须 0.0.0.0，否则只能在容器内访问、宿主机连不上
CMD ["uvicorn", "d1_agent_api:app", "--host", "0.0.0.0", "--port", "8000"]
