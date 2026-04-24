
import requests

url = "https://jc.titan007.com/xml/bf_jc.txt"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'utf-8'

parts = response.text.split('$')
if len(parts) > 1:
    matches = parts[1].split('!')
    
    print("分析所有比赛的状态码:")
    print("="*80)
    
    status_stats = {}
    
    for match_str in matches:
        if not match_str.strip():
            continue
        
        fields = match_str.split('^')
        if len(fields) < 5:
            continue
        
        status = fields[3]
        match_id = fields[4] if len(fields) > 4 else "未知"
        
        if status not in status_stats:
            status_stats[status] = []
        
        status_stats[status].append(match_id)
    
    # 显示统计
    for status, match_list in status_stats.items():
        print(f"\n状态码 {status}: {len(match_list)} 场比赛")
        print(f"  示例: {', '.join(match_list[:5])}")
        
        # 显示第一个示例的完整数据
        if match_list:
            first_match = match_list[0]
            for match_str in matches:
                if first_match in match_str:
                    fields = match_str.split('^')
                    print(f"  开始时间: {fields[1]}")
                    print(f"  更新时间: {fields[2]}")
                    if len(fields) > 11:
                        print(f"  比分: {fields[11]}:{fields[12]}")
                    break
