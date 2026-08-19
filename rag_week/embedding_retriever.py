"""
升级版检索器：用真实神经网络 embedding 模型（bge-small-zh）替代 TF-IDF
接口与 TfidfRetriever 完全一致：build / search / save / load
- 语义向量：中文"懂意思"，不再是字面字符匹配
- 维度固定 512（由模型决定），不再是词表大小
依赖：sentence-transformers（已装）
"""
import os, json
import numpy as np
from sentence_transformers import SentenceTransformer

DOC = os.path.expanduser("~/WorkBuddy/work/FDE转行90天执行手册.md")
INDEX_DIR = os.path.expanduser("~/fde/rag_week/index_emb")   # 单独目录，和 TF-IDF 索引区分
MODEL_NAME = "BAAI/bge-small-zh-v1.5"
# bge 中文模型在「查询」时加这句指令，向量质量更好（文档侧不加）
QUERY_INSTRUCTION = "为这个句子生成表示以用于检索相关文章："


class EmbeddingRetriever:
    def __init__(self, model_name=MODEL_NAME):
        self.model = SentenceTransformer(model_name)   # 首次会下载权重
        self.chunks = []
        self.matrix = None

    def _split(self, text):
        chunks, cur = [], []
        for line in text.splitlines():
            if line.startswith("#") and cur:
                chunks.append("\n".join(cur).strip()); cur = []
            cur.append(line)
        if cur:
            chunks.append("\n".join(cur).strip())
        return [c for c in chunks if len(c) > 20]

    def build(self, text):
        self.chunks = self._split(text)
        embs = self.model.encode(self.chunks, normalize_embeddings=True, show_progress_bar=False)
        self.matrix = np.array(embs)
        return self

    def search(self, query, top_k=3):
        q_emb = self.model.encode([QUERY_INSTRUCTION + query],
                                   normalize_embeddings=True, show_progress_bar=False)[0]
        scores = self.matrix @ q_emb          # 归一化后点积=余弦
        ranked = np.argsort(-scores)[:top_k]
        return [(float(scores[i]), self.chunks[i]) for i in ranked]

    def save(self, path):
        os.makedirs(path, exist_ok=True)
        np.save(os.path.join(path, "matrix.npy"), self.matrix)
        with open(os.path.join(path, "chunks.json"), "w", encoding="utf-8") as f:
            json.dump({"chunks": self.chunks}, f, ensure_ascii=False)

    @classmethod
    def load(cls, path, model_name=MODEL_NAME):
        r = cls(model_name)                   # 加载模型（查询也要用）
        r.matrix = np.load(os.path.join(path, "matrix.npy"))
        with open(os.path.join(path, "chunks.json"), encoding="utf-8") as f:
            r.chunks = json.load(f)["chunks"]
        return r
