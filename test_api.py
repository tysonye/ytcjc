
import requests
from datetime import datetime, timedelta

def test_date(date_str, url_type):
    if url_type == 'today':
        url = 'https://jc.titan007.com/xml/bf_jc.txt'
    else:
        url = f'https://jc.titan007.com/handle/JcResult.aspx?d={date_str}'
    
    print(f'\n{"="*80}')
    print(f'Testing {url_type}: {date_str}')
    print(f'URL: {url}')
    print(f'{"="*80}')
    
    response = requests.get(url)
    print(f'Status: {response.status_code}')
    content = response.content.decode('utf-8')
    
    # 解析数据看看
    if '$' in content:
        parts = content.split('$')
        
        # 打印前3场比赛
        match_data = parts[1] if len(parts) > 1 else ''
        match_entries = match_data.split('!')[:3]
        
        print('前3场比赛数据:')
        for i, entry in enumerate(match_entries):
            if not entry.strip():
                continue
            print(f'  第 {i} 场:')
            fields = entry.split('^')
            for j, field in enumerate(fields):
                if j in [3, 4, 11, 12]:  # 只打印关键字段
                    print(f'    字段 {j} : {repr(field)}')

# 测试今天的数据
today = datetime.now().strftime('%Y-%m-%d')
test_date(today, 'today')

# 测试昨天的数据
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
test_date(yesterday, 'history')
