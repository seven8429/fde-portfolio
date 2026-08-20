"""
D5：多工具路由（Agent 学会在多个工具里选对的那个）
新增工具 top_dealers(n)：查销量最高的前 n 个经销商（不看区域）
关键：用「分发器 dispatch」按工具名路由到不同函数，而不是像 D4 那样写死 query_sales
依赖：openai、d2_query_sales.py（里面有 query_sales）
"""
import os, json
import sqlite3
from openai import OpenAI
from d2_query_sales import query_sales

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先 source ~/.zshrc")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

DB = os.path.expanduser("~/fde/04-db/sales.db")

# ---------- 新增工具 ②：top_dealers ----------
def top_dealers(n: int) -> str:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT 经销商, 销量 FROM dealers_csv ORDER BY 销量 DESC LIMIT ?", (n,))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return "数据库里没有经销商销量记录"
    lines = [f"{i+1}. {name}：{sales}" for i, (name, sales) in enumerate(rows)]
    return f"销量前 {n} 的经销商：\n" + "\n".join(lines)

# ---------- 工具清单（两个）----------
tools = [
    {
        "type": "function",
        "function": {
            "name": "query_sales",
            "description": "查询某个区域的经销商总销量",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "区域名，如 华东 / 华北 / 华南"}
                },
                "required": ["region"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "top_dealers",
            "description": "查询销量最高的前 n 个经销商（不看区域，看整体排名）",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "description": "返回前几名，例如 3"}
                },
                "required": ["n"],
            },
        },
    },
]

# ---------- 分发器：按工具名路由到对应函数 ----------
def dispatch(name, args):
    if name == "query_sales":
        return query_sales(args["region"])
    if name == "top_dealers":
        return top_dealers(args["n"])
    return f"未知工具：{name}"

# ---------- Agent 循环（只改「执行工具」那一行，其余同 D4）----------
def run_agent(question, max_steps=5):
    messages = [{"role": "user", "content": question}]
    for step in range(1, max_steps + 1):
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        msg = resp.choices[0].message

        if msg.tool_calls:
            print(f"\n[第 {step} 步] 模型决定调工具：")
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
                print(f"   → 执行 {tc.function.name}({args})")
                result = dispatch(tc.function.name, args)   # ← 路由到不同函数
                print(f"   ← 结果：{result}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })
            continue

        print(f"\n[第 {step} 步] 模型给出最终回答：")
        print(msg.content)
        return msg.content

    print("\n⚠️ 达到最大步数，强制结束（可能陷入循环）")
    return None

if __name__ == "__main__":
    run_agent("销量最高的前 3 个经销商是谁？")
    run_agent("华东区总销量多少？华南区呢？各差多少？")
    run_agent("销量前三的经销商分别属于哪个区域？")