"""测试网页数据获取"""
import requests
from bs4 import BeautifulSoup

def test_fetch():
    """测试获取网页数据"""
    url = "http://zq.titan007.com/analysis/2871799.htm"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    })
    
    try:
        response = session.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        print(f"状态码：{response.status_code}")
        print(f"内容长度：{len(response.text)}")
        
        # 保存 HTML 到文件以便分析
        with open('test_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print("\n已保存 HTML 到 test_page.html")
        
        # 解析并查找赔率表格
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有表格
        tables = soup.find_all('table')
        print(f"\n找到 {len(tables)} 个表格")
        
        # 查找包含赔率数据的表格
        for i, table in enumerate(tables):
            table_text = table.get_text(strip=True)
            if '初' in table_text or '即' in table_text or '勝' in table_text or '赔' in table_text:
                print(f"\n表格 {i} 包含赔率数据:")
                print(f"内容预览：{table_text[:200]}...")
                
                # 打印表格结构
                rows = table.find_all('tr')
                print(f"行数：{len(rows)}")
                for j, row in enumerate(rows[:5]):
                    cells = row.find_all(['td', 'th'])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    print(f"  行{j}: {row_data}")
        
        # 查找特定 div
        print("\n\n查找包含数据的 div:")
        for div in soup.find_all('div', class_=lambda x: x and ('data' in x.lower() or 'odds' in x.lower())):
            print(f"Div: {div.get('class')} - {div.get_text(strip=True)[:100]}")
            
    except Exception as e:
        print(f"错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_fetch()
