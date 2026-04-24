
import requests
import re

# 尝试获取实时数据接口
urls_to_try = [
    "https://jc.titan007.com/xml/bf_jc.txt",
    "https://jc.titan007.com/handle/JcResult.aspx?d=2026-04-25",
]

for url in urls_to_try:
    print(f"\n检查: {url}")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.encoding = 'utf-8'
        
        # 查找时间相关数据
        if '2799987' in response.text:
            # 找到这场比赛的数据
            idx = response.text.find('2799987')
            context = response.text[idx:idx+200]
            print(f"  找到比赛数据: {context}")
            
    except Exception as e:
        print(f"  错误: {e}")
