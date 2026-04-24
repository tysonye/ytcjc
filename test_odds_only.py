"""测试盘口数据解析"""
import requests
from bs4 import BeautifulSoup

def test_odds_parse():
    """测试解析盘口数据"""
    # 读取之前保存的 HTML
    try:
        with open('test_page.html', 'r', encoding='utf-8') as f:
            html = f.read()
    except:
        # 如果没有保存的文件，重新获取
        url = "http://zq.titan007.com/analysis/2871799.htm"
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
        response = session.get(url, timeout=10)
        response.encoding = 'utf-8'
        html = response.text
    
    soup = BeautifulSoup(html, 'html.parser')
    
    content = []
    tables = soup.find_all('table')
    
    # 1. 全场亚让盘
    content.append("\n【全场亚盘】")
    asian_found = False
    for table in tables:
        table_text = table.get_text(strip=True)
        if '全場' in table_text and '亚讓盤' in table_text:
            if not asian_found:
                asian_found = True
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data and len(row_data) > 1:
                    content.append("  ".join(row_data))
    
    # 2. 半场亚让盘
    content.append("\n【半场亚盘】")
    half_asian_found = False
    for table in tables:
        table_text = table.get_text(strip=True)
        if '半場' in table_text and '亚讓盤' in table_text:
            if not half_asian_found:
                half_asian_found = True
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data and len(row_data) > 1:
                    content.append("  ".join(row_data))
    
    # 3. 进球数
    content.append("\n【进球数】")
    goal_found = False
    for table in tables:
        table_text = table.get_text(strip=True)
        if '進球數' in table_text and ('大球' in table_text or '小球' in table_text):
            if not goal_found:
                goal_found = True
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data and len(row_data) > 1:
                    content.append("  ".join(row_data))
    
    result = "\n".join(content) if content else "暂无盘口数据"
    print(result)
    
    # 保存到文件
    with open('test_odds_result.txt', 'w', encoding='utf-8') as f:
        f.write(result)
    print("\n\n已保存到 test_odds_result.txt")

if __name__ == '__main__':
    test_odds_parse()
