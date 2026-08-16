from fastapi import FastAPI

# 创建一个服务实例（uvicorn 后面就找这个 app 变量）
app = FastAPI(title="FDE 经销商分析服务")

# 访问根路径 http://localhost:8000/ 时返回
@app.get("/")
def root():
    return {"service": "fde-fast-api", "version": "0.1"}

# 访问 /health 时返回（健康检查接口，运维/部署常用）
@app.get("/health")
def health():
    return {"status": "ok", "msg": "服务正常运行"}