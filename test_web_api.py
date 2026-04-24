
import requests
from bs4 import BeautifulSoup

# 添加真实浏览器的请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Referer': 'http://zq.titan007.com/'
}

url = "http://zq.titan007.com/analysis/2913592.htm"

try:
    print(f"正在请求: {url}")
    response = requests.get(url, headers=headers, timeout=15)
    response.encoding = 'utf-8'
    
    print(f"状态码: {response.status_code}")
    print(f"内容长度: {len(response.text)}")
    
    if len(response.text) > 500:
        # 保存到文件
        with open('page_content.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("已保存到 page_content.html")
        
        # 尝试解析
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        print(f"\n找到 {len(tables)} 个表格")
        
        # 查看所有包含特定关键词的表格
        print("\n" + "="*80)
        print("查找包含 '亚盘'、'进球'、'胜平负' 的表格:")
        print("="*80)
        
        for i, table in enumerate(tables):
            table_text = table.get_text(strip=True)
            if any(keyword in table_text for keyword in ['亚盘', '进球', '胜平负', '胜', '平', '负']):
                print(f"\n--- 表格 {i} ---")
                print(f"文本长度: {len(table_text)}")
                print(f"内容预览: {table_text[:400]}")
                
                # 查看前5行
                rows = table.find_all('tr')
                if rows:
                    print("\n前5行:")
                    for j, row in enumerate(rows[:5]):
                        cells = row.find_all(['td', 'th'])
                        cell_text = [c.get_text(strip=True) for c in cells]
                        print(f"  行{j+1}: {' | '.join(cell_text)}")
                
except Exception as e:
    print(f"错误: {e}")
