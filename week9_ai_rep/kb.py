"""
Week9 D1：把 knowledge/ 下的 .md 切块 + 向量化建索引（复用 bge 语义模型）
依赖：sentence-transformers（已装）；首次需模型权重（你已缓存，离线即可）
"""
import os, glob, json
import numpy as np
from sentence_transformers import SentenceTransformer

KNOWLEDGE_DIR = os.path.expanduser("~/fde/week9_ai_rep/knowledge")
INDEX_DIR = os.path.expanduser("~/fde/week9_ai_rep/index")
MODEL_NAME = "BAAI/bge-small-zh-v1.5"
QUERY_INSTRUCTION = "为这个句子生成表示以用于检索相关文章："

model = SentenceTransformer(MODEL_NAME)   # 权重已缓存，离线加载

def chunk_by_heading(text):
    chunks, cur = [], []
    for line in text.splitlines():
        if line.startswith("#") and cur:
            chunks.append("\n".join(cur).strip()); cur = []
        cur.append(line)
    if cur:
        chunks.append("\n".join(cur).strip())
    return [c for c in chunks if len(c) > 20]

def split_long(text, max_chars=400, overlap=60):
    """超长块再按字符窗口切，确保每块不超 embedding 模型 token 上限（bge=512）"""
    if len(text) <= max_chars:
        return [text]
    pieces, start = [], 0
    while start < len(text):
        end = start + max_chars
        pieces.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap          # 留重叠，避免切断语义
    return pieces

def load_knowledge():
    docs = []
    for path in sorted(glob.glob(os.path.join(KNOWLEDGE_DIR, "*.md"))):
        name = os.path.basename(path)
        text = open(path, encoding="utf-8").read()
        for c in chunk_by_heading(text):
            for piece in split_long(c):        # ← 超长块再切
                docs.append({"source": name, "text": piece})
    return docs

def build():
    docs = load_knowledge()
    texts = [d["text"] for d in docs]
    embs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    matrix = np.array(embs)
    os.makedirs(INDEX_DIR, exist_ok=True)
    np.save(os.path.join(INDEX_DIR, "matrix.npy"), matrix)
    with open(os.path.join(INDEX_DIR, "docs.json"), "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False)
    print(f"建索引完成：{len(docs)} 块，来自 {len(set(d['source'] for d in docs))} 个文档")
    # 自检验索可用
    q = model.encode([QUERY_INSTRUCTION + "陈列费核销需要什么材料"], normalize_embeddings=True)[0]
    scores = matrix @ q
    top = np.argsort(-scores)[:2]
    print("检索自检：", [(docs[i]["source"], round(float(scores[i]), 3)) for i in top])

if __name__ == "__main__":
    build()
