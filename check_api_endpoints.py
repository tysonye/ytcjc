
import requests

# 尝试不同的API端点
endpoints = [
    "https://jc.titan007.com/xml/bf.xml",
    "https://jc.titan007.com/xml/live.xml",
    "https://jc.titan007.com/handle/live.ashx",
    "https://jc.titan007.com/handle/change.ashx",
]

for url in endpoints:
    print(f"\n尝试: {url}")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        print(f"  状态: {response.status_code}")
        if response.status_code == 200:
            print(f"  内容长度: {len(response.text)}")
            print(f"  前100字符: {response.text[:100]}")
    except Exception as e:
        print(f"  错误: {e}")
