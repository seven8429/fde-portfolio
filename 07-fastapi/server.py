from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import os

app = FastAPI(title="FDE 经销商分析服务", version="1.0")

# 默认读第2/5周那个真实文件
DEFAULT_CSV = os.path.expanduser("~/fde/02-file/dealers.csv")

# —— 数据模板（Pydantic，D2 学过的自动校验） ——
class Dealer(BaseModel):
    经销商: str
    区域: str
    销量: int

class AnalyzeRequest(BaseModel):
    dealers: List[Dealer]

class PathRequest(BaseModel):
    csv_path: str

# —— 核心分析逻辑（抽函数，所有接口共用，D3 学过的复用思想） ——
def analyze_csv(path: str):
    df = pd.read_csv(path).dropna(subset=["经销商"])
    df["销量"] = df["销量"].astype(int)
    region = df.groupby("区域")["销量"].sum().reset_index()
    top = df.sort_values("销量", ascending=False).iloc[0]
    return {
        "数据源": path,
        "经销商数": len(df),
        "总销量": int(df["销量"].sum()),
        "各区域销量": [
            {"区域": r["区域"], "销量": int(r["销量"])}
            for r in region.to_dict("records")
        ],
        "销量冠军": {"经销商": top["经销商"], "销量": int(top["销量"])},
    }

# —— D1：健康检查 ——
@app.get("/health")
def health():
    return {"status": "ok", "msg": "服务正常运行"}

# —— D2：接收 dealers 列表，直接分析 ——
@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    df = pd.DataFrame([d.model_dump() for d in req.dealers])
    region = df.groupby("区域")["销量"].sum().reset_index()
    return {
        "经销商数": len(df),
        "总销量": int(df["销量"].sum()),
        "各区域销量": [
            {"区域": r["区域"], "销量": int(r["销量"])}
            for r in region.to_dict("records")
        ],
    }

# —— D3+D4：读默认文件，文件缺失 → 404 ——
@app.get("/report")
def report():
    if not os.path.exists(DEFAULT_CSV):
        raise HTTPException(status_code=404, detail="默认数据文件不存在")
    return analyze_csv(DEFAULT_CSV)

# —— D3+D4：收任意路径，缺失 → 404，空数据 → 400 ——
@app.post("/report-from-path")
def report_from_path(req: PathRequest):
    if not os.path.exists(req.csv_path):
        raise HTTPException(status_code=404, detail=f"文件不存在: {req.csv_path}")
    df = pd.read_csv(req.csv_path).dropna(subset=["经销商"])
    if df.empty:
        raise HTTPException(status_code=400, detail="文件无有效数据（经销商列为空）")
    return analyze_csv(req.csv_path)
