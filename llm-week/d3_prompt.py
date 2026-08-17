import os
import pandas as pd
from openai import OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 读真实经销商数据（温习第5周 pandas），转成文本喂给模型
CSV = os.path.expanduser("~/fde/02-file/dealers.csv")
df = pd.read_csv(CSV).dropna(subset=["经销商"])
df["销量"] = df["销量"].astype(int)
data_text = df.to_string(index=False)

# —— 四要素都在这里 ——
system = """你是一名快消行业的区域销售顾问。
任务：根据提供的经销商销量数据，给出业务解读。
约束：
- 只用数据里的事实，不要编造数字
- 用 Markdown 表格输出，列：区域/销量/建议
- 用中文，口语化
示例输出格式：
1. 华南区销量最高（4000），是核心阵地；
2. 华北区（3600）紧追，建议加投；
3. 华东区（3200）偏低，需排查渠道。"""

#用 Markdown 表格输出，列：区域/销量/建议   #输出 3 条"洞察"，每条一句话
#system = ""

user = f"这是各经销商销量数据：\n{data_text}\n\n请按上面格式给出 3 条洞察。"

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": system},
        {"role": "user",   "content": user},
    ],
    temperature=0.7,
)
print(resp.choices[0].message.content)
