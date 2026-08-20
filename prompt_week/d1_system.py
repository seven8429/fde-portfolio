"""
D1：System Prompt —— 给模型定「角色」和「边界」
核心认知：
  user 问的是"问题"，system 定的是"你是谁、该怎么答、不能做什么"。
  同一个 user 问题，system 不同，回答天差地别。
运行：python3 d1_system.py
"""
import os
from openai import OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先 source ~/.zshrc")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def ask(system, user, temp=0.7):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temp,
    )
    return resp.choices[0].message.content

# ---- 三个 system 预设，回答同一个问题 ----
PRESETS = {
    "裸问(无角色)": "你是一个有帮助的助手。",
    "角色+格式约束": "你是快消行业 15 年资深业务代表导师，只用大白话、结合一线实战经验回答，不超过 3 句话。",
    "角色+边界(防编造)": "你是快消行业资深业代导师。只基于你确知的行业常识回答；若遇到具体公司政策、数字、你不确定的人名，明确说「我不知道」，不要编造。",
}

if __name__ == "__main__":
    q = "我们公司想让经销商月底压货冲量，有什么风险？"
    for name, sys_p in PRESETS.items():
        print(f"\n===== system 预设：{name} =====")
        print(ask(sys_p, q))

if __name__ == "__main__":
    q = "华东区上个月经销商总销量是多少？"
    for name, sys_p in PRESETS.items():
        print(f"\n===== system 预设：{name} =====")
        print(ask(sys_p, q))

if __name__ == "__main__":
    q = "你是快消公司区域经理，正在面试我，用压力面试风格连问三个尖锐问题"
    for name, sys_p in PRESETS.items():
        print(f"\n===== system 预设：{name} =====")
        print(ask(sys_p, q))