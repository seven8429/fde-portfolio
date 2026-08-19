"""
Week9 D3：问答链路封装 ask(query)
检索（RepRetriever）+ 拼业务 prompt + 调 DeepSeek + 返回 (answer, sources)
依赖：openai（llm-week 已装）、retriever.py（同目录）
"""
import os
from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from retriever import RepRetriever

retriever = RepRetriever()          # 加载索引（首次会加载模型，已缓存则离线）
TOP_K = 3

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先 source ~/.zshrc 或 export")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 业务人设：资深业代导师，只基于资料、不编造
SYSTEM = (
    "你是一名有 15 年快消行业经验的资深业代导师，专帮一线业代解决渠道政策、"
    "费用核销、客户拜访中的实际问题。只能根据下面提供的「资料」回答，"
    "资料里没有的内容就明确说「资料里没有提到」，不要编造政策数字或流程。"
    "回答要口语化、可操作，像师傅带徒弟一样给具体做法。"
)

def ask(query):
    hits = retriever.search(query, top_k=TOP_K)
    # 透明展示检索来源（RAG 可解释性）
    print("   📚 检索到：")
    for i, (s, src, _) in enumerate(hits, 1):
        print(f"      [{i}] 相似度={s:.4f}  {src}")
    context = "\n\n".join(
        f"【资料{i+1}｜来源：{src}】\n{txt}"
        for i, (_, src, txt) in enumerate(hits)
    )
    user_prompt = f"资料：\n{context}\n\n问题：{query}"
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": SYSTEM},
                      {"role": "user", "content": user_prompt}],
            temperature=0.3,
        )
        answer = resp.choices[0].message.content
        sources = [src for _, src, _ in hits]
        return answer, sources
    except (APITimeoutError, RateLimitError, APIError) as e:
        return f"⚠️ 调用 DeepSeek 出错：{e}", []

if __name__ == "__main__":
    #q = "陈列费核销需要什么材料？"
    q = "看不到门店"
    answer, sources = ask(q)
    print("\n===== 回答 =====")
    print(answer)
    print("\n参考来源：", sources)
