import requests
import csv
import os

#封装get函数
def safe_get(url, params=None, timeout=10):
    headers = {"User-Agent": "fde-learner"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
            print(f"{url} 返回状态码 {resp.status_code}")
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"{url} 请求出错：{e}")
        return None

def safe_post(url, payload, timeout=10):
    headers = {"User-Agent": "fde-learner"}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
            print(f"POST {url} 返回状态码：{resp.status_code}")
            return None
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"{url} 请求出错：{e}")
        return None

#调GitHub API，解析结构化字段
user = safe_get("https://api.github.com/users/octocat")
if user:
    print(f"用户名：{user["login"]}, 粉丝：{user["followers"]}, 公开仓库：{user["public_repos"]}")
else:
    print("if user is false")

bad = safe_get("https://api.github.com/users/__not_exist_999__")
print(f"不存在用户接口返回：{bad}")

#读取第2周的csv文件，post出去验证
csv_path = os.path.expanduser("~/fde/02-file/dealers.csv")
if os.path.exists(csv_path):
    with open(csv_path, encoding="utf-8") as f:
        rows = [dict(r) for r in csv.DictReader(f)]
        print(f"读取到 {len(rows)} 条经销商数据")
        result = safe_post("https://postman-echo.com/post", {"dealers": rows[:3]})
        if result:
            print(f"已提交 {len(rows)} 条经销商数据，服务端回显：{result.get("json")}")
        else:
            print(f"未找到文件：{csv_path}，跳过 POST 演示")
                 