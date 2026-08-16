import requests, tempfile, os

BASE = "http://localhost:8000"
DEFAULT = os.path.expanduser("~/fde/02-file/dealers.csv")

def check(name, resp, expect):
    ok = resp.status_code == expect
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: 实际 {resp.status_code} / 期望 {expect}")
    return ok

print("=== D5 系统测试（requests 调自己的 FastAPI 服务）===\n")
all_ok = True

# 1) GET 默认报表 → 200
r = requests.get(f"{BASE}/report")
all_ok &= check("GET /report 默认文件", r, 200)
if r.ok:
    print("   经销商数:", r.json()["经销商数"], "总销量:", r.json()["总销量"])

# 2) POST 正常路径 → 200
r = requests.post(f"{BASE}/report-from-path", json={"csv_path": DEFAULT})
all_ok &= check("POST 正常路径", r, 200)
if r.ok:
    print("   销量冠军:", r.json()["销量冠军"])

# 3) POST 不存在文件 → 404
r = requests.post(f"{BASE}/report-from-path", json={"csv_path": "/tmp/nope.csv"})
all_ok &= check("POST 文件不存在", r, 404)

# 4) POST 空数据（临时造一个只有表头的 csv）→ 400
with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
    f.write("区域,经销商,销量\n")
    empty = f.name
r = requests.post(f"{BASE}/report-from-path", json={"csv_path": empty})
all_ok &= check("POST 空数据", r, 400)
os.unlink(empty)

print("\n=== 测试结果:", "全部通过 ✅" if all_ok else "有失败 ❌", "===")

assert all_ok, "有测试用例失败"
