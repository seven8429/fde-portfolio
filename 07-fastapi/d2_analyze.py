from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd

app = FastAPI(title="FDE 经销商分析服务")

# 1) 定义数据模板：一条经销商记录长啥样
class Dealer(BaseModel):
    经销商: str
    区域: str
    销量: int

# 2) 请求体：包一层 dealers 列表
class AnalyzeRequest(BaseModel):
    dealers: List[Dealer]

@app.get("/health")
def health():
    return {"status": "ok"}

# 3) POST 接口：接收数据 → pandas 算各区域合计 → 返回结果
@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    # 把 Pydantic 对象转成 DataFrame（温习第5周）
    df = pd.DataFrame([d.model_dump() for d in req.dealers])

    # 按区域汇总
    result = df.groupby("区域")["销量"].sum().reset_index()

    return {
        "经销商数": len(df),
        "总销量": int(df["销量"].sum()),
        "各区域销量": [
            {"区域": r["区域"], "销量": int(r["销量"])}
            for r in result.to_dict("records")
        ],
    }
