"""
Week9 D4/D5：多轮对话记忆（改进版，import 安全）
把 retriever / client 初始化移进 RepChat 内部，模块被 import 时不触发加载/强制 key
依赖：openai、retriever.py（同目录）
"""
import os
from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from retriever import RepRetriever

SYSTEM = (
    "你是一名有 15 年快消行业经验的资深业代导师，专帮一线业代解决渠道政策、"
    "费用核销、客户拜访中的实际问题。只能根据下面提供的「资料」回答，"
    "资料里没有的内容就明确说「资料里没有提到」，不要编造政策数字或流程。"
    "回答要口语化、可操作。如果用户的提问有指代或省略（比如「那特价的呢」），"
    "请结合前面的对话上下文理解他的真实意思。"
)

class RepChat:
    def __init__(self):
        self.retriever = RepRetriever()   # 首次会加载模型+索引（约5秒，需离线环境变量）
        self._client = None
        self.history = []                 # [(user_q, assistant_a)]

    def _client_or_raise(self):
        if self._client is None:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise RuntimeError("未找到 DEEPSEEK_API_KEY，请先 source ~/.zshrc 或 export")
            self._client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        return self._client

    def chat(self, query):
        hits = self.retriever.search(query, top_k=3)
        print("   📚 检索到：")
        for i, (s, src, _) in enumerate(hits, 1):
            print(f"      [{i}] 相似度={s:.3f}  {src}")
        context = "\n\n".join(
            f"【资料{i+1}｜来源：{src}】\n{txt}"
            for i, (_, src, txt) in enumerate(hits)
        )
        messages = [{"role": "system", "content": SYSTEM}]
        for q, a in self.history:
            messages.append({"role": "user", "content": q})
            messages.append({"role": "assistant", "content": a})
        messages.append({"role": "user", "content": f"资料：\n{context}\n\n问题：{query}"})
        try:
            resp = self._client_or_raise().chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.3,
            )
            answer = resp.choices[0].message.content
            self.history.append((query, answer))
            return answer, [src for _, src, _ in hits]
        except (APITimeoutError, RateLimitError, APIError) as e:
            return f"⚠️ 调用 DeepSeek 出错：{e}", []

if __name__ == "__main__":
    bot = RepChat()
    for q in ["陈列费核销需要什么材料", "那特价的呢", "这些材料去哪提交"]:
        print(f"\n=== 你问：{q} ===")
        answer, sources = bot.chat(q)
        print("助手：", answer)
        print("来源：", sources)
