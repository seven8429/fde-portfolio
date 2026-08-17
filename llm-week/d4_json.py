import os
import json
import pandas as pd
from openai import OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先 export")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

CSV = os.path.expanduser("~/fde/02-file/dealers.csv")
df = pd.read_csv(CSV).dropna(subset=["经销商"])
df["销量"] = df["销量"].astype(int)
data_text = df.to_string(index=False)

# system 里直接规定输出 JSON 的字段结构
system = """你是一名快消行业销售顾问。
请基于给定数据，输出 JSON（不要任何多余文字，只输出 JSON）。
字段要求：
{
  "总销量": <整数>,
  "销量冠军": {"经销商": <字符串>, "销量": <整数>},
  "建议": [<字符串数组，3 条行动建议>]
}"""

user = f"各经销商销量数据：\n{data_text}"

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": system},
        {"role": "user",   "content": user},
    ],
    temperature=0.3,
    response_format={"type": "json_object"},   # ← 强制 JSON 输出
)

# 模型返回的是 JSON 字符串，用 json.loads 转成字典
raw = resp.choices[0].message.content
print("模型原始返回：")
print(raw)

data = json.loads(raw)        # 字符串 → 字典
print("\n解析后（可直接当数据用）：")
print("总销量:", data["总销量"])
print("销量冠军:", data["销量冠军"]["经销商"], data["销量冠军"]["销量"])
print("建议条数:", len(data["建议"]))
for i, s in enumerate(data["建议"], 1):
    print(f"  {i}. {s}")

json.dumps(data, ensure_ascii=False, indent=2)