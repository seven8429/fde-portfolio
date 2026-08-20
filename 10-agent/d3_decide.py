"""
D3：让模型决定调用 + 我们执行工具（观察到「决策→执行」全链）
复用 D2 的真实 query_sales；重点在 json.loads 解析模型填的参数
依赖：openai、d2_query_sales.py（同目录）
"""
import os, json
from openai import OpenAI
from d2_query_sales import query_sales

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先 source ~/.zshrc")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 工具清单（和 D2 函数签名一致）
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

question = "华东区的总销量是多少？"
print("用户问：", question)

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": question}],
    tools=tools,
    tool_choice="auto",
)
msg = resp.choices[0].message

if msg.tool_calls:
    tc = msg.tool_calls[0]
    print("① 模型决定调用 →", tc.function.name)
    args = json.loads(tc.function.arguments)      # 模型返回的是 JSON 字符串，要解析
    print("② 填的参数 →", args)
    result = query_sales(args["region"])          # 你的代码（框架）来执行
    print("③ 工具执行结果 →", result)
else:
    print("模型没调工具，直接答：", msg.content)
