import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from modules.cache import DataCache


class MatchScraper:

    def __init__(self):
        self.today_url = "https://jc.titan007.com/xml/bf_jc.txt"
        self.history_url = "https://jc.titan007.com/handle/JcResult.aspx"
        self.session = requests.Session()
        retry = Retry(total=2, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503])
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep-alive',
        })
        self.detail_cache = DataCache(max_size=50, ttl=120)
        self.list_cache = DataCache(max_size=10, ttl=60)

    def get_url_for_date(self, date_str: str) -> str:
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        if date_str == today:
            return self.today_url
        else:
            return f"{self.history_url}?d={date_str}"

    def fetch_page(self, url: Optional[str] = None) -> Optional[str]:
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

                status_map = {
                    '0': '未开始',
                    '1': '上半场',
                    '2': '中场',
                    '3': '下半场',
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
        return ""

    def get_all_matches(self, date_str: Optional[str] = None) -> List[Dict]:
        from datetime import datetime
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')

        url = self.get_url_for_date(date_str)
        content = self.fetch_page(url)

        if not content:
            return []

        matches = self.parse_matches(content)
        return matches

    def fetch_match_analysis(self, match: Dict, cancel_event=None) -> Dict:
        match_unique_id = match.get('match_unique_id', '')
        if not match_unique_id:
            return {}

        cache_key = f"detail_{match_unique_id}"
        cached = self.detail_cache.get(cache_key)
        if cached:
            print(f"[缓存] 使用缓存数据: {match_unique_id}")
            return cached

        url = f"https://zq.titan007.com/analysis/{match_unique_id}.htm"
        print(f"正在获取分析页面: {url}")

        try:
            response = self.session.get(url, timeout=8)
            response.encoding = 'utf-8'

            if cancel_event and cancel_event.is_set():
                return {}

            if response.status_code == 200:
                analysis_data = self.parse_analysis_data(response.text)

                with ThreadPoolExecutor(max_workers=2) as executor:
                    future_odds = executor.submit(self.fetch_odds_trend, match_unique_id)
                    future_jc = executor.submit(self.fetch_jc_odds, match_unique_id)

                    try:
                        odds_data = future_odds.result(timeout=8)
                        if odds_data:
                            analysis_data['odds_trend'] = odds_data
                    except Exception as e:
                        print(f"获取走势数据超时或失败: {e}")

                    try:
                        jc_odds = future_jc.result(timeout=8)
                        if jc_odds:
                            analysis_data['jc_odds'] = jc_odds
                    except Exception as e:
                        print(f"获取竞彩指数超时或失败: {e}")

                self.detail_cache.set(cache_key, analysis_data)
                return analysis_data
        except Exception as e:
            print(f"获取分析页面失败: {e}")

        return {}

    def fetch_odds_trend(self, schedule_id: str) -> List[Dict]:
        try:
            url = f"https://zq.titan007.com/analysis/odds/{schedule_id}.htm"
            response = self.session.get(url, timeout=8)
            if response.status_code != 200:
                return []

            content = response.content.decode('utf-8', errors='replace')
            return self._parse_odds_trend(content)
        except Exception as e:
            print(f"获取走势数据失败: {e}")
            return []

    def fetch_jc_odds(self, schedule_id: str) -> Dict:
        try:
            url = f"https://zq.titan007.com/default/getAnalyData?sid={schedule_id}&t=1&r={int(__import__('time').time()*1000)}"
            response = self.session.get(url, timeout=8)
            if response.status_code != 200:
                return {}
            return self._parse_jc_odds(response.text)
        except Exception as e:
            print(f"获取竞彩指数失败: {e}")
            return {}

    def _parse_jc_odds(self, content: str) -> Dict:
        try:
            import json
            obj = json.loads(content)
            jc = obj.get('jcOdds', {})
            if not jc:
                return {}
            result = {}
            wl = jc.get('wlOdds', {})
            if wl:
                wl_live = wl.get('live', {})
                wl_first = wl.get('first', {})
                result['eu_init_home'] = wl_first.get('win', '')
                result['eu_init_draw'] = wl_first.get('draw', '')
                result['eu_init_away'] = wl_first.get('lose', '')
                result['eu_curr_home'] = wl_live.get('win', '')
                result['eu_curr_draw'] = wl_live.get('draw', '')
                result['eu_curr_away'] = wl_live.get('lose', '')
            sf = jc.get('sfOdds', {})
            if sf:
                sf_live = sf.get('live', {})
                sf_first = sf.get('first', {})
                result['asian_hcp'] = sf.get('rf', '')
                result['asian_init_home'] = sf_first.get('win', '')
                result['asian_init_draw'] = sf_first.get('draw', '')
                result['asian_init_away'] = sf_first.get('lose', '')
                result['asian_curr_home'] = sf_live.get('win', '')
                result['asian_curr_draw'] = sf_live.get('draw', '')
                result['asian_curr_away'] = sf_live.get('lose', '')
            goal = jc.get('goalOdds', {})
            if goal:
                goal_live = goal.get('live', {})
                goal_init = goal.get('init', {})
                result['goal_init_g0'] = goal_init.get('g0', '')
                result['goal_init_g1'] = goal_init.get('g1', '')
                result['goal_init_g2'] = goal_init.get('g2', '')
                result['goal_init_g3'] = goal_init.get('g3', '')
                result['goal_init_g4'] = goal_init.get('g4', '')
                result['goal_init_g5'] = goal_init.get('g5', '')
                result['goal_init_g6'] = goal_init.get('g6', '')
                result['goal_init_g7'] = goal_init.get('g7', '')
                result['goal_curr_g0'] = goal_live.get('g0', '')
                result['goal_curr_g1'] = goal_live.get('g1', '')
                result['goal_curr_g2'] = goal_live.get('g2', '')
                result['goal_curr_g3'] = goal_live.get('g3', '')
                result['goal_curr_g4'] = goal_live.get('g4', '')
                result['goal_curr_g5'] = goal_live.get('g5', '')
                result['goal_curr_g6'] = goal_live.get('g6', '')
                result['goal_curr_g7'] = goal_live.get('g7', '')
            score = jc.get('scoreOdds', {})
            if score:
                score_live = score.get('live', {})
                result['score_live'] = {
                    '10': score_live.get('score10', ''),
                    '20': score_live.get('score20', ''),
                    '21': score_live.get('score21', ''),
                    '30': score_live.get('score30', ''),
                    '31': score_live.get('score31', ''),
                    '32': score_live.get('score32', ''),
                    '40': score_live.get('score40', ''),
                    '41': score_live.get('score41', ''),
                    '42': score_live.get('score42', ''),
                    '50': score_live.get('score50', ''),
                    '51': score_live.get('score51', ''),
                    '52': score_live.get('score52', ''),
                    'win_other': score_live.get('scoreWin', ''),
                    '00': score_live.get('score00', ''),
                    '11': score_live.get('score11', ''),
                    '22': score_live.get('score22', ''),
                    '33': score_live.get('score33', ''),
                    'draw_other': score_live.get('scoreDraw', ''),
                    '01': score_live.get('score01', ''),
                    '02': score_live.get('score02', ''),
                    '12': score_live.get('score12', ''),
                    '03': score_live.get('score03', ''),
                    '13': score_live.get('score13', ''),
                    '23': score_live.get('score23', ''),
                    '04': score_live.get('score04', ''),
                    '14': score_live.get('score14', ''),
                    '24': score_live.get('score24', ''),
                    '05': score_live.get('score05', ''),
                    '15': score_live.get('score15', ''),
                    '25': score_live.get('score25', ''),
                    'lose_other': score_live.get('scoreLose', ''),
                }
            hf = jc.get('hfOdds', {})
            if hf:
                hf_live = hf.get('live', {})
                result['hf_live'] = {
                    'ww': hf_live.get('hfww', ''),
                    'wd': hf_live.get('hfwd', ''),
                    'wl': hf_live.get('hfwl', ''),
                    'dw': hf_live.get('hfdw', ''),
                    'dd': hf_live.get('hfdd', ''),
                    'dl': hf_live.get('hfdl', ''),
                    'lw': hf_live.get('hflw', ''),
                    'ld': hf_live.get('hfld', ''),
                    'll': hf_live.get('hfll', ''),
                }
            return result
        except Exception as e:
            print(f"解析竞彩指数失败: {e}")
            return {}

    def _parse_odds_trend(self, content: str) -> List[Dict]:
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
        self._parse_venue_weather(html, analysis_data)
        self._parse_standings_js(soup, html, analysis_data)
        self._parse_h2h_records(soup, analysis_data)
        self._parse_recent_form(soup, analysis_data)
        self._parse_half_full_stats(soup, analysis_data)
        self._parse_goal_stats(soup, analysis_data)
        self._parse_odds_tables(soup, analysis_data)
        self._parse_trend_data(soup, analysis_data)

        return analysis_data

    def _parse_vs_eodds(self, html: str, analysis_data: Dict):
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

    def _parse_venue_weather(self, html: str, analysis_data: Dict):
        try:
            place_match = re.search(r"class=['\"]place['\"][^>]*>(.*?)</a>", html)
            if place_match:
                place_text = place_match.group(1)
                venue = re.sub(r'^.*?[：:]', '', place_text).strip()
                if venue:
                    analysis_data['venue'] = venue

            full_row = re.search(r"class=['\"]place['\"].*?</div>", html, re.DOTALL)
            if full_row:
                row_text = re.sub(r'<[^>]+>', '', full_row.group(0))
                row_text = row_text.replace('&nbsp;', ' ')

                weather_match = re.search(r'天氣[：:]\s*(\S+)', row_text)
                if weather_match:
                    analysis_data['weather'] = weather_match.group(1)

                temp_match = re.search(r'溫度[：:]\s*(\S+)', row_text)
                if temp_match:
                    analysis_data['temperature'] = temp_match.group(1)

            img_matches = re.findall(r'<img[^>]*src="([^"]*image/team[^"]*)"[^>]*alt="([^"]*)"', html)
            if len(img_matches) >= 2:
                analysis_data['home_logo'] = 'https:' + img_matches[0][0] if img_matches[0][0].startswith('//') else img_matches[0][0]
                analysis_data['away_logo'] = 'https:' + img_matches[1][0] if img_matches[1][0].startswith('//') else img_matches[1][0]

            lname_match = re.search(r"class=['\"]LName['\"][^>]*>(.*?)</a>", html)
            if lname_match:
                analysis_data['league_round'] = lname_match.group(1).strip()

            date_row = re.search(r"class=['\"]LName['\"].*?</div>", html, re.DOTALL)
            if date_row:
                date_text = re.sub(r'<[^>]+>', '', date_row.group(0))
                date_text = date_text.replace('&nbsp;', ' ').strip()
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})\s*(\d{1,2}:\d{2})\s*(\S+)', date_text)
                if date_match:
                    analysis_data['match_date'] = date_match.group(1)
                    analysis_data['match_day'] = date_match.group(3)
        except Exception as e:
            print(f"解析场地天气失败: {e}")

    def _parse_standings_js(self, soup, html: str, analysis_data: Dict):
        try:
            result = {
                'home_team': None,
                'away_team': None,
                'total': [],
                'home': [],
                'away': [],
            }

            porlet_5 = soup.find('div', id='porlet_5')
            if porlet_5:
                team_data = self._parse_porlet5_tables(porlet_5)
                if team_data:
                    result['home_team'] = team_data.get('home_team')
                    result['away_team'] = team_data.get('away_team')

            js_data = self._parse_standings_js_vars(html)
            if js_data:
                result['total'] = js_data.get('total', [])
                result['home'] = js_data.get('home', [])
                result['away'] = js_data.get('away', [])

            has_team = result['home_team'] or result['away_team']
            has_league = any(result.get(k) for k in ['total', 'home', 'away'])
            if has_team or has_league:
                analysis_data['standings_data'] = result
        except Exception as e:
            print(f"解析赛前积分榜失败: {e}")

    def _parse_porlet5_tables(self, porlet_5) -> Dict:
        try:
            result = {'home_team': None, 'away_team': None}
            outer_table = porlet_5.find('table')
            if not outer_table:
                return None
            tr = outer_table.find('tr')
            if not tr:
                return None
            tds = tr.find_all('td', recursive=False)
            if len(tds) < 2:
                return None
            for idx, td in enumerate(tds):
                team_key = 'home_team' if idx == 0 else 'away_team'
                nested_table = td.find('table')
                if not nested_table:
                    continue
                team_data = self._parse_team_standings_table(nested_table)
                if team_data:
                    result[team_key] = team_data
            if result['home_team'] or result['away_team']:
                return result
            return None
        except Exception as e:
            print(f"解析porlet_5表格失败: {e}")
            return None

    def _parse_team_standings_table(self, table) -> Dict:
        try:
            rows = table.find_all('tr')
            if len(rows) < 3:
                return None
            first_row = rows[0]
            name_text = first_row.get_text(strip=True)
            name_match = re.search(r'\]([^\]]+)$', name_text)
            team_name = name_match.group(1).strip() if name_match else name_text
            result = {'name': team_name}
            type_map = {'總': 'total', '总': 'total', '主': 'home', '客': 'away'}
            for row in rows[2:]:
                cells = row.find_all(['td'])
                if len(cells) < 10:
                    continue
                cell_texts = [c.get_text(strip=True) for c in cells]
                row_type = cell_texts[0]
                mapped_type = type_map.get(row_type)
                if not mapped_type:
                    continue
                result[mapped_type] = {
                    'played': cell_texts[1] if len(cell_texts) > 1 else '',
                    'won': cell_texts[2] if len(cell_texts) > 2 else '',
                    'drawn': cell_texts[3] if len(cell_texts) > 3 else '',
                    'lost': cell_texts[4] if len(cell_texts) > 4 else '',
                    'gf': cell_texts[5] if len(cell_texts) > 5 else '',
                    'ga': cell_texts[6] if len(cell_texts) > 6 else '',
                    'gd': cell_texts[7] if len(cell_texts) > 7 else '',
                    'points': cell_texts[8] if len(cell_texts) > 8 else '',
                    'rank': cell_texts[9] if len(cell_texts) > 9 else '',
                    'win_rate': cell_texts[10] if len(cell_texts) > 10 else '',
                }
            return result if len(result) > 1 else None
        except Exception as e:
            print(f"解析球队积分表失败: {e}")
            return None

    def _parse_standings_js_vars(self, html: str) -> Dict:
        try:
            result = {'total': [], 'home': [], 'away': [], 'format': 'league'}
            for var_name, key in [('totalScoreStr', 'total'), ('homeScoreStr', 'home'), ('guestScoreStr', 'away')]:
                m = re.search(rf'var\s+{var_name}\s*=\s*(\[\[.*?\]\]);', html, re.DOTALL)
                if not m:
                    continue
                raw = m.group(1)
                fixed = raw.replace("'", '"')
                try:
                    data = json.loads(fixed)
                    for item in data:
                        if key == 'total' and len(item) >= 5:
                            result[key].append({
                                'rank': str(item[1]),
                                'team': str(item[3]),
                                'points': str(item[4]),
                            })
                        elif len(item) >= 4:
                            result[key].append({
                                'rank': str(item[0]),
                                'team': str(item[2]),
                                'points': str(item[3]),
                            })
                except Exception as e:
                    print(f"解析{var_name}失败: {e}")
            has_data = any(result[k] for k in ['total', 'home', 'away'])
            return result if has_data else None
        except Exception as e:
            print(f"解析积分JS变量失败: {e}")
            return None

    def _parse_h2h_records(self, soup, analysis_data):
        try:
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
                                if len(analysis_data['home_recent']) <= len(analysis_data['away_recent']):
                                    analysis_data['home_recent'].append(record)
                                else:
                                    analysis_data['away_recent'].append(record)
        except Exception as e:
            print(f"解析近期战绩失败: {e}")

    def _parse_half_full_stats(self, soup, analysis_data):
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
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 3:
                first_row = rows[0]
                headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
                header_text = ' '.join(headers)

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
        try:
            tables = soup.find_all('table')
            for table in tables:
                text = table.get_text()
                if '时间' in text and ('亚' in text or '让' in text or '大' in text or '欧' in text):
                    rows = table.find_all('tr')
                    print(f"找到即时走势表格，共 {len(rows)} 行")
                    if len(rows) >= 2:
                        data_start = 2 if len(rows) > 2 and '时间' in rows[0].get_text() else 1
                        for row in rows[data_start:]:
                            cells = row.find_all(['td', 'th'])
                            print(f"行数据: {len(cells)} 个单元格")
                            if len(cells) >= 5:
                                cell_texts = [c.get_text(strip=True) for c in cells]
                                print(f"单元格内容: {cell_texts}")

                                trend_item = {
                                    'time': cell_texts[0] if len(cell_texts) > 0 else '',
                                    'score': cell_texts[1] if len(cell_texts) > 1 else '',
                                    'half_full': cell_texts[2] if len(cell_texts) > 2 else '',
                                }

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
