"""
D4：思维链 CoT + 防幻觉（RAG 式「只基于资料」硬约束）
1) CoT：复杂推理/计算任务，让模型「一步步思考」再给答案，准确率明显提升
2) 防幻觉：给资料 + 硬约束「只基于以下资料，没有就说不知道」，模型就不会编
运行：python3 d4_cot_ground.py
"""
import os
from openai import OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先 source ~/.zshrc")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def reason(question, cot=False):
    sys_p = "你是快消销售分析助手。"
    if cot:
        sys_p += "请一步步思考（chain of thought），写出推理过程，再给最终答案。"
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": question}],
        temperature=0,
    )
    return resp.choices[0].message.content

def grounded(question, context, strict=True):
    sys_p = "你是知识库问答助手。"
    if strict:
        sys_p += "只基于下面提供的「资料」回答；资料里没有的信息，明确说「资料未提及」，不要编造。"
    prompt = f"资料：\n{context}\n\n问题：{question}"
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": prompt}],
        temperature=0,
    )
    return resp.choices[0].message.content

if __name__ == "__main__":
    # --- CoT 对比 ---
    q = "华东销量3200、华北3600、华南4000。若公司要求明年整体增长10%，明年总目标是多少？请给出计算过程。"
    print("===== 无 CoT =====")
    print(reason(q, cot=False))
    print("\n===== 有 CoT（一步步思考）=====")
    print(reason(q, cot=True))

    # --- 防幻觉对比 ---
    ctx = "公司规定：单笔促销费用超过5万元需大区总监审批；陈列费核销需提供带日期的现场照片。"
    q2 = "单笔促销费用超过多少需要总裁审批？"
    print("\n===== 防幻觉：宽松（可能瞎编）=====")
    print(grounded(q2, ctx, strict=False))
    print("\n===== 防幻觉：严格（应说资料未提及）=====")
    print(grounded(q2, ctx, strict=True))
