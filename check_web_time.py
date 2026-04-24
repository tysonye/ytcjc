
import requests
from datetime import datetime

url = "https://jc.titan007.com/xml/bf_jc.txt"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'utf-8'

parts = response.text.split('$')
if len(parts) > 1:
    matches = parts[1].split('!')
    
    print("对比网页显示时间和计算时间:")
    print("="*80)
    
    for match_str in matches[:5]:
        if not match_str.strip():
            continue
        
        fields = match_str.split('^')
        if len(fields) < 20:
            continue
        
        status = fields[3] if len(fields) > 3 else ""
        match_id = fields[4] if len(fields) > 4 else ""
        
        if status not in ['1', '3']:
            continue
        
        print(f"\n{match_id} (状态:{status}):")
        print(f"  开始时间: {fields[1]}")
        print(f"  更新时间: {fields[2]}")
        
        # 我们的计算方式
        try:
            start_parts = fields[1].split(',')
            update_parts = fields[2].split(',')
            
            start_h = int(start_parts[3])
            start_m = int(start_parts[4])
            update_h = int(update_parts[3])
            update_m = int(update_parts[4])
            
            start_total = start_h * 60 + start_m
            update_total = update_h * 60 + update_m
            
            diff = update_total - start_total
            print(f"  计算时间: {diff} 分钟")
            
            # 网页可能显示的时间格式
            print(f"  可能显示: {int(diff)}'")
            
        except Exception as e:
            print(f"  计算错误: {e}")
