
import requests

# 获取今天的数据
url = "https://jc.titan007.com/xml/bf_jc.txt"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'utf-8'

lines = response.text.split('\n')

# 分析字段
print("=" * 100)
print("前3场比赛，完整字段分析：")
print("=" * 100)

count = 0
for line in lines[:10]:
    line = line.strip()
    if not line:
        continue
    fields = line.split('|')
    if len(fields) < 10:
        continue
    
    count += 1
    print(f"\n\n比赛 {count}:")
    print(f"总字段数: {len(fields)}")
    print("-" * 100)
    for i, f in enumerate(fields):
        if f:
            print(f"[{i:2}] {f}")
    print("-" * 100)
    
    if count >= 3:
        break
