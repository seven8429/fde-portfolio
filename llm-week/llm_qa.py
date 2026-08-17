import os
import json
import pandas as pd
from openai import OpenAI
from openai import APIError, APITimeoutError, RateLimitError

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# —— 复用 D5 的 chat 封装 ——
def chat(messages, temperature=0.3, json_mode=False):
    kwargs = {"model": "deepseek-chat", "messages": messages, "temperature": temperature}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    try:
        return client.chat.completions.create(**kwargs).choices[0].message.content
    except (APITimeoutError, RateLimitError, APIError) as e:
        print(f"⚠️ 调用失败: {e}")
        return None

# —— 1) pandas 算指标（温习第5周）——
CSV = os.path.expanduser("~/fde/02-file/dealers.csv")
df = pd.read_csv(CSV).dropna(subset=["经销商"])
df["销量"] = df["销量"].astype(int)
region = df.groupby("区域")["销量"].sum().reset_index().sort_values("销量", ascending=False)
top = df.sort_values("销量", ascending=False).iloc[0]
total = int(df["销量"].sum())

stats_text = (f"总销量 {total}；销量冠军 {top['经销商']}({int(top['销量'])})；"
              f"各区域合计：\n" +
              "\n".join(f"  {r['区域']}: {int(r['销量'])}" for _, r in region.iterrows()))

# —— 2) 调 chat 做自然语言解读 + 结构化建议（温习 D3/D4）——
system = """你是快消行业区域销售顾问。基于给定销量数据，只输出 JSON：
{
  "解读": <字符串，2-3 句业务解读>,
  "建议": [<字符串数组，3 条可落地行动建议>]
}
不要输出 JSON 以外的任何文字。"""
user = f"经销商销量数据：\n{stats_text}"

raw = chat(
    [{"role": "system", "content": system}, {"role": "user", "content": user}],
    json_mode=True,
)

print("=== 销量统计 ===")
print(stats_text)
print("\n=== 模型解读与建议 ===")
if raw:
    data = json.loads(raw)
    print("解读:", data["解读"])
    for i, s in enumerate(data["建议"], 1):
        print(f"  {i}. {s}")
    out = os.path.expanduser("~/fde/llm-week/销量解读.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 已导出: {out}")
else:
    print("⚠️ 模型调用失败，但前面的 pandas 统计已正常输出")
