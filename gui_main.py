import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
import threading
from bs4 import BeautifulSoup


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
            # 今天使用当天的接口
            return self.today_url
        else:
            # 历史日期使用历史接口
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
        
        # 解析联赛信息
        league_info = {}
        league_entries = league_data.split('!')
        for entry in league_entries:
            if not entry.strip():
                continue
            if '^' in entry:
                league_parts = entry.split('^')
                if len(league_parts) >= 4:
                    league_id = league_parts[0]
                    # 字段 [3] 格式："英文名，中文名"
                    league_name_raw = league_parts[3] if len(league_parts) > 3 else ""
                    if ',' in league_name_raw:
                        name_parts = league_name_raw.split(',')
                        league_name = name_parts[1].strip() if len(name_parts) >= 2 else name_parts[0].strip()
                    else:
                        league_name = league_name_raw.strip()
                    league_info[league_id] = league_name
        
        # 解析比赛数据
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
                
                start_time = fields[1] if len(fields) > 1 else ""
                
                # 主队：字段 [8] 格式："简体名，繁体名，英文名"
                home_team_full = fields[8] if len(fields) > 8 else ""
                if ',' in home_team_full:
                    home_parts = home_team_full.split(',')
                    home_team = home_parts[0].strip() if len(home_parts) >= 1 else home_team_full
                else:
                    home_team = home_team_full
                
                # 客队：字段 [10] 格式："简体名，繁体名，英文名"
                away_team_full = fields[10] if len(fields) > 10 else ""
                if ',' in away_team_full:
                    away_parts = away_team_full.split(',')
                    away_team = away_parts[0].strip() if len(away_parts) >= 1 else away_team_full
                else:
                    away_team = away_team_full
                
                home_score = fields[11] if len(fields) > 11 else "0"
                away_score = fields[12] if len(fields) > 12 else "0"
                
                status = fields[3] if len(fields) > 3 else "0"
                status_map = {
                    '0': '未开始',
                    '1': '进行中',
                    '2': '已完场',
                    '3': '中场',
                    '-1': '已完场'
                }
                status_text = status_map.get(status, '未知')
                
                # 解析时间
                time_parts = start_time.split(',')
                if len(time_parts) >= 5:
                    match_time = f"{time_parts[3]}:{time_parts[4]}"
                else:
                    match_time = ""
                
                # 获取盘口数据
                handicap = fields[22] if len(fields) > 22 else ""  # 让球/盘口
                
                # 数据源中只有盘口数据，欧洲指数需要从网页获取
                # 这里先使用盘口数据作为占位
                init_home_odd = ""
                init_draw_odd = ""
                init_away_odd = ""
                curr_home_odd = ""
                curr_draw_odd = ""
                curr_away_odd = ""
                
                match_info = {
                    'match_id': match_id.strip(),
                    'league': league_name,
                    'match_time': match_time,
                    'start_time': start_time,
                    'status': status_text,
                    'home_team': home_team.strip(),
                    'away_team': away_team.strip(),
                    'score': f"{home_score}:{away_score}" if home_score != '0' or away_score != '0' else '',
                    'league_id': league_id,
                    'handicap': handicap,  # 盘口数据 (如：0.5, 0.25)
                    'init_home_odd': init_home_odd,
                    'init_draw_odd': init_draw_odd,
                    'init_away_odd': init_away_odd,
                    'curr_home_odd': curr_home_odd,
                    'curr_draw_odd': curr_draw_odd,
                    'curr_away_odd': curr_away_odd,
                    'raw_data': fields
                }
                matches.append(match_info)
                
            except Exception as e:
                print(f"解析比赛失败：{e}")
                continue
        
        return matches
    
    def get_all_matches(self, date_str: Optional[str] = None) -> List[Dict]:
        """获取所有比赛数据"""
        from datetime import datetime
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        url = self.get_url_for_date(date_str)
        content = self.fetch_page(url)
        
        if not content:
            return []
        
        return self.parse_matches(content)
    
    def fetch_match_analysis(self, match_id: str) -> Dict:
        """获取比赛分析数据"""
        # 这里需要从原始数据中获取真实的比赛 ID
        # 暂时使用示例 ID
        if not match_id:
            return {}
        
        # 示例：从 raw_data 中获取 ID
        raw_data = match_id.get('raw_data', []) if isinstance(match_id, dict) else []
        real_id = raw_data[0] if raw_data else None
        
        if not real_id:
            return {}
        
        url = f"https://zq.titan007.com/analysis/{real_id}.htm"
        
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                return self.parse_analysis_data(response.text)
        except:
            pass
        
        return {}
    
    def parse_analysis_data(self, html: str) -> Dict:
        """解析分析页面数据"""
        soup = BeautifulSoup(html, 'html.parser')
        
        analysis_data = {
            'european_odds': [],
            'asian_odds': [],
            'goal_odds': []
        }
        
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 3:
                # 检测表格第一行判断类型
                first_row = rows[0]
                headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
                header_text = ' '.join(headers)
                
                # 解析欧洲指数
                if '勝' in header_text or '平' in header_text or '負' in header_text:
                    for row in rows[1:]:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 10:
                            company = cells[0].get_text(strip=True)
                            if company and '*' in company:
                                analysis_data['european_odds'].append({
                                    'company': company,
                                    'home_init': cells[1].get_text(strip=True),
                                    'draw_init': cells[2].get_text(strip=True),
                                    'away_init': cells[3].get_text(strip=True),
                                    'home_curr': cells[4].get_text(strip=True) if len(cells) > 4 else '',
                                    'draw_curr': cells[5].get_text(strip=True) if len(cells) > 5 else '',
                                    'away_curr': cells[6].get_text(strip=True) if len(cells) > 6 else ''
                                })
                
                # 解析亚洲盘口
                elif '亞' in header_text or '讓' in header_text:
                    for row in rows[1:]:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 8:
                            company = cells[0].get_text(strip=True)
                            if company and '*' in company:
                                analysis_data['asian_odds'].append({
                                    'company': company,
                                    'home_init': cells[1].get_text(strip=True),
                                    'handicap_init': cells[2].get_text(strip=True),
                                    'away_init': cells[3].get_text(strip=True),
                                    'home_curr': cells[4].get_text(strip=True) if len(cells) > 4 else '',
                                    'handicap_curr': cells[5].get_text(strip=True) if len(cells) > 5 else '',
                                    'away_curr': cells[6].get_text(strip=True) if len(cells) > 6 else ''
                                })
                
                # 解析进球数
                elif '大' in header_text or '小' in header_text:
                    for row in rows[1:]:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 8:
                            company = cells[0].get_text(strip=True)
                            if company and '*' in company:
                                analysis_data['goal_odds'].append({
                                    'company': company,
                                    'goal_init': cells[1].get_text(strip=True),
                                    'big_init': cells[2].get_text(strip=True),
                                    'small_init': cells[3].get_text(strip=True),
                                    'goal_curr': cells[4].get_text(strip=True) if len(cells) > 4 else '',
                                    'big_curr': cells[5].get_text(strip=True) if len(cells) > 5 else '',
                                    'small_curr': cells[6].get_text(strip=True) if len(cells) > 6 else ''
                                })
        
        return analysis_data


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
        
        self.setup_ui()
        self.refresh_data()
    
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
            text="🏆 竞彩足球比赛数据大屏展示系统",
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
            text="🔄 刷新数据",
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
            values=["全部", "未开始", "进行中", "已完场"]
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
            text="📋 比赛列表",
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

        # 绑定鼠标滚轮事件到画布
        self.list_canvas.bind("<MouseWheel>", lambda e: self._on_mousewheel(e, self.list_canvas))
        self.list_canvas.bind("<Button-4>", lambda e: self._on_mousewheel(e, self.list_canvas))
        self.list_canvas.bind("<Button-5>", lambda e: self._on_mousewheel(e, self.list_canvas))
        # 使用bind_all确保全局可滚动（使用当前滚动对象）
        self.root.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e))
        self.root.bind_all("<Button-4>", lambda e: self._on_mousewheel(e))
        self.root.bind_all("<Button-5>", lambda e: self._on_mousewheel(e))
        # 鼠标进入列表区域时切换当前滚动对象
        def on_enter_list(event):
            self.current_scroll_canvas = self.list_canvas
        left_frame.bind("<Enter>", on_enter_list)
        # 保存当前滚动的画布引用
        self.current_scroll_canvas = self.list_canvas

        # 右侧详情区域
        right_frame = tk.Frame(main_paned, bg='#0f3460')
        main_paned.add(right_frame)

        detail_title_font_size = max(10, int(16 * self.scale))
        detail_title = tk.Label(
            right_frame,
            text="📊 比赛详情",
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
            text="👈 请点击左侧比赛查看详情",
            font=('Microsoft YaHei', 18, 'bold'),
            fg='#ffffff',
            bg='#0f3460'
        )
        welcome_label.pack(expand=True)
    
    def refresh_data(self, date_str: Optional[str] = None):
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
        self.stats_label.config(text=f"显示：{len(self.filtered_matches)}/{len(self.matches)}")
        
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

        # 获取比分
        score = match.get('score', '')
        home_score = ''
        away_score = ''
        has_score = False
        if score and ':' in score:
            home_score, away_score = score.split(':')
            has_score = True

        # 主队信息
        home_team = match.get('home_team', '')
        if home_team:
            home_label = tk.Label(info_frame, text=home_team, font=('Microsoft YaHei', max(10, int(13*s)), 'bold'), fg='#00ff88', bg='#1a1a2e', anchor='w')
            home_label.grid(row=0, column=0, sticky='w', padx=(0, 10))
            home_label.bind('<Button-1>', on_click)

        # 比分显示
        if has_score:
            score_text = f"{home_score} - {away_score}"
            score_label = tk.Label(info_frame, text=score_text, font=('Microsoft YaHei', max(12, int(18*s)), 'bold'), fg='#ffd700', bg='#1a1a2e')
            score_label.grid(row=0, column=1, rowspan=2, padx=10)
            score_label.bind('<Button-1>', on_click)

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
        if status:
            status_label = tk.Label(status_frame, text=status, font=('Microsoft YaHei', max(8, int(10*s)), 'bold'), fg='#ffffff', bg='#0f3460', padx=int(10*s), pady=int(5*s))
            status_label.pack(side=tk.LEFT)
            status_label.bind('<Button-1>', on_click)

        handicap = match.get('handicap', '')
        if handicap:
            odds_frame = tk.Frame(status_frame, bg='#1a1a2e')
            odds_frame.pack(side=tk.RIGHT, padx=int(5*s))
            handicap_label = tk.Label(odds_frame, text=f"盘口：{handicap}", font=('Microsoft YaHei', max(8, int(10*s)), 'bold'), fg='#00ffff', bg='#1a1a2e', padx=int(10*s))
            handicap_label.pack(side=tk.RIGHT)
            handicap_label.bind('<Button-1>', on_click)

        return card
    
    def fetch_web_analysis(self, match: Dict) -> str:
        """从网页获取详细分析数据"""
        return self.parse_web_content("", match)
    
    def parse_web_content(self, html: str, match: Dict) -> str:
        """解析网页内容 - 清晰显示比赛信息"""
        # 构建清晰的内容
        lines = []
        lines.append("")
        lines.append("")
        lines.append("")
        
        # 标题
        lines.append("")
        lines.append("")
        lines.append("")
        lines.append(f"     ★ 比赛详情 - {match.get('match_id', '')} ★")
        lines.append("")
        lines.append("")
        
        # 对阵双方
        lines.append("")
        lines.append("")
        lines.append(f"     【 对阵双方 】")
        lines.append("")
        lines.append(f"           主队: {match.get('home_team', '')}")
        lines.append(f"           客队: {match.get('away_team', '')}")
        lines.append("")
        lines.append("")
        
        # 基本信息
        lines.append("")
        lines.append("")
        lines.append(f"     【 基本信息 】")
        lines.append("")
        lines.append(f"           联赛: {match.get('league', '未知')}")
        lines.append(f"           状态: {match.get('status', '未知')}")
        lines.append(f"           时间: {match.get('match_time', '未知')}")
        
        score = match.get('score', '')
        if score:
            lines.append(f"           比分: {score}")
        
        handicap = match.get('handicap', '')
        if handicap:
            try:
                handicap_val = float(handicap)
                if handicap_val > 0:
                    handicap_text = f"主队让 {handicap_val} 球"
                elif handicap_val < 0:
                    handicap_text = f"客队让 {abs(handicap_val)} 球"
                else:
                    handicap_text = "平手盘"
                lines.append(f"           盘口: {handicap} ({handicap_text})")
            except:
                lines.append(f"           盘口: {handicap}")
        
        lines.append("")
        lines.append("")
        
        # 数据统计
        lines.append("")
        lines.append("")
        lines.append(f"     【 数据统计 】")
        lines.append("")
        raw_data = match.get('raw_data', [])
        if raw_data:
            lines.append(f"           原始数据字段: {len(raw_data)}")
        
        lines.append("")
        lines.append("")
        lines.append("")
        lines.append("")
        
        return "\n".join(lines)
    
    def display_web_analysis(self, match: Dict, web_data: str, loading_label):
        s = self.scale
        loading_label.destroy()
        canvas = tk.Canvas(self.detail_frame, bg='#0f3460', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.detail_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#0f3460')
        
        detail_window_id = None
        
        def on_detail_canvas_config(event):
            if detail_window_id:
                canvas.itemconfig(detail_window_id, width=event.width)
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_detail_frame_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        canvas.bind("<Configure>", on_detail_canvas_config)
        scrollable_frame.bind("<Configure>", on_detail_frame_config)
        
        detail_window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.bind("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas))
        canvas.bind("<Button-4>", lambda e: self._on_mousewheel(e, canvas))
        canvas.bind("<Button-5>", lambda e: self._on_mousewheel(e, canvas))
        
        def on_enter_detail(event):
            self.current_scroll_canvas = canvas
        def on_leave_detail(event):
            self.current_scroll_canvas = self.list_canvas
        self.detail_frame.bind("<Enter>", on_enter_detail)
        self.detail_frame.bind("<Leave>", on_leave_detail)
        
        if web_data:
            # 美化显示
            lines = web_data.split('\n')
            for line in lines:
                line = line.rstrip()
                if not line:
                    line = ' '
                
                # 更美观的颜色方案
                fg_color = '#c0c0c0'
                bg_color = '#0f3460'
                font_size = max(10, int(12*s))
                font_weight = 'normal'
                anchor = 'w'
                
                # 根据内容类型
                if '★' in line:
                    fg_color = '#ffd700'
                    font_weight = 'bold'
                    font_size = max(14, int(16*s))
                elif '【' in line and '】' in line:
                    fg_color = '#00ff88'
                    font_weight = 'bold'
                    font_size = max(12, int(14*s))
                elif '主队:' in line or '客队:' in line or '联赛:' in line or '状态:' in line or '时间:' in line or '比分:' in line or '盘口:' in line:
                    fg_color = '#00ffff'
                else:
                    fg_color = '#e0e0e0'
                
                line_label = tk.Label(
                    scrollable_frame,
                    text=line,
                    font=('Microsoft YaHei', font_size, font_weight),
                    fg=fg_color,
                    bg=bg_color,
                    justify=tk.LEFT,
                    anchor=anchor
                )
                line_label.pack(fill=tk.X, padx=int(20*s), pady=int(3*s))
    
    def show_match_detail(self, match: Dict):
        s = self.scale
        for widget in self.detail_frame.winfo_children():
            widget.destroy()
        loading_label = tk.Label(self.detail_frame, text="正在加载详细数据...", font=('Microsoft YaHei', max(10, int(16*s))), fg='#00ff88', bg='#0f3460')
        loading_label.pack(expand=True)
        def load_web_data():
            web_data = self.fetch_web_analysis(match)
            self.root.after(0, lambda: self.display_web_analysis(match, web_data, loading_label))
        thread = threading.Thread(target=load_web_data, daemon=True)
        thread.start()
    
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
            text=f"📊 {match_id} 比赛数据详情",
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
            text="💰 让球盘口",
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
            text="📊 欧洲指数",
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
            text="🎯 亚洲盘口",
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
            text="⚽ 进球数",
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
