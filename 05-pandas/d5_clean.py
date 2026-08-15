import pandas as pd
import numpy as np

# 故意造几条缺失值（真实数据常有的坑：None/空串都会变 NaN）
data = {
    "经销商": ["杭州佰诚","北京光彩","广州兴盛","南京苏果","武汉中百", None],
    "区域":   ["华东","华北","华南","华东", None, "西北"],
    "销量":   [3200,3600,None,2800,1900,2600],
}
df = pd.DataFrame(data)

print("原始数据：")
print(df)
print("\n各列缺失计数：")
print(df.isna().sum())                 # 先摸清哪列缺多少

# 1) 删除"任意列"缺失的行
print("\ndropna() 后（删掉含缺失的行）：")
print(df.dropna())

# 2) 只删"销量"缺失的行（其余列缺失保留）
print("\n只删销量缺失的行：")
print(df.dropna(subset=["销量"]))

# 3) 填充：销量填均值，区域/经销商填占位文本
df_fill = df.copy()                    # 先复制，别动原表
df_fill["销量"] = df_fill["销量"].fillna(df_fill["销量"].mean())
df_fill["区域"] = df_fill["区域"].fillna("未知")
df_fill["经销商"] = df_fill["经销商"].fillna("未命名")
print("\n填充后：")
print(df_fill)

# 4) 清洗后做聚合（之前学的 groupby 直接复用）
print("\n清洗后按区域汇总销量：")
print(df_fill.groupby("区域")["销量"].sum().round(0))
