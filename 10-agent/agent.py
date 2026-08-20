"""
agent.py —— 第10周综合作品：销量分析 Agent（可交互 CLI）
把 D1~D5 的东西收成一个能一直对话的程序。
相比 D5 的两点升级：
  1) 工具注册表（registry）：用 @tool 装饰器登记，新增工具不用改循环、不用写 if/elif
  2) 多轮：messages 在整个会话里一直累积，模型记得你前面问过啥（"那华北呢？"能接上）
运行：python3 agent.py   （退出输入 exit / quit）
"""
import os, json, sqlite3
from openai import OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先 source ~/.zshrc")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

DB = os.path.expanduser("~/fde/04-db/sales.db")

# ---------- ① 工具注册表 ----------
registry = {}

def tool(spec):
    """装饰器：把函数登记进 registry，并带上给模型的 JSON Schema"""
    def deco(fn):
        registry[fn.__name__] = {"fn": fn, "spec": spec}
        return fn
    return deco

@tool({
    "type": "function",
    "function": {
        "name": "query_sales",
        "description": "查询某个区域的经销商总销量",
        "parameters": {
            "type": "object",
            "properties": {"region": {"type": "string", "description": "区域名，如 华东 / 华北 / 华南"}},
            "required": ["region"],
        },
    },
})
def query_sales(region: str) -> str:
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("SELECT SUM(销量) FROM dealers_csv WHERE 区域 = ?", (region,))
    total = cur.fetchone()[0]; conn.close()
    if total is None:
        return f"未找到区域「{region}」的销量数据"
    return f"{region}区经销商总销量：{total}"

@tool({
    "type": "function",
    "function": {
        "name": "top_dealers",
        "description": "查询销量最高的前 n 个经销商（不看区域，看整体排名）",
        "parameters": {
            "type": "object",
            "properties": {"n": {"type": "integer", "description": "返回前几名，例如 3"}},
            "required": ["n"],
        },
    },
})
def top_dealers(n: int) -> str:
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("SELECT 经销商, 销量 FROM dealers_csv ORDER BY 销量 DESC LIMIT ?", (n,))
    rows = cur.fetchall(); conn.close()
    if not rows:
        return "数据库里没有经销商销量记录"
    lines = [f"{i+1}. {name}：{sales}" for i, (name, sales) in enumerate(rows)]
    return f"销量前 {n} 的经销商：\n" + "\n".join(lines)

# 从注册表生成给模型的 tools 列表
def get_tools():
    return [v["spec"] for v in registry.values()]

# 分发：直接拿名字去注册表里查函数（D5 的 if/elif 升级成查表）
def dispatch(name, args):
    entry = registry.get(name)
    if not entry:
        return f"未知工具：{name}"
    return entry["fn"](**args)

# ---------- ② Agent 循环（一次回答，内部可能多步调工具）----------
def run_agent(messages, max_steps=5):
    for step in range(1, max_steps + 1):
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=get_tools(),
            tool_choice="auto",
        )
        msg = resp.choices[0].message

        if msg.tool_calls:
            print(f"\n[第 {step} 步] 模型调工具：")
            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [{
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                } for tc in msg.tool_calls],
            })
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                print(f"   → {tc.function.name}({args})")
                result = dispatch(tc.function.name, args)
                print(f"   ← {result}")
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            continue

        print(f"\n[第 {step} 步] 回答：\n{msg.content}")
        messages.append({"role": "assistant", "content": msg.content})
        return

    print("\n⚠️ 达到最大步数，强制结束（可能陷入循环）")

# ---------- ③ 交互式 CLI（多轮，messages 一直累积）----------
def main():
    print("🤖 销量分析 Agent（输入 exit / quit 退出）")
    messages = []
    while True:
        try:
            q = input("\n你> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye"); break
        if not q:
            continue
        if q.lower() in ("exit", "quit", "退出"):
            print("bye"); break
        messages.append({"role": "user", "content": q})
        run_agent(messages)

if __name__ == "__main__":
    main()
