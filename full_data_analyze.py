
import requests
from bs4 import BeautifulSoup

url = "https://jc.titan007.com/xml/bf_jc.txt"

headers = {
    'User-Agent': 'Mozilla/5.0'
}

response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'utf-8'

lines = response.text.split('\n')

# 详细分析前5场比赛的所有字段
count = 0
for line in lines:
    line = line.strip()
    if not line:
        continue
    fields = line.split('|')
    if len(fields) < 10:
        continue
    
    count += 1
    print(f"\n{'='*120}")
    print(f"  比赛 {count}:")
    print(f"  总字段数: {len(fields)}")
    print(f"{'='*120}")
    
    # 显示所有有值的字段
    for i, f in enumerate(fields):
        if f:
            print(f"[{i:2} {repr(f)}")
    
    print(f"\n")
    
    if count >= 5:
        break

print(f"\n\n分析了 {count} 场比赛\n")

# 保存分析一场比赛的全部数据
print("\n保存所有可能的字段解释")
print("-" * 120)

first_line = None
for line in lines:
    line = line.strip()
    if line and len(line.split('|')) > 20:
        first_line = line
        break

if first_line:
    fields = first_line.split('|')
    print(f"总字段数: {len(fields)}")
    print()
    
    for i in range(len(fields)):
        if i < len(fields) and fields[i]:
            print(f"[{i:2}] {repr(fields[i])}")
