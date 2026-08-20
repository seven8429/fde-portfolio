"""
D4：Agent 循环（完整闭环）
模型 → 调函数 → 结果回传(role=tool) → 模型总结 → 如需再调就继续，直到给出最终回答
依赖：openai、d2_query_sales.py（同目录）
"""
import os, json
from openai import OpenAI
from d2_query_sales import query_sales

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先 source ~/.zshrc")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

tools = [{
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
}]

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

        # 情况 A：模型还要调工具
        if msg.tool_calls:
            print(f"\n[第 {step} 步] 模型决定调工具：")
            # ① 把模型的"意图"原样记进对话历史（含 tool_calls）
            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [{
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                } for tc in msg.tool_calls],
            })
            # ② 逐个执行工具，把结果以 role=tool 回传（tool_call_id 要对上）
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                print(f"   → 执行 {tc.function.name}({args})")
                result = query_sales(args["region"])
                print(f"   ← 结果：{result}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })
            continue   # 带着工具结果再问一次模型

        # 情况 B：模型不再调工具，给出最终回答
        print(f"\n[第 {step} 步] 模型给出最终回答：")
        print(msg.content)
        return msg.content

    print("\n⚠️ 达到最大步数，强制结束（可能陷入循环）")
    return None

if __name__ == "__main__":
    run_agent("华东区的总销量是多少？")
