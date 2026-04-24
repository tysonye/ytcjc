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
    
    # 查看前 3 场比赛
    for i, entry in enumerate(match_entries[:3]):
        fields = entry.split('^')
        print(f"\n{'='*60}")
        print(f"比赛 {i+1}: {fields[4] if len(fields)>4 else 'N/A'}")
        print(f"字段总数：{len(fields)}")
        
        # 显示所有包含数字和小数点的字段
        print("\n可能包含赔率的字段:")
        for j, field in enumerate(fields):
            if field and '.' in field and len(field) <= 10:
                print(f"  [{j:2d}]: {field}")
