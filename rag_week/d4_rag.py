"""
D4：检索增强生成（RAG）核心 —— 检索 top_k 块 + 拼进 prompt 问 DeepSeek
学会点：
  1. 用 D3 的 TfidfRetriever 捞出最相关块
  2. 把块拼成「资料」塞进 user prompt，让 LLM 基于资料作答
  3. 调 DeepSeek（OpenAI 兼容 SDK），拿到有依据的回答
依赖：numpy、openai（llm-week 已装）、d3_retrieval.py（同目录）
"""
import os
from openai import OpenAI
#from d3_retrieval import TfidfRetriever, DOC, INDEX_DIR
from embedding_retriever import EmbeddingRetriever, DOC, INDEX_DIR

# ---------- 1. 加载知识库（直接读 D3 建好的索引，没有就现建）----------
if os.path.exists(os.path.join(INDEX_DIR, "matrix.npy")):
    #retriever = TfidfRetriever.load(INDEX_DIR)
    retriever = EmbeddingRetriever.load(INDEX_DIR)
else:
    text = open(DOC, encoding="utf-8").read()
    retriever = TfidfRetriever().build(text)
    retriever.save(INDEX_DIR)
print(f"知识库就绪：{len(retriever.chunks)} 块")

# ---------- 2. 检索 ----------
query = "第7周 FastAPI 主要学什么"
hits = retriever.search(query, top_k=3)
print(f"\n检索到 {len(hits)} 个相关块，拼进 prompt：")
for i, (score, chunk) in enumerate(hits, 1):
    print(f"  [{i}] 相似度={score:.3f}  {chunk.splitlines()[0][:36]}")

# ---------- 3. 拼 RAG prompt ----------
context = "\n\n".join(f"【资料{i+1}】\n{chunk}" for i, (_, chunk) in enumerate(hits))
system_prompt = (
    "你是一个严谨的答疑助手。只能根据下面提供的「资料」回答问题，"
    "资料里没有的内容，就明确说「资料中没有提到」，不要编造。"
)
user_prompt = f"资料：\n{context}\n\n问题：{query}"

# ---------- 4. 调 DeepSeek ----------
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DEEPSEEK_API_KEY，请先 source ~/.zshrc 或在终端 export")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
    temperature=0.3,
)
print("\n===== DeepSeek 回答 =====")
print(resp.choices[0].message.content)
