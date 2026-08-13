import csv
#用list创建表头，表格数据
rows = [
    ["区域","经销商","销量"],
    ["华东","杭州佰诚",3200],
    ["华北","北京光彩",3600],
    ["华南","广州兴盛",4000]
]

with open("dealers.csv", "w", encoding="utf-8", newline="") as f:
    csv.writer(f).writerows(rows)

print("经销商销量csv文件已创建成功")

#读取创建的csv文件
with open("dealers.csv", "r", encoding="utf-8") as f:
    for row in csv.reader(f):
        print(row)