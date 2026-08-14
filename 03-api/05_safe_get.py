import requests

def safe_get(url, params=None, timeout=10):
    headers = {"User-Agent": "fde-learner"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"⚠️ {url} 返回状态码： {resp.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 请求出错：{e}")
        return None

data = safe_get("https://api.github.com/users/octocat")
if data:
    print("用户名：", data["login"], " | 粉丝：", data["followers"])

miss = safe_get("https://api.github.com/users/__not_exist_999__")
print("不存在用户结果：", miss)

bad = safe_get("https://httpbin.org/delay/30", timeout=3)
print("超时/异常结果：", bad)