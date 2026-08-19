"""
D3：把 D2 的向量化封装成一个可复用的「检索器 / 向量库」
学会点：
  1. 把散装代码收敛成一个类（知识库 = 块 + 向量）
  2. search(query, top_k) 返回最相关的 top_k 块
  3. 持久化：向量只算一次，存盘后下次直接加载（RAG 的「建索引」）
依赖：numpy
"""
import os, re, math, json
import numpy as np

DOC = os.path.expanduser("~/WorkBuddy/work/FDE转行90天执行手册.md")
INDEX_DIR = os.path.expanduser("~/fde/rag_week/index")   # 持久化目录

class TfidfRetriever:
    def __init__(self, n=2):
        self.n = n
        self.vocab = {}      # term -> 列号
        self.df = {}         # term -> 出现块数
        self.chunks = []     # 原始文本块
        self.matrix = None   # (块数, 维度) 向量矩阵

    # --- 中文分词：字符 N-gram ---
    def _ngrams(self, t):
        t = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]+", "", t)
        return [t[i:i+self.n] for i in range(len(t)-self.n+1)]

    # --- 建索引：切分 + 向量化 ---
    def build(self, text):
        chunks, cur = [], []
        for line in text.splitlines():
            if line.startswith("#") and cur:
                chunks.append("\n".join(cur).strip()); cur=[]
            cur.append(line)
        if cur: chunks.append("\n".join(cur).strip())
        self.chunks = [c for c in chunks if len(c) > 20]

        self.df = {}
        for c in self.chunks:
            for g in set(self._ngrams(c)):
                self.df[g] = self.df.get(g, 0) + 1
        self.vocab = {t:i for i,t in enumerate(self.df)}
        V, N = len(self.vocab), len(self.chunks)

        X = np.zeros((N, V))
        for i, c in enumerate(self.chunks):
            grams = self._ngrams(c); total = len(grams); tf = {}
            for g in grams: tf[g] = tf.get(g,0)+1
            for g, cnt in tf.items():
                if g in self.vocab:
                    X[i, self.vocab[g]] = (cnt/total) * math.log(N/(1+self.df[g]))
            norm = np.linalg.norm(X[i])
            if norm > 0: X[i] /= norm
        self.matrix = X
        return self

    # --- 查询：返回 top_k 块 ---
    def search(self, query, top_k=3):
        qv = np.zeros(len(self.vocab))
        grams = self._ngrams(query); total = len(grams); tf = {}
        for g in grams: tf[g] = tf.get(g,0)+1
        N = len(self.chunks)
        for g, cnt in tf.items():
            if g in self.vocab:
                qv[self.vocab[g]] = (cnt/total) * math.log(N/(1+self.df[g]))
        norm = np.linalg.norm(qv)
        if norm > 0: qv /= norm
        scores = self.matrix @ qv          # 矩阵乘法一次算完所有块的余弦
        ranked = np.argsort(-scores)[:top_k]
        return [(float(scores[i]), self.chunks[i]) for i in ranked]

    # --- 持久化：向量只算一次 ---
    def save(self, path):
        os.makedirs(path, exist_ok=True)
        np.save(os.path.join(path, "matrix.npy"), self.matrix)
        with open(os.path.join(path, "chunks.json"), "w", encoding="utf-8") as f:
            json.dump({"vocab": self.vocab, "df": self.df, "chunks": self.chunks}, f, ensure_ascii=False)

    @classmethod
    def load(cls, path):
        r = cls()
        r.matrix = np.load(os.path.join(path, "matrix.npy"))
        with open(os.path.join(path, "chunks.json"), encoding="utf-8") as f:
            d = json.load(f)
        r.vocab, r.df, r.chunks = d["vocab"], d["df"], d["chunks"]
        return r


# ===== 演示 =====
if __name__ == "__main__":
    # 第一次：建索引 + 存盘；之后：直接加载
    if not os.path.exists(os.path.join(INDEX_DIR, "matrix.npy")):
        text = open(DOC, encoding="utf-8").read()
        retriever = TfidfRetriever().build(text)
        retriever.save(INDEX_DIR)
        print(f"建索引完成：{len(retriever.chunks)} 块，已存到 {INDEX_DIR}")
    else:
        retriever = TfidfRetriever.load(INDEX_DIR)
        print(f"从磁盘加载索引：{len(retriever.chunks)} 块")

    for q in ["第7周 FastAPI 怎么写接口",
              "pandas 怎么处理缺失值",
              "简历什么时候开始准备"]:
        print(f"\n查询：{q!r}")
        for score, chunk in retriever.search(q, top_k=2):
            head = chunk.splitlines()[0][:36]
            print(f"  相似度={score:.3f}  {head}")
