"""
D2：图表 / 截图 / 文档理解 + 结构化抽取
把 prompt 周学的 JSON 约束，用在「图」上：
  - 模型看完图，把关键信息抽成固定字段的 JSON
  - FDE 场景：报表截图→数据、发票照片→报销字段、货架照片→陈列问题
关键点：
  1) content 是 [image, text] 列表（同 D1）
  2) response_format={"type":"json_object"} 强制 JSON 输出
  3) 字段在 system 里定义清楚，抽不出填 null（接 D1 边界 + D2 JSON）
依赖：DASHSCOPE_API_KEY，openai SDK（已装，免装 dashscope）
运行：python3 d2_chart_json.py
"""
import os, base64, json
from openai import OpenAI

api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise SystemExit("❌ 未找到 DASHSCOPE_API_KEY，请先 export DASHSCOPE_API_KEY=...")
client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

# 本地图片转 base64 data URL（按扩展名判断 mime，jpg/png/webp/gif 都支持）
def img_b64(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp", "gif": "gif"}.get(ext, "jpeg")
    with open(path, "rb") as f:
        return f"data:image/{mime};base64," + base64.b64encode(f.read()).decode()

def extract(image_url, fields_prompt):
    system = (
        "你是数据录入助手。只依据图片内容抽取信息并输出 JSON。"
        "不要编造图片里看不到的内容；推断不出或图片未显示字段填 null。"
        "只输出 JSON，不要任何解释文字或 markdown 代码块标记。"
    )
    user_text = (
        f"请从这张图片中抽取以下字段，返回 JSON：\n{fields_prompt}\n"
        "示例格式：{\"字段1\": 值, \"字段2\": 值}"
    )
    resp = client.chat.completions.create(
        model="qwen-omni-turbo",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": user_text},
            ],
        }],
        extra_body={"modalities": ["text"]},
        response_format={"type": "json_object"},
        temperature=0,
    )
    raw = resp.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": raw}   # 兜底：万一模型多吐了文字，原样返回排查

if __name__ == "__main__":
    # ===== 换成你自己的图 =====
    # 例1 销售报表/图表截图：
    # image = img_b64("/Users/seven/Desktop/sales_chart.png")
    # fields = "month(月份字符串), sales(销量数字), region(区域)"
    # 例2 费用报销单/发票照片：
    # image = img_b64("/Users/seven/Desktop/receipt.jpg")
    # fields = "vendor(开票方), amount(金额数字), date(日期字符串), category(费用类别: 陈列费/促销费/其他)"
    # 例3 货架陈列照片：
    # image = img_b64("/Users/seven/Desktop/shelf.jpg")
    # fields = "has_promotion(是否促销堆头 bool), brands_visible(可见品牌列表), issue(陈列问题描述或null)"

    # 先用 D1 公开示例图跑通流程（无真实业务字段，看模型怎么组织 JSON）
    #image = "https://help-static-aliyun-doc.aliyun.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg"
    #fields = "has_dog(是否含狗 bool), has_person(是否含人 bool), scene(场景一句话简述)"
    image = img_b64("/Users/seven/Desktop/汇贤.jpg")
    fields = "desc(这是一张冰柜的图片), has_text(图中是否含香飘飘价格标签和广告宣传物料 bool)"

    result = extract(image, fields)
    print(json.dumps(result, ensure_ascii=False, indent=2))
