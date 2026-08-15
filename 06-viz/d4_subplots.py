import matplotlib.pyplot as plt
import os

plt.rcParams["font.sans-serif"] = ["PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False

regions = ["华东","华北","华南","华中","西北","东北"]
sales   = [6000, 6200, 7300, 4000, 1500, 1700]
quarters = ["Q1","Q2","Q3","Q4"]
hua_dong = [6000, 6500, 7000, 7200]
hua_bei  = [5800, 6000, 5900, 6200]
hua_nan  = [6800, 7100, 7300, 7600]
region_dealers = [2, 2, 2, 2, 1, 1]

# 建 2行2列 的子图网格；fig 是整张画布，axes 是 4 个子图对象
fig, axes = plt.subplots(2, 2, figsize=(12, 9))
ax1, ax2, ax3, ax4 = axes.flatten()

# 1) 柱状图
ax1.bar(regions, sales, color="#4C72B0")
ax1.set_title("各区域销量")
ax1.set_ylabel("销量")
ax1.tick_params(axis="x", rotation=45)

# 2) 折线图
ax2.plot(quarters, hua_dong, marker="o", label="华东")
ax2.plot(quarters, hua_bei,  marker="s", label="华北")
ax2.plot(quarters, hua_nan,  marker="^", label="华南")
ax2.set_title("逐季销量趋势")
ax2.legend(); ax2.grid(True, alpha=0.3)

# 3) 饼图
ax3.pie(sales, labels=regions, autopct="%.1f%%", startangle=90)
ax3.set_title("销量占比"); ax3.axis("equal")

# 4) 散点图（气泡大小随销量，温习 D3 的列表推导式）
ax4.scatter(region_dealers, sales, s=[x/10 for x in sales], color="#55A868")
for i, r in enumerate(regions):
    ax4.annotate(r, (region_dealers[i], sales[i]), fontsize=9)
ax4.set_title("经销商数 vs 总销量")
ax4.set_xlabel("经销商数量"); ax4.set_ylabel("总销量"); ax4.grid(True, alpha=0.3)

fig.suptitle("经销商销售分析报表", fontsize=16)   # 整张画布的总标题
fig.tight_layout()
out = os.path.expanduser("~/fde/06-viz/report_grid.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
plt.savefig(out)
print("已保存图片:", out)
plt.show()