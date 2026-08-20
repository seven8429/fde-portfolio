"""
D2：定义第一个真实工具函数 query_sales(region)
它会真的去查第4周的 sales.db，返回某区域的经销商总销量
后续 D4 的 Agent「调用」的就是这个函数
依赖：sqlite3（标准库，无需安装）
"""
import os
import sqlite3

DB = os.path.expanduser("~/fde/04-db/sales.db")

def query_sales(region: str) -> str:
    """查询某区域的经销商总销量，如 query_sales("华东")"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "SELECT SUM(销量) FROM dealers_csv WHERE 区域 = ?",
        (region,),          # 参数化，防 SQL 注入（呼应第4周）
    )
    total = cur.fetchone()[0]
    conn.close()
    if total is None:
        return f"未找到区域「{region}」的销量数据"
    return f"{region}区经销商总销量：{total}"

if __name__ == "__main__":
    # 先看看数据库里到底有哪些区域，免得瞎猜
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT 区域 FROM dealers_csv")
    regions = [r[0] for r in cur.fetchall()]
    conn.close()
    print("数据库中可用区域：", regions)
    for region in regions[:3]:        # 演示前 3 个区域
        print(query_sales(region))
