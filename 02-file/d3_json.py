import json

#把字典写成json文件
data = {
    "姓名":"seven",
    "方向":"转行fde",
    "能力":{"行业":"10年快销品行业经验","工作经历":"开发、乙方公司项目实施、甲方品牌方经历","优势":"有技术背景、做个项目、品牌方工作经历，了解业务"}
}

with open("report.json","w",encoding="utf-8") as f:
    json.dump(data ,f ,ensure_ascii=False ,indent=2)

print("report.json 文件已生成")

#读取json文件
with open("report.json" ,"r" ,encoding="utf-8") as f:
    loaded = json.load(f)

print("读回：",loaded)
print("\n")
print("工作经历:",loaded["能力"]["工作经历"])
print("优势:",loaded["能力"]["优势"])