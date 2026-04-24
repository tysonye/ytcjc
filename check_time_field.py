
import requests

url = "https://jc.titan007.com/xml/bf_jc.txt"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'utf-8'

# 解析数据
parts = response.text.split('$')
if len(parts) > 1:
    matches = parts[1].split('!')
    
    print("分析前5场比赛的时间字段:")
    print("="*80)
    
    for i, match_str in enumerate(matches[:5]):
        if not match_str.strip():
            continue
        
        fields = match_str.split('^')
        if len(fields) < 20:
            continue
        
        match_id = fields[4] if len(fields) > 4 else ""
        status = fields[3] if len(fields) > 3 else ""
        
        # 时间字段分析
        print(f"\n比赛 {match_id}:")
        print(f"  状态码: {status}")
        print(f"  [1] 开始时间: {fields[1]}")
        print(f"  [2] 更新时间: {fields[2]}")
        
        # 查找是否有进行时间字段
        for j in range(10, min(25, len(fields))):
            if fields[j] and fields[j] not in ['0', '']:
                print(f"  [{j}] {fields[j]}")
