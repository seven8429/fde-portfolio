import sqlite3

conn = sqlite3.connect("sales.db")
cur = conn.cursor()

# 建订单表：每个经销商有多笔订单（dealer_name 用来和 dealers 表关联）
cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id          INTEGER PRIMARY KEY,
    dealer_name TEXT,
    amount      INTEGER,
    quarter     TEXT
)
""")
cur.execute("DELETE FROM orders")   # 清掉，重复跑不报错
cur.executemany(
    "INSERT INTO orders (dealer_name, amount, quarter) VALUES (?, ?, ?)",
    [
        ("杭州华联", 1200, "Q1"),
        ("杭州华联",  900, "Q2"),
        ("南京苏果", 1500, "Q1"),
        ("郑州丹尼斯", 800, "Q1"),
        ("武汉中百", 1100, "Q2"),
        ("成都红旗", 1000, "Q1"),
        ("苏州美佳", 700, "Q1"),
    ],
)
conn.commit()

# —— JOIN：经销商表 × 订单表，按经销商汇总订单总额 ——
print("=== 每个经销商的订单总额 (INNER JOIN) ===")
cur.execute("""
SELECT d.region, d.name, SUM(o.amount) AS total_amount
FROM dealers d
JOIN orders o ON d.name = o.dealer_name
GROUP BY d.name
ORDER BY total_amount DESC
""")
for row in cur.fetchall():
    print(f"区域：{row[0]} | 名称：{row[1]} | 订单总额：{row[2]}")

# —— JOIN：经销商表 × 订单表，按经销商汇总订单总额 ——
print("=== 每个经销商的订单总额 (left JOIN) ===")
cur.execute("""
SELECT d.region, d.name, SUM(o.amount) AS total_amount
FROM dealers d
right JOIN orders o ON d.name = o.dealer_name
GROUP BY d.region
ORDER BY total_amount DESC
""")
for row in cur.fetchall():
    print(f"区域：{row[0]} | 名称：{row[1]} | 订单总额：{row[2]}")
conn.close()
