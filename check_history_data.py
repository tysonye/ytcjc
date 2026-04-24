
import requests

date = "2026-04-24"
url = f"https://jc.titan007.com/handle/JcResult.aspx?d={date}"

headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'utf-8'

with open('history_data.txt', 'w', encoding='utf-8') as f:
    f.write(response.text)

print(f"历史数据保存到 history_data.txt")
print(f"长度: {len(response.text)}")
print()

# 解析
parts = response.text.split('$')
print(f"总部分数: {len(parts)}")
print()

if len(parts) > 1:
    matches_part = parts[1]
    matches = matches_part.split('!')
    print(f"比赛数: {len(matches)}")
    print()
    
    for i, match_str in enumerate(matches[:3]):
        if not match_str:
            continue
        
        fields = match_str.split('^')
        print(f"比赛 {i+1}: {len(fields)} 字段")
        for j, f in enumerate(fields):
            if f:
                print(f"  [{j:2}] {repr(f)}")
        print()
