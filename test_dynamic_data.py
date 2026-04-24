
import requests
import json

# 正确的请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'http://zq.titan007.com/'
}

# 动态数据URL
url = 'http://zq.titan007.com/default/getScheduleInfo?sid=2913592'

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"内容长度: {len(response.text)}")
    
    with open('dynamic_data.js', 'w', encoding='utf-8') as f:
        f.write(response.text)
        
    print("已保存到 dynamic_data.js")
    
except Exception as e:
    print(f"错误: {e}")
