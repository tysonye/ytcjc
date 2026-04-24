import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
import time
import os
from colorama import init, Fore, Style


init()


class RealTimeMatchMonitor:
    """实时比赛数据监控器"""
    
    def __init__(self, url: str = "https://jc.titan007.com/index.aspx", refresh_interval: int = 60):
        self.url = url
        self.refresh_interval = refresh_interval
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self.previous_matches = []
        self.data_file = 'historical_data.json'
    
    def fetch_page(self) -> Optional[str]:
        """获取网页内容"""
        try:
            response = self.session.get(self.url, timeout=10)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.text
            else:
                print(f"{Fore.RED}获取网页失败，状态码：{response.status_code}{Style.RESET_ALL}")
                return None
        except Exception as e:
            print(f"{Fore.RED}请求异常：{e}{Style.RESET_ALL}")
            return None
    
    def parse_matches(self, html: str) -> List[Dict]:
        """解析比赛数据"""
        soup = BeautifulSoup(html, 'html.parser')
        matches = []
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                match_data = self._parse_match_row(row)
                if match_data and match_data.get('match_id'):
                    matches.append(match_data)
        
        if not matches:
            text_content = soup.get_text()
            lines = text_content.split('\n')
            current_match = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                match_id_match = re.match(r'(周五 | 周六 | 周日)(\d{3})', line)
                if match_id_match:
                    if current_match:
                        matches.append(current_match)
                    current_match = {
                        'match_id': match_id_match.group(0),
                        'league': '',
                        'match_time': '',
                        'status': '',
                        'home_team': '',
                        'away_team': '',
                        'score': '',
                        'odds': {'home': '', 'draw': '', 'away': ''},
                        'analysis': {'ai_prediction': ''}
                    }
                
                if current_match:
                    league_pattern = r'(澳超 | 日职联 | 德甲 | 英超 | 西甲 | 意甲 | 法甲 | 芬超 | 沙特联 | 德乙 | 法乙 | 荷乙 | 葡超 | 韩 K 联 | 亚冠精英 | 荷甲| 法乙)'
                    league_match = re.search(league_pattern, line)
                    if league_match and not current_match['league']:
                        current_match['league'] = league_match.group(1)
                    
                    time_match = re.search(r'(\d{2}:\d{2})', line)
                    if time_match and not current_match['match_time']:
                        current_match['match_time'] = time_match.group(1)
                    
                    if '-' in line and (current_match['home_team'] or current_match['away_team']):
                        parts = line.split('-')
                        if len(parts) == 2 and len(parts[0].strip()) > 0 and len(parts[1].strip()) > 0:
                            if not current_match['home_team']:
                                current_match['home_team'] = parts[0].strip()
                            if not current_match['away_team']:
                                current_match['away_team'] = parts[1].split()[0].strip() if parts[1] else ''
                    
                    odds_matches = re.findall(r'(\d+\.\d{2})', line)
                    if len(odds_matches) >= 3 and not current_match['odds']['home']:
                        current_match['odds'] = {
                            'home': odds_matches[0],
                            'draw': odds_matches[1],
                            'away': odds_matches[2]
                        }
                    
                    if 'AI 预测' in line:
                        current_match['analysis']['ai_prediction'] = line
            
            if current_match:
                matches.append(current_match)
        
        return matches
    
    def _parse_match_row(self, row) -> Optional[Dict]:
        """解析单行比赛数据"""
        cells = row.find_all(['td', 'div'])
        
        if len(cells) < 3:
            return None
        
        match_info = {
            'match_id': '',
            'league': '',
            'match_time': '',
            'status': '',
            'home_team': '',
            'away_team': '',
            'score': '',
            'odds': {'home': '', 'draw': '', 'away': ''},
            'analysis': {'ai_prediction': ''}
        }
        
        for cell in cells:
            text = cell.get_text(strip=True)
            
            if re.match(r'(周五 | 周六 | 周日)\d{3}', text):
                match_info['match_id'] = text
            
            league_pattern = r'(澳超 | 日职联 | 德甲 | 英超 | 西甲 | 意甲 | 法甲 | 芬超 | 沙特联 | 德乙 | 法乙 | 荷乙 | 葡超 | 韩 K 联 | 亚冠精英 | 荷甲)'
            if re.search(league_pattern, text):
                match_info['league'] = text
            
            if re.match(r'\d{2}:\d{2}', text):
                match_info['match_time'] = text
            
            if '-' in text:
                parts = text.split('-')
                if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                    match_info['home_team'] = parts[0].strip()
                    match_info['away_team'] = parts[1].strip()
            
            odds_values = re.findall(r'\d+\.\d{2}', text)
            if len(odds_values) >= 3 and not match_info['odds']['home']:
                match_info['odds'] = {
                    'home': odds_values[0],
                    'draw': odds_values[1],
                    'away': odds_values[2]
                }
            
            if 'AI 预测' in text:
                match_info['analysis']['ai_prediction'] = text
        
        return match_info if match_info['match_id'] else None
    
    def detect_changes(self, new_matches: List[Dict]) -> List[Dict]:
        """检测变化"""
        changes = []
        
        for new_match in new_matches:
            match_id = new_match.get('match_id')
            
            prev_match = next((m for m in self.previous_matches if m.get('match_id') == match_id), None)
            
            if not prev_match:
                changes.append({
                    'type': 'new',
                    'match': new_match
                })
            else:
                if new_match.get('odds') != prev_match.get('odds'):
                    changes.append({
                        'type': 'odds_change',
                        'match': new_match,
                        'old_odds': prev_match.get('odds'),
                        'new_odds': new_match.get('odds')
                    })
                
                if new_match.get('status') != prev_match.get('status'):
                    changes.append({
                        'type': 'status_change',
                        'match': new_match,
                        'old_status': prev_match.get('status'),
                        'new_status': new_match.get('status')
                    })
        
        return changes
    
    def print_changes(self, changes: List[Dict]):
        """打印变化"""
        if not changes:
            print(f"{Fore.GREEN}无变化{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}发现 {len(changes)} 处变化:{Style.RESET_ALL}")
        
        for change in changes:
            match = change['match']
            match_id = match.get('match_id', 'N/A')
            teams = f"{match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')}"
            
            if change['type'] == 'new':
                print(f"\n{Fore.GREEN}[新增比赛] {match_id} - {teams}{Style.RESET_ALL}")
            elif change['type'] == 'odds_change':
                old = change['old_odds']
                new = change['new_odds']
                print(f"\n{Fore.YELLOW}[赔率变化] {match_id} - {teams}{Style.RESET_ALL}")
                print(f"  旧：主{old.get('home', 'N/A')} 平{old.get('draw', 'N/A')} 客{old.get('away', 'N/A')}")
                print(f"  新：主{new.get('home', 'N/A')} 平{new.get('draw', 'N/A')} 客{new.get('away', 'N/A')}")
            elif change['type'] == 'status_change':
                print(f"\n{Fore.RED}[状态变化] {match_id} - {teams}{Style.RESET_ALL}")
                print(f"  {change['old_status']} -> {change['new_status']}")
    
    def save_historical_data(self, matches: List[Dict]):
        """保存历史数据"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'matches': matches
        }
        
        historical = []
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    historical = json.load(f)
            except:
                historical = []
        
        historical.append(data)
        
        if len(historical) > 100:
            historical = historical[-100:]
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(historical, f, ensure_ascii=False, indent=2)
    
    def monitor(self, duration_minutes: Optional[int] = None):
        """开始监控"""
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}竞彩足球实时监控系统{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"目标网址：{self.url}")
        print(f"刷新间隔：{self.refresh_interval}秒")
        if duration_minutes:
            print(f"监控时长：{duration_minutes}分钟")
        else:
            print("监控时长：持续监控 (Ctrl+C 停止)")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        start_time = time.time()
        iteration = 0
        
        try:
            while True:
                iteration += 1
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                print(f"\n[{current_time}] 第 {iteration} 次刷新...")
                
                html = self.fetch_page()
                if not html:
                    print(f"{Fore.RED}获取数据失败，等待下次刷新...{Style.RESET_ALL}")
                    time.sleep(self.refresh_interval)
                    continue
                
                matches = self.parse_matches(html)
                
                if not matches:
                    print(f"{Fore.RED}未能解析到比赛数据{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}获取到 {len(matches)} 场比赛{Style.RESET_ALL}")
                    
                    if self.previous_matches:
                        changes = self.detect_changes(matches)
                        self.print_changes(changes)
                    else:
                        print(f"{Fore.GREEN}首次运行，已获取初始数据{Style.RESET_ALL}")
                    
                    self.save_historical_data(matches)
                    self.previous_matches = matches
                
                if duration_minutes and (time.time() - start_time) > (duration_minutes * 60):
                    print(f"\n{Fore.CYAN}监控时长已达 {duration_minutes} 分钟，停止监控{Style.RESET_ALL}")
                    break
                
                time.sleep(self.refresh_interval)
        
        except KeyboardInterrupt:
            print(f"\n\n{Fore.CYAN}用户中断，停止监控{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}监控结束，数据已保存到 {self.data_file}{Style.RESET_ALL}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='竞彩足球实时监控系统')
    parser.add_argument('--interval', type=int, default=60, help='刷新间隔 (秒)，默认 60 秒')
    parser.add_argument('--duration', type=int, help='监控时长 (分钟)，不指定则持续监控')
    parser.add_argument('--url', type=str, default='https://jc.titan007.com/index.aspx', help='目标网址')
    
    args = parser.parse_args()
    
    monitor = RealTimeMatchMonitor(url=args.url, refresh_interval=args.interval)
    monitor.monitor(duration_minutes=args.duration)


if __name__ == "__main__":
    main()
