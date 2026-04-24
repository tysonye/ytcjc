
import requests

# 获取数据
url = "https://jc.titan007.com/xml/bf_jc.txt"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'utf-8'

# 解析数据
parts = response.text.split('$')
if len(parts) > 1:
    matches = parts[1].split('!')
    
    print("查找比赛2799985的时间数据:")
    print("="*80)
    
    for match_str in matches:
        if not match_str.strip():
            continue
        
        fields = match_str.split('^')
        if len(fields) < 20:
            continue
        
        match_id = fields[4] if len(fields) > 4 else ""
        
        if match_id == "周五005":  # 2799985对应周五005
            print(f"\n比赛ID: {match_id}")
            print(f"唯一ID: {fields[0]}")
            print(f"状态码: {fields[3]}")
            print(f"开始时间: {fields[1]}")
            print(f"更新时间: {fields[2]}")
            
            # 显示所有字段
            print("\n所有字段:")
            for i, f in enumerate(fields):
                if f:
                    print(f"  [{i}] {f}")
            
            # 查找可能的时间字段
            print("\n可能的时间相关字段:")
            for i in range(10, min(25, len(fields))):
                if fields[i] and fields[i] not in ['0', '']:
                    print(f"  [{i}] {fields[i]}")
