import matplotlib.pyplot as plt
import os

# macOS 中文显示：指定系统中文字体，否则中文标签变方块
plt.rcParams["font.sans-serif"] = ["PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False   # 让负号正常显示

regions = ["华东", "华北", "华南", "华中", "西北", "东北"]
sales   = [6000, 6200, 7300, 4000, 1500, 1700]

plt.figure(figsize=(8, 5))
plt.bar(regions, sales, color="#4C72B0")
plt.title("各区域销量")
plt.xlabel("区域")
plt.ylabel("销量")
plt.tight_layout()

# 存成图片（终端里 plt.show() 不一定能弹窗，存文件最稳）
out = os.path.expanduser("~/fde/06-viz/region_sales.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
plt.savefig(out)
print("已保存图片:", out)
plt.show()   # 有图形界面时可取消注释直接弹窗看
