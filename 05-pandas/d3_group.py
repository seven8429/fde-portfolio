import pandas as pd

data = {
    "经销商": ["杭州佰诚","北京光彩","广州兴盛","南京苏果","武汉中百",
             "成都红旗","郑州丹尼斯","西安爱家","沈阳中兴","福州永辉"],
    "区域":   ["华东","华北","华南","华东","华中",
             "华北","华中","西北","东北","华南"],
    "销量":   [3200,3600,4000,2800,1900,2600,2100,1500,1700,3300],
    "季度":   ["Q1","Q1","Q2","Q1","Q2","Q1","Q2","Q1","Q2","Q2"],
}
df = pd.DataFrame(data)

# 1) 按区域汇总销量（对比 SQL: SELECT 区域, SUM(销量) GROUP BY 区域）
print("各区域销量合计：")
print(df.groupby("区域")["销量"].sum())

# 2) 多指标聚合：每区域的 经销商数 / 总销量 / 平均销量
print("\n各区域多指标：")
print(df.groupby("区域").agg(
    经销商数=("经销商", "count"),
    总销量=("销量", "sum"),
    平均销量=("销量", "mean"),
))

# 3) 变回普通表（reset_index：否则"区域"只是索引不是列）
region_stats = (
    df.groupby("区域")["销量"].sum()
      .reset_index().sort_values("销量", ascending=False)
)
print("\n排序后的区域合计：")
print(region_stats)

# 4) 双维度：区域 × 季度
print("\n区域 × 季度 销量合计：")
print(df.groupby(["区域", "季度"])["销量"].sum().reset_index())
