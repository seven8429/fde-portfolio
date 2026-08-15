import sqlite3

conn = sqlite3.connect("sales.db")
cur = conn.cursor()

# 模拟"用户输入"（实际来自前端/客户系统）
region_input = "华东"

# ✅ 正确：? 占位符 + 参数单独传元组。数据库把 region_input 当纯数据
cur.execute("SELECT name, sales FROM dealers WHERE region = ?", (region_input,))
print(f"区域 = {region_input} 的经销商：")
for row in cur.fetchall():
    print(f"  {row[0]} | 销量 {row[1]}")

# 多参数：区域 + 最低销量
cur.execute(
    "SELECT name, sales FROM dealers WHERE region = ? AND sales >= ?",
    (region_input, 3000),
)
print(f"\n区域 = {region_input} 且销量 ≥ 2500：")
for row in cur.fetchall():
    print(f"  {row[0]} | 销量 {row[1]}")

# —— 对比：如果用户输入带恶意内容，参数化依然把它当"普通字符串" ——
# 这种输入在拼接写法里会破坏 SQL，但 ? 占位符下只是一次"查不到"
evil = "华东' OR '1'='1"
cur.execute("SELECT name FROM dealers WHERE region = ?", (evil,))
print(f"\n用恶意串 '{evil}' 查询，参数化下结果（应为空，因为没这个区域名）：")
print("  ", cur.fetchall())

conn.close()
