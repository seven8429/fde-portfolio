"""
D1：多模态入门 —— 让模型「看图」（Qwen-Omni via DashScope 兼容端点）
关键点：
  1) 不用装 dashscope SDK，直接复用已装的 openai SDK，base_url 指向 DashScope 兼容模式
  2) messages 里 content 不再是纯字符串，而是 [{"type":"image_url",...},{"type":"text",...}] 的「多模态列表」
  3) 图片可以是网络 URL，也可以是本地文件的 base64（见下方 img_b64 辅助）
依赖：DASHSCOPE_API_KEY（阿里云百炼控制台获取）
运行：python3 d1_vision.py
"""
import os, base64
from openai import OpenAI

api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DASHSCOPE_API_KEY，请先 export DASHSCOPE_API_KEY=...")
client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

# 把本地图片读成 base64 data URL（网络图直接用 URL 即可，不用这步）
def img_b64(path):
    with open(path, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()

def see(image_url, question):
    resp = client.chat.completions.create(
        model="qwen-omni-turbo",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": question},
            ],
        }],
        extra_body={"modalities": ["text"]},   # 只要文字回复，不要语音
    )
    return resp.choices[0].message.content

if __name__ == "__main__":
    # 用阿里公开示例图（联网即可）
    sample = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg"
    # 本地图改成：
    sample = img_b64("/Users/seven/Desktop/汇贤.jpg")
    print(see(sample, "用一句话描述这张图里有什么，并判断它适合用在什么销售/营销场景"))
