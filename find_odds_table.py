import requests
from bs4 import BeautifulSoup
import re

# 测试获取赔率数据
url = "http://zq.titan007.com/analysis/2871799.htm"
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
})

response = session.get(url, timeout=10)
response.encoding = 'utf-8'
html = response.text

soup = BeautifulSoup(html, 'html.parser')

# 查找包含"初"或"即"的所有文字
all_text = soup.get_text()
lines = all_text.split('\n')

print("查找包含'初'和'即'以及赔率数字的行:")
for i, line in enumerate(lines):
    if ('初' in line or '即' in line) and re.search(r'\d+\.\d{2}', line):
        # 清理文本
        clean_line = ' '.join(line.split())
        print(f"\n行{i}: {clean_line[:200]}")

# 查找所有包含赔率数字的表格
print("\n\n查找包含赔率数字的表格:")
tables = soup.find_all('table')

for i, table in enumerate(tables):
    text = table.get_text()
    # 检查是否包含初盘和即时盘赔率
    if re.search(r'初.*?\d+\.\d{2}.*?\d+\.\d{2}.*?\d+\.\d{2}', text) or \
       re.search(r'即.*?\d+\.\d{2}.*?\d+\.\d{2}.*?\d+\.\d{2}', text):
        print(f"\n表格 {i}: 可能包含赔率")
        rows = table.find_all('tr')
        for j, row in enumerate(rows[:5]):
            cells = row.find_all(['td', 'th'])
            cell_texts = [cell.get_text(strip=True) for cell in cells[:10]]
            print(f"  行{j}: {cell_texts}")
