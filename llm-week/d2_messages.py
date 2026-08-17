import os
from openai import OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先 export")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 多轮消息：system 定人设 + user 提问 + assistant 历史 + user 追问
messages = [
    {"role": "system",    "content": "你是一名资深快消行业数据分析师，回答简洁、用中文、带数据视角。"},
    {"role": "user",      "content": "华东区销量 6000，华南区 7300，哪个强？"},
    {"role": "assistant", "content": "华南区更强，销量 7300 比华东 6000 高约 21.7%。"},  # 伪造的历史，演示用
    {"role": "user",      "content": "那如果华东下季度涨到 7200 呢？"},
]

# 数值类任务把 temperature 调低，模型不会乱编
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    temperature=0.3,
)
print(resp)
print(resp.choices[0].message.content)
