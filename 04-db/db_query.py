import sqlite3
import csv
import os

DB = "sales.db"
CSV_PATH = os.path.expanduser("~/fde/02-file/dealers.csv")

def load_to_db():
    """读 CSV → 建表 → 灌入，返回连接"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    with open(CSV_PATH, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r.get("经销商")]
    cur.execute("DROP TABLE IF EXISTS dealers_csv")
    cur.execute("""
    CREATE TABLE dealers_csv (
        区域    TEXT,
        经销商  TEXT,
        销量    INTEGER
    )
    """)
    cur.executemany(
        "INSERT INTO dealers_csv (区域, 经销商, 销量) VALUES (?, ?, ?)",
        [(r["区域"], r["经销商"], int(r["销量"])) for r in rows],
    )
    conn.commit()
    return conn

def report(conn):
    cur = conn.cursor()
    print("=" * 34)
    print("       经销商销量报表")
    print("=" * 34)

    # 1) 总览
    cur.execute("SELECT COUNT(*), SUM(销量) FROM dealers_csv")
    cnt, total = cur.fetchone()
    print(f"经销商数: {cnt}    总销量: {total}")

    # 2) 按区域合计（降序）
    cur.execute(
        "SELECT 区域, SUM(销量) FROM dealers_csv "
        "GROUP BY 区域 ORDER BY SUM(销量) DESC"
    )
    print("\n各区域销量合计：")
    for region, s in cur.fetchall():
        print(f"  {region}: {s}")

    # 3) 销量冠军
    cur.execute("SELECT 经销商, 销量 FROM dealers_csv ORDER BY 销量 DESC LIMIT 1")
    top_name, top_sales = cur.fetchone()
    print(f"\n销量冠军: {top_name}（{top_sales}）")

    # 4) 高销量经销商（> 3500）
    cur.execute(
        "SELECT 经销商, 销量 FROM dealers_csv "
        "WHERE 销量 > 3500 ORDER BY 销量 DESC"
    )
    print("\n高销量经销商（>3500）：")
    for name, s in cur.fetchall():
        print(f"  {name}: {s}")

    print("=" * 34)

if __name__ == "__main__":
    conn = load_to_db()
    report(conn)
    conn.close()
