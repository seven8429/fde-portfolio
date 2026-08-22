"""
D1：把 AI Agent 包装成 HTTP 服务（FastAPI）—— 部署第一步：从「脚本」变「服务」
为什么关键：前面所有周都是命令行跑（python3 xxx.py）。
部署 = 让程序能被「网络请求」调用，前端/其他系统才能用。
复用：第7周 FastAPI 基础 + 第10周 Agent 的 run_agent 逻辑。

端点：
  GET  /health   健康检查（云平台用它判断服务是否活着，必备！）
  POST /agent    {"question": "华东区总销量多少？"} -> {"answer": "..."}

装包（你自己装）：pip install fastapi uvicorn
运行：
  cd ~/fde/12-deploy
  uvicorn d1_agent_api:app --reload --port 8000
测试（另开终端）：
  curl -X POST localhost:8000/agent -H 'Content-Type: application/json' -d '{"question":"华东区总销量多少？"}'
  浏览器开 http://localhost:8000/docs 看自动生成的接口文档
"""
import os, json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import sqlite3
from dotenv import load_dotenv

_env_path = os.path.expanduser("~/fde/fde-portfolio/.env")
load_dotenv(dotenv_path=_env_path, override=True) if os.path.exists(_env_path) else load_dotenv(override=True)

# ---------- 1) 基础设置 ----------
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise RuntimeError("❌ 未找到 DEEPSEEK_API_KEY，请先 export")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

DB = os.path.expanduser("~/fde/04-db/sales.db")

# ---------- 2) 工具（来自第10周，原样复用）----------
def query_sales(region: str) -> str:
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("SELECT SUM(销量) FROM dealers_csv WHERE 区域 = ?", (region,))
    total = cur.fetchone()[0]; conn.close()
    if total is None:
        return f"未找到区域「{region}」的销量数据"
    return f"{region}区经销商总销量：{total}"

def top_dealers(n: int) -> str:
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("SELECT 经销商, 销量 FROM dealers_csv ORDER BY 销量 DESC LIMIT ?", (n,))
    rows = cur.fetchall(); conn.close()
    return "、".join(f"{name}({vol})" for name, vol in rows)

TOOLS = [
  {"type":"function","function":{"name":"query_sales",
    "description":"查询某区域经销商总销量","parameters":{"type":"object","properties":{"region":{"type":"string","description":"区域名，如 华东"}},"required":["region"]}}},
  {"type":"function","function":{"name":"top_dealers",
    "description":"查询销量前 n 名的经销商","parameters":{"type":"object","properties":{"n":{"type":"integer","description":"返回前几名"}},"required":["n"]}}},
]

# ---------- 3) Agent 循环（来自第10周 D4）----------
def run_agent(question, max_steps=5):
    messages = [{"role":"user","content":question}]
    for step in range(1, max_steps+1):
        resp = client.chat.completions.create(model="deepseek-chat", messages=messages, tools=TOOLS, tool_choice="auto")
        msg = resp.choices[0].message
        if msg.tool_calls:
            messages.append({"role":"assistant","content":msg.content,"tool_calls":[
                {"id":tc.id,"type":"function","function":{"name":tc.function.name,"arguments":tc.function.arguments}} for tc in msg.tool_calls]})
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                fn = {"query_sales":query_sales,"top_dealers":top_dealers}[tc.function.name]
                result = fn(**args)
                messages.append({"role":"tool","tool_call_id":tc.id,"content":result})
            continue
        return msg.content
    return "⚠️ 达到最大步数，未完成"

# ---------- 4) 暴露成 HTTP 服务 ----------
app = FastAPI(title="FDE 销量分析 Agent API")

class Question(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/agent")
def agent(q: Question):
    if not q.question.strip():
        raise HTTPException(status_code=400, detail="question 不能为空")
    try:
        answer = run_agent(q.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"answer": answer}
