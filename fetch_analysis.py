import requests
import re
from bs4 import BeautifulSoup

# 测试获取分析页面数据
url = "https://zq.titan007.com/analysis/2871799.htm"
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
})

try:
    response = session.get(url, timeout=10)
    response.encoding = 'utf-8'
    html = response.text
    
    print(f"状态码：{response.status_code}")
    print(f"内容长度：{len(html)}")
    
    # 查找赔率表格
    soup = BeautifulSoup(html, 'html.parser')
    
    # 查找所有表格
    tables = soup.find_all('table')
    print(f"\n找到 {len(tables)} 个表格")
    
    for i, table in enumerate(tables[:5]):
        rows = table.find_all('tr')
        print(f"\n表格 {i+1}: {len(rows)} 行")
        for j, row in enumerate(rows[:3]):
            cells = row.find_all(['td', 'th'])
            cell_texts = [cell.get_text(strip=True) for cell in cells[:8]]
            print(f"  行{j+1}: {cell_texts}")
    
    # 查找包含赔率的 div
    odds_divs = soup.find_all('div', class_=lambda x: x and ('odds' in x.lower() or 'data' in x.lower()))
    print(f"\n找到 {len(odds_divs)} 个赔率相关的 div")
    
except Exception as e:
    print(f"错误：{e}")
    import traceback
    traceback.print_exc()
