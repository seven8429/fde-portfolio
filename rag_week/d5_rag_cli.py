"""
D5：最小可跑的 RAG 问答系统（命令行版）
把 D3 检索 + D4 生成串成持续问答循环，可直接收进 fde-portfolio
依赖：numpy、openai（llm-week 已装）、d3_retrieval.py（同目录）
"""
import os
from openai import OpenAI, APIError, APITimeoutError, RateLimitError
#from d3_retrieval import TfidfRetriever, DOC, INDEX_DIR
from embedding_retriever import EmbeddingRetriever, DOC, INDEX_DIR

# ---------- 1. 知识库 ----------
if os.path.exists(os.path.join(INDEX_DIR, "matrix.npy")):
    #retriever = TfidfRetriever.load(INDEX_DIR)
    retriever = EmbeddingRetriever.load(INDEX_DIR)
else:
    text = open(DOC, encoding="utf-8").read()
    retriever = TfidfRetriever().build(text)
    retriever.save(INDEX_DIR)
print(f"✅ 知识库就绪：{len(retriever.chunks)} 块\n")

# ---------- 2. 配置 ----------
TOP_K = 1
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先 source ~/.zshrc 或在终端 export")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

SYSTEM = ("你是一个严谨的答疑助手。只能根据下面提供的「资料」回答问题，"
          "资料里没有的内容，就明确说「资料中没有提到」，不要编造。")

# ---------- 3. 核心：检索 + 生成 ----------
def ask(query):
    hits = retriever.search(query, top_k=TOP_K)
    context = "\n\n".join(f"【资料{i+1}】\n{c}" for i, (_, c) in enumerate(hits))
    # 透明展示检索来源（RAG 可解释性）
    print("   📚 检索到：")
    for i, (s, c) in enumerate(hits, 1):
        print(f"      [{i}] 相似度={s:.3f}  {c.splitlines()[0][:34]}")
    user_prompt = f"资料：\n{context}\n\n问题：{query}"
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": SYSTEM},
                      {"role": "user", "content": user_prompt}],
            temperature=0.3,
        )
        return resp.choices[0].message.content
    except (APITimeoutError, RateLimitError, APIError) as e:
        return f"⚠️ 调用 DeepSeek 出错：{e}"

# ---------- 4. 问答循环 ----------
print("💬 RAG 问答已启动，输入问题回车提问，输入 exit 退出\n")
while True:
    try:
        query = input("你的问题> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n👋 退出")
        break
    if not query:
        continue
    if query.lower() == "exit":
        print("👋 退出")
        break
    print(ask(query))
    print()
