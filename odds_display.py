
import tkinter as tk
from tkinter import ttk
from typing import Dict, List


class OddsTableDisplay:
    """专业赔率表格显示组件"""
    
    def __init__(self, parent_frame, scale=1.0):
        self.parent = parent_frame
        self.scale = scale
        self.bg_color = '#0f3460'
        self.header_bg = '#1a5f9e'
        self.row_bg1 = '#0f3460'
        self.row_bg2 = '#1a3a5c'
        self.border_color = '#2a7cc7'
        
    def create_table(self, title: str, headers: List[str], rows: List[List], 
                     col_widths: List[int] = None, title_color: str = '#00ff88'):
        """创建一个专业表格"""
        s = self.scale
        
        # 标题
        title_frame = tk.Frame(self.parent, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(10, 0), padx=5)
        
        title_label = tk.Label(
            title_frame,
            text=f" ▼ {title} ",
            font=('Microsoft YaHei', max(12, int(14*s)), 'bold'),
            fg=title_color,
            bg=self.bg_color
        )
        title_label.pack(anchor='w')
        
        # 表格框架
        table_frame = tk.Frame(self.parent, bg=self.border_color, bd=1)
        table_frame.pack(fill=tk.X, padx=5, pady=(2, 10))
        
        # 表头
        header_frame = tk.Frame(table_frame, bg=self.header_bg)
        header_frame.pack(fill=tk.X)
        
        if not col_widths:
            col_widths = [15] * len(headers)
        
        for i, header in enumerate(headers):
            width = col_widths[i] if i < len(col_widths) else 15
            lbl = tk.Label(
                header_frame,
                text=header,
                font=('Microsoft YaHei', max(9, int(10*s)), 'bold'),
                fg='#ffffff',
                bg=self.header_bg,
                width=width,
                relief='solid',
                bd=1
            )
            lbl.pack(side=tk.LEFT, fill=tk.Y)
        
        # 数据行
        for row_idx, row_data in enumerate(rows):
            bg = self.row_bg1 if row_idx % 2 == 0 else self.row_bg2
            row_frame = tk.Frame(table_frame, bg=bg)
            row_frame.pack(fill=tk.X)
            
            for i, cell_data in enumerate(row_data):
                width = col_widths[i] if i < len(col_widths) else 15
                
                # 根据数值设置颜色
                fg = '#e0e0e0'
                if isinstance(cell_data, str):
                    if '↑' in cell_data or '涨' in cell_data:
                        fg = '#ff4444'
                    elif '↓' in cell_data or '跌' in cell_data:
                        fg = '#44ff44'
                    elif cell_data in ['主胜', '大球', '上单']:
                        fg = '#ff6b6b'
                    elif cell_data in ['客胜', '小球', '下单']:
                        fg = '#4ecdc4'
                    elif cell_data == '平局':
                        fg = '#ffd700'
                
                lbl = tk.Label(
                    row_frame,
                    text=str(cell_data),
                    font=('Consolas', max(9, int(10*s))),
                    fg=fg,
                    bg=bg,
                    width=width,
                    relief='solid',
                    bd=1
                )
                lbl.pack(side=tk.LEFT, fill=tk.Y)
    
    def create_info_card(self, match: Dict):
        """创建比赛信息卡片 - 区分实际比分和竞彩比分"""
        s = self.scale
        
        # 主信息区
        info_frame = tk.Frame(self.parent, bg='#1a5f9e', bd=2, relief='solid')
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 比赛ID和联赛
        header = tk.Frame(info_frame, bg='#1a5f9e')
        header.pack(fill=tk.X, padx=5, pady=5)
        
        match_id = match.get('match_id', '')
        league = match.get('league', '')
        
        tk.Label(header, text=match_id, font=('Microsoft YaHei', max(14, int(16*s)), 'bold'),
                fg='#ffd700', bg='#1a5f9e').pack(side=tk.LEFT)
        tk.Label(header, text=f"  {league}", font=('Microsoft YaHei', max(10, int(12*s))),
                fg='#00ff88', bg='#1a5f9e').pack(side=tk.LEFT)
        
        # 对阵双方和比分
        teams_frame = tk.Frame(info_frame, bg='#1a5f9e')
        teams_frame.pack(fill=tk.X, padx=5, pady=5)
        
        home_team = match.get('home_team', '')
        away_team = match.get('away_team', '')
        
        # 实际比分 (全场)
        home_score = match.get('home_score', '')
        away_score = match.get('away_score', '')
        # 竞彩比分 (半场)
        home_jc = match.get('home_jc_score', '')
        away_jc = match.get('away_jc_score', '')
        
        # 主队
        home_frame = tk.Frame(teams_frame, bg='#1a5f9e')
        home_frame.pack(side=tk.LEFT, expand=True)
        tk.Label(home_frame, text=home_team, font=('Microsoft YaHei', max(12, int(14*s)), 'bold'),
                fg='#ff6b6b', bg='#1a5f9e').pack()
        
        # 实际比分 (大号显示)
        if home_score != '':
            tk.Label(home_frame, text=home_score, font=('Microsoft YaHei', max(18, int(22*s)), 'bold'),
                    fg='#ffd700', bg='#1a5f9e').pack()
        
        # VS 和比分说明
        vs_frame = tk.Frame(teams_frame, bg='#1a5f9e')
        vs_frame.pack(side=tk.LEFT, padx=15)
        
        # 如果有两种比分，显示说明
        if (home_score != '' or away_score != '') and (home_jc != '' or away_jc != ''):
            tk.Label(vs_frame, text="实际", font=('Microsoft YaHei', max(8, int(10*s))),
                    fg='#00ff88', bg='#1a5f9e').pack()
        
        tk.Label(vs_frame, text="VS", font=('Microsoft YaHei', max(14, int(16*s)), 'bold'),
                fg='#ffffff', bg='#1a5f9e').pack()
        
        if (home_score != '' or away_score != '') and (home_jc != '' or away_jc != ''):
            tk.Label(vs_frame, text="竞彩", font=('Microsoft YaHei', max(8, int(10*s))),
                    fg='#ff6b6b', bg='#1a5f9e').pack()
        
        # 客队
        away_frame = tk.Frame(teams_frame, bg='#1a5f9e')
        away_frame.pack(side=tk.LEFT, expand=True)
        tk.Label(away_frame, text=away_team, font=('Microsoft YaHei', max(12, int(14*s)), 'bold'),
                fg='#4ecdc4', bg='#1a5f9e').pack()
        
        # 实际比分 (大号显示)
        if away_score != '':
            tk.Label(away_frame, text=away_score, font=('Microsoft YaHei', max(18, int(22*s)), 'bold'),
                    fg='#ffd700', bg='#1a5f9e').pack()
        
        # 竞彩比分区域 (如果与实际不同)
        if (home_jc != '' or away_jc != '') and (home_jc != home_score or away_jc != away_score):
            jc_frame = tk.Frame(info_frame, bg='#2a1a5e', bd=1, relief='solid')
            jc_frame.pack(fill=tk.X, padx=5, pady=2)
            
            jc_text = f"竞彩比分: {home_jc}:{away_jc}"
            tk.Label(jc_frame, text=jc_text, font=('Microsoft YaHei', max(10, int(12*s))),
                    fg='#ffaaaa', bg='#2a1a5e').pack()
        
        # 状态和时间
        status_frame = tk.Frame(info_frame, bg='#1a5f9e')
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        status = match.get('status', '')
        match_time = match.get('match_time', '')
        
        status_color = '#00ff88' if '未开始' in status else '#ffd700' if '进行中' in status else '#ff6b6b'
        
        tk.Label(status_frame, text=f"状态: {status}", font=('Microsoft YaHei', max(10, int(12*s))),
                fg=status_color, bg='#1a5f9e').pack(side=tk.LEFT, padx=10)
        tk.Label(status_frame, text=f"时间: {match_time}", font=('Microsoft YaHei', max(10, int(12*s))),
                fg='#00ffff', bg='#1a5f9e').pack(side=tk.LEFT, padx=10)
    
    def create_european_odds_table(self, match: Dict):
        """创建欧洲指数表格"""
        init_home = match.get('init_home_odd', '')
        init_draw = match.get('init_draw_odd', '')
        init_away = match.get('init_away_odd', '')
        curr_home = match.get('curr_home_odd', '')
        curr_draw = match.get('curr_draw_odd', '')
        curr_away = match.get('curr_away_odd', '')
        
        # 显示所有数据，即使是0
        headers = ['类型', '主胜', '平局', '客胜']
        rows = [
            ['初盘', init_home or '-', init_draw or '-', init_away or '-'],
            ['即时', curr_home or '-', curr_draw or '-', curr_away or '-']
        ]
        
        self.create_table('欧洲指数 (1X2)', headers, rows, [10, 12, 12, 12], '#ff6b6b')
    
    def create_asian_handicap_table(self, match: Dict):
        """创建亚洲让球表格"""
        handicap = match.get('handicap', '')
        
        # 解析让球
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
        rows = [
            [handicap, handicap_text]
        ]
        
        self.create_table('亚洲盘口 (让球)', headers, rows, [15, 30], '#4ecdc4')
    
    def create_match_stats(self, match: Dict):
        """创建比赛统计 - 区分实际比分和竞彩比分"""
        home_score = match.get('home_score', '')
        away_score = match.get('away_score', '')
        home_jc = match.get('home_jc_score', '')
        away_jc = match.get('away_jc_score', '')
        
        # 0也要显示，只有空字符串才显示为-
        headers = ['', '实际比分', '竞彩比分']
        rows = [
            ['主队', home_score if home_score != '' else '-', home_jc if home_jc != '' else '-'],
            ['客队', away_score if away_score != '' else '-', away_jc if away_jc != '' else '-']
        ]
        
        self.create_table('比分统计', headers, rows, [10, 10, 10], '#ffd700')
    
    def create_league_standings(self, match: Dict):
        """创建联赛积分排名表格"""
        # 这里可以从网页获取真实数据，现在使用示例数据展示格式
        headers = ['排名', '球队', '赛', '胜', '平', '负', '得', '失', '净', '积分', '胜率']
        
        # 示例数据 - 实际应从网页获取
        rows = [
            ['1', '示例球队A', '10', '8', '1', '1', '25', '10', '15', '25', '80%'],
            ['2', '示例球队B', '10', '7', '2', '1', '22', '12', '10', '23', '70%'],
        ]
        
        self.create_table('联赛积分排名', headers, rows, [6, 12, 5, 5, 5, 5, 5, 5, 5, 6, 8], '#00ff88')
    
    def create_h2h_record(self, match: Dict):
        """创建对赛往绩表格"""
        headers = ['日期', '赛事', '主队', '比分', '客队', '盘口', '结果']
        
        # 示例数据
        rows = [
            ['2024-01-15', '法乙', '阿美恩斯', '2-1', '蒙彼利埃', '-0.5', '主胜'],
            ['2023-09-20', '法乙', '蒙彼利埃', '1-1', '阿美恩斯', '0.25', '平局'],
        ]
        
        self.create_table('对赛往绩', headers, rows, [10, 8, 12, 8, 12, 8, 8], '#ffd700')
    
    def create_recent_form(self, match: Dict):
        """创建近期战绩表格"""
        headers = ['日期', '赛事', '主队', '比分', '客队', '盘口', '结果']
        
        # 示例数据
        rows = [
            ['2024-04-20', '法乙', '阿美恩斯', '1-0', '南锡', '-0.5', '主胜'],
            ['2024-04-13', '法乙', '红星', '2-1', '阿美恩斯', '0.25', '客负'],
        ]
        
        self.create_table('近期战绩', headers, rows, [10, 8, 12, 8, 12, 8, 8], '#4ecdc4')
    
    def create_half_full_stats(self, match: Dict):
        """创建半全场统计"""
        headers = ['类型', '赛', '胜', '平', '负', '得', '失', '净', '胜率']
        
        rows = [
            ['全场-总', '31', '6', '6', '19', '36', '55', '-19', '19.4%'],
            ['全场-主', '15', '2', '3', '10', '16', '27', '-11', '13.3%'],
            ['全场-客', '16', '4', '3', '9', '20', '28', '-8', '25.0%'],
            ['半场-总', '31', '8', '11', '12', '17', '26', '-9', '25.8%'],
            ['半场-主', '15', '1', '6', '8', '7', '16', '-9', '6.7%'],
            ['半场-客', '16', '7', '5', '4', '10', '10', '0', '43.8%'],
        ]
        
        self.create_table('半全场统计', headers, rows, [10, 5, 5, 5, 5, 5, 5, 5, 8], '#ff6b6b')
    
    def create_goal_stats(self, match: Dict):
        """创建进球数统计"""
        headers = ['进球数', '0球', '1球', '2球', '3球', '4球', '5球', '6球', '7+球']
        
        rows = [
            ['全场', '11', '8', '13', '4', '3', '5', '1', '4'],
            ['半场', '5', '10', '8', '5', '2', '1', '0', '0'],
        ]
        
        self.create_table('进球数统计', headers, rows, [8, 6, 6, 6, 6, 6, 6, 6, 6], '#ffd700')
    
    def create_full_display(self, match: Dict):
        """创建完整的显示，包含所有表格"""
        self.create_info_card(match)
        self.create_match_stats(match)
        self.create_european_odds_table(match)
        self.create_asian_handicap_table(match)
        self.create_league_standings(match)
        self.create_h2h_record(match)
        self.create_recent_form(match)
        self.create_half_full_stats(match)
        self.create_goal_stats(match)
