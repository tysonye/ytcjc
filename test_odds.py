import requests
import re

url = "https://jc.titan007.com/xml/bf_jc.txt"
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
})

response = session.get(url, timeout=10)
content = response.content.decode('utf-8')

parts = content.split('$')
if len(parts) > 1:
    match_data = parts[1]
    match_entries = match_data.split('!')
    
    print("查找赔率字段...")
    
    # 查看前 3 场比赛
    for i, entry in enumerate(match_entries[:3]):
        fields = entry.split('^')
        print(f"\n=== 比赛 {i+1}: {fields[4] if len(fields)>4 else 'N/A'} ===")
        
        # 查找所有包含小数点的字段（可能是赔率）
        for j, field in enumerate(fields):
            if field and re.match(r'^\d+\.\d+$', field):
                print(f"  [{j:2d}]: {field}")
        
        # 显示 20-30 字段（可能包含赔率）
        print(f"  [20-30]: {[fields[k] for k in range(20, min(30, len(fields)))]}")
