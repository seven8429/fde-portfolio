"""
D5：提示词实验室（Prompt Lab）—— 把 D1~D4 收成一个可交互 CLI
可以切换不同「预设 system」，实时试 prompt，看每种技巧的效果。
预设：
  base      基础助手（无技巧）
  role      角色 + 边界（D1）
  json      JSON 结构化抽取（D2）
  fewshot   示例学习分类（D3）
  cot       思维链推理（D4）
  rag       防幻觉：只基于资料（D4）
命令（在「你>」后输入）：
  !preset <名字>   切换预设
  !ctx <文本>      给 rag 预设设置资料（其他预设忽略）
  exit / quit      退出
运行：python3 d5_prompt_lab.py
"""
import os, json
from openai import OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先 source ~/.zshrc")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

PRESETS = {
    "base":    {"system": "你是一个有帮助的助手。", "json": False, "ctx": False},
    "role":    {"system": "你是快消行业 15 年资深业务代表导师。只基于确知的行业常识回答；"
                         "遇到具体公司政策、数字、不确定的人名，明确说「我不知道」，不要编造。"
                         "回答用大白话，不超过 3 句话。", "json": False, "ctx": False},
    "json":    {"system": "你是销售运营助手。把记录抽成 JSON，只输出 JSON。字段："
                         "dealer(经销商名), region(华东/华北/华南/未知), issue(缺货/窜货/客诉/回款/其他), "
                         "urgency(高/中/低), summary(≤30字)。推断不出填 null。", "json": True, "ctx": False},
    "fewshot": {"system": "你是销售运营助手。标准异议编码：O1价格偏高/O2竞品更便宜/O3库存积压/O4账期回款/O5决策人不在。"
                         "映射到编码，只输出编码。", "json": False, "ctx": False,
                "shots": [("客户说：你们这价也太贵了，比别家高不少", "O1"),
                          ("客户说：隔壁竞品一箱便宜我三块", "O2"),
                          ("客户说：我仓库还堆着上批货呢", "O3")]},
    "cot":     {"system": "你是快消销售分析助手。复杂问题请一步步思考（chain of thought），"
                         "写出推理过程，再给最终答案。", "json": False, "ctx": False},
    "rag":     {"system": "你是知识库问答助手。只基于下面「资料」回答；资料没有的信息明确说「资料未提及」，不要编造。",
                "json": False, "ctx": True},
}

def chat(system, user, *, use_json=False, shots=None):
    msgs = [{"role": "system", "content": system}]
    if shots:
        for q, a in shots:
            msgs.append({"role": "user", "content": q})
            msgs.append({"role": "assistant", "content": a})
    msgs.append({"role": "user", "content": user})
    kwargs = {"model": "deepseek-chat", "messages": msgs, "temperature": 0}
    if use_json:
        kwargs["response_format"] = {"type": "json_object"}
    return client.chat.completions.create(**kwargs).choices[0].message.content

def main():
    print("🧪 提示词实验室（输入 !preset / !ctx / exit）")
    name = "base"; ctx = ""; preset = PRESETS[name]
    print(f"当前预设：{name}（!preset 可切换：{', '.join(PRESETS)}）")
    while True:
        try:
            line = input("\n你> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye"); break
        if not line:
            continue
        if line.lower() in ("exit", "quit"):
            print("bye"); break
        if line.startswith("!preset "):
            n = line[8:].strip()
            if n in PRESETS:
                name, preset = n, PRESETS[n]
                print(f"已切换预设：{name}")
            else:
                print(f"未知预设，可选：{', '.join(PRESETS)}")
            continue
        if line.startswith("!ctx "):
            ctx = line[5:].strip()
            print(f"已设置资料：{ctx[:40]}...")
            continue
        user = line
        if preset["ctx"]:
            if not ctx:
                print("⚠️ 当前是 rag 预设，请先用 !ctx <资料> 设置资料")
                continue
            user = f"资料：\n{ctx}\n\n问题：{user}"
        try:
            ans = chat(preset["system"], user, use_json=preset["json"], shots=preset.get("shots"))
        except Exception as e:
            ans = f"❌ 调用出错：{e}"
        print(f"\n[{name}] {ans}")

if __name__ == "__main__":
    main()
