import csv, json

try:
    with open("dealers.csv", "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
except FileNotFoundError:
    print("请先跑 D2 生成 dealers.csv")
    exit()

region_sales = {}
for r in rows:
    reg = r["区域"]
    s = float(r["销量"])
    region_sales[reg] = region_sales.get(reg, 0) + s

report = {
    "各区域销量合计": region_sales,
    "销量最高区域": max(region_sales, key=region_sales.get),
    "总销量": sum(region_sales.values()),
}
with open("report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print("已生成 report.json：")
print(json.dumps(report, ensure_ascii=False, indent=2))
