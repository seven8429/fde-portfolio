import requests

url = 'https://api.github.com/search/users'
params = {"q": "language:python", "per_page": 3}
headers = {"User-Agent": "fde-learner"}

# timeout=10：最多等 10 秒，超时就抛异常（调外部接口必须加，不然后台卡死）
resp = requests.get(url, params=params, headers=headers, timeout=10)

print("状态码：",resp.status_code)
data = resp.json()
print("匹配用户总数：", data["total_count"])

# 只取前 3 个用户的 login 和 followers —— 像 SELECT login, followers
for user in data["items"][:3]:
    print("用户名：",user["login"], " | 相关度：",user["score"])
    #print(user)