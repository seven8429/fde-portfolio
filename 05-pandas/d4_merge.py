import pandas as pd

# 表1：经销商实际销量
dealers = pd.DataFrame({
    "经销商": ["杭州佰诚","北京光彩","广州兴盛","南京苏果","武汉中百",
             "成都红旗","郑州丹尼斯","西安爱家","沈阳中兴","福州永辉"],
    "区域":   ["华东","华北","华南","华东","华中",
             "华北","华中","西北","东北","华南"],
    "销量":   [3200,3600,4000,2800,1900,2600,2100,1500,1700,3300],
})

# 表2：各区域销售目标
targets = pd.DataFrame({
    "区域": ["华东","华北","华中","西北","东北"],
    "目标": [6000,6000,4000,2000,2000],
})

# 1) 直接 merge：每行经销商带上所在区域目标（对比 SQL JOIN ... ON 区域）
merged = dealers.merge(targets, on="区域", how="left")
print("拼接后（经销商 + 区域目标）：")
print(merged)

# 2) 先按区域汇总实际，再和目标合并，算完成率
region_actual = dealers.groupby("区域")["销量"].sum().reset_index()
region_full = region_actual.merge(targets, on="区域")
region_full["完成率%"] = (region_full["销量"] / region_full["目标"] * 100).round(1)
print("\n各区域实际 vs 目标：")
print(region_full)
