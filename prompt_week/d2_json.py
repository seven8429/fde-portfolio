"""
D2：输出格式约束 —— 让模型吐 JSON（把非结构化文本抽成结构化字段）
FDE 刚需：客户微信语音转文字、拜访记录、投诉邮件，都是乱文本，要变成能进库/能统计的字段。
两个关键技巧：
  1) 在 prompt 里写清楚"字段名 + 类型 + 含义 + 取值约束"
  2) 开 response_format={"type":"json_object"} 强制 JSON（DeepSeek 支持）
依赖：DEEPSEEK_API_KEY
"""
import os, json
from openai import OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先 source ~/.zshrc")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

SYSTEM = """你是快消行业的销售运营助手。
请把用户的原始记录抽取成结构化 JSON，严格只输出 JSON，不要任何解释文字。
字段定义：
  dealer   : 字符串，经销商名称
  region   : 字符串，区域（华东/华北/华南 之一，推断不出写「未知」）
  issue    : 字符串，问题类型（缺货/窜货/客诉/回款/其他 之一）
  urgency  : 字符串，紧急程度（高/中/低）
  summary  : 字符串，一句话摘要（不超过 30 字）
若某字段无法从文本得出，填 null。"""

def extract(text):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": text},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    raw = resp.choices[0].message.content
    return json.loads(raw)   # 解析失败会抛 JSONDecodeError，真实项目要 try/except 兜底

#SAMPLE = "老王反馈华东的杭州佰诚那边窜货严重，隔壁区便宜两块多，这事儿挺急的得尽快处理"
SAMPLE = "我今天去看了个店，感觉陈列不太行"
if __name__ == "__main__":
    data = extract(SAMPLE)
    print(json.dumps(data, ensure_ascii=False, indent=2))
