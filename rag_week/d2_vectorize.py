"""
D2：把 D1 切出的文本块向量化（教学级 TF-IDF 向量化器，纯 numpy）
理解「文本 → 数字向量 → 余弦相似度」这条 RAG 核心链路
依赖：numpy（已装），不装任何重型库
"""
import os, re, math
import numpy as np

DOC = os.path.expanduser("~/WorkBuddy/work/FDE转行90天执行手册.md")
text = open(DOC, encoding="utf-8").read()

def chunk_by_heading(text):
    chunks, cur = [], []
    for line in text.splitlines():
        if line.startswith("#") and cur:
            chunks.append("\n".join(cur).strip()); cur = []
        cur.append(line)
    if cur:
        chunks.append("\n".join(cur).strip())
    return [c for c in chunks if len(c) > 20]

chunks = chunk_by_heading(text)
print(f"切出 {len(chunks)} 个块，准备向量化")

# ---------- 1. 中文分词：字符 N-gram ----------
# 中文没空格，用“连续 N 个字符”当一个词（bigram=2）
def char_ngrams(t, n=2):
    t = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]+", "", t)  # 去掉符号/空白/markdown
    return [t[i:i+n] for i in range(len(t)-n+1)]

print("\n[分词演示] 第1块 bi-gram 前 10：", char_ngrams(chunks[0])[:10])

# ---------- 2. 建词表（term -> 列号）----------
df = {}
for c in chunks:
    for g in set(char_ngrams(c)):
        df[g] = df.get(g, 0) + 1
vocab = {t: i for i, t in enumerate(df)}
V, N = len(vocab), len(chunks)
print(f"\n向量维度 = 词表大小 = {V}")

# ---------- 3. TF-IDF 向量 ----------
# tf  = 词在块中出现次数 / 块总词数
# idf = log(N / (1+df))，越常见的词越不重要
# 向量 = tf*idf，再 L2 归一化（归一化后点积=余弦）
def tfidf_vector(chunk):
    grams = char_ngrams(chunk)
    total = len(grams)
    tf = {}
    for g in grams:
        tf[g] = tf.get(g, 0) + 1
    vec = np.zeros(V)
    for g, cnt in tf.items():
        if g in vocab:
            vec[vocab[g]] = (cnt / total) * math.log(N / (1 + df[g]))
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec

X = np.stack([tfidf_vector(c) for c in chunks])   # (块数, 维度)
print(f"向量矩阵形状：{X.shape}")

# ---------- 4. 余弦相似度检索 ----------
def cosine(a, b):
    return float(np.dot(a, b))   # 已归一化，点积即余弦

for query in ["FastAPI 怎么写接口",
              "RAG 是怎么工作的"]:
    qv = tfidf_vector(query)
    scores = [cosine(qv, X[i]) for i in range(N)]
    ranked = sorted(range(N), key=lambda i: scores[i], reverse=True)
    print(f"\n[检索] 查询：{query!r}")
    for r, i in enumerate(ranked[:5], 1):
        print(f"  {r}. 相似度={scores[i]:.3f}  {chunks[i].splitlines()[0][:38]}")
