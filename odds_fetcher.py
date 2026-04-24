import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional


class OddsDataFetcher:
    """欧洲指数赔率数据获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        })
    
    def fetch_match_odds(self, match_id: int) -> Optional[Dict]:
        """获取比赛的欧洲指数赔率"""
        url = f"https://zq.titan007.com/analysis/{match_id}.htm"
        
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                return self.parse_european_odds(response.text)
        except Exception as e:
            print(f"获取赔率失败 {match_id}: {e}")
        
        return None
    
    def parse_european_odds(self, html: str) -> Dict:
        """解析欧洲指数赔率"""
        soup = BeautifulSoup(html, 'html.parser')
        
        odds_data = {
            'init': {'home': '', 'draw': '', 'away': ''},
            'current': {'home': '', 'draw': '', 'away': ''},
            'companies': []
        }
        
        # 查找所有表格
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) >= 3:
                # 检查是否是欧洲指数表格
                first_row_text = ' '.join([cell.get_text(strip=True) for cell in rows[0].find_all(['td', 'th'])])
                
                if '勝' in first_row_text or '平' in first_row_text or '負' in first_row_text:
                    # 解析赔率数据
                    for row in rows[1:]:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 10:
                            company_text = cells[0].get_text(strip=True)
                            if '*' in company_text:  # 只取带*的公司（如澳*）
                                # 初盘赔率
                                init_home = cells[1].get_text(strip=True)
                                init_draw = cells[2].get_text(strip=True)
                                init_away = cells[3].get_text(strip=True)
                                
                                # 即时赔率
                                curr_home = cells[4].get_text(strip=True) if len(cells) > 4 else ''
                                curr_draw = cells[5].get_text(strip=True) if len(cells) > 5 else ''
                                curr_away = cells[6].get_text(strip=True) if len(cells) > 6 else ''
                                
                                odds_data['init'] = {
                                    'home': init_home,
                                    'draw': init_draw,
                                    'away': init_away
                                }
                                odds_data['current'] = {
                                    'home': curr_home,
                                    'draw': curr_draw,
                                    'away': curr_away
                                }
                                odds_data['companies'].append(company_text)
                                
                                # 只取第一个公司（澳*）
                                break
        
        return odds_data
    
    def fetch_all_matches_odds(self, matches: List[Dict]) -> Dict[int, Dict]:
        """批量获取所有比赛的赔率数据"""
        all_odds = {}
        
        for match in matches:
            # 从 raw_data 中获取比赛 ID
            raw_data = match.get('raw_data', [])
            if raw_data:
                # 假设第一个字段是比赛 ID
                match_id = raw_data[0]
                if match_id.isdigit():
                    odds = self.fetch_match_odds(int(match_id))
                    if odds:
                        all_odds[int(match_id)] = odds
        
        return all_odds


# 测试
if __name__ == '__main__':
    fetcher = OddsDataFetcher()
    
    # 测试获取某个比赛的赔率
    test_id = 2871799
    odds = fetcher.fetch_match_odds(test_id)
    
    if odds:
        print(f"比赛 {test_id} 的赔率:")
        print(f"初盘：主胜={odds['init']['home']}, 平局={odds['init']['draw']}, 客胜={odds['init']['away']}")
        print(f"即时：主胜={odds['current']['home']}, 平局={odds['current']['draw']}, 客胜={odds['current']['away']}")
        print(f"公司：{odds['companies']}")
