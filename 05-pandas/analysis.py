import pandas as pd
import os

CSV_PATH = os.path.expanduser("~/fde/02-file/dealers.csv")
OUT_DIR = os.path.expanduser("~/fde/05-pandas")

# 1) 读 CSV（表头是中文：区域,经销商,销量。pandas 一行搞定，对比第2周的 csv 模块）
df = pd.read_csv(CSV_PATH)
print("原始数据：")
print(df)
print("\n缺失计数：")
print(df.isna().sum())

# 2) 清洗：删掉"经销商"为空的行（原文件末行空行），销量转整数
df = df.dropna(subset=["经销商"])
df["销量"] = df["销量"].astype(int)
print("\n清洗后：")
print(df)

# 3) 分析：按区域汇总（groupby，复用 D3）
region_stats = (
    df.groupby("区域")["销量"].sum()
      .reset_index().sort_values("销量", ascending=False)
)
region_stats.columns = ["区域", "总销量"]
print("\n各区域销量合计：")
print(region_stats)

# 4) 导出
os.makedirs(OUT_DIR, exist_ok=True)
csv_out = os.path.join(OUT_DIR, "经销商分析.csv")
# utf-8-sig：让 Excel 打开中文不乱码（普通 utf-8 在 Windows Excel 会乱码）
region_stats.to_csv(csv_out, index=False, encoding="utf-8-sig")
print(f"\n✅ 已导出 CSV: {csv_out}")

try:
    xlsx_out = os.path.join(OUT_DIR, "经销商分析.xlsx")
    region_stats.to_excel(xlsx_out, index=False)
    print(f"✅ 已导出 Excel: {xlsx_out}")
except ModuleNotFoundError:
    print("⚠️ 导出 Excel 需安装 openpyxl：pip3 install openpyxl")
