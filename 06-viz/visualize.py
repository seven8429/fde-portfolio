import pandas as pd
import matplotlib.pyplot as plt
import os

plt.rcParams["font.sans-serif"] = ["PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False

# 1) 读真实数据（第5周学的 pd.read_csv）+ 清洗
CSV = os.path.expanduser("~/fde/02-file/dealers.csv")
df = pd.read_csv(CSV).dropna(subset=["经销商"])
df["销量"] = df["销量"].astype(int)

region_stats = df.groupby("区域")["销量"].sum()                     # 区域→总销量
dealer_sorted = df.sort_values("销量", ascending=False).set_index("经销商")["销量"]  # 经销商→销量

# 2) 2×2 子图报表（温习 D4）；pandas 图用 ax= 画到指定子图
fig, axes = plt.subplots(2, 2, figsize=(12, 9))
ax1, ax2, ax3, ax4 = axes.flatten()

region_stats.plot(kind="bar", color="#4C72B0", ax=ax1)
ax1.set_title("各区域销量合计"); ax1.set_ylabel("销量")

region_stats.plot(kind="pie", autopct="%.1f%%", startangle=90, ax=ax2)
ax2.set_title("各区域销量占比"); ax2.set_ylabel("")

dealer_sorted.plot(kind="bar", color="#55A868", ax=ax3)
ax3.set_title("各经销商销量（降序）"); ax3.set_ylabel("销量")
ax3.tick_params(axis="x", rotation=45)

dealer_sorted.plot(kind="barh", color="#CCB974", ax=ax4)
ax4.set_title("各经销商销量（横向）"); ax4.set_xlabel("销量")

fig.suptitle("经销商销售分析报表（数据源：dealers.csv）", fontsize=15)
fig.tight_layout()

out = os.path.expanduser("~/fde/06-viz/visualize_report.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
plt.savefig(out)
print("已保存图片:", out)
plt.show()