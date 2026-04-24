"""测试网页数据解析"""
import requests
from bs4 import BeautifulSoup

def test_parse():
    """测试解析网页数据"""
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
    
    # 标题
    title = soup.find('title')
    if title:
        content.append(f"【比赛信息】\n{title.get_text(strip=True)}\n")
    
    tables = soup.find_all('table')
    
    # 1. 战绩统计
    print("=" * 80)
    print("【战绩统计】")
    print("=" * 80)
    stats_found = False
    for table in tables:
        table_text = table.get_text(strip=True)
        if '總' in table_text and '主' in table_text and '客' in table_text and '勝率' in table_text:
            if not stats_found:
                stats_found = True
            rows = table.find_all('tr')
            for row in rows[:6]:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data:
                    print("  ".join(row_data))
    
    # 2. 盘路走势
    print("\n" + "=" * 80)
    print("【盘路走势】")
    print("=" * 80)
    path_found = False
    for table in tables:
        table_text = table.get_text(strip=True)
        if '初盘' in table_text and ('赢' in table_text or '輸' in table_text):
            if not path_found:
                path_found = True
            rows = table.find_all('tr')
            for row in rows[:10]:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data and len(row_data) > 1:
                    print("  ".join(row_data))
    
    # 3. 半场/全场统计
    print("\n" + "=" * 80)
    print("【半场/全场统计】")
    print("=" * 80)
    half_found = False
    for table in tables:
        table_text = table.get_text(strip=True)
        if '半場' in table_text and '全場' in table_text:
            if not half_found:
                half_found = True
            rows = table.find_all('tr')
            for row in rows[:6]:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data:
                    print("  ".join(row_data))
    
    # 4. 净胜球统计
    print("\n" + "=" * 80)
    print("【净胜球统计】")
    print("=" * 80)
    goal_diff_found = False
    for table in tables:
        table_text = table.get_text(strip=True)
        if '凈勝' in table_text or '凈輸' in table_text:
            if not goal_diff_found:
                goal_diff_found = True
            rows = table.find_all('tr')
            for row in rows[:8]:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data:
                    print("  ".join(row_data))

if __name__ == '__main__':
    test_parse()
