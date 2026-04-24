
import requests
import re

# 尝试从网页获取动态加载的时间数据
# 通常这些数据会通过单独的API接口获取

urls_to_try = [
    "https://jc.titan007.com/xml/bf_jc.txt",
    "https://jc.titan007.com/handle/change.ashx",
    "https://jc.titan007.com/handle/live.ashx",
]

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://jc.titan007.com/index.aspx',
})

# 先访问主页获取session
main_response = session.get("https://jc.titan007.com/index.aspx", timeout=10)
print(f"主页状态: {main_response.status_code}")

for url in urls_to_try:
    print(f"\n尝试: {url}")
    try:
        response = session.get(url, timeout=10)
        print(f"  状态: {response.status_code}")
        
        if response.status_code == 200:
            # 查找时间数据
            time_pattern = r'(\d+):(\d+)'
            matches = re.findall(time_pattern, response.text)
            print(f"  找到 {len(matches)} 个时间格式数据")
            
            # 查找特定比赛
            if '2799985' in response.text or '2799987' in response.text:
                print("  找到目标比赛数据!")
                # 提取相关行
                lines = response.text.split('\n')
                for line in lines:
                    if '2799985' in line or '2799987' in line:
                        print(f"  数据: {line[:200]}")
                        
    except Exception as e:
        print(f"  错误: {e}")
