from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI(title="FDE 经销商分析服务")

# 默认读第2/5周那个真实文件
DEFAULT_CSV = os.path.expanduser("~/fde/02-file/dealers.csv")

def analyze_csv(path: str):
    """读 CSV → 清洗 → groupby，返回结果字典（复用第5周逻辑）"""
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

@app.get("/report")
def report():
    """读默认 dealers.csv，返回分析"""
    if not os.path.exists(DEFAULT_CSV):
        return {"error": "未找到默认数据文件"}
    return analyze_csv(DEFAULT_CSV)

class PathRequest(BaseModel):
    csv_path: str

@app.post("/report-from-path")
def report_from_path(req: PathRequest):
    """接收任意 CSV 路径，返回分析"""
    if not os.path.exists(req.csv_path):
        return {"error": f"文件不存在: {req.csv_path}"}
    return analyze_csv(req.csv_path)
