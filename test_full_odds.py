import requests
import re

# 尝试获取赔率数据
urls_to_try = [
    "https://jc.titan007.com/xml/bf_jc.txt",
]

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
})

for url in urls_to_try:
    try:
        response = session.get(url, timeout=10)
        content = response.content.decode('utf-8')
        
        parts = content.split('$')
        if len(parts) > 1:
            match_data = parts[1]
            match_entries = match_data.split('!')
            
            print(f"比赛数量：{len(match_entries)}")
            
            # 查看第一场比赛的所有字段
            if match_entries:
                first_entry = match_entries[0]
                fields = first_entry.split('^')
                print(f"\n字段总数：{len(fields)}")
                
                # 显示所有字段
                for i, field in enumerate(fields):
                    print(f"[{i:2d}]: {field}")
    except Exception as e:
        print(f"错误：{e}")
