
import requests
from datetime import datetime

url = "https://jc.titan007.com/xml/bf_jc.txt"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'utf-8'

parts = response.text.split('$')
if len(parts) > 1:
    matches = parts[1].split('!')
    
    print("查找进行中的比赛时间字段:")
    print("="*80)
    
    for match_str in matches:
        if not match_str.strip():
            continue
        
        fields = match_str.split('^')
        if len(fields) < 25:
            continue
        
        status = fields[3] if len(fields) > 3 else ""
        match_id = fields[4] if len(fields) > 4 else ""
        
        # 只显示进行中的比赛 (status=1 或 3)
        if status in ['1', '3']:
            print(f"\n比赛 {match_id} (状态:{status}):")
            
            # 计算已进行时间
            try:
                start_time = fields[1]  # 开始时间
                update_time = fields[2]  # 更新时间
                
                start_parts = start_time.split(',')
                update_parts = update_time.split(',')
                
                if len(start_parts) >= 6 and len(update_parts) >= 6:
                    start_dt = datetime(int(start_parts[0]), int(start_parts[1]), int(start_parts[2]),
                                       int(start_parts[3]), int(start_parts[4]), int(start_parts[5]))
                    update_dt = datetime(int(update_parts[0]), int(update_parts[1]), int(update_parts[2]),
                                        int(update_parts[3]), int(update_parts[4]), int(update_parts[5]))
                    
                    diff = update_dt - start_dt
                    minutes = diff.total_seconds() // 60
                    
                    print(f"  开始: {start_time}")
                    print(f"  更新: {update_time}")
                    print(f"  已进行: {int(minutes)} 分钟")
            except Exception as e:
                print(f"  时间计算错误: {e}")
            
            # 显示所有可能有用的字段
            print(f"  [15] 红黄牌: {fields[15]}")
            print(f"  [16] 初盘主胜: {fields[16]}")
            print(f"  [17] 初盘平局: {fields[17]}")
            print(f"  [18] 初盘客胜: {fields[18]}")
            print(f"  [19] 即时主胜: {fields[19]}")
            print(f"  [20] 即时平局: {fields[20]}")
            print(f"  [21] 即时客胜: {fields[21]}")
            print(f"  [22] 让球: {fields[22]}")
            print(f"  [23] 其他: {fields[23]}")
