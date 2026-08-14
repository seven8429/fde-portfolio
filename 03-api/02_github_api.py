import requests

url = 'https://api.github.com/users/octocat'
headers = {"User-Agent" : "fde-learner"}
resp = requests.get(url , headers=headers)

print("状态码：" , resp.status_code)
print("返回类型：" , resp.headers.get("Content-Type"))

#resp.json() 把返回的 JSON 文本转成 dict
data = resp.json()
#print(data)
print(data["login"])
print(data["followers"])
print(data["location"])