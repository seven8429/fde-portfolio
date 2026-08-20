"""
D1：Function Calling 最小示例 —— 观察模型"决定调哪个工具"
只演示"模型返回意图"，不执行函数（执行是 D2/D4 的事）
依赖：openai（llm-week 已装）
"""
import os
from openai import OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先 source ~/.zshrc")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 1) 给模型列工具清单（OpenAI 兼容格式）
tools = [{
    "type": "function",
    "function": {
        "name": "query_sales",
        "description": "查询某个区域的经销商总销量",
        "parameters": {
            "type": "object",
            "properties": {
                "region": {
                    "type": "string",
                    "description": "区域名，如 华东 / 华北 / 华南",
                }
            },
            "required": ["region"],
        },
    },
}]

# 2) 提问，让模型自己决定要不要调工具
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "华东区的总销量是多少？"}],
    tools=tools,
    tool_choice="auto",   # 让模型自己选：调或不调
)

msg = resp.choices[0].message
print("finish_reason:", resp.choices[0].finish_reason)
if msg.tool_calls:
    for tc in msg.tool_calls:
        print("模型决定调用 →", tc.function.name)
        print("参数 →", tc.function.arguments)   # JSON 字符串，如 {"region":"华东"}
else:
    print("模型没调工具，直接回答:", msg.content)
