import os
import json
from openai import OpenAI
from openai import APIError, APITimeoutError, RateLimitError

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def chat(messages, temperature=0.3, json_mode=False):
    """统一的对话封装：成功返回模型回复字符串，失败返回 None"""
    kwargs = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": temperature,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    try:
        resp = client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content
    except APITimeoutError:
        print("⚠️ 请求超时")
        return None
    except RateLimitError:
        print("⚠️ 触发限流（额度/频率），稍后重试")
        return None
    except APIError as e:
        print(f"⚠️ API 错误: {e}")
        return None

# 用法1：普通问答
ans = chat([
    {"role": "system", "content": "你是快消行业顾问，回答简洁中文。"},
    {"role": "user",   "content": "一句话：华东和华南谁销量强？"},
])
print("问答:", ans)

# 用法2：JSON 模式 + 解析（温习 D4）
raw = chat(
    [
        {"role": "system", "content": '只输出 JSON: {"结论": <字符串>, "差距": <整数>}'},
        {"role": "user",   "content": "华东 6000，华南 7300，谁强、差多少？"},
    ],
    json_mode=True,
)
if raw:
    data = json.loads(raw)
    print("JSON 解析:", data)