
import requests

url = "http://zq.titan007.com/analysis/2913592.htm"
response = requests.get(url)
response.encoding = 'utf-8'
html = response.text

print(f"状态码: {response.status_code}")
print(f"内容长度: {len(html)}")
print(f"\n{'='*80}")
print("前1500字符:")
print(f"{'='*80}")
print(html[:1500])
print(f"\n{'='*80}")
print("后500字符:")
print(f"{'='*80}")
print(html[-500:])

# 检查是否有iframe或script
if 'iframe' in html.lower():
    print("\n找到 iframe 标签")
if 'script' in html.lower():
    print("找到 script 标签")
