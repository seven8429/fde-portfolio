"""
D5：多模态综合应用 CLI —— 本周收口
把 D1~D4 串成一个可交互命令行工具：
  img <图片路径>    处理发票/报销单/货架图 → 抽字段 → 入库
  audio <音频路径>  处理客户/拜访录音 → 抽字段 → 入库
  list [n]          查看最近 n 条记录（默认 10）
  stats             按费用类别/区域统计（SQL GROUP BY，第4周功）
  auto <自然语言>   交给 D4 的 Agent 自己判断调哪个工具（炫技用）
  exit              退出
依赖：DEEPSEEK_API_KEY + DASHSCOPE_API_KEY，openai SDK（已装）
运行：python3 d5_multimodal_cli.py
"""
import os, base64, json, sqlite3
from openai import OpenAI

ds = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
qw = OpenAI(api_key=os.getenv("DASHSCOPE_API_KEY"), base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
DB = os.path.expanduser("~/fde/11-multimodal/agent.db")

# ---------- 底座（与 D4 相同）----------
def init_db():
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT, dealer TEXT, region TEXT,
        amount REAL, date TEXT, category TEXT,
        issue TEXT, urgency TEXT, summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit(); conn.close()

def img_b64(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg":"jpeg","jpeg":"jpeg","png":"png","webp":"webp","gif":"gif"}.get(ext,"jpeg")
    with open(path,"rb") as f:
        return f"data:image/{mime};base64,"+base64.b64encode(f.read()).decode()

def audio_b64(path, fmt="wav"):
    with open(path,"rb") as f:
        return f"data:audio/{fmt};base64,"+base64.b64encode(f.read()).decode()

def resolve_path(p):
    if os.path.exists(p):
        return p
    # 模型可能只抽出文件名（如"发票.png"），回退到桌面找
    cand = os.path.expanduser(f"~/Desktop/{os.path.basename(p)}")
    if os.path.exists(cand):
        return cand
    raise FileNotFoundError(f"找不到文件：{p}（也不在 ~/Desktop）")

def extract_image(image_path):
    image_path = resolve_path(image_path)
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
        response_format={"type":"json_object"}, temperature=0)
    try:
        return json.loads(resp.choices[0].message.content)
    except json.JSONDecodeError:
        return {"error": resp.choices[0].message.content}

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
        response_format={"type":"json_object"}, temperature=0)
    try:
        return json.loads(resp.choices[0].message.content)
    except json.JSONDecodeError:
        return {"error": resp.choices[0].message.content}

def save_record(fields):
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

# ---------- CLI 命令 ----------
def cmd_img(path):
    if not os.path.exists(path): print("❌ 文件不存在"); return
    print("⏳ 识别图片中...")
    data = extract_image(path)
    print("抽取结果：", json.dumps(data, ensure_ascii=False))
    print(save_record(json.dumps(data, ensure_ascii=False)))

def cmd_audio(path):
    if not os.path.exists(path): print("❌ 文件不存在"); return
    print("⏳ 识别录音中...")
    data = extract_audio(path)
    print("抽取结果：", json.dumps(data, ensure_ascii=False))
    print(save_record(json.dumps(data, ensure_ascii=False)))

def cmd_list(n=10):
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("SELECT id, source, dealer, region, amount, category, summary FROM records ORDER BY id DESC LIMIT ?", (n,))
    rows = cur.fetchall(); conn.close()
    if not rows: print("（库为空）"); return
    print(f"{'id':>3} {'来源':<8} {'经销商':<10} {'区域':<6} {'金额':<8} {'类别':<8} 摘要")
    for r in rows:
        print(f"{r[0]:>3} {str(r[1]):<8} {str(r[2]):<10} {str(r[3]):<6} {str(r[4]):<8} {str(r[5]):<8} {r[6]}")

def cmd_stats():
    conn = sqlite3.connect(DB); cur = conn.cursor()
    print("-- 按费用类别 --")
    for row in cur.execute("SELECT category, COUNT(*), SUM(amount) FROM records GROUP BY category"):
        print(f"  {row[0]}: {row[1]} 笔, 金额合计 {row[2]}")
    print("-- 按区域 --")
    for row in cur.execute("SELECT region, COUNT(*) FROM records GROUP BY region"):
        print(f"  {row[0]}: {row[1]} 笔")
    conn.close()

# ---------- D4 的 Agent（auto 命令）----------
TOOLS = [
  {"type":"function","function":{"name":"extract_image",
    "description":"从图片抽取结构化字段，返回 JSON。","parameters":{"type":"object","properties":{"image_path":{"type":"string"}},"required":["image_path"]}}},
  {"type":"function","function":{"name":"extract_audio",
    "description":"从录音抽取结构化字段，返回 JSON。","parameters":{"type":"object","properties":{"audio_path":{"type":"string"}},"required":["audio_path"]}}},
  {"type":"function","function":{"name":"save_record",
    "description":"把字段 JSON 字符串存入 SQLite。","parameters":{"type":"object","properties":{"fields":{"type":"string"}},"required":["fields"]}}},
]
def run_agent(question, max_steps=6):
    messages = [{"role":"system","content":
        "你是快消 FDE 助手。根据用户描述，自己决定调用 extract_image / extract_audio 抽取，再用 save_record 入库。"},
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
                messages.append({"role":"tool","tool_call_id":tc.id,"content":str(fn(**args))})
            continue
        print(f"[Agent 第 {step} 步] {msg.content}"); return
    print("⚠️ 达到最大步数")

def main():
    init_db()
    print("🎛 多模态 FDE 助手（img/audio/list/stats/auto/exit）")
    while True:
        try:
            line = input("\n你> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye"); break
        if not line: continue
        if line.lower() in ("exit","quit"): print("bye"); break
        parts = line.split(maxsplit=1)
        cmd, arg = parts[0].lower(), parts[1] if len(parts) > 1 else ""
        if cmd == "img": cmd_img(arg)
        elif cmd == "audio": cmd_audio(arg)
        elif cmd == "list": cmd_list(int(arg) if arg.isdigit() else 10)
        elif cmd == "stats": cmd_stats()
        elif cmd == "auto":
            if not arg: print("请给自然语言，如：auto 处理 /Users/seven/Desktop/receipt.jpg 入库"); continue
            run_agent(arg)
        else:
            print("未知命令：img/audio/list/stats/auto/exit")

if __name__ == "__main__":
    main()
