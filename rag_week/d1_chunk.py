import os

DOC = os.path.expanduser("~/WorkBuddy/work/FDE转行90天执行手册.md")
with open(DOC, encoding="utf-8") as f:
    text = f.read()

def chunk_by_heading(text):
    """按 Markdown 标题(#)切分，每块保留所在章节上下文"""
    chunks, current = [], []
    for line in text.splitlines():
        if line.startswith("#") and current:
            chunks.append("\n".join(current).strip())
            current = []
        current.append(line)
    if current:
        chunks.append("\n".join(current).strip())
    return [c for c in chunks if len(c) > 20]   # 过滤太短的块

chunks = chunk_by_heading(text)
print(f"切出 {len(chunks)} 个块")

for i, c in enumerate(chunks[:2]):
    print(f"\n--- 块 {i+1}（前 80 字）---")
    print(c[:80])
