from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI(title="FDE 经销商分析服务")
DEFAULT_CSV = os.path.expanduser("~/fde/02-file/dealers.csv")

def analyze_csv(path: str):
    df = pd.read_csv(path).dropna(subset=["经销商"])
    df["销量"] = df["销量"].astype(int)
    region = df.groupby("区域")["销量"].sum().reset_index()
    top = df.sort_values("销量", ascending=False).iloc[0]
    return {
        "经销商数": len(df),
        "总销量": int(df["销量"].sum()),
        "各区域销量": [
            {"区域": r["区域"], "销量": int(r["销量"])}
            for r in region.to_dict("records")
        ],
        "销量冠军": {"经销商": top["经销商"], "销量": int(top["销量"])},
    }

@app.get("/report")
def report():
    # 文件缺失 → 404
    if not os.path.exists(DEFAULT_CSV):
        raise HTTPException(status_code=404, detail="默认数据文件不存在")
    return analyze_csv(DEFAULT_CSV)

class PathRequest(BaseModel):
    csv_path: str

@app.post("/report-from-path")
def report_from_path(req: PathRequest):
    if not os.path.exists(req.csv_path):
        raise HTTPException(status_code=404, detail=f"文件不存在: {req.csv_path}")
    df = pd.read_csv(req.csv_path).dropna(subset=["经销商"])
    # 空数据 → 400（客户端传的文件没有有效行）
    if df.empty:
        raise HTTPException(status_code=400, detail="文件无有效数据（经销商列为空）")
    return analyze_csv(req.csv_path)
