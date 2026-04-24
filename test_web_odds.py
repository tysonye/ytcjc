import requests
from bs4 import BeautifulSoup

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

# 查找所有表格
tables = soup.find_all('table')
print(f"找到 {len(tables)} 个表格\n")

for i, table in enumerate(tables[:5]):
    rows = table.find_all('tr')
    print(f"表格 {i+1}: {len(rows)} 行")
    
    # 显示前 3 行
    for j, row in enumerate(rows[:3]):
        cells = row.find_all(['td', 'th'])
        cell_texts = [cell.get_text(strip=True) for cell in cells]
        print(f"  行{j+1}: {cell_texts[:10]}")
    
    print()

# 查找包含"勝""平""負"的表格
print("\n查找欧洲指数表格...")
for i, table in enumerate(tables):
    rows = table.find_all('tr')
    if rows:
        first_row_text = ' '.join([cell.get_text(strip=True) for cell in rows[0].find_all(['td', 'th'])])
        if '勝' in first_row_text or '平' in first_row_text or '負' in first_row_text:
            print(f"\n找到欧洲指数表格！表格 {i+1}")
            print(f"表头：{first_row_text}")
            
            # 显示所有数据行
            for j, row in enumerate(rows[1:], 1):
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                print(f"  数据行{j}: {cell_texts[:10]}")
