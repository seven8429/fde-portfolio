"""
D3：听语音（audio 输入）—— qwen-omni-turbo 同时吃图/音/文
注意：DashScope 兼容模式下，音频 base64 必须包成 data URL（data:audio/wav;base64,...），
      裸 base64 会被当成 URL 解析而报 400。
运行：python3 d3_audio.py
"""
import os, base64
from openai import OpenAI

api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DASHSCOPE_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

def audio_b64(path, fmt="wav"):
    if not os.path.exists(path):
        raise SystemExit(f"❌ 找不到音频文件：{path}\n   请先造测试音频，或改代码路径。")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:audio/{fmt};base64,{b64}", fmt

def listen(audio_data, fmt, question):
    print("⏳ 正在调用 qwen-omni 处理音频（最多等 60 秒）...")
    resp = client.chat.completions.create(
        model="qwen-omni-turbo",
        messages=[{
            "role": "user",
            "content": [
                {"type": "input_audio", "input_audio": {"data": audio_data, "format": fmt}},
                {"type": "text", "text": question},
            ],
        }],
        extra_body={"modalities": ["text"]},
        temperature=0,
        timeout=60,
    )
    print("✅ 模型已返回")
    return resp.choices[0].message.content

if __name__ == "__main__":
    data, fmt = audio_b64("/Users/seven/Desktop/test_voice.wav", "wav")
    q = ("请总结这段录音：①客户说了什么原话；②主要异议类型"
         "（O1价格偏高/O2竞品更便宜/O3库存积压/O4账期回款/O5决策人不在）；"
         "③情绪偏积极还是消极。")
    print(listen(data, fmt, q))
