"""
Week9 D2：把第8周 embedding 检索封装成可复用的查询函数
load：读 D1 建好的索引；search(query, top_k)：返回 [(score, source, text), ...]
"""
import os, json
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_DIR = os.path.expanduser("~/fde/week9_ai_rep/index")
MODEL_NAME = "BAAI/bge-small-zh-v1.5"
QUERY_INSTRUCTION = "为这个句子生成表示以用于检索相关文章："

class RepRetriever:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)   # 权重已缓存，离线加载
        self.matrix = np.load(os.path.join(INDEX_DIR, "matrix.npy"))
        with open(os.path.join(INDEX_DIR, "docs.json"), encoding="utf-8") as f:
            self.docs = json.load(f)

    def search(self, query, top_k=3):
        q = self.model.encode([QUERY_INSTRUCTION + query],
                              normalize_embeddings=True, show_progress_bar=False)[0]
        scores = self.matrix @ q                      # 归一化后点积=余弦
        top = np.argsort(-scores)[:top_k]
        return [(float(scores[i]), self.docs[i]["source"], self.docs[i]["text"])
                for i in top]


if __name__ == "__main__":
    r = RepRetriever()
    for q in ["陈列费核销需要什么材料",
              "客户说价格高怎么回",
              "特价促销核销要哪些东西"]:
        print(f"\n查询：{q}")
        for s, src, txt in r.search(q, top_k=2):
            print(f"  {s:.3f}  [{src}]  {txt.splitlines()[0][:30]}")
