import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
import threading
import random
from bs4 import BeautifulSoup
from odds_display import OddsTableDisplay


class MatchScraper:
    """竞彩足球比赛数据爬虫"""

    def __init__(self):
        self.today_url = "https://jc.titan007.com/xml/bf_jc.txt"
        self.history_url = "https://jc.titan007.com/handle/JcResult.aspx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        })

    def get_url_for_date(self, date_str: str) -> str:
        """根据日期获取对应的URL"""
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        if date_str == today:
            return self.today_url
        else:
            return f"{self.history_url}?d={date_str}"

    def fetch_page(self, url: Optional[str] = None) -> Optional[str]:
        """获取网页内容"""
        try:
            target_url = url or self.base_url
            response = self.session.get(target_url, timeout=10)
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                return content
            else:
                return None
        except Exception as e:
            print(f"请求异常：{e}")
            return None

    def parse_matches(self, content: str) -> List[Dict]:
        """解析比赛数据"""
        matches = []

        if not content or '$' not in content:
            return matches

        parts = content.split('$')

        if len(parts) < 2:
            return matches

        league_data = parts[0]
        match_data = parts[1] if len(parts) > 1 else ""

        league_info = {}
        league_entries = league_data.split('!')
        for entry in league_entries:
            if not entry.strip():
                continue
            if '^' in entry:
                league_parts = entry.split('^')
                if len(league_parts) >= 4:
                    league_id = league_parts[0]
                    league_name_raw = league_parts[3] if len(league_parts) > 3 else ""
                    if ',' in league_name_raw:
                        name_parts = league_name_raw.split(',')
                        league_name = name_parts[1].strip() if len(name_parts) >= 2 else name_parts[0].strip()
                    else:
                        league_name = league_name_raw.strip()
                    league_info[league_id] = league_name

        match_entries = match_data.split('!')

        for entry in match_entries:
            if not entry.strip():
                continue

            fields = entry.split('^')

            if len(fields) < 24:
                continue

            try:
                match_id = fields[4] if len(fields) > 4 else ""

                if not match_id or not re.match(r'周[一二三四五六日]\d{3}', match_id):
                    continue

                league_id = fields[5] if len(fields) > 5 else ""
                league_name = league_info.get(league_id, "")

                match_unique_id = fields[0] if len(fields) > 0 else ""
                start_time_str = fields[1] if len(fields) > 1 else ""
                update_time_str = fields[2] if len(fields) > 2 else ""
                status_code = fields[3] if len(fields) > 3 else ""

                home_team_id = fields[7] if len(fields) > 7 else ""
                home_team_full = fields[8] if len(fields) > 8 else ""

                away_team_id = fields[9] if len(fields) > 9 else ""
                away_team_full = fields[10] if len(fields) > 10 else ""

                home_full_score = fields[11] if len(fields) > 11 else ""
                away_full_score = fields[12] if len(fields) > 12 else ""
                home_jc_score = fields[13] if len(fields) > 13 else ""
                away_jc_score = fields[14] if len(fields) > 14 else ""

                red_yellow = fields[15] if len(fields) > 15 else ""
                handicap = fields[22] if len(fields) > 22 else ""
                other_flag = fields[23] if len(fields) > 23 else ""

                home_team = ""
                if ',' in home_team_full:
                    home_team = home_team_full.split(',')[0].strip()
                else:
                    home_team = home_team_full.strip()

                away_team = ""
                if ',' in away_team_full:
                    away_team = away_team_full.split(',')[0].strip()
                else:
                    away_team = away_team_full.strip()

                match_time = ""
                time_parts = start_time_str.split(',')
                if len(time_parts) >= 5:
                    match_time = f"{time_parts[3]}:{time_parts[4]}"

                # 状态映射 - 基于球探网实际状态码
                # 0=未开始, 1=上半场, 2=已完场, 3=下半场, -1=已完场
                # 注意：网页上显示69',70',71'等时间时，状态码实际上是3（下半场进行中）
                status_map = {
                    '0': '未开始',
                    '1': '上半场',
                    '2': '中场',
                    '3': '下半场',  # 状态码3实际表示下半场进行中
                    '4': '加时',
                    '-1': '已完场'
                }
                status_text = status_map.get(status_code, '未知')

                score = f"{home_full_score}:{away_full_score}"
                jc_score = f"{home_jc_score}:{away_jc_score}"

                match_info = {
                    'match_id': match_id.strip(),
                    'match_unique_id': match_unique_id,
                    'league': league_name,
                    'league_id': league_id,
                    'match_time': match_time,
                    'start_time': start_time_str,
                    'update_time': update_time_str,
                    'status': status_text,
                    'status_code': status_code,
                    'home_team': home_team,
                    'home_team_id': home_team_id,
                    'home_team_full': home_team_full,
                    'away_team': away_team,
                    'away_team_id': away_team_id,
                    'away_team_full': away_team_full,
                    'score': score,
                    'jc_score': jc_score,
                    'home_score': home_full_score,
                    'away_score': away_full_score,
                    'home_jc_score': home_jc_score,
                    'away_jc_score': away_jc_score,
                    'handicap': handicap,
                    'red_yellow': red_yellow,
                    'other_flag': other_flag,
                    'raw_data': fields
                }

                matches.append(match_info)

            except Exception as e:
                print(f"解析比赛失败：{e}")
                continue

        return matches

    def fetch_web_time(self, match_unique_id: str) -> str:
        """从网页获取服务器时间差 - 用于精确计算比赛时间"""
        return ""

    def get_all_matches(self, date_str: Optional[str] = None) -> List[Dict]:
        """获取所有比赛数据"""
        from datetime import datetime
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')

        url = self.get_url_for_date(date_str)
        content = self.fetch_page(url)

        if not content:
            return []

        matches = self.parse_matches(content)
        return matches

    def fetch_match_analysis(self, match: Dict) -> Dict:
        """获取比赛分析数据"""
        match_unique_id = match.get('match_unique_id', '')
        if not match_unique_id:
            return {}

        url = f"https://zq.titan007.com/analysis/{match_unique_id}.htm"
        print(f"正在获取分析页面: {url}")

        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code == 200:
                analysis_data = self.parse_analysis_data(response.text)
                # 获取即时走势赔率数据
                odds_data = self.fetch_odds_trend(match_unique_id)
                if odds_data:
                    analysis_data['odds_trend'] = odds_data
                # 获取竞彩指数数据
                jc_odds = self.fetch_jc_odds(match_unique_id)
                if jc_odds:
                    analysis_data['jc_odds'] = jc_odds
                return analysis_data
        except Exception as e:
            print(f"获取分析页面失败: {e}")

        return {}

    def fetch_odds_trend(self, schedule_id: str) -> List[Dict]:
        """获取即时走势赔率数据 - 让球/大小球/欧洲指数"""
        try:
            url = f"https://zq.titan007.com/analysis/odds/{schedule_id}.htm"
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return []

            content = response.content.decode('utf-8', errors='replace')
            return self._parse_odds_trend(content)
        except Exception as e:
            print(f"获取走势数据失败: {e}")
            return []

    def fetch_jc_odds(self, schedule_id: str) -> Dict:
        """获取竞彩指数数据 - 从live.titan007.com/jsData/获取sOdds"""
        try:
            path = schedule_id[:2] + "/" + schedule_id[2:4] + "/"
            url = f"https://live.titan007.com/jsData/{path}{schedule_id}.js"
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return {}
            content = response.content.decode('utf-8', errors='replace')
            return self._parse_jc_odds(content)
        except Exception as e:
            print(f"获取竞彩指数失败: {e}")
            return {}

    def _parse_jc_odds(self, content: str) -> Dict:
        """解析sOdds竞彩指数数据
        sOdds[0] = [时间, 主分, 客分,
          让球半场: [3]主水,[4]盘口,[5]客水,[6]主水即时,[7]盘口即时,[8]客水即时,
          让球全场: [9]主水,[10]盘口,[11]客水,[12]主水即时,[13]盘口即时,[14]客水即时,
          进球数半场: [15]大水,[16]盘口,[17]小水,[18]大水即时,[19]盘口即时,[20]小水即时,
          进球数全场: [21]大水,[22]盘口,[23]小水,[24]大水即时,[25]盘口即时,[26]小水即时,
          欧指半场: [27]主胜,[28]平局,[29]客胜,[30]主胜即时,[31]平局即时,[32]客胜即时,
          欧指全场: [33]主胜,[34]平局,[35]客胜,[36]主胜即时,[37]平局即时,[38]客胜即时,
          [39]状态, ...
        ]
        """
        match = re.search(r'var\s+sOdds\s*=\s*\[\[(.+?)\]\]', content)
        if not match:
            return {}
        raw = match.group(1)
        vals = raw.split(',')
        if len(vals) < 39:
            return {}

        def safe_float(idx):
            try:
                v = vals[idx].strip().strip("'\"")
                return v if v else ''
            except:
                return ''

        return {
            'asian_half_init_home': safe_float(3),
            'asian_half_init_hcp': safe_float(4),
            'asian_half_init_away': safe_float(5),
            'asian_half_curr_home': safe_float(6),
            'asian_half_curr_hcp': safe_float(7),
            'asian_half_curr_away': safe_float(8),
            'asian_full_init_home': safe_float(9),
            'asian_full_init_hcp': safe_float(10),
            'asian_full_init_away': safe_float(11),
            'asian_full_curr_home': safe_float(12),
            'asian_full_curr_hcp': safe_float(13),
            'asian_full_curr_away': safe_float(14),
            'goal_half_init_big': safe_float(15),
            'goal_half_init_line': safe_float(16),
            'goal_half_init_small': safe_float(17),
            'goal_half_curr_big': safe_float(18),
            'goal_half_curr_line': safe_float(19),
            'goal_half_curr_small': safe_float(20),
            'goal_full_init_big': safe_float(21),
            'goal_full_init_line': safe_float(22),
            'goal_full_init_small': safe_float(23),
            'goal_full_curr_big': safe_float(24),
            'goal_full_curr_line': safe_float(25),
            'goal_full_curr_small': safe_float(26),
            'eu_half_init_home': safe_float(27),
            'eu_half_init_draw': safe_float(28),
            'eu_half_init_away': safe_float(29),
            'eu_half_curr_home': safe_float(30),
            'eu_half_curr_draw': safe_float(31),
            'eu_half_curr_away': safe_float(32),
            'eu_full_init_home': safe_float(33),
            'eu_full_init_draw': safe_float(34),
            'eu_full_init_away': safe_float(35),
            'eu_full_curr_home': safe_float(36),
            'eu_full_curr_draw': safe_float(37),
            'eu_full_curr_away': safe_float(38),
        }

    def _parse_odds_trend(self, content: str) -> List[Dict]:
        """解析走势数据 - /analysis/odds/ 响应格式
        格式: <input type='hidden' value='公司1数据^公司2数据...'>
        每个公司: companyID;companyName;初盘;即时;滚球;状态
        每组14值: 欧指(3)+欧转亚盘(4)+实际亚盘(4)+进球数(3)
        """
        results = []
        value_match = re.search(r"value='([^']+)'", content)
        if not value_match:
            return results

        raw_data = value_match.group(1)
        company_entries = raw_data.split('^')

        for entry in company_entries:
            if not entry.strip():
                continue
            parts = entry.split(';')
            if len(parts) < 5:
                continue

            company_id = parts[0]
            company_name = parts[1]
            init_str = parts[2].rstrip(',')
            curr_str = parts[3].rstrip(',')
            live_str = parts[4].rstrip(',') if len(parts) > 4 else ''

            init_vals = init_str.split(',') if init_str else []
            curr_vals = curr_str.split(',') if curr_str else []
            live_vals = live_str.split(',') if live_str else []

            def safe_get(arr, idx, default=''):
                if idx < len(arr):
                    v = arr[idx].strip()
                    return v if v else default
                return default

            item = {
                'company_id': company_id,
                'company': company_name,
                'eu_init_home': safe_get(init_vals, 0),
                'eu_init_draw': safe_get(init_vals, 1),
                'eu_init_away': safe_get(init_vals, 2),
                'eua_init_home': safe_get(init_vals, 3),
                'eua_init_handicap': safe_get(init_vals, 4),
                'eua_init_away': safe_get(init_vals, 5),
                'eua_init_total': safe_get(init_vals, 6),
                'real_init_home': safe_get(init_vals, 7),
                'real_init_handicap': safe_get(init_vals, 8),
                'real_init_away': safe_get(init_vals, 9),
                'real_init_total': safe_get(init_vals, 10),
                'goal_init_big': safe_get(init_vals, 11),
                'goal_init_line': safe_get(init_vals, 12),
                'goal_init_small': safe_get(init_vals, 13),
                'eu_curr_home': safe_get(curr_vals, 0),
                'eu_curr_draw': safe_get(curr_vals, 1),
                'eu_curr_away': safe_get(curr_vals, 2),
                'eua_curr_home': safe_get(curr_vals, 3),
                'eua_curr_handicap': safe_get(curr_vals, 4),
                'eua_curr_away': safe_get(curr_vals, 5),
                'eua_curr_total': safe_get(curr_vals, 6),
                'real_curr_home': safe_get(curr_vals, 7),
                'real_curr_handicap': safe_get(curr_vals, 8),
                'real_curr_away': safe_get(curr_vals, 9),
                'real_curr_total': safe_get(curr_vals, 10),
                'goal_curr_big': safe_get(curr_vals, 11),
                'goal_curr_line': safe_get(curr_vals, 12),
                'goal_curr_small': safe_get(curr_vals, 13),
                'eu_live_home': safe_get(live_vals, 0),
                'eu_live_draw': safe_get(live_vals, 1),
                'eu_live_away': safe_get(live_vals, 2),
                'eua_live_home': safe_get(live_vals, 3),
                'eua_live_handicap': safe_get(live_vals, 4),
                'eua_live_away': safe_get(live_vals, 5),
                'eua_live_total': safe_get(live_vals, 6),
                'real_live_home': safe_get(live_vals, 7),
                'real_live_handicap': safe_get(live_vals, 8),
                'real_live_away': safe_get(live_vals, 9),
                'real_live_total': safe_get(live_vals, 10),
                'goal_live_big': safe_get(live_vals, 11),
                'goal_live_line': safe_get(live_vals, 12),
                'goal_live_small': safe_get(live_vals, 13),
            }
            results.append(item)

        print(f"解析走势数据: {len(results)} 个公司")
        return results

    def parse_analysis_data(self, html: str) -> Dict:
        """解析分析页面数据 - 增强版"""
        soup = BeautifulSoup(html, 'html.parser')

        analysis_data = {
            'european_odds': [],
            'asian_odds': [],
            'goal_odds': [],
            'trend_data': [],
            'league_standings': {'home': [], 'away': []},
            'h2h_records': [],
            'home_recent': [],
            'away_recent': [],
            'half_full_stats': {'home': {}, 'away': {}},
            'goal_stats': {'home': {}, 'away': {}},
            'match_info': {},
            'instant_eu_odds': {}
        }

        self._parse_vs_eodds(html, analysis_data)

        # 解析联赛积分排名
        self._parse_league_standings(soup, analysis_data)

        # 解析对赛往绩
        self._parse_h2h_records(soup, analysis_data)

        # 解析近期战绩
        self._parse_recent_form(soup, analysis_data)

        # 解析半全场统计
        self._parse_half_full_stats(soup, analysis_data)

        # 解析进球数统计
        self._parse_goal_stats(soup, analysis_data)

        # 解析赔率表格
        self._parse_odds_tables(soup, analysis_data)

        # 解析即时走势数据
        self._parse_trend_data(soup, analysis_data)

        return analysis_data

    def _parse_vs_eodds(self, html: str, analysis_data: Dict):
        """从分析页面提取Vs_eOdds即时欧指数据"""
        try:
            import json
            e_match = re.search(r'var\s+Vs_eOdds\s*=\s*(\[.+?\]);', html, re.DOTALL)
            if not e_match:
                return
            e_odds = json.loads(e_match.group(1).replace("'", '"'))
            company_names = {3: 'Crow*', 1: '澳*', 8: '36*', 12: '易胜*', 4: '立*', 18: '12*', 115: '威廉希*', 281: '36*', 80: '澳*'}
            priority = [3, 1, 8, 12, 4, 18, 115, 281, 80]
            for cid in priority:
                for item in e_odds:
                    if len(item) >= 8 and item[1] == cid:
                        analysis_data['instant_eu_odds'] = {
                            'company': company_names.get(cid, str(cid)),
                            'init_home': item[2],
                            'init_draw': item[3],
                            'init_away': item[4],
                            'curr_home': item[5],
                            'curr_draw': item[6],
                            'curr_away': item[7],
                        }
                        return
        except Exception as e:
            print(f"解析Vs_eOdds失败: {e}")

    def _parse_league_standings(self, soup, analysis_data):
        """解析联赛积分排名"""
        try:
            # 查找包含积分排名的表格
            tables = soup.find_all('table')
            for table in tables:
                text = table.get_text()
                if '排名' in text and '赛' in text and '胜' in text:
                    rows = table.find_all('tr')
                    if len(rows) >= 3:
                        current_team = None
                        for row in rows:
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 10:
                                row_text = [c.get_text(strip=True) for c in cells]
                                # 检测是否是球队名称行
                                if len(row_text) == 1 and row_text[0]:
                                    current_team = row_text[0]
                                elif current_team and row_text[0].isdigit():
                                    # 数据行
                                    data = {
                                        'rank': row_text[0],
                                        'team': current_team,
                                        'played': row_text[1] if len(row_text) > 1 else '',
                                        'won': row_text[2] if len(row_text) > 2 else '',
                                        'drawn': row_text[3] if len(row_text) > 3 else '',
                                        'lost': row_text[4] if len(row_text) > 4 else '',
                                        'gf': row_text[5] if len(row_text) > 5 else '',
                                        'ga': row_text[6] if len(row_text) > 6 else '',
                                        'gd': row_text[7] if len(row_text) > 7 else '',
                                        'points': row_text[8] if len(row_text) > 8 else '',
                                        'win_rate': row_text[9] if len(row_text) > 9 else ''
                                    }
                                    if 'home' not in analysis_data['league_standings'] or not analysis_data['league_standings']['home']:
                                        analysis_data['league_standings']['home'].append(data)
                                    else:
                                        analysis_data['league_standings']['away'].append(data)
        except Exception as e:
            print(f"解析联赛排名失败: {e}")

    def _parse_h2h_records(self, soup, analysis_data):
        """解析对赛往绩"""
        try:
            # 查找对赛往绩表格
            tables = soup.find_all('table')
            for table in tables:
                text = table.get_text()
                if '对赛往绩' in text or ('日期' in text and '赛事' in text and '主队' in text):
                    rows = table.find_all('tr')
                    if len(rows) >= 2:
                        for row in rows[1:]:
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 7:
                                analysis_data['h2h_records'].append({
                                    'date': cells[0].get_text(strip=True),
                                    'league': cells[1].get_text(strip=True),
                                    'home_team': cells[2].get_text(strip=True),
                                    'score': cells[3].get_text(strip=True),
                                    'away_team': cells[4].get_text(strip=True),
                                    'handicap': cells[5].get_text(strip=True),
                                    'result': cells[6].get_text(strip=True)
                                })
        except Exception as e:
            print(f"解析对赛往绩失败: {e}")

    def _parse_recent_form(self, soup, analysis_data):
        """解析近期战绩"""
        try:
            tables = soup.find_all('table')
            for table in tables:
                text = table.get_text()
                if '近期战绩' in text or ('日期' in text and '比分' in text):
                    rows = table.find_all('tr')
                    if len(rows) >= 2:
                        for row in rows[1:]:
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 7:
                                record = {
                                    'date': cells[0].get_text(strip=True),
                                    'league': cells[1].get_text(strip=True),
                                    'home_team': cells[2].get_text(strip=True),
                                    'score': cells[3].get_text(strip=True),
                                    'away_team': cells[4].get_text(strip=True),
                                    'handicap': cells[5].get_text(strip=True),
                                    'result': cells[6].get_text(strip=True)
                                }
                                # 简单区分主客队近期战绩
                                if len(analysis_data['home_recent']) <= len(analysis_data['away_recent']):
                                    analysis_data['home_recent'].append(record)
                                else:
                                    analysis_data['away_recent'].append(record)
        except Exception as e:
            print(f"解析近期战绩失败: {e}")

    def _parse_half_full_stats(self, soup, analysis_data):
        """解析半全场统计"""
        try:
            tables = soup.find_all('table')
            for table in tables:
                text = table.get_text()
                if '半全场' in text or ('半场' in text and '赛' in text and '胜' in text):
                    rows = table.find_all('tr')
                    if len(rows) >= 3:
                        stats = []
                        for row in rows[1:]:
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 9:
                                stats.append({
                                    'type': cells[0].get_text(strip=True),
                                    'played': cells[1].get_text(strip=True),
                                    'won': cells[2].get_text(strip=True),
                                    'drawn': cells[3].get_text(strip=True),
                                    'lost': cells[4].get_text(strip=True),
                                    'gf': cells[5].get_text(strip=True),
                                    'ga': cells[6].get_text(strip=True),
                                    'gd': cells[7].get_text(strip=True),
                                    'win_rate': cells[8].get_text(strip=True)
                                })
                        if stats:
                            analysis_data['half_full_stats']['home'] = stats[:3]
                            analysis_data['half_full_stats']['away'] = stats[3:6]
        except Exception as e:
            print(f"解析半全场统计失败: {e}")

    def _parse_goal_stats(self, soup, analysis_data):
        """解析进球数统计"""
        try:
            tables = soup.find_all('table')
            for table in tables:
                text = table.get_text()
                if '进球数' in text or ('0球' in text and '1球' in text):
                    rows = table.find_all('tr')
                    if len(rows) >= 2:
                        for row in rows[1:]:
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 9:
                                data = {
                                    'type': cells[0].get_text(strip=True),
                                    '0': cells[1].get_text(strip=True),
                                    '1': cells[2].get_text(strip=True),
                                    '2': cells[3].get_text(strip=True),
                                    '3': cells[4].get_text(strip=True),
                                    '4': cells[5].get_text(strip=True),
                                    '5': cells[6].get_text(strip=True),
                                    '6': cells[7].get_text(strip=True),
                                    '7+': cells[8].get_text(strip=True)
                                }
                                if 'home' not in analysis_data['goal_stats'] or not analysis_data['goal_stats'].get('home'):
                                    analysis_data['goal_stats']['home'] = data
                                else:
                                    analysis_data['goal_stats']['away'] = data
        except Exception as e:
            print(f"解析进球数统计失败: {e}")

    def _parse_odds_tables(self, soup, analysis_data):
        """解析赔率表格"""
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 3:
                first_row = rows[0]
                headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
                header_text = ' '.join(headers)

                # 欧洲指数
                if any(k in header_text for k in ['勝', '平', '負', '主胜', '平局', '客胜']):
                    for row in rows[1:]:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 6:
                            company = cells[0].get_text(strip=True)
                            if company:
                                analysis_data['european_odds'].append({
                                    'company': company,
                                    'home_init': cells[1].get_text(strip=True),
                                    'draw_init': cells[2].get_text(strip=True),
                                    'away_init': cells[3].get_text(strip=True),
                                    'home_curr': cells[4].get_text(strip=True) if len(cells) > 4 else '',
                                    'draw_curr': cells[5].get_text(strip=True) if len(cells) > 5 else '',
                                    'away_curr': cells[6].get_text(strip=True) if len(cells) > 6 else ''
                                })

                # 亚洲盘口
                elif any(k in header_text for k in ['亞', '讓', '让球', '盘口']):
                    for row in rows[1:]:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 6:
                            company = cells[0].get_text(strip=True)
                            if company:
                                analysis_data['asian_odds'].append({
                                    'company': company,
                                    'home_init': cells[1].get_text(strip=True),
                                    'handicap_init': cells[2].get_text(strip=True),
                                    'away_init': cells[3].get_text(strip=True),
                                    'home_curr': cells[4].get_text(strip=True) if len(cells) > 4 else '',
                                    'handicap_curr': cells[5].get_text(strip=True) if len(cells) > 5 else '',
                                    'away_curr': cells[6].get_text(strip=True) if len(cells) > 6 else ''
                                })

                # 进球数
                elif any(k in header_text for k in ['大', '小', '进球数']):
                    for row in rows[1:]:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 6:
                            company = cells[0].get_text(strip=True)
                            if company:
                                analysis_data['goal_odds'].append({
                                    'company': company,
                                    'goal_init': cells[1].get_text(strip=True),
                                    'big_init': cells[2].get_text(strip=True),
                                    'small_init': cells[3].get_text(strip=True),
                                    'goal_curr': cells[4].get_text(strip=True) if len(cells) > 4 else '',
                                    'big_curr': cells[5].get_text(strip=True) if len(cells) > 5 else '',
                                    'small_curr': cells[6].get_text(strip=True) if len(cells) > 6 else ''
                                })

    def _parse_trend_data(self, soup, analysis_data):
        """解析即时走势数据 - 包含让球/大小球/欧洲指数"""
        try:
            # 查找包含即时走势的表格
            tables = soup.find_all('table')
            for table in tables:
                text = table.get_text()
                # 检测即时走势表格特征 - 必须有时间和让球/大小球/欧指相关列
                if '时间' in text and ('亚' in text or '让' in text or '大' in text or '欧' in text):
                    rows = table.find_all('tr')
                    print(f"找到即时走势表格，共 {len(rows)} 行")
                    if len(rows) >= 2:
                        # 跳过表头行(通常是前两行合并表头)
                        data_start = 2 if len(rows) > 2 and '时间' in rows[0].get_text() else 1
                        for row in rows[data_start:]:
                            cells = row.find_all(['td', 'th'])
                            print(f"行数据: {len(cells)} 个单元格")
                            if len(cells) >= 5:
                                # 根据实际网页结构解析
                                # 时间列可能有rowspan，需要处理
                                cell_texts = [c.get_text(strip=True) for c in cells]
                                print(f"单元格内容: {cell_texts}")
                                
                                # 基础数据
                                trend_item = {
                                    'time': cell_texts[0] if len(cell_texts) > 0 else '',
                                    'score': cell_texts[1] if len(cell_texts) > 1 else '',
                                    'half_full': cell_texts[2] if len(cell_texts) > 2 else '',
                                }
                                
                                # 让球数据 - 根据实际列数动态解析
                                idx = 3
                                if len(cell_texts) > idx:
                                    trend_item['asian_home_init'] = cell_texts[idx]; idx += 1
                                if len(cell_texts) > idx:
                                    trend_item['asian_handicap_init'] = cell_texts[idx]; idx += 1
                                if len(cell_texts) > idx:
                                    trend_item['asian_away_init'] = cell_texts[idx]; idx += 1
                                if len(cell_texts) > idx:
                                    trend_item['asian_home_curr'] = cell_texts[idx]; idx += 1
                                if len(cell_texts) > idx:
                                    trend_item['asian_handicap_curr'] = cell_texts[idx]; idx += 1
                                if len(cell_texts) > idx:
                                    trend_item['asian_away_curr'] = cell_texts[idx]; idx += 1
                                
                                # 进球数数据
                                if len(cell_texts) > idx:
                                    trend_item['goal_big_init'] = cell_texts[idx]; idx += 1
                                if len(cell_texts) > idx:
                                    trend_item['goal_handicap_init'] = cell_texts[idx]; idx += 1
                                if len(cell_texts) > idx:
                                    trend_item['goal_small_init'] = cell_texts[idx]; idx += 1
                                if len(cell_texts) > idx:
                                    trend_item['goal_big_curr'] = cell_texts[idx]; idx += 1
                                if len(cell_texts) > idx:
                                    trend_item['goal_handicap_curr'] = cell_texts[idx]; idx += 1
                                if len(cell_texts) > idx:
                                    trend_item['goal_small_curr'] = cell_texts[idx]; idx += 1
                                
                                # 欧洲指数
                                if len(cell_texts) > idx:
                                    trend_item['euro_home'] = cell_texts[idx]; idx += 1
                                if len(cell_texts) > idx:
                                    trend_item['euro_draw'] = cell_texts[idx]; idx += 1
                                if len(cell_texts) > idx:
                                    trend_item['euro_away'] = cell_texts[idx]
                                
                                analysis_data['trend_data'].append(trend_item)
                                print(f"添加走势数据: {trend_item}")
        except Exception as e:
            print(f"解析即时走势数据失败: {e}")
            import traceback
            traceback.print_exc()


class MatchDisplayApp:
    """比赛数据大屏展示应用"""

    def __init__(self, root):
        self.root = root
        self.root.title("竞彩足球比赛数据大屏展示系统")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.scale = min(screen_width / 1920, screen_height / 1080)
        window_width = int(min(1400 * self.scale, screen_width * 0.95))
        window_height = int(min(900 * self.scale, screen_height * 0.9))
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.configure(bg='#1a1a2e')
        self.root.bind('<Configure>', self.on_resize)

        self.matches = []
        self.filtered_matches = []
        self.scraper = MatchScraper()
        self.auto_refresh_after_id = None

        self.setup_ui()
        self.refresh_data()
        self.start_auto_refresh()

    def on_resize(self, event):
        if event.widget == self.root:
            new_scale = min(event.width / 1920, event.height / 1080)
            self.scale = max(0.5, new_scale)
            self.update_layout()

    def update_layout(self):
        pass

    def get_font(self, base_size, weight='normal'):
        size = max(8, int(base_size * self.scale))
        return ('Microsoft YaHei', size, weight)

    def get_pad(self, base_pad):
        return max(2, int(base_pad * self.scale))

    def setup_ui(self):
        """设置 UI 界面"""
        pad = self.get_pad(10)
        title_height = int(80 * self.scale)

        title_frame = tk.Frame(self.root, bg='#16213e', height=title_height)
        title_frame.pack(fill=tk.X, padx=pad, pady=pad)

        title_font_size = max(12, int(24 * self.scale))
        title_label = tk.Label(
            title_frame,
            text="竞彩足球比赛数据大屏展示系统",
            font=('Microsoft YaHei', title_font_size, 'bold'),
            fg='#00ff88',
            bg='#16213e'
        )
        title_label.pack(pady=int(20*self.scale))

        time_font_size = max(8, int(12 * self.scale))
        self.time_label = tk.Label(
            title_frame,
            text="",
            font=('Microsoft YaHei', time_font_size),
            fg='#ffffff',
            bg='#16213e'
        )
        self.time_label.pack()
        self.update_time()

        # 控制按钮区域
        control_frame = tk.Frame(self.root, bg='#1a1a2e')
        control_frame.pack(fill=tk.X, padx=pad, pady=pad)

        btn_font_size = max(8, int(12 * self.scale))
        refresh_btn = tk.Button(
            control_frame,
            text="刷新数据",
            command=self.refresh_data,
            font=('Microsoft YaHei', btn_font_size, 'bold'),
            bg='#0f3460',
            fg='#ffffff',
            relief=tk.FLAT,
            cursor='hand2',
            padx=int(20*self.scale),
            pady=int(10*self.scale)
        )
        refresh_btn.pack(side=tk.LEFT, padx=self.get_pad(5))

        label_font_size = max(8, int(12 * self.scale))
        tk.Label(
            control_frame,
            text="日期选择:",
            font=('Microsoft YaHei', label_font_size),
            fg='#ffffff',
            bg='#1a1a2e'
        ).pack(side=tk.LEFT, padx=self.get_pad(10))

        # 生成往前7天的日期列表（包含今天）
        from datetime import datetime, timedelta
        today = datetime.now()
        date_list = [(today + timedelta(days=-i)).strftime('%Y-%m-%d') for i in range(7)]
        self.date_var = tk.StringVar(value=today.strftime('%Y-%m-%d'))
        combo_font_size = max(8, int(11 * self.scale))
        self.date_combo = ttk.Combobox(
            control_frame,
            textvariable=self.date_var,
            state="readonly",
            width=12,
            font=('Microsoft YaHei', combo_font_size),
            values=date_list
        )
        self.date_combo.pack(side=tk.LEFT, padx=self.get_pad(5))
        self.date_combo.bind('<<ComboboxSelected>>', self.on_date_selected)

        tk.Label(
            control_frame,
            text="联赛筛选:",
            font=('Microsoft YaHei', label_font_size),
            fg='#ffffff',
            bg='#1a1a2e'
        ).pack(side=tk.LEFT, padx=self.get_pad(10))

        self.league_var = tk.StringVar(value="全部")
        combo_font_size = max(8, int(11 * self.scale))
        self.league_combo = ttk.Combobox(
            control_frame,
            textvariable=self.league_var,
            state="readonly",
            width=15,
            font=('Microsoft YaHei', combo_font_size)
        )
        self.league_combo.pack(side=tk.LEFT, padx=self.get_pad(5))
        self.league_combo.bind('<<ComboboxSelected>>', self.filter_matches)

        tk.Label(
            control_frame,
            text="状态筛选:",
            font=('Microsoft YaHei', label_font_size),
            fg='#ffffff',
            bg='#1a1a2e'
        ).pack(side=tk.LEFT, padx=self.get_pad(10))

        self.status_var = tk.StringVar(value="全部")
        self.status_combo = ttk.Combobox(
            control_frame,
            textvariable=self.status_var,
            state="readonly",
            width=10,
            font=('Microsoft YaHei', combo_font_size),
            values=["全部", "未开始", "上半场", "中场", "下半场", "已完场"]
        )
        self.status_combo.set("全部")
        self.status_combo.pack(side=tk.LEFT, padx=self.get_pad(5))
        self.status_combo.bind('<<ComboboxSelected>>', self.filter_matches)

        self.stats_label = tk.Label(
            control_frame,
            text="总场次：0",
            font=('Microsoft YaHei', btn_font_size, 'bold'),
            fg='#00ff88',
            bg='#1a1a2e'
        )
        self.stats_label.pack(side=tk.RIGHT, padx=self.get_pad(20))

        # 主内容区域
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg='#1a1a2e')
        main_paned.pack(fill=tk.BOTH, expand=True, padx=pad, pady=pad)

        left_width = int(250 * self.scale)
        left_frame = tk.Frame(main_paned, bg='#16213e')
        main_paned.add(left_frame, width=left_width)

        list_title_font_size = max(10, int(16 * self.scale))
        list_title = tk.Label(
            left_frame,
            text="比赛列表",
            font=('Microsoft YaHei', list_title_font_size, 'bold'),
            fg='#e94560',
            bg='#16213e'
        )
        list_title.pack(pady=self.get_pad(10))

        # 比赛列表滚动区域
        list_canvas_frame = tk.Frame(left_frame, bg='#16213e')
        list_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=self.get_pad(10), pady=self.get_pad(10))

        self.list_canvas = tk.Canvas(
            list_canvas_frame,
            bg='#16213e',
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            list_canvas_frame,
            orient="vertical",
            command=self.list_canvas.yview
        )

        self.matches_list_frame = tk.Frame(
            self.list_canvas,
            bg='#16213e'
        )

        # 窗口ID，用于后续操作
        self.list_window_id = None

        def on_canvas_config(event):
            # 当 canvas 大小改变时，更新内部 frame 宽度
            if self.list_window_id:
                self.list_canvas.itemconfig(self.list_window_id, width=event.width)
            # 更新滚动区域
            self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))

        def on_frame_config(event):
            # 更新滚动区域
            self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))

        self.list_canvas.bind("<Configure>", on_canvas_config)
        self.matches_list_frame.bind("<Configure>", on_frame_config)

        # 创建窗口
        self.list_window_id = self.list_canvas.create_window((0, 0), window=self.matches_list_frame, anchor="nw")
        self.list_canvas.configure(yscrollcommand=scrollbar.set)

        self.list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 全局鼠标滚轮绑定 - 根据鼠标位置自动判断滚动哪个区域
        def on_global_mousewheel(event):
            # 获取鼠标在屏幕上的位置
            x = event.x_root
            y = event.y_root

            # 检查鼠标是否在详情区域上方
            try:
                if self.detail_frame.winfo_exists():
                    dx = self.detail_frame.winfo_rootx()
                    dy = self.detail_frame.winfo_rooty()
                    dw = self.detail_frame.winfo_width()
                    dh = self.detail_frame.winfo_height()
                    if dx <= x <= dx + dw and dy <= y <= dy + dh:
                        # 鼠标在详情区域，查找详情canvas
                        for widget in self.detail_frame.winfo_children():
                            if isinstance(widget, tk.Canvas) and widget.winfo_exists():
                                self._on_mousewheel(event, widget)
                                return
            except tk.TclError:
                pass

            # 默认滚动左边列表
            try:
                if self.list_canvas.winfo_exists():
                    self._on_mousewheel(event, self.list_canvas)
            except tk.TclError:
                pass

        self.root.bind_all("<MouseWheel>", on_global_mousewheel)
        self.root.bind_all("<Button-4>", on_global_mousewheel)
        self.root.bind_all("<Button-5>", on_global_mousewheel)

        # 右侧详情区域
        right_frame = tk.Frame(main_paned, bg='#0f3460')
        main_paned.add(right_frame)

        # 保存当前滚动的画布引用
        self.current_scroll_canvas = self.list_canvas

        detail_title_font_size = max(10, int(16 * self.scale))
        detail_title = tk.Label(
            right_frame,
            text="盘口详情",
            font=('Microsoft YaHei', detail_title_font_size, 'bold'),
            fg='#e94560',
            bg='#0f3460'
        )
        detail_title.pack(pady=self.get_pad(10))

        # 详情内容区域
        self.detail_frame = tk.Frame(right_frame, bg='#0f3460')
        self.detail_frame.pack(fill=tk.BOTH, expand=True, padx=self.get_pad(20), pady=self.get_pad(10))

        self.show_welcome()

    def _on_mousewheel(self, event, canvas=None):
        """鼠标滚轮事件"""
        if canvas is None:
            canvas = self.current_scroll_canvas
        if canvas is None:
            return

        try:
            # 检查Canvas是否还存在（未被销毁）
            if not canvas.winfo_exists():
                return

            # 获取当前滚动位置
            current_pos = canvas.yview()

            if event.num == 4 or event.num == 5:
                # Linux/macOS
                if event.num == 4:
                    # 向上滚动
                    if current_pos[0] > 0:
                        canvas.yview_scroll(-1, "units")
                else:
                    # 向下滚动
                    if current_pos[1] < 1:
                        canvas.yview_scroll(1, "units")
            else:
                # Windows
                delta = int(-1*(event.delta/120))
                if delta < 0:
                    # 向上滚动
                    if current_pos[0] > 0:
                        canvas.yview_scroll(delta, "units")
                else:
                    # 向下滚动
                    if current_pos[1] < 1:
                        canvas.yview_scroll(delta, "units")

        except tk.TclError:
            # Canvas已被销毁，忽略错误
            pass
        except Exception as e:
            print(f"滚动错误: {e}")

    def update_time(self):
        """更新时间"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.time_label.config(text=f"当前时间：{current_time}")
        self.root.after(1000, self.update_time)

    def show_welcome(self):
        """显示欢迎信息"""
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        welcome_label = tk.Label(
            self.detail_frame,
            text="请点击左侧比赛查看详情",
            font=('Microsoft YaHei', 18, 'bold'),
            fg='#ffffff',
            bg='#0f3460'
        )
        welcome_label.pack(expand=True)

    def start_auto_refresh(self):
        """启动自动刷新，每隔1-3分钟随机间隔"""
        # 取消之前的定时器
        if self.auto_refresh_after_id:
            self.root.after_cancel(self.auto_refresh_after_id)
            self.auto_refresh_after_id = None

        # 随机间隔 1-3 分钟（60000-180000 毫秒）
        interval_ms = random.randint(60, 180) * 1000
        print(f"下次自动刷新将在 {interval_ms // 1000} 秒后执行")

        def do_refresh():
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 自动刷新数据...")
            self.refresh_data(auto=True)

        self.auto_refresh_after_id = self.root.after(interval_ms, do_refresh)

    def stop_auto_refresh(self):
        """停止自动刷新"""
        if self.auto_refresh_after_id:
            self.root.after_cancel(self.auto_refresh_after_id)
            self.auto_refresh_after_id = None

    def refresh_data(self, date_str: Optional[str] = None, auto: bool = False):
        """刷新数据"""
        # 如果没有传入日期，使用下拉框中选择的日期
        if not date_str:
            date_str = self.date_var.get()

        # 禁用刷新按钮防止重复点击
        self.stats_label.config(text="加载中...")

        # 使用线程获取数据，避免界面卡顿
        def fetch_thread():
            try:
                self.matches = self.scraper.get_all_matches(date_str)
                self.root.after(0, self.on_data_loaded)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"获取数据失败：{e}"))
                self.root.after(0, self.on_data_loaded)

        thread = threading.Thread(target=fetch_thread, daemon=True)
        thread.start()

        # 如果是手动刷新，重新启动自动刷新计时器
        if not auto:
            self.start_auto_refresh()

    def on_date_selected(self, event=None):
        """日期选择变化时刷新数据"""
        date_str = self.date_var.get()
        self.refresh_data(date_str)

    def on_data_loaded(self):
        """数据加载完成"""
        if not self.matches:
            messagebox.showerror("错误", "获取数据失败，请检查网络连接")
            self.stats_label.config(text="总场次：0")
            return

        # 更新联赛筛选选项
        leagues = sorted(list(set([m['league'] for m in self.matches if m.get('league')])))
        self.league_combo['values'] = ["全部"] + leagues

        # 更新统计
        self.stats_label.config(text=f"总场次：{len(self.matches)}")

        # 过滤并显示
        self.filter_matches()

        # 自动刷新：数据加载完成后，安排下一次自动刷新
        self.start_auto_refresh()

    def filter_matches(self, event=None):
        """过滤比赛"""
        league = self.league_var.get()
        status = self.status_var.get()

        self.filtered_matches = []
        for match in self.matches:
            # 联赛筛选
            if league != "全部":
                match_league = match.get('league', '').strip()
                if match_league != league.strip():
                    continue

            # 状态筛选
            if status != "全部":
                match_status = match.get('status', '')
                if match_status != status:
                    continue

            self.filtered_matches.append(match)

        # 更新统计
        self.stats_label.config(text=f"赛事数量：{len(self.filtered_matches)}/{len(self.matches)}")

        self.display_matches_list()

    def display_matches_list(self):
        """显示比赛列表"""
        # 清空列表
        for widget in self.matches_list_frame.winfo_children():
            widget.destroy()

        # 显示比赛
        for i, match in enumerate(self.filtered_matches):
            match_card = self.create_match_card(match, i)
            match_card.pack(fill=tk.X, padx=10, pady=5)

        if not self.filtered_matches:
            no_data_label = tk.Label(
                self.matches_list_frame,
                text="没有符合条件的比赛",
                font=('Microsoft YaHei', 14),
                fg='#ffffff',
                bg='#16213e'
            )
            no_data_label.pack(pady=50)

    def create_match_card(self, match: Dict, index: int):
        s = self.scale
        card = tk.Frame(self.matches_list_frame, bg='#1a1a2e', cursor='hand2')
        def on_click(event):
            self.show_match_detail(match)

        top_frame = tk.Frame(card, bg='#e94560')
        top_frame.pack(fill=tk.X)
        top_frame.bind('<Button-1>', on_click)

        match_id = match.get('match_id', '')
        if match_id:
            match_id_label = tk.Label(top_frame, text=match_id, font=('Microsoft YaHei', max(8, int(10*s)), 'bold'), fg='#ffffff', bg='#e94560', padx=int(10*s), pady=int(5*s))
            match_id_label.pack(side=tk.LEFT)
            match_id_label.bind('<Button-1>', on_click)

        league_name = match.get('league', '')
        if league_name:
            league_label = tk.Label(top_frame, text=league_name, font=('Microsoft YaHei', max(8, int(10*s))), fg='#ffffff', bg='#e94560', padx=int(10*s))
            league_label.pack(side=tk.LEFT)
            league_label.bind('<Button-1>', on_click)

        match_time = match.get('match_time', '')
        if match_time:
            time_label = tk.Label(top_frame, text=match_time, font=('Microsoft YaHei', max(8, int(10*s))), fg='#ffffff', bg='#e94560', padx=int(10*s))
            time_label.pack(side=tk.RIGHT)
            time_label.bind('<Button-1>', on_click)

        info_frame = tk.Frame(card, bg='#1a1a2e')
        info_frame.pack(fill=tk.X, pady=int(12*s), padx=int(15*s))
        info_frame.bind('<Button-1>', on_click)

        # 获取比分 - 使用独立字段
        home_score = match.get('home_score', '')
        away_score = match.get('away_score', '')
        home_jc = match.get('home_jc_score', '')
        away_jc = match.get('away_jc_score', '')
        has_score = False
        if home_score != '' or away_score != '':
            has_score = True

        # 主队信息
        home_team = match.get('home_team', '')
        if home_team:
            home_label = tk.Label(info_frame, text=home_team, font=('Microsoft YaHei', max(10, int(13*s)), 'bold'), fg='#00ff88', bg='#1a1a2e', anchor='w')
            home_label.grid(row=0, column=0, sticky='w', padx=(0, 10))
            home_label.bind('<Button-1>', on_click)

        # 比分显示
        if has_score:
            # 主比分显示区域
            score_frame = tk.Frame(info_frame, bg='#1a1a2e')
            score_frame.grid(row=0, column=1, rowspan=2, padx=10)

            # 实际比分
            score_text = f"{home_score} - {away_score}"
            score_label = tk.Label(score_frame, text=score_text, font=('Microsoft YaHei', max(12, int(18*s)), 'bold'), fg='#ffd700', bg='#1a1a2e')
            score_label.pack()
            score_label.bind('<Button-1>', on_click)

            # 竞彩比分 (括号内显示)
            if home_jc != '' or away_jc != '':
                jc_text = f"({home_jc}:{away_jc})"
                jc_label = tk.Label(score_frame, text=jc_text, font=('Microsoft YaHei', max(8, int(10*s))), fg='#aaaaaa', bg='#1a1a2e')
                jc_label.pack()
                jc_label.bind('<Button-1>', on_click)

        # 客队信息
        away_team = match.get('away_team', '')
        if away_team:
            away_label = tk.Label(info_frame, text=away_team, font=('Microsoft YaHei', max(10, int(13*s)), 'bold'), fg='#ff6b6b', bg='#1a1a2e', anchor='w')
            away_label.grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(5, 0))
            away_label.bind('<Button-1>', on_click)

        # 配置Grid列权重
        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=0)

        status_frame = tk.Frame(card, bg='#0f3460')
        status_frame.pack(fill=tk.X)
        status_frame.bind('<Button-1>', on_click)

        status = match.get('status', '')
        status_code = match.get('status_code', '')
        if status:
            status_label = tk.Label(status_frame, text=status, font=('Microsoft YaHei', max(8, int(10*s)), 'bold'), fg='#ffffff', bg='#0f3460', padx=int(10*s), pady=int(5*s))
            status_label.pack(side=tk.LEFT)
            status_label.bind('<Button-1>', on_click)

        # 显示比赛进行时间 - 完全按照网页football.js的逻辑
        # JS源码: this.startTime = AmountTimeDiff(arr[2])  // arr[2]是update_time
        # JS计算: goTime = Math.floor((now - startTime - difftime) / 60000) + (state == "1" ? 0 : 46)
        # 上半场(1): goTime = (now - start_time) / 60000
        # 下半场(3): goTime = (now - update_time) / 60000 + 46
        if status_code in ['1', '3']:
            display_time = None
            try:
                from datetime import datetime

                if status_code == '1':
                    # 上半场: 用开球时间计算
                    time_str = match.get('start_time', '')
                else:
                    # 下半场: 用更新时间计算（JS的startTime = update_time）
                    time_str = match.get('update_time', '')
                
                if time_str:
                    parts = time_str.split(',')
                    if len(parts) >= 6:
                        dt = datetime(int(parts[0]), int(parts[1])+1,
                                     int(parts[2]), int(parts[3]),
                                     int(parts[4]), int(parts[5]))
                        now_dt = datetime.now()
                        elapsed = int((now_dt - dt).total_seconds() // 60)
                        
                        if status_code == '1':  # 上半场
                            if elapsed > 45:
                                display_time = "45+"
                            elif elapsed < 1:
                                display_time = "1'"
                            else:
                                display_time = f"{elapsed}'"
                        elif status_code == '3':  # 下半场: elapsed + 46
                            go_time = elapsed + 46
                            if go_time > 90:
                                display_time = "90+"
                            elif go_time < 46:
                                display_time = "46'"
                            else:
                                display_time = f"{go_time}'"
            except Exception as e:
                print(f"时间计算错误: {e}")
            
            if display_time:
                time_frame = tk.Frame(status_frame, bg='#1a1a2e')
                time_frame.pack(side=tk.RIGHT, padx=int(5*s))

                time_label = tk.Label(time_frame, text=display_time,
                                     font=('Microsoft YaHei', max(8, int(10*s)), 'bold'),
                                     fg='#00ff00', bg='#1a1a2e', padx=int(10*s))
                time_label.pack(side=tk.RIGHT)
                time_label.bind('<Button-1>', on_click)

        return card

    def fetch_web_analysis(self, match: Dict) -> str:
        """从网页获取详细分析数据"""
        match_unique_id = match.get('match_unique_id', '')
        if not match_unique_id:
            return self.parse_web_content("", match, {})

        url = f"https://zq.titan007.com/analysis/{match_unique_id}.htm"
        print(f"正在获取分析页面: {url}")

        try:
            response = self.scraper.session.get(url, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code == 200:
                html = response.text
                analysis_data = self.scraper.parse_analysis_data(html)
                return self.parse_web_content(html, match, analysis_data)
        except Exception as e:
            print(f"获取分析页面失败: {e}")

        return self.parse_web_content("", match, {})

    def parse_web_content(self, html: str, match: Dict, analysis_data: Dict) -> str:
        """解析网页内容 - 专业完整的赔率显示"""
        lines = []
        lines.append("")

        # 标题
        lines.append("")
        lines.append(f"        ┌─────────────────────────────────────────────────────────────┐")
        lines.append(f"        │                    比赛详情: {match.get('match_id', '')}                      │")
        lines.append(f"        └─────────────────────────────────────────────────────────────┘")
        lines.append("")

        # 对阵双方
        home_team = match.get('home_team', '')
        away_team = match.get('away_team', '')
        lines.append(f"                       {home_team}  VS  {away_team}")
        lines.append("")

        # 基本信息
        lines.append("")
        lines.append(f"     ┌─────────────────────────────────────────────────────────────────┐")
        lines.append(f"     │                        基本信息                                   │")
        lines.append(f"     ├─────────────────────────────────────────────────────────────────┤")
        lines.append(f"     │ 联赛: {match.get('league', ''):<51} │")
        lines.append(f"     │ 状态: {match.get('status', ''):<51} │")
        lines.append(f"     │ 时间: {match.get('match_time', ''):<51} │")

        score = match.get('score', '')
        if score:
            lines.append(f"     │ 比分: {score:<51} │")
        lines.append(f"     └─────────────────────────────────────────────────────────────────┘")
        lines.append("")

        # 胜平负赔率表格
        init_home = ''
        init_draw = ''
        init_away = ''
        curr_home = ''
        curr_draw = ''
        curr_away = ''
        jc = analysis_data.get('jc_odds', {}) if analysis_data else {}
        if jc:
            init_home = jc.get('eu_full_init_home', '')
            init_draw = jc.get('eu_full_init_draw', '')
            init_away = jc.get('eu_full_init_away', '')
            curr_home = jc.get('eu_full_curr_home', '')
            curr_draw = jc.get('eu_full_curr_draw', '')
            curr_away = jc.get('eu_full_curr_away', '')
        if not init_home:
            instant = analysis_data.get('instant_eu_odds', {}) if analysis_data else {}
            if instant:
                init_home = instant.get('init_home', '')
                init_draw = instant.get('init_draw', '')
                init_away = instant.get('init_away', '')
                curr_home = instant.get('curr_home', '')
                curr_draw = instant.get('curr_draw', '')
                curr_away = instant.get('curr_away', '')
        if not init_home:
            odds_trend = analysis_data.get('odds_trend', []) if analysis_data else []
            for item in odds_trend:
                if item.get('company_id') == '3' or item.get('company') == 'Crow*':
                    init_home = item.get('eu_init_home', '')
                    init_draw = item.get('eu_init_draw', '')
                    init_away = item.get('eu_init_away', '')
                    curr_home = item.get('eu_curr_home', '')
                    curr_draw = item.get('eu_curr_draw', '')
                    curr_away = item.get('eu_curr_away', '')
                    break
            if not init_home:
                for item in odds_trend:
                    if item.get('eu_init_home'):
                        init_home = item.get('eu_init_home', '')
                        init_draw = item.get('eu_init_draw', '')
                        init_away = item.get('eu_init_away', '')
                        curr_home = item.get('eu_curr_home', '')
                        curr_draw = item.get('eu_curr_draw', '')
                        curr_away = item.get('eu_curr_away', '')
                        break

        lines.append(f"     ┌─────────────────────────────────────────────────────────────────┐")
        lines.append(f"     │                       胜平负赔率                                  │")
        lines.append(f"     ├───────────┬───────────────┬───────────────┬──────────────────────┤")
        lines.append(f"     │   类型    │     主胜      │     平局      │     客胜             │")
        lines.append(f"     ├───────────┼───────────────┼───────────────┼──────────────────────┤")
        lines.append(f"     │   初盘    │  {init_home:<12} │  {init_draw:<12} │  {init_away:<16}       │")
        lines.append(f"     │   即时    │  {curr_home:<12} │  {curr_draw:<12} │  {curr_away:<16}       │")
        lines.append(f"     └───────────┴───────────────┴───────────────┴──────────────────────┘")
        lines.append("")

        # 让球盘口
        handicap = match.get('handicap', '')
        handicap_text = ""
        if handicap:
            try:
                handicap_val = float(handicap)
                if handicap_val > 0:
                    handicap_text = f"主队让 {handicap_val} 球"
                elif handicap_val < 0:
                    handicap_text = f"客队让 {abs(handicap_val)} 球"
                else:
                    handicap_text = "平手盘"
            except:
                handicap_text = handicap

        lines.append(f"     ┌─────────────────────────────────────────────────────────────────┐")
        lines.append(f"     │                       让球盘口                                   │")
        lines.append(f"     ├─────────────────────────────────────────────────────────────────┤")
        lines.append(f"     │ 盘口: {handicap:<49} │")
        if handicap_text:
            lines.append(f"     │ 说明: {handicap_text:<49} │")
        lines.append(f"     └─────────────────────────────────────────────────────────────────┘")
        lines.append("")

        # 欧洲指数详细表格
        european_odds = analysis_data.get('european_odds', [])
        if european_odds:
            lines.append(f"     ┌─────────────────────────────────────────────────────────────────┐")
            lines.append(f"     │                      欧洲指数公司赔率                              │")
            lines.append(f"     ├────────────┬───────────┬──────────┬───────────┬──────────┬────────┤")
            lines.append(f"     │   公司     │   主胜初  │  平初   │  客胜初   │  即时主 │即时平  │")
            lines.append(f"     ├────────────┼───────────┼──────────┼───────────┼──────────┼────────┤")

            for i, odd in enumerate(european_odds[:8]):
                company = odd.get('company', '')
                home_init = odd.get('home_init', '')
                draw_init = odd.get('draw_init', '')
                away_init = odd.get('away_init', '')
                home_curr = odd.get('home_curr', '')
                draw_curr = odd.get('draw_curr', '')

                lines.append(f"     │ {company:<10} │ {home_init:<9} │ {draw_init:<8} │ {away_init:<9} │ {home_curr:<8} │ {draw_curr:<8} │")

            lines.append(f"     └────────────┴───────────┴──────────┴───────────┴──────────┴────────┘")
            lines.append("")

        # 亚洲指数详细表格
        asian_odds = analysis_data.get('asian_odds', [])
        if asian_odds:
            lines.append(f"     ┌─────────────────────────────────────────────────────────────────┐")
            lines.append(f"     │                      亚洲盘口赔率                                  │")
            lines.append(f"     ├────────────┬───────────┬──────────┬───────────┬──────────┬────────┤")
            lines.append(f"     │   公司     │   主胜初  │  让球初  │  客胜初   │  即时主 │即让球  │")
            lines.append(f"     ├────────────┼───────────┼──────────┼───────────┼──────────┼────────┤")

            for i, odd in enumerate(asian_odds[:8]):
                company = odd.get('company', '')
                home_init = odd.get('home_init', '')
                handicap_init = odd.get('handicap_init', '')
                away_init = odd.get('away_init', '')
                home_curr = odd.get('home_curr', '')
                handicap_curr = odd.get('handicap_curr', '')

                lines.append(f"     │ {company:<10} │ {home_init:<9} │ {handicap_init:<8} │ {away_init:<9} │ {home_curr:<8} │ {handicap_curr:<8} │")

            lines.append(f"     └────────────┴───────────┴──────────┴───────────┴──────────┴────────┘")
            lines.append("")

        # 其他数据
        lines.append(f"     ┌─────────────────────────────────────────────────────────────────┐")
        lines.append(f"     │                        其他信息                                   │")
        lines.append(f"     ├─────────────────────────────────────────────────────────────────┤")
        lines.append(f"     │ 比赛唯一ID: {match.get('match_unique_id', ''):<44} │")
        lines.append(f"     └─────────────────────────────────────────────────────────────────┘")
        lines.append("")
        lines.append("")

        return "\n".join(lines)

    def display_web_analysis(self, match: Dict, analysis_data: Dict, loading_label):
        s = self.scale

        # 检查loading_label是否还存在
        try:
            if loading_label.winfo_exists():
                loading_label.destroy()
        except tk.TclError:
            pass

        # 检查detail_frame是否还存在
        try:
            if not self.detail_frame.winfo_exists():
                return
        except tk.TclError:
            return

        # 清除之前的绑定
        for widget in self.detail_frame.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

        # 创建Canvas和滚动条
        canvas = tk.Canvas(self.detail_frame, bg='#0f3460', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.detail_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#0f3460')

        detail_window_id = None

        def on_detail_canvas_config(event):
            try:
                if detail_window_id and canvas.winfo_exists():
                    canvas.itemconfig(detail_window_id, width=event.width)
                    canvas.configure(scrollregion=canvas.bbox("all"))
            except tk.TclError:
                pass

        def on_detail_frame_config(event):
            try:
                if canvas.winfo_exists():
                    canvas.configure(scrollregion=canvas.bbox("all"))
            except tk.TclError:
                pass

        canvas.bind("<Configure>", on_detail_canvas_config)
        scrollable_frame.bind("<Configure>", on_detail_frame_config)

        detail_window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 使用新的专业表格显示 - 传入analysis_data显示完整数据
        odds_display = OddsTableDisplay(scrollable_frame, s)
        odds_display.create_full_display(match, analysis_data)

    def show_match_detail(self, match: Dict):
        s = self.scale
        # 清除详情区域
        for widget in self.detail_frame.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

        loading_label = tk.Label(self.detail_frame, text="正在加载详细数据...", font=('Microsoft YaHei', max(10, int(16*s))), fg='#00ff88', bg='#0f3460')
        loading_label.pack(expand=True)

        # 异步加载网页分析数据
        def load_detail():
            analysis_data = self.scraper.fetch_match_analysis(match)
            # 使用after确保在主线程更新UI
            self.root.after(0, lambda: self._safe_display_web_analysis(match, analysis_data, loading_label))

        thread = threading.Thread(target=load_detail, daemon=True)
        thread.start()

    def _safe_display_web_analysis(self, match: Dict, analysis_data: Dict, loading_label):
        """安全地显示网页分析，处理widget可能已被销毁的情况"""
        try:
            # 检查主窗口是否还存在
            if not self.root.winfo_exists():
                return
            self.display_web_analysis(match, analysis_data, loading_label)
        except tk.TclError as e:
            print(f"显示详情时出错(窗口可能已关闭): {e}")
        except Exception as e:
            print(f"显示详情时出错: {e}")

    def show_odds_analysis(self, match: Dict):
        """显示盘口分析"""
        # 创建新窗口
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title(f"比赛数据详情 - {match.get('match_id', 'Unknown')}")
        analysis_window.geometry("900x750")
        analysis_window.configure(bg='#1a1a2e')

        # 标题
        match_id = match.get('match_id', '')
        title_label = tk.Label(
            analysis_window,
            text=f" {match_id} 比赛数据详情",
            font=('Microsoft YaHei', 20, 'bold'),
            fg='#e94560',
            bg='#1a1a2e'
        )
        title_label.pack(pady=15)

        # 对阵信息
        teams_text = f"{match.get('home_team', '')} VS {match.get('away_team', '')}"
        teams_label = tk.Label(
            analysis_window,
            text=teams_text,
            font=('Microsoft YaHei', 16, 'bold'),
            fg='#ffffff',
            bg='#1a1a2e'
        )
        teams_label.pack(pady=10)

        # 创建选项卡
        notebook = ttk.Notebook(analysis_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 基本信息标签页
        basic_frame = tk.Frame(notebook, bg='#16213e')
        notebook.add(basic_frame, text="基本信息")
        self.create_basic_info_tab(basic_frame, match)

        # 盘口数据标签页
        odds_frame = tk.Frame(notebook, bg='#16213e')
        notebook.add(odds_frame, text="盘口数据")
        self.create_odds_data_tab(odds_frame, match)

        # 原始数据标签页
        raw_frame = tk.Frame(notebook, bg='#16213e')
        notebook.add(raw_frame, text="原始数据")
        self.create_raw_data_tab(raw_frame, match)

        # 关闭按钮
        close_btn = tk.Button(
            analysis_window,
            text="关闭",
            command=analysis_window.destroy,
            font=('Microsoft YaHei', 12, 'bold'),
            bg='#e94560',
            fg='#ffffff',
            relief=tk.FLAT,
            cursor='hand2',
            padx=40,
            pady=10
        )
        close_btn.pack(pady=15)

    def create_basic_info_tab(self, parent, match: Dict):
        """创建基本信息标签页"""
        # 滚动区域
        canvas = tk.Canvas(parent, bg='#16213e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#16213e')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 基本信息
        info_data = [
            ("比赛编号", match.get('match_id', 'N/A')),
            ("联赛", match.get('league', 'N/A')),
            ("比赛时间", match.get('match_time', 'N/A')),
            ("比赛状态", match.get('status', 'N/A')),
            ("主队", match.get('home_team', 'N/A')),
            ("客队", match.get('away_team', 'N/A')),
            ("比分", match.get('score', '未开始') if match.get('score') else '未开始'),
        ]

        for i, (label, value) in enumerate(info_data):
            row_frame = tk.Frame(scrollable_frame, bg='#16213e')
            row_frame.pack(fill=tk.X, pady=5, padx=20)

            label_widget = tk.Label(
                row_frame,
                text=f"{label}:",
                font=('Microsoft YaHei', 12, 'bold'),
                fg='#00ff88',
                bg='#16213e',
                width=15,
                anchor='w'
            )
            label_widget.pack(side=tk.LEFT)

            value_widget = tk.Label(
                row_frame,
                text=value,
                font=('Microsoft YaHei', 12),
                fg='#ffffff',
                bg='#16213e',
                anchor='w'
            )
            value_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def create_odds_data_tab(self, parent, match: Dict):
        """创建盘口数据标签页"""
        # 滚动区域
        canvas = tk.Canvas(parent, bg='#16213e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#16213e')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 加载分析数据
        loading_label = tk.Label(
            scrollable_frame,
            text="正在加载赔率数据...",
            font=('Microsoft YaHei', 12),
            fg='#00ff88',
            bg='#16213e'
        )
        loading_label.pack(pady=20)

        # 使用线程加载数据
        def load_odds():
            analysis_data = self.scraper.fetch_match_analysis(match)
            self.root.after(0, lambda: self.display_odds_data(scrollable_frame, match, analysis_data, loading_label))

        thread = threading.Thread(target=load_odds, daemon=True)
        thread.start()

    def display_odds_data(self, parent, match: Dict, analysis_data: Dict, loading_label):
        """显示赔率数据"""
        loading_label.destroy()

        # 基础盘口信息
        handicap = match.get('handicap', '')
        if handicap:
            self.create_handicap_section(parent, handicap)

        # 欧洲指数
        euro_odds = analysis_data.get('european_odds', [])
        if euro_odds:
            self.create_european_odds_section(parent, euro_odds)

        # 亚洲盘口
        asian_odds = analysis_data.get('asian_odds', [])
        if asian_odds:
            self.create_asian_odds_section(parent, asian_odds)

        # 进球数
        goal_odds = analysis_data.get('goal_odds', [])
        if goal_odds:
            self.create_goal_odds_section(parent, goal_odds)

        if not handicap and not euro_odds and not asian_odds and not goal_odds:
            no_data_label = tk.Label(
                parent,
                text="暂无详细赔率数据",
                font=('Microsoft YaHei', 14),
                fg='#aaaaaa',
                bg='#16213e'
            )
            no_data_label.pack(pady=50)

    def create_handicap_section(self, parent, handicap: str):
        """创建让球盘口区"""
        frame = tk.Frame(parent, bg='#0f3460', padx=20, pady=15)
        frame.pack(fill=tk.X, pady=10, padx=20)

        title = tk.Label(
            frame,
            text="让球盘口",
            font=('Microsoft YaHei', 14, 'bold'),
            fg='#e94560',
            bg='#0f3460'
        )
        title.pack(anchor='w', pady=(0, 10))

        try:
            val = float(handicap)
            if val > 0:
                text = f"主队让 {val} 球"
                desc = "主队让球方"
            elif val < 0:
                text = f"客队让 {abs(val)} 球"
                desc = "客队让球方"
            else:
                text = "平手盘"
                desc = "双方平手"
        except:
            text = handicap
            desc = "盘口数据"

        info = tk.Label(
            frame,
            text=text,
            font=('Microsoft YaHei', 16, 'bold'),
            fg='#00ffff',
            bg='#0f3460'
        )
        info.pack(anchor='w')

        desc_label = tk.Label(
            frame,
            text=desc,
            font=('Microsoft YaHei', 10),
            fg='#aaaaaa',
            bg='#0f3460'
        )
        desc_label.pack(anchor='w', pady=(5, 0))

    def create_european_odds_section(self, parent, odds_list: List[Dict]):
        """创建欧洲指数区"""
        frame = tk.Frame(parent, bg='#0f3460', padx=20, pady=15)
        frame.pack(fill=tk.X, pady=10, padx=20)

        title = tk.Label(
            frame,
            text="欧洲指数",
            font=('Microsoft YaHei', 14, 'bold'),
            fg='#e94560',
            bg='#0f3460'
        )
        title.pack(anchor='w', pady=(0, 10))

        # 创建表格
        self.create_odds_table(frame, odds_list, [
            ("公司", "company", 10),
            ("初主胜", "home_init", 8),
            ("初平局", "draw_init", 8),
            ("初客胜", "away_init", 8),
            ("现主胜", "home_curr", 8),
            ("现平局", "draw_curr", 8),
            ("现客胜", "away_curr", 8)
        ])

    def create_asian_odds_section(self, parent, odds_list: List[Dict]):
        """创建亚洲盘口区"""
        frame = tk.Frame(parent, bg='#0f3460', padx=20, pady=15)
        frame.pack(fill=tk.X, pady=10, padx=20)

        title = tk.Label(
            frame,
            text="亚洲盘口",
            font=('Microsoft YaHei', 14, 'bold'),
            fg='#e94560',
            bg='#0f3460'
        )
        title.pack(anchor='w', pady=(0, 10))

        # 创建表格
        self.create_odds_table(frame, odds_list, [
            ("公司", "company", 10),
            ("初盘水", "home_init", 8),
            ("初盘口", "handicap_init", 8),
            ("初盘水", "away_init", 8),
            ("现盘水", "home_curr", 8),
            ("现盘口", "handicap_curr", 8),
            ("现盘水", "away_curr", 8)
        ])

    def create_goal_odds_section(self, parent, odds_list: List[Dict]):
        """创建进球数区"""
        frame = tk.Frame(parent, bg='#0f3460', padx=20, pady=15)
        frame.pack(fill=tk.X, pady=10, padx=20)

        title = tk.Label(
            frame,
            text="进球数",
            font=('Microsoft YaHei', 14, 'bold'),
            fg='#e94560',
            bg='#0f3460'
        )
        title.pack(anchor='w', pady=(0, 10))

        # 创建表格
        self.create_odds_table(frame, odds_list, [
            ("公司", "company", 10),
            ("初盘口", "goal_init", 8),
            ("初大球", "big_init", 8),
            ("初小球", "small_init", 8),
            ("现盘口", "goal_curr", 8),
            ("现大球", "big_curr", 8),
            ("现小球", "small_curr", 8)
        ])

    def create_odds_table(self, parent, data_list: List[Dict], columns: List[tuple]):
        """创建赔率表格"""
        table_frame = tk.Frame(parent, bg='#0f3460')
        table_frame.pack(fill=tk.X)

        # 表头
        for i, (header, key, width) in enumerate(columns):
            label = tk.Label(
                table_frame,
                text=header,
                font=('Microsoft YaHei', 10, 'bold'),
                fg='#ffffff',
                bg='#16213e',
                width=width,
                relief=tk.RIDGE,
                borderwidth=1
            )
            label.grid(row=0, column=i, sticky='nsew')

        # 数据行
        for row_idx, data in enumerate(data_list[:10], 1):  # 限制显示 10 条
            for col_idx, (header, key, width) in enumerate(columns):
                value = data.get(key, '')
                bg_color = '#0f3460' if row_idx % 2 == 1 else '#16213e'
                fg_color = '#00ff88' if key in ['home_curr', 'home_init'] and value else '#ffffff'

                label = tk.Label(
                    table_frame,
                    text=value,
                    font=('Microsoft YaHei', 9),
                    fg=fg_color,
                    bg=bg_color,
                    width=width,
                    relief=tk.RIDGE,
                    borderwidth=1
                )
                label.grid(row=row_idx, column=col_idx, sticky='nsew')

    def create_raw_data_tab(self, parent, match: Dict):
        """创建原始数据标签页"""
        # 滚动区域
        canvas = tk.Canvas(parent, bg='#16213e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#16213e')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        raw_data = match.get('raw_data', [])

        if raw_data:
            # 表头
            header_frame = tk.Frame(scrollable_frame, bg='#0f3460')
            header_frame.pack(fill=tk.X, pady=5, padx=20)

            tk.Label(
                header_frame,
                text="字段索引",
                font=('Microsoft YaHei', 10, 'bold'),
                fg='#ffffff',
                bg='#0f3460',
                width=10
            ).pack(side=tk.LEFT, padx=5)

            tk.Label(
                header_frame,
                text="字段值",
                font=('Microsoft YaHei', 10, 'bold'),
                fg='#ffffff',
                bg='#0f3460'
            ).pack(side=tk.LEFT)

            # 数据行
            for i, field in enumerate(raw_data):
                row_frame = tk.Frame(scrollable_frame, bg='#16213e' if i % 2 == 0 else '#0f3460')
                row_frame.pack(fill=tk.X, pady=1, padx=20)

                tk.Label(
                    row_frame,
                    text=f"[{i:2d}]",
                    font=('Microsoft YaHei', 9),
                    fg='#00ff88',
                    bg=row_frame.cget('bg'),
                    width=10
                ).pack(side=tk.LEFT, padx=5)

                tk.Label(
                    row_frame,
                    text=field if field else '(空)',
                    font=('Microsoft YaHei', 9),
                    fg='#ffffff',
                    bg=row_frame.cget('bg'),
                    anchor='w'
                ).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def generate_analysis_text(self, match: Dict) -> str:
        """生成分析文本"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 获取盘口信息
        handicap = match.get('handicap', '')
        odd_field = match.get('odd_field', '')

        init_handicap = handicap if handicap else '暂无'
        curr_handicap = odd_field if odd_field else (handicap if handicap else '暂无')

        analysis = f"""【比赛信息】
联赛：{match.get('league', 'N/A')}
时间：{match.get('match_time', 'N/A')}
状态：{match.get('status', 'N/A')}

【对阵双方】
主队：{match.get('home_team', 'N/A')}
客队：{match.get('away_team', 'N/A')}

【比分】
{match.get('score', '未开始') if match.get('score') else '比赛未开始'}

【盘口信息】
初盘：{init_handicap}
即时盘：{curr_handicap}

【分析说明】
本系统提供实时比赛数据展示，
盘口数据来自官方数据源。

【数据更新】
数据源：球探体育
最后更新：{current_time}
"""
        return analysis


def main():
    """主函数"""
    root = tk.Tk()
    app = MatchDisplayApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
