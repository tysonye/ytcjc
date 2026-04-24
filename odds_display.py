
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
        """创建比赛信息卡片"""
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
        
        # 对阵双方
        teams_frame = tk.Frame(info_frame, bg='#1a5f9e')
        teams_frame.pack(fill=tk.X, padx=5, pady=5)
        
        home_team = match.get('home_team', '')
        away_team = match.get('away_team', '')
        home_score = match.get('home_score', '')
        away_score = match.get('away_score', '')
        
        # 主队
        home_frame = tk.Frame(teams_frame, bg='#1a5f9e')
        home_frame.pack(side=tk.LEFT, expand=True)
        tk.Label(home_frame, text=home_team, font=('Microsoft YaHei', max(12, int(14*s)), 'bold'),
                fg='#ff6b6b', bg='#1a5f9e').pack()
        if home_score and home_score != '0':
            tk.Label(home_frame, text=home_score, font=('Microsoft YaHei', max(16, int(20*s)), 'bold'),
                    fg='#ffd700', bg='#1a5f9e').pack()
        
        # VS
        vs_frame = tk.Frame(teams_frame, bg='#1a5f9e')
        vs_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(vs_frame, text="VS", font=('Microsoft YaHei', max(14, int(16*s)), 'bold'),
                fg='#ffffff', bg='#1a5f9e').pack()
        
        # 客队
        away_frame = tk.Frame(teams_frame, bg='#1a5f9e')
        away_frame.pack(side=tk.LEFT, expand=True)
        tk.Label(away_frame, text=away_team, font=('Microsoft YaHei', max(12, int(14*s)), 'bold'),
                fg='#4ecdc4', bg='#1a5f9e').pack()
        if away_score and away_score != '0':
            tk.Label(away_frame, text=away_score, font=('Microsoft YaHei', max(16, int(20*s)), 'bold'),
                    fg='#ffd700', bg='#1a5f9e').pack()
        
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
        
        if not any([init_home, init_draw, init_away, curr_home, curr_draw, curr_away]):
            return
        
        headers = ['类型', '主胜', '平局', '客胜', '变化']
        rows = [
            ['初盘', init_home, init_draw, init_away, '-'],
            ['即时', curr_home, curr_draw, curr_away, '-']
        ]
        
        self.create_table('欧洲指数 (1X2)', headers, rows, [10, 12, 12, 12, 10], '#ff6b6b')
    
    def create_asian_handicap_table(self, match: Dict):
        """创建亚洲让球表格"""
        handicap = match.get('handicap', '')
        
        if not handicap:
            return
        
        # 解析让球
        handicap_text = ""
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
        
        headers = ['盘口', '说明', '主队水位', '客队水位']
        rows = [
            [handicap, handicap_text, '-', '-']
        ]
        
        self.create_table('亚洲盘口 (让球)', headers, rows, [12, 20, 12, 12], '#4ecdc4')
    
    def create_match_stats(self, match: Dict):
        """创建比赛统计"""
        home_score = match.get('home_score', '0')
        away_score = match.get('away_score', '0')
        home_half = match.get('home_half_score', '0')
        away_half = match.get('away_half_score', '0')
        
        if home_score == '0' and away_score == '0':
            return
        
        headers = ['', '全场', '半场']
        rows = [
            ['主队', home_score, f"{home_half}"],
            ['客队', away_score, f"{away_half}"]
        ]
        
        self.create_table('比分统计', headers, rows, [10, 10, 10], '#ffd700')
