import sqlite3

#链接数据库
conn = sqlite3.connect("sales.db")
cur = conn.cursor()

#建表
cur.execute("""
            create table if not exists dealers(
                id      integer primary key ,
                name    text ,
                region  text ,
                sales   float
            )
""")

#写入数据
#如果不先删除，每执行一次就会重复一次
cur.execute("delete from dealers")
cur.executemany("insert into dealers (name ,region ,sales) values (?, ?, ?)",
    [
        ("杭州华联", "华东", 3200),
        ("南京苏果", "华东", 2800),
        ("郑州丹尼斯", "华中", 2100),
        ("武汉中百", "华中", 1900),
        ("成都红旗", "西南", 2600)
    ],)

conn.commit()

cur.execute("""
select region ,sum(sales) as total 
from dealers 
group by region 
having sum(sales) > 3000
order by total desc
""")

print("各区域销量统计：")
for region , total in cur.fetchall():
    print(f"{region}: {total}")

conn.close()