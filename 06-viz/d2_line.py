import matplotlib.pyplot as plt
import os

plt.rcParams["font.sans-serif"] = ["PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False

quarters = ["Q1", "Q2", "Q3", "Q4"]
hua_dong = [6000, 6500, 7000, 7200]   # 华东逐季销量
hua_bei  = [5800, 6000, 5900, 6200]   # 华北
hua_nan  = [6800, 7100, 7300, 7600]   # 华南
hua_zhong = [4000,4200,4100,4300]     #华中

plt.figure(figsize=(8, 5))
plt.plot(quarters, hua_dong, marker="o", label="华东")   # marker=数据点样式
plt.plot(quarters, hua_bei,  marker="s", label="华北")
plt.plot(quarters, hua_nan,  marker="^", label="华南")
plt.plot(quarters, hua_zhong, marker="D", label="华中", linestyle="--")

plt.title("各区域逐季销量趋势")
plt.xlabel("季度")
plt.ylabel("销量")
plt.legend()                 # 显示右上角图例（配合上面的 label）
plt.grid(True, alpha=0.3)    # 淡网格线，方便读数
plt.tight_layout()

out = os.path.expanduser("~/fde/06-viz/quarter_trend.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
plt.savefig(out)
print("已保存图片:", out)
plt.show()