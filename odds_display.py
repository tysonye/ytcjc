
import tkinter as tk
from tkinter import ttk
from typing import Dict, List


class OddsTableDisplay:
    """专业赔率表格显示组件 - 1:1复制网页效果"""

    def __init__(self, parent_frame, scale=1.0):
        self.parent = parent_frame
        self.scale = scale
        # 网页风格配色
        self.bg_color = '#f5f5f5'
        self.header_bg = '#e8e8e8'
        self.row_bg1 = '#ffffff'
        self.row_bg2 = '#f9f9f9'
        self.border_color = '#cccccc'
        self.text_color = '#333333'
        self.title_color = '#0066cc'

    def create_section_title(self, title: str):
        """创建章节标题 - 模仿网页蓝色标题栏"""
        s = self.scale
        title_frame = tk.Frame(self.parent, bg='#0066cc', bd=0)
        title_frame.pack(fill=tk.X, pady=(15, 0), padx=5)

        tk.Label(
            title_frame,
            text=f" {title} ",
            font=('Microsoft YaHei', max(11, int(13*s)), 'bold'),
            fg='#ffffff',
            bg='#0066cc',
            padx=10,
            pady=5
        ).pack(anchor='w')

    def create_odds_table_web_style(self, title: str, headers: List[str], rows: List[List],
                                    col_widths: List[int] = None, show_header: bool = True):
        """创建网页风格的赔率表格 - 使用Grid布局确保对齐"""
        s = self.scale

        # 标题
        if title:
            self.create_section_title(title)

        # 表格容器
        table_outer = tk.Frame(self.parent, bg=self.border_color, bd=1)
        table_outer.pack(fill=tk.X, padx=5, pady=(0, 10))

        # 使用Canvas作为表格容器
        table_canvas = tk.Canvas(table_outer, bg=self.border_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_outer, orient="horizontal", command=table_canvas.xview)
        table_canvas.configure(xscrollcommand=scrollbar.set)

        table_container = tk.Frame(table_canvas, bg=self.border_color)
        table_window = table_canvas.create_window((0, 0), window=table_container, anchor="nw")

        def on_table_config(event):
            table_canvas.configure(scrollregion=table_canvas.bbox("all"))
            table_canvas.itemconfig(table_window, width=event.width)

        table_container.bind("<Configure>", on_table_config)
        table_canvas.bind("<Configure>", lambda e: table_canvas.itemconfig(table_window, width=e.width))

        table_canvas.pack(side=tk.TOP, fill=tk.X, expand=True)

        if not col_widths:
            col_widths = [12] * len(headers)

        char_width = max(8, int(10 * s))
        base_width = char_width * 2

        # 表头
        if show_header and headers:
            for i, header in enumerate(headers):
                width = col_widths[i] if i < len(col_widths) else 12
                cell_width = width * base_width
                lbl = tk.Label(
                    table_container,
                    text=header,
                    font=('Microsoft YaHei', char_width, 'bold'),
                    fg='#333333',
                    bg=self.header_bg,
                    width=width,
                    relief='solid',
                    bd=1,
                    padx=2,
                    pady=3
                )
                lbl.grid(row=0, column=i, sticky='nsew')
                table_container.grid_columnconfigure(i, minsize=cell_width)

        # 数据行
        for row_idx, row_data in enumerate(rows):
            bg = self.row_bg1 if row_idx % 2 == 0 else self.row_bg2

            for i, cell_data in enumerate(row_data):
                width = col_widths[i] if i < len(col_widths) else 12

                fg = '#333333'
                font_weight = 'normal'

                if isinstance(cell_data, str):
                    if cell_data.startswith('+') or '↑' in cell_data:
                        fg = '#ff0000'
                    elif cell_data.startswith('-') or '↓' in cell_data:
                        fg = '#008000'
                    elif cell_data in ['主胜', '大', '上单']:
                        fg = '#cc0000'
                    elif cell_data in ['客胜', '小', '下单']:
                        fg = '#0066cc'
                    elif cell_data == '平':
                        fg = '#009900'
                    elif i == 0 and len(cell_data) > 1:
                        font_weight = 'bold'
                        fg = '#0066cc'

                lbl = tk.Label(
                    table_container,
                    text=str(cell_data),
                    font=('Microsoft YaHei', char_width, font_weight),
                    fg=fg,
                    bg=bg,
                    width=width,
                    relief='solid',
                    bd=1,
                    padx=2,
                    pady=2
                )
                lbl.grid(row=row_idx + 1, column=i, sticky='nsew')

        for r in range(len(rows) + 1):
            table_container.grid_rowconfigure(r, weight=1)

    def create_trend_table(self, title: str, trend_data: List[Dict]):
        """创建即时走势表格 - 包含让球/大小球/欧洲指数"""
        if not trend_data:
            return

        headers = ['时间', '比分', '半全场', '让球-开盘主水', '让球-开盘盘口', '让球-开盘客水',
                   '让球-即时主水', '让球-即时盘口', '让球-即时客水',
                   '进球数-开盘大球', '进球数-开盘盘口', '进球数-开盘小球',
                   '进球数-即时大球', '进球数-即时盘口', '进球数-即时小球',
                   '欧指-主胜', '欧指-平局', '欧指-客胜']
        col_widths = [6, 6, 6, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]

        rows = []
        for item in trend_data:
            rows.append([
                item.get('time', ''),
                item.get('score', ''),
                item.get('half_full', ''),
                item.get('asian_home_init', ''),
                item.get('asian_handicap_init', ''),
                item.get('asian_away_init', ''),
                item.get('asian_home_curr', ''),
                item.get('asian_handicap_curr', ''),
                item.get('asian_away_curr', ''),
                item.get('goal_big_init', ''),
                item.get('goal_handicap_init', ''),
                item.get('goal_small_init', ''),
                item.get('goal_big_curr', ''),
                item.get('goal_handicap_curr', ''),
                item.get('goal_small_curr', ''),
                item.get('euro_home', ''),
                item.get('euro_draw', ''),
                item.get('euro_away', '')
            ])

        self.create_odds_table_web_style(title, headers, rows, col_widths)

    def create_company_odds_table(self, title: str, odds_list: List[Dict], odds_type: str):
        """创建公司赔率表格 - 网页标准格式"""
        if not odds_list:
            return

        if odds_type == 'european':
            headers = ['公司', '主胜(初)', '平局(初)', '客胜(初)', '主胜(即)', '平局(即)', '客胜(即)']
            col_widths = [12, 10, 10, 10, 10, 10, 10]
            rows = []
            for odd in odds_list:
                rows.append([
                    odd.get('company', ''),
                    odd.get('home_init', '-'),
                    odd.get('draw_init', '-'),
                    odd.get('away_init', '-'),
                    odd.get('home_curr', '-'),
                    odd.get('draw_curr', '-'),
                    odd.get('away_curr', '-')
                ])

        elif odds_type == 'asian':
            headers = ['公司', '主水(初)', '盘口(初)', '客水(初)', '主水(即)', '盘口(即)', '客水(即)']
            col_widths = [12, 10, 10, 10, 10, 10, 10]
            rows = []
            for odd in odds_list:
                rows.append([
                    odd.get('company', ''),
                    odd.get('home_init', '-'),
                    odd.get('handicap_init', '-'),
                    odd.get('away_init', '-'),
                    odd.get('home_curr', '-'),
                    odd.get('handicap_curr', '-'),
                    odd.get('away_curr', '-')
                ])

        elif odds_type == 'goal':
            headers = ['公司', '盘口(初)', '大球(初)', '小球(初)', '盘口(即)', '大球(即)', '小球(即)']
            col_widths = [12, 10, 10, 10, 10, 10, 10]
            rows = []
            for odd in odds_list:
                rows.append([
                    odd.get('company', ''),
                    odd.get('goal_init', '-'),
                    odd.get('big_init', '-'),
                    odd.get('small_init', '-'),
                    odd.get('goal_curr', '-'),
                    odd.get('big_curr', '-'),
                    odd.get('small_curr', '-')
                ])
        else:
            return

        self.create_odds_table_web_style(title, headers, rows, col_widths)

    def create_standings_table(self, title: str, teams_data: List[Dict]):
        """创建积分排名表格"""
        headers = ['排名', '球队', '赛', '胜', '平', '负', '得', '失', '净', '积分', '胜率']
        col_widths = [6, 14, 5, 5, 5, 5, 5, 5, 6, 6, 8]

        rows = []
        for team in teams_data:
            rows.append([
                team.get('rank', ''),
                team.get('team', '')[:10],
                team.get('played', ''),
                team.get('won', ''),
                team.get('drawn', ''),
                team.get('lost', ''),
                team.get('gf', ''),
                team.get('ga', ''),
                team.get('gd', ''),
                team.get('points', ''),
                team.get('win_rate', '')
            ])

        self.create_odds_table_web_style(title, headers, rows, col_widths)

    def create_match_record_table(self, title: str, records: List[Dict]):
        """创建比赛记录表格"""
        headers = ['日期', '赛事', '主队', '比分', '客队', '盘口', '结果']
        col_widths = [10, 8, 12, 8, 12, 8, 8]

        rows = []
        for record in records:
            rows.append([
                record.get('date', ''),
                record.get('league', ''),
                record.get('home_team', '')[:8],
                record.get('score', ''),
                record.get('away_team', '')[:8],
                record.get('handicap', ''),
                record.get('result', '')
            ])

        self.create_odds_table_web_style(title, headers, rows, col_widths)

    def create_stats_table(self, title: str, stats_data: List[Dict]):
        """创建统计数据表格"""
        if not stats_data:
            return

        first = stats_data[0] if stats_data else {}
        if '0' in first:
            headers = ['类型', '0球', '1球', '2球', '3球', '4球', '5球', '6球', '7+球']
            col_widths = [8, 7, 7, 7, 7, 7, 7, 7, 7]
            rows = []
            for stat in stats_data:
                rows.append([
                    stat.get('type', ''),
                    stat.get('0', ''),
                    stat.get('1', ''),
                    stat.get('2', ''),
                    stat.get('3', ''),
                    stat.get('4', ''),
                    stat.get('5', ''),
                    stat.get('6', ''),
                    stat.get('7+', '')
                ])
        else:
            headers = ['类型', '赛', '胜', '平', '负', '得', '失', '净', '胜率']
            col_widths = [10, 5, 5, 5, 5, 5, 5, 6, 8]
            rows = []
            for stat in stats_data:
                rows.append([
                    stat.get('type', ''),
                    stat.get('played', ''),
                    stat.get('won', ''),
                    stat.get('drawn', ''),
                    stat.get('lost', ''),
                    stat.get('gf', ''),
                    stat.get('ga', ''),
                    stat.get('gd', ''),
                    stat.get('win_rate', '')
                ])

        self.create_odds_table_web_style(title, headers, rows, col_widths)

    def create_info_card(self, match: Dict):
        """创建比赛信息卡片"""
        s = self.scale

        info_frame = tk.Frame(self.parent, bg='#ffffff', bd=2, relief='solid')
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        header = tk.Frame(info_frame, bg='#0066cc')
        header.pack(fill=tk.X)

        match_id = match.get('match_id', '')
        league = match.get('league', '')

        tk.Label(header, text=f" {match_id} ", font=('Microsoft YaHei', max(14, int(16*s)), 'bold'),
                fg='#ffffff', bg='#0066cc', padx=10, pady=5).pack(side=tk.LEFT)
        tk.Label(header, text=f" {league} ", font=('Microsoft YaHei', max(10, int(12*s))),
                fg='#ffffff', bg='#0066cc', pady=5).pack(side=tk.LEFT)

        teams_frame = tk.Frame(info_frame, bg='#ffffff')
        teams_frame.pack(fill=tk.X, padx=10, pady=10)

        home_team = match.get('home_team', '')
        away_team = match.get('away_team', '')
        home_score = match.get('home_score', '')
        away_score = match.get('away_score', '')
        home_jc = match.get('home_jc_score', '')
        away_jc = match.get('away_jc_score', '')

        home_frame = tk.Frame(teams_frame, bg='#ffffff')
        home_frame.pack(side=tk.LEFT, expand=True)
        tk.Label(home_frame, text=home_team, font=('Microsoft YaHei', max(12, int(14*s)), 'bold'),
                fg='#cc0000', bg='#ffffff').pack()
        if home_score != '':
            tk.Label(home_frame, text=home_score, font=('Microsoft YaHei', max(20, int(24*s)), 'bold'),
                    fg='#cc0000', bg='#ffffff').pack()

        vs_frame = tk.Frame(teams_frame, bg='#ffffff')
        vs_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(vs_frame, text="VS", font=('Microsoft YaHei', max(14, int(16*s)), 'bold'),
                fg='#666666', bg='#ffffff').pack()

        away_frame = tk.Frame(teams_frame, bg='#ffffff')
        away_frame.pack(side=tk.LEFT, expand=True)
        tk.Label(away_frame, text=away_team, font=('Microsoft YaHei', max(12, int(14*s)), 'bold'),
                fg='#0066cc', bg='#ffffff').pack()
        if away_score != '':
            tk.Label(away_frame, text=away_score, font=('Microsoft YaHei', max(20, int(24*s)), 'bold'),
                    fg='#0066cc', bg='#ffffff').pack()

        if (home_jc != '' or away_jc != '') and (home_jc != home_score or away_jc != away_score):
            jc_frame = tk.Frame(info_frame, bg='#fff8e1', bd=1, relief='solid')
            jc_frame.pack(fill=tk.X, padx=10, pady=5)
            jc_text = f"半场比分: {home_jc}:{away_jc}"
            tk.Label(jc_frame, text=jc_text, font=('Microsoft YaHei', max(10, int(12*s))),
                    fg='#ff6600', bg='#fff8e1').pack(pady=3)

        status_frame = tk.Frame(info_frame, bg='#f5f5f5')
        status_frame.pack(fill=tk.X, padx=10, pady=5)

        status = match.get('status', '')
        match_time = match.get('match_time', '')

        status_color = '#009900' if '未开始' in status else '#ff6600' if '场' in status else '#cc0000'

        tk.Label(status_frame, text=f"状态: {status}", font=('Microsoft YaHei', max(10, int(12*s))),
                fg=status_color, bg='#f5f5f5').pack(side=tk.LEFT, padx=10, pady=5)
        tk.Label(status_frame, text=f"时间: {match_time}", font=('Microsoft YaHei', max(10, int(12*s))),
                fg='#666666', bg='#f5f5f5').pack(side=tk.LEFT, padx=10, pady=5)

    def create_european_odds_table(self, match: Dict):
        """创建简版欧洲指数表格"""
        init_home = match.get('init_home_odd', '')
        init_draw = match.get('init_draw_odd', '')
        init_away = match.get('init_away_odd', '')
        curr_home = match.get('curr_home_odd', '')
        curr_draw = match.get('curr_draw_odd', '')
        curr_away = match.get('curr_away_odd', '')

        # 调试输出
        print(f"赔率数据: 初盘 {init_home}/{init_draw}/{init_away}, 即时 {curr_home}/{curr_draw}/{curr_away}")

        headers = ['', '主胜', '平局', '客胜']
        col_widths = [10, 12, 12, 12]
        rows = [
            ['初盘', init_home or '-', init_draw or '-', init_away or '-'],
            ['即时', curr_home or '-', curr_draw or '-', curr_away or '-']
        ]

        self.create_odds_table_web_style('即时赔率', headers, rows, col_widths)

    def create_asian_handicap_table(self, match: Dict):
        """创建简版亚洲盘口表格"""
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
        else:
            handicap = '-'
            handicap_text = '暂无数据'

        headers = ['盘口', '说明']
        col_widths = [15, 35]
        rows = [[handicap, handicap_text]]

        self.create_odds_table_web_style('让球盘口', headers, rows, col_widths)

    def create_full_display(self, match: Dict, analysis_data: Dict = None):
        """创建完整的显示，包含即时走势三个选项"""
        # 比赛信息卡
        self.create_info_card(match)

        # 即时赔率
        self.create_european_odds_table(match)
        self.create_asian_handicap_table(match)

        if analysis_data:
            # 即时走势 - 包含让球/大小球/欧洲指数
            trend_data = analysis_data.get('trend_data', [])
            if trend_data:
                self.create_trend_table('即时走势 (让球/大小球/欧洲指数)', trend_data)

            # 欧洲指数
            euro_odds = analysis_data.get('european_odds', [])
            if euro_odds:
                self.create_company_odds_table('欧洲指数', euro_odds, 'european')

            # 亚洲盘口
            asian_odds = analysis_data.get('asian_odds', [])
            if asian_odds:
                self.create_company_odds_table('亚洲盘口', asian_odds, 'asian')

            # 进球数
            goal_odds = analysis_data.get('goal_odds', [])
            if goal_odds:
                self.create_company_odds_table('进球数', goal_odds, 'goal')

            # 联赛积分排名
            standings = analysis_data.get('league_standings', {})
            home_standings = standings.get('home', [])
            away_standings = standings.get('away', [])
            if home_standings:
                self.create_standings_table(f'{match.get("home_team", "主队")} 联赛排名', home_standings)
            if away_standings:
                self.create_standings_table(f'{match.get("away_team", "客队")} 联赛排名', away_standings)

            # 对赛往绩
            h2h = analysis_data.get('h2h_records', [])
            if h2h:
                self.create_match_record_table('对赛往绩', h2h)

            # 近期战绩
            home_recent = analysis_data.get('home_recent', [])
            away_recent = analysis_data.get('away_recent', [])
            if home_recent:
                self.create_match_record_table(f'{match.get("home_team", "主队")} 近期战绩', home_recent)
            if away_recent:
                self.create_match_record_table(f'{match.get("away_team", "客队")} 近期战绩', away_recent)

            # 半全场统计
            half_full = analysis_data.get('half_full_stats', {})
            home_hf = half_full.get('home', [])
            away_hf = half_full.get('away', [])
            if home_hf or away_hf:
                all_hf = home_hf + away_hf
                if all_hf:
                    self.create_stats_table('半全场统计', all_hf)

            # 进球数统计
            goal_stats = analysis_data.get('goal_stats', {})
            home_goal = goal_stats.get('home', {})
            away_goal = goal_stats.get('away', {})
            if home_goal or away_goal:
                all_goals = []
                if home_goal:
                    all_goals.append(home_goal)
                if away_goal:
                    all_goals.append(away_goal)
                if all_goals:
                    self.create_stats_table('进球数统计', all_goals)
