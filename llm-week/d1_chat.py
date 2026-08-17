import os
from openai import OpenAI

# 从环境变量读 key（不写死，避免泄露/误提交）
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先在终端 export 你的 key")

# DeepSeek 兼容 OpenAI 协议，只改 base_url
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 发一次对话
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "用一句话解释什么是 FDE（Forward Deployed Engineer）"}
    ],
    temperature=0.7,
)

print("模型回复：")
print(resp)
print(resp.choices[0].message.content)
