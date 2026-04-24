import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional


class AnalysisDataFetcher:
    """比赛分析数据获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        })
    
    def fetch_analysis(self, match_id: str) -> Optional[Dict]:
        """获取比赛分析数据"""
        # 从 match_id 提取比赛 ID（需要从原始数据中获取）
        # 这里假设 match_id 是 "周五 001" 格式，需要映射到实际 ID
        # 实际使用时需要从原始数据中获取真实的 match_id
        
        # 示例 URL
        url = f"https://zq.titan007.com/analysis/{match_id}.htm"
        
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                return self.parse_analysis(response.text)
            else:
                return None
        except Exception as e:
            print(f"获取分析数据失败：{e}")
            return None
    
    def parse_analysis(self, html: str) -> Dict:
        """解析分析页面数据"""
        soup = BeautifulSoup(html, 'html.parser')
        
        data = {
            'european_odds': [],  # 欧洲指数
            'asian_odds': [],     # 亚洲盘口
            'goal_odds': [],      # 进球数
            'companies': []       # 博彩公司
        }
        
        # 查找所有表格
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 2:
                # 尝试解析赔率表格
                table_data = self.parse_odds_table(rows)
                if table_data:
                    if 'european' in table_data.get('type', ''):
                        data['european_odds'] = table_data['data']
                    elif 'asian' in table_data.get('type', ''):
                        data['asian_odds'] = table_data['data']
                    elif 'goal' in table_data.get('type', ''):
                        data['goal_odds'] = table_data['data']
                    
                    if 'companies' in table_data:
                        data['companies'] = table_data['companies']
        
        return data
    
    def parse_odds_table(self, rows) -> Optional[Dict]:
        """解析赔率表格"""
        # 检测表格类型并解析
        first_row_text = ' '.join([cell.get_text(strip=True) for cell in rows[0].find_all(['td', 'th'])])
        
        if '欧' in first_row_text or '胜' in first_row_text:
            return self.parse_european_odds(rows)
        elif '亚' in first_row_text or '盘' in first_row_text:
            return self.parse_asian_odds(rows)
        elif '球' in first_row_text or '大小' in first_row_text:
            return self.parse_goal_odds(rows)
        
        return None
    
    def parse_european_odds(self, rows) -> Dict:
        """解析欧洲指数"""
        data = []
        companies = []
        
        for row in rows[1:]:  # 跳过表头
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 4:
                company = cells[0].get_text(strip=True)
                if company:
                    companies.append(company)
                    data.append({
                        'company': company,
                        'home': cells[1].get_text(strip=True),
                        'draw': cells[2].get_text(strip=True),
                        'away': cells[3].get_text(strip=True)
                    })
        
        return {
            'type': 'european',
            'data': data,
            'companies': companies
        }
    
    def parse_asian_odds(self, rows) -> Dict:
        """解析亚洲盘口"""
        data = []
        companies = []
        
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 6:
                company = cells[0].get_text(strip=True)
                if company:
                    companies.append(company)
                    data.append({
                        'company': company,
                        'handicap': cells[2].get_text(strip=True),
                        'home_water': cells[1].get_text(strip=True),
                        'away_water': cells[3].get_text(strip=True)
                    })
        
        return {
            'type': 'asian',
            'data': data,
            'companies': companies
        }
    
    def parse_goal_odds(self, rows) -> Dict:
        """解析进球数赔率"""
        data = []
        companies = []
        
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 4:
                company = cells[0].get_text(strip=True)
                if company:
                    companies.append(company)
                    data.append({
                        'company': company,
                        'goal_line': cells[1].get_text(strip=True),
                        'big_water': cells[2].get_text(strip=True),
                        'small_water': cells[3].get_text(strip=True)
                    })
        
        return {
            'type': 'goal',
            'data': data,
            'companies': companies
        }


# 测试
if __name__ == '__main__':
    fetcher = AnalysisDataFetcher()
    data = fetcher.fetch_analysis('2871799')
    
    if data:
        print("欧洲指数:")
        for item in data['european_odds'][:3]:
            print(f"  {item}")
        
        print("\n亚洲盘口:")
        for item in data['asian_odds'][:3]:
            print(f"  {item}")
        
        print("\n进球数:")
        for item in data['goal_odds'][:3]:
            print(f"  {item}")
