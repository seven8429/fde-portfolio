import requests

url = 'https://postman-echo.com/post'
payload = {"name":"杭州佰诚" , "region":"华东" , "sales":3200}
headers = {"User-Agent": "fde-learner"}

try:
    resp = requests.post(url, json=payload, headers=headers, timeout=10)

    if resp.status_code == 200:
        data = resp.json()
        print("✅ 提交成功")
        print("服务端原样收到的数据：", data.get("json", "无json字段，看原始返回"))
    else:
        print(f"❌ 请求失败，状态码：{resp.status_code}")

except requests.exceptions.RequestException as e:
    print("⚠️ 请求出错：", e)