import pandas as pd
import matplotlib.pyplot as plt
import os

plt.rcParams["font.sans-serif"] = ["PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False

# 读数据（第5周学过的 pd.read_csv）+ 清洗
CSV = os.path.expanduser("~/fde/02-file/dealers.csv")
df = pd.read_csv(CSV).dropna(subset=["经销商"])
df["销量"] = df["销量"].astype(int)

# groupby 得到 区域→总销量 的 Series
region_series = df.groupby("区域")["销量"].sum()

# pandas 直接画图：Series 自带 .plot()，底层调 matplotlib
ax = region_series.plot(kind="pie", color="#4C72B0", figsize=(8, 5))
ax.set_title("各区域销量（pandas 直出）")
ax.set_xlabel("区域")
ax.set_ylabel("销量")
plt.tight_layout()

out = os.path.expanduser("~/fde/06-viz/pandas_bar.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
plt.savefig(out)
print("已保存图片:", out)
plt.show()