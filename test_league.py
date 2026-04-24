import requests

url = "https://jc.titan007.com/xml/bf_jc.txt"
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
})

response = session.get(url, timeout=10)
content = response.content.decode('utf-8')

parts = content.split('$')
league_data = parts[0]

print("=== 联赛数据 ===")
league_entries = league_data.split('!')
print(f"联赛数量：{len(league_entries)}")

for i, entry in enumerate(league_entries[:10]):
    if entry.strip():
        fields = entry.split('^')
        print(f"\n{i+1}. 字段数：{len(fields)}")
        for j, field in enumerate(fields[:8]):
            print(f"   [{j}]: {field[:100] if len(field) > 100 else field}")

print("\n\n=== 比赛数据 ===")
if len(parts) > 1:
    match_data = parts[1]
    match_entries = match_data.split('!')
    print(f"比赛数量：{len(match_entries)}")
    
    for i, entry in enumerate(match_entries[:3]):
        if entry.strip():
            fields = entry.split('^')
            print(f"\n比赛 {i+1}: 字段数={len(fields)}")
            print(f"  [4] 比赛编号：{fields[4] if len(fields) > 4 else 'N/A'}")
            print(f"  [5] 联赛 ID: {fields[5] if len(fields) > 5 else 'N/A'}")
            print(f"  [8] 主队：{fields[8] if len(fields) > 8 else 'N/A'}")
            print(f"  [10] 客队：{fields[10] if len(fields) > 10 else 'N/A'}")
