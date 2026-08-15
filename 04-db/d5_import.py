import sqlite3
import csv
import os

conn = sqlite3.connect("sales.db")
cur = conn.cursor()

csv_path = os.path.expanduser("~/fde/02-file/dealers.csv")

# 读 CSV（表头是中文：区域, 经销商, 销量），跳过空行
with open(csv_path, encoding="utf-8") as f:
    rows = [r for r in csv.DictReader(f) if r.get("经销商")]
print(f"读取到 {len(rows)} 条经销商数据")

# 建表（用 CSV 真实列名）
cur.execute("DROP TABLE IF EXISTS dealers_csv")   # 重复跑不报错
cur.execute("""
CREATE TABLE dealers_csv (
    区域    TEXT,
    经销商  TEXT,
    销量    INTEGER
)
""")

# 灌入：值用 ? 占位符（温习 D4 参数化，脏数据也只当数据）
cur.executemany(
    "INSERT INTO dealers_csv (区域, 经销商, 销量) VALUES (?, ?, ?)",
    [(r["区域"], r["经销商"], int(r["销量"])) for r in rows],
)
conn.commit()

# 验证：按区域统计销量合计（温习 D1 GROUP BY）
cur.execute("""
SELECT 区域, SUM(销量) AS 合计
FROM dealers_csv
GROUP BY 区域
ORDER BY 合计 DESC
""")
print("\n灌入后按区域统计：")
for region, total in cur.fetchall():
    print(f"  {region}: {total}")

conn.close()
