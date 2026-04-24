
import requests
import re

url = "https://zq.titan007.com/analysis/2913592.htm"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers, timeout=15)
response.encoding = 'utf-8'

text = response.text

# 搜索特定模式
print("搜索 Vs_eOdds:")
idx = text.find('Vs_eOdds')
if idx > 0:
    print(f"找到位置: {idx}")
    print(text[idx:idx+200])
else:
    print("未找到")

print("\n搜索 Vs_hOdds:")
idx = text.find('Vs_hOdds')
if idx > 0:
    print(f"找到位置: {idx}")
    print(text[idx:idx+200])
else:
    print("未找到")

print("\n搜索 v_data:")
idx = text.find('v_data')
if idx > 0:
    print(f"找到位置: {idx}")
    print(text[idx:idx+200])
