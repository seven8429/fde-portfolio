"""
D4：多模态 Agent —— 图/语音 → 抽取 → 存 SQLite
把本周多模态(D1-D3) + 第10周 Agent + 第4周 SQL 串成综合应用。
场景：用户用自然语言说"处理某张发票照片/某段录音"，AI Agent 自己决定：
  1) 调 extract_image / extract_audio 把多模态内容抽成结构化字段（qwen-omni）
  2) 调 save_record 把字段写进 SQLite（sqlite3）
后端：Agent 决策用 DeepSeek（function calling 稳），多模态抽取用 qwen-omni。
依赖：DEEPSEEK_API_KEY + DASHSCOPE_API_KEY，openai SDK（已装）
运行：python3 d4_multimodal_agent.py
"""
import os, base64, json, sqlite3
from openai import OpenAI

# --- 两个 client：Agent 决策走 DeepSeek，多模态抽取走 qwen-omni ---
ds = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
qw = OpenAI(api_key=os.getenv("DASHSCOPE_API_KEY"), base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

DB = os.path.expanduser("~/fde/11-multimodal/agent.db")

def init_db():
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT, dealer TEXT, region TEXT,
        amount REAL, date TEXT, category TEXT,
        issue TEXT, urgency TEXT, summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit(); conn.close()

# --- base64 助手（注意：DashScope 必须 data URL 前缀，见新坑②）---
def img_b64(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg":"jpeg","jpeg":"jpeg","png":"png","webp":"webp","gif":"gif"}.get(ext,"jpeg")
    with open(path,"rb") as f:
        return f"data:image/{mime};base64,"+base64.b64encode(f.read()).decode()

def audio_b64(path, fmt="wav"):
    with open(path,"rb") as f:
        return f"data:audio/{fmt};base64,"+base64.b64encode(f.read()).decode()

# --- 工具1：图片抽字段（qwen-omni）---
def extract_image(image_path):
    user = ("请从这张图片抽取字段返回 JSON：\n"
            "source(来源: 发票/报销单/货架照片/其他), dealer(经销商名或null), "
            "region(华东/华北/华南/未知/个人), amount(金额数字或null), "
            "date(日期字符串或null), category(费用类别: 陈列费/促销费/其他/未知), "
            "issue(问题描述或null), summary(≤30字概述)")
    resp = qw.chat.completions.create(
        model="qwen-omni-turbo",
        messages=[{"role":"user","content":[
            {"type":"image_url","image_url":{"url":img_b64(image_path)}},
            {"type":"text","text":user}]}],
        extra_body={"modalities":["text"]},
        response_format={"type":"json_object"},
        temperature=0)
    try:
        return json.loads(resp.choices[0].message.content)
    except json.JSONDecodeError:
        return {"error": resp.choices[0].message.content}

# --- 工具2：音频抽字段（qwen-omni）---
def extract_audio(audio_path):
    user = ("请从这段录音抽取字段返回 JSON：\n"
            "source(来源: 客户录音/拜访录音/其他), dealer(经销商名或null), "
            "region(华东/华北/华南/未知), issue(主要问题: 缺货/窜货/客诉/回款/其他/无), "
            "urgency(高/中/低), summary(≤30字客户原话要点)")
    resp = qw.chat.completions.create(
        model="qwen-omni-turbo",
        messages=[{"role":"user","content":[
            {"type":"input_audio","input_audio":{"data":audio_b64(audio_path),"format":"wav"}},
            {"type":"text","text":user}]}],
        extra_body={"modalities":["text"]},
        response_format={"type":"json_object"},
        temperature=0)
    try:
        return json.loads(resp.choices[0].message.content)
    except json.JSONDecodeError:
        return {"error": resp.choices[0].message.content}

# --- 工具3：存 SQLite（第4周 SQL）---
def save_record(fields: str):
    """fields 是 JSON 字符串，含 source/dealer/region/amount/date/category/issue/urgency/summary"""
    try:
        d = json.loads(fields)
    except Exception as e:
        return f"❌ 字段不是合法 JSON：{e}"
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("""INSERT INTO records
        (source, dealer, region, amount, date, category, issue, urgency, summary)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (d.get("source"), d.get("dealer"), d.get("region"),
         d.get("amount"), d.get("date"), d.get("category"),
         d.get("issue"), d.get("urgency"), d.get("summary")))
    conn.commit(); rid = cur.lastrowid; conn.close()
    return f"✅ 已存入数据库，记录 id={rid}"

# --- 工具注册表（第10周 D5 模式）---
TOOLS = [
  {"type":"function","function":{
    "name":"extract_image",
    "description":"从一张图片（发票/报销单/货架照片等）中抽取结构化字段，返回 JSON。",
    "parameters":{"type":"object","properties":{
      "image_path":{"type":"string","description":"本地图片绝对路径"}},
      "required":["image_path"]}}},
  {"type":"function","function":{
    "name":"extract_audio",
    "description":"从一段录音中抽取结构化字段（经销商/区域/问题/紧急度等），返回 JSON。",
    "parameters":{"type":"object","properties":{
      "audio_path":{"type":"string","description":"本地音频绝对路径(wav/m4a)"}},
      "required":["audio_path"]}}},
  {"type":"function","function":{
    "name":"save_record",
    "description":"把抽取出的结构化字段 JSON 字符串存入 SQLite 数据库。",
    "parameters":{"type":"object","properties":{
      "fields":{"type":"string","description":"JSON 字符串，含 source/dealer/region/amount/date/category/issue/urgency/summary"}},
      "required":["fields"]}}},
]

def run_agent(question, max_steps=6):
    init_db()
    messages = [{"role":"system","content":
        "你是快消 FDE 助手。根据用户描述，自己决定调用 extract_image / extract_audio 抽取多模态信息，"
        "再用 save_record 存入数据库。需要路径时从用户描述里提取。一步步完成。"},
        {"role":"user","content":question}]
    for step in range(1, max_steps+1):
        resp = ds.chat.completions.create(model="deepseek-chat", messages=messages, tools=TOOLS, tool_choice="auto")
        msg = resp.choices[0].message
        if msg.tool_calls:
            messages.append({"role":"assistant","content":msg.content,"tool_calls":[
                {"id":tc.id,"type":"function","function":{"name":tc.function.name,"arguments":tc.function.arguments}} for tc in msg.tool_calls]})
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                fn = {"extract_image":extract_image,"extract_audio":extract_audio,"save_record":save_record}[tc.function.name]
                result = fn(**args)
                messages.append({"role":"tool","tool_call_id":tc.id,"content":str(result)})
            continue
        print(f"[第 {step} 步] 最终回答：\n{msg.content}")
        return msg.content
    print("⚠️ 达到最大步数")
    return None

if __name__ == "__main__":
    # 改成你自己的图/音频路径即可（先准备素材）
    q = "帮我处理这张发票照片 /Users/seven/Desktop/发票.png，把信息存进数据库"
    run_agent(q)
    q = "这段客户录音 /Users/seven/Desktop/test_voice.wav 说了什么，存进数据库"
    run_agent(q)
