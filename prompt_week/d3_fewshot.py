"""
D3：few-shot 示例学习 —— 给几个例子，模型在陌生/难定义任务上立刻变准
对比 zero-shot(只给规则) vs few-shot(再给 2~3 个 input→output 样例)。
场景：把一线业代口语化的「客户异议」，映射到你们公司标准的异议编码。
这种"公司自定义编码"是文字说不清、但举例就懂的典型场景。

核心机制：few-shot 的样例就是 messages 里的 user/assistant 对，放在真实提问【之前】。
"""
import os
from openai import OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先 source ~/.zshrc")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 标准编码（文字能列，但边界模糊；举例最清楚）
SYSTEM = ("你是快消销售运营助手。标准异议编码："
         "O1 价格偏高 / O2 竞品更便宜 / O3 库存积压 / O4 账期回款 / O5 决策人不在。"
         "把客户异议映射到编码，只输出编码本身，不要解释。")

# few-shot：样例就是 user 提问 + assistant 标准答案，排在真实提问前
FEW_SHOT = [
    {"role": "user", "content": "客户说：你们这价也太贵了，比别家高不少"},
    {"role": "assistant", "content": "O1"},
    {"role": "user", "content": "客户说：隔壁竞品一箱便宜我三块，你这没法卖"},
    {"role": "assistant", "content": "O2"},
    {"role": "user", "content": "客户说：我仓库还堆着上批货呢，先不进"},
    {"role": "assistant", "content": "O3"},
]

def classify(text, few_shot=False):
    msgs = [{"role": "system", "content": SYSTEM}]
    if few_shot:
        msgs += FEW_SHOT
    msgs.append({"role": "user", "content": f"客户说：{text}"})
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=msgs,
        temperature=0,   # 分类任务要稳定，temperature 设 0
    )
    return resp.choices[0].message.content.strip()

if __name__ == "__main__":
    tests = [
        "你这价想涨就涨，当我冤大头啊",
        "上次说的返点啥时候到账，没返我不付款",
        "这事得我们老板拍板，我说了不算",
        "你们东西贵，而且隔壁还便宜三块",
    ]
    for t in tests:
        z = classify(t, few_shot=False)
        f = classify(t, few_shot=True)
        print(f"输入：{t}\n  zero-shot → {z}   |   few-shot → {f}\n")
