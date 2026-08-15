import matplotlib.pyplot as plt
import os

plt.rcParams["font.sans-serif"] = ["PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False

regions = ["华东", "华北", "华南", "华中", "西北", "东北"]
sales   = [6000, 6200, 7300, 4000, 1500, 1700]

# —— 1) 饼图：各区域销量占比 ——
plt.figure(figsize=(6, 6))
plt.pie(sales, labels=regions, autopct="%.1f%%", startangle=90, colors=["#4C72B0","#55A868","#C44E52","#8172B3","#CCB974","#64B5CD"])
plt.title("各区域销量占比")
plt.axis("equal")          # 保证是正圆，不是椭圆
plt.tight_layout()
out1 = os.path.expanduser("~/fde/06-viz/region_pie.png")
os.makedirs(os.path.dirname(out1), exist_ok=True)
plt.savefig(out1)
print("已保存图片:", out1)
plt.show()

# —— 2) 散点图：经销商数量 vs 区域总销量（看相关性）——
region_dealers = [2, 2, 2, 2, 1, 1]   # 各区域经销商数
plt.figure(figsize=(7, 5))
plt.scatter(region_dealers, sales, s=[x / 10 for x in sales], color="#08F58A")
for i, r in enumerate(regions):        # 给每个点标上区域名
    plt.annotate(r, (region_dealers[i], sales[i]), fontsize=9)
plt.title("经销商数量 vs 区域总销量")
plt.xlabel("经销商数量")
plt.ylabel("总销量")
plt.grid(True, alpha=0.3)
plt.tight_layout()
out2 = os.path.expanduser("~/fde/06-viz/dealer_scatter.png")
plt.savefig(out2)
print("已保存图片:", out2)
plt.show()
