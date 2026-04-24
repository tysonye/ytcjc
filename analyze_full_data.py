
import requests
from bs4 import BeautifulSoup
import re
import json

url = "https://zq.titan007.com/analysis/2913592.htm"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers, timeout=15)
response.encoding = 'utf-8'

# 提取所有JavaScript变量数据
patterns = [
    r'var\s+(\w+)\s*=\s*(\[.*?\]);',
    r'var\s+(\w+)\s*=\s*(\{.*?\});',
]

all_vars = {}
for pattern in patterns:
    matches = re.findall(pattern, response.text, re.DOTALL)
    for var_name, data in matches:
        try:
            # 尝试解析为Python对象
            py_data = eval(data)
            all_vars[var_name] = py_data
        except:
            pass

# 打印所有找到的变量
print("找到的数据变量:")
for name, data in all_vars.items():
    if isinstance(data, list) and len(data) > 0:
        print(f"\n{name}: {len(data)} 条记录")
        if len(data) > 0:
            print(f"  第一条: {data[0]}")
    elif isinstance(data, dict):
        print(f"\n{name}: 字典")
        print(f"  键: {list(data.keys())[:5]}")

# 特别关注赔率数据
print("\n" + "="*80)
print("赔率数据:")
print("="*80)

# 欧洲指数
if 'Vs_eOdds' in all_vars:
    print(f"\n欧洲指数 (Vs_eOdds): {len(all_vars['Vs_eOdds'])} 条")
    for item in all_vars['Vs_eOdds'][:3]:
        print(f"  {item}")

# 亚洲盘口
if 'Vs_hOdds' in all_vars:
    print(f"\n亚洲盘口 (Vs_hOdds): {len(all_vars['Vs_hOdds'])} 条")
    for item in all_vars['Vs_hOdds'][:3]:
        print(f"  {item}")

# 大小球
if 'Vs_oOdds' in all_vars:
    print(f"\n大小球 (Vs_oOdds): {len(all_vars['Vs_oOdds'])} 条")
    for item in all_vars['Vs_oOdds'][:3]:
        print(f"  {item}")

# 联赛积分
if 'totalScoreStr' in all_vars:
    print(f"\n联赛积分 (totalScoreStr): {len(all_vars['totalScoreStr'])} 条")
    for item in all_vars['totalScoreStr'][:3]:
        print(f"  {item}")
