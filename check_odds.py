import requests

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
    
    # 查看第一场比赛的所有字段
    if match_entries:
        first_entry = match_entries[0]
        fields = first_entry.split('^')
        print(f"第一场比赛字段数：{len(fields)}")
        
        # 显示 20-35 字段（赔率相关）
        print("\n赔率相关字段:")
        for i in range(20, min(35, len(fields))):
            print(f"[{i:2d}]: {fields[i]}")
