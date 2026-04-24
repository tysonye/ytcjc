
import requests
from datetime import datetime

url = "https://jc.titan007.com/xml/bf_jc.txt"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'utf-8'

parts = response.text.split('$')
if len(parts) > 1:
    matches = parts[1].split('!')
    
    print("所有比赛状态和时间:")
    print("="*80)
    
    for match_str in matches[:10]:
        if not match_str.strip():
            continue
        
        fields = match_str.split('^')
        if len(fields) < 10:
            continue
        
        status = fields[3] if len(fields) > 3 else ""
        match_id = fields[4] if len(fields) > 4 else ""
        
        status_map = {'0': '未开始', '1': '进行中', '2': '已完场', '3': '中场', '-1': '已完场'}
        status_text = status_map.get(status, '未知')
        
        print(f"\n{match_id} - {status_text} (状态码:{status})")
        print(f"  开始时间: {fields[1]}")
        print(f"  更新时间: {fields[2]}")
        
        # 尝试计算已进行时间
        try:
            start_parts = fields[1].split(',')
            update_parts = fields[2].split(',')
            
            if len(start_parts) >= 5 and len(update_parts) >= 5:
                start_h = int(start_parts[3])
                start_m = int(start_parts[4])
                update_h = int(update_parts[3])
                update_m = int(update_parts[4])
                
                start_total = start_h * 60 + start_m
                update_total = update_h * 60 + update_m
                
                if update_total >= start_total:
                    diff = update_total - start_total
                    print(f"  已进行: {diff} 分钟")
        except:
            pass
