import sqlite3

conn = sqlite3.connect("sales.db")
cur = conn.cursor()

print("=== 每个区域内销量排名 (ROW_NUMBER) ===")
cur.execute("""
select region, row_number() over(partition by region order by sales desc) as seq, name, sales from dealers
""")

for row in cur.fetchall():
    print(f"区域：{row[0]} | 销量排名：{row[1]} | 名称：{row[2]} | 销量：{row[3]}")

print("\n=== 每行带上区域总销量 (SUM OVER，对比 GROUP BY) ===")
cur.execute("""
select region, name, sales, sum(sales) over(partition by region) as region_total from dealers
""")

for row in cur.fetchall():
    print(f"区域：{row[0]} | 名称：{row[1]} | 销量：{row[2]} | 区域总销量：{row[3]}")

print("\n=== 每个区域内销量排名 (rank/DENSE_RANK) ===")
cur.execute("""
select region, 
rank() over(partition by region order by sales desc) as rand, 
dense_rank() over(partition by region order by sales desc) as dense_rank,
name, sales from dealers
""")

for row in cur.fetchall():
    print(f"区域：{row[0]} | rank:{row[1]} | dense_rank:{row[2]} | 名称:{row[3]} | 销量:{row[4]}")

conn.close()