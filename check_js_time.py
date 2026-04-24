
import requests
import re

url = "https://jc.titan007.com/index.aspx"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers, timeout=15)
response.encoding = 'utf-8'

# 查找JavaScript中的时间数据
# 通常格式: var match_time = {...} 或类似
patterns = [
    r'var\s+\w+\s*=\s*\[.*?\];',
    r'"time"\s*:\s*"(\d+)"',
    r'class="t\s+red"\s*>(\d+)<',
]

for pattern in patterns:
    matches = re.findall(pattern, response.text, re.DOTALL)
    if matches:
        print(f"找到匹配 (pattern: {pattern[:30]}...):")
        for m in matches[:5]:
            print(f"  {m}")
        print()

# 查找特定比赛的HTML
time_pattern = r'<td[^>]*id="time_\d+"[^>]*>.*?<i[^>]*>(\d+)</i>.*?</td>'
time_matches = re.findall(time_pattern, response.text, re.DOTALL)
if time_matches:
    print(f"找到 {len(time_matches)} 个时间td")
    for t in time_matches[:10]:
        print(f"  时间: {t}")
