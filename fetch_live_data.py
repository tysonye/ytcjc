
import requests
import re

# 尝试获取实时数据
# 网页上的时间可能是通过ajax加载的

# 首先获取网页，查找JavaScript中的数据接口
url = "https://jc.titan007.com/index.aspx"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

response = requests.get(url, headers=headers, timeout=15)
response.encoding = 'utf-8'

# 查找JavaScript中的数据URL
js_patterns = [
    r'src\s*=\s*"([^"]*live[^"]*)"',
    r'src\s*=\s*"([^"]*bf[^"]*)"',
    r'url\s*:\s*"([^"]*live[^"]*)"',
    r'url\s*:\s*"([^"]*bf[^"]*)"',
    r'\.get\s*\(\s*"([^"]*live[^"]*)"',
    r'\.get\s*\(\s*"([^"]*bf[^"]*)"',
]

found_urls = []
for pattern in js_patterns:
    matches = re.findall(pattern, response.text, re.IGNORECASE)
    found_urls.extend(matches)

print("找到的实时数据URL:")
for url in set(found_urls):
    print(f"  {url}")

# 也查找iframe
iframe_pattern = r'<iframe[^>]*src\s*=\s*"([^"]*)"'
iframe_matches = re.findall(iframe_pattern, response.text)
print("\n找到的iframe:")
for url in iframe_matches:
    print(f"  {url}")
