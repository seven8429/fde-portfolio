import csv

filename = "dealers.csv"
try:
    with open(filename , "r" , encoding="utf-8") as f:
        for row in csv.reader(f):
            print(row)
    print("读取成功")
except FileNotFoundError:
    print(f"文件：{filename} 不存在，请先执行d2_csv.py 生成")
except Exception as e:
    print(e)