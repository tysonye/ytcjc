import requests
import json
import re
from datetime import datetime
from typing import List, Dict, Optional


class MatchScraper:
    """竞彩足球比赛数据爬虫"""
    
    def __init__(self, url: str = "https://jc.titan007.com/xml/bf_jc.txt"):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        })
    
    def fetch_page(self) -> Optional[str]:
        """获取网页内容"""
        try:
            response = self.session.get(self.url, timeout=10)
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                return content
            else:
                print(f"获取网页失败，状态码：{response.status_code}")
                return None
        except Exception as e:
            print(f"请求异常：{e}")
            return None
    
    def parse_matches(self, content: str) -> List[Dict]:
        """解析比赛数据"""
        matches = []
        
        if not content or '$' not in content:
            print("数据格式不正确")
            return matches
        
        parts = content.split('$')
        
        if len(parts) < 2:
            return matches
        
        league_data = parts[0]
        match_data = parts[1] if len(parts) > 1 else ""
        
        league_info = {}
        league_entries = league_data.split('!')
        for entry in league_entries:
            if '^' in entry:
                league_parts = entry.split('^')
                if len(league_parts) >= 4:
                    league_id = league_parts[0]
                    league_name = league_parts[3].split(',')[0] if len(league_parts) > 3 else ""
                    league_info[league_id] = league_name
        
        match_entries = match_data.split('!')
        
        for entry in match_entries:
            if not entry.strip():
                continue
            
            fields = entry.split('^')
            
            if len(fields) < 20:
                continue
            
            try:
                match_id = fields[4] if len(fields) > 4 else ""
                
                if not match_id or not re.match(r'周.+\d{3}', match_id):
                    continue
                
                league_id = fields[5] if len(fields) > 5 else ""
                league_name = league_info.get(league_id, "")
                
                start_time = fields[1] if len(fields) > 1 else ""
                
                home_team_full = fields[8] if len(fields) > 8 else ""
                home_team = home_team_full.split(',')[2] if ',' in home_team_full else home_team_full
                
                away_team_full = fields[10] if len(fields) > 10 else ""
                away_team = away_team_full.split(',')[2] if ',' in away_team_full else away_team_full
                
                home_score = fields[11] if len(fields) > 11 else "0"
                away_score = fields[12] if len(fields) > 12 else "0"
                
                status = fields[3] if len(fields) > 3 else "0"
                status_map = {
                    '0': '未开始',
                    '1': '进行中',
                    '2': '已完场',
                    '3': '中场'
                }
                status_text = status_map.get(status, '未知')
                
                home_odd = fields[21] if len(fields) > 21 else ""
                draw_odd = ""
                away_odd = ""
                
                time_parts = start_time.split(',')
                if len(time_parts) >= 5:
                    match_time = f"{time_parts[3]}:{time_parts[4]}"
                else:
                    match_time = ""
                
                match_info = {
                    'match_id': match_id.strip(),
                    'league': league_name,
                    'match_time': match_time,
                    'start_time': start_time,
                    'status': status_text,
                    'home_team': home_team.strip(),
                    'away_team': away_team.strip(),
                    'score': f"{home_score}:{away_score}" if home_score != '0' or away_score != '0' else '',
                    'odds': {
                        'home': home_odd,
                        'draw': draw_odd,
                        'away': away_odd
                    },
                    'league_id': league_id,
                }
                matches.append(match_info)
                
            except Exception as e:
                continue
        
        return matches
    
    def get_all_matches(self) -> List[Dict]:
        """获取所有比赛数据"""
        content = self.fetch_page()
        if not content:
            return []
        
        return self.parse_matches(content)
    
    def print_matches(self, matches: List[Dict]):
        """打印比赛信息"""
        print(f"\n{'='*80}")
        print(f"获取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"比赛场次总数：{len(matches)}")
        print(f"{'='*80}\n")
        
        for i, match in enumerate(matches, 1):
            print(f"[{i}] {match.get('match_id', 'N/A')}")
            print(f"    联赛：{match.get('league', 'N/A')}")
            print(f"    时间：{match.get('match_time', 'N/A')}")
            print(f"    状态：{match.get('status', 'N/A')}")
            print(f"    对阵：{match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')}")
            print(f"    比分：{match.get('score', 'N/A')}")
            
            odds = match.get('odds', {})
            if odds.get('home'):
                print(f"    赔率：主胜 {odds.get('home')} | 平 {odds.get('draw')} | 客胜 {odds.get('away')}")
            
            print()


def main():
    """主函数"""
    print("竞彩足球比赛数据获取与盘口分析系统")
    print("="*80)
    
    scraper = MatchScraper()
    
    print("\n正在获取比赛数据...")
    matches = scraper.get_all_matches()
    
    if not matches:
        print("未能获取到比赛数据，请检查网络连接或数据接口是否变化")
        return
    
    scraper.print_matches(matches)
    
    print("\n数据获取完成！")
    
    with open('matches_data.json', 'w', encoding='utf-8') as f:
        json.dump({
            'fetch_time': datetime.now().isoformat(),
            'total_matches': len(matches),
            'matches': matches
        }, f, ensure_ascii=False, indent=2)
    
    print(f"数据已保存到 matches_data.json")


if __name__ == "__main__":
    main()
