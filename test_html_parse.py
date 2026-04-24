
import requests
from bs4 import BeautifulSoup

url = "http://zq.titan007.com/analysis/2913592.htm"
response = requests.get(url)
response.encoding = 'utf-8'
html = response.text

soup = BeautifulSoup(html, 'html.parser')

# 先看看有多少个表格
tables = soup.find_all('table')
print(f"找到 {len(tables)} 个表格\n")

# 打印前5个表格的内容预览
for i, table in enumerate(tables[:5]):
    print(f"\n{'='*60}")
    print(f"表格 {i+1}")
    print(f"{'='*60}")
    
    # 打印表格文本的前300字符
    table_text = table.get_text(strip=True)
    print(f"文本长度: {len(table_text)}")
    print(f"内容预览: {table_text[:200]}...")
    
    # 查看表格的属性
    if table.get('class'):
        print(f"Class: {table.get('class')}")
    
    # 查看前3行
    rows = table.find_all('tr')
    if rows:
        print(f"\n前3行:")
        for j, row in enumerate(rows[:3]):
            cells = row.find_all(['td', 'th'])
            cell_text = [c.get_text(strip=True) for c in cells]
            print(f"  行{j+1}: {' | '.join(cell_text[:5])}")
