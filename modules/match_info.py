import tkinter as tk
from tkinter import ttk
from typing import Dict
from io import BytesIO
import os
import hashlib
import threading
from modules.utils import goal2goal_cn
from modules.standings import StandingsTooltip


class MatchInfoPanel:
    def __init__(self, parent, scale=1.0):
        self.parent = parent
        self.scale = scale
        self.bg_color = '#ffffff'
        self.current_match = None
        self.current_analysis = None

    def update_data(self, match: Dict, analysis_data: Dict = None):
        self.current_match = match
        self.current_analysis = analysis_data
        for widget in self.parent.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

        if not match:
            self._show_no_data()
            return

        s = self.scale
        self._create_info_card(self.parent, match, analysis_data, s)

    def _show_no_data(self):
        s = self.scale
        tk.Label(
            self.parent,
            text="请选择比赛查看信息",
            font=('Microsoft YaHei', max(10, int(12*s))),
            fg='#aaaaaa',
            bg=self.bg_color
        ).pack(expand=True, pady=10)

    def _create_info_card(self, parent, match: Dict, analysis_data: Dict, s):
        info_frame = tk.Frame(parent, bg='#ffffff', bd=1, relief='solid')
        info_frame.pack(fill=tk.X, padx=2, pady=2)

        header = tk.Frame(info_frame, bg='#0066cc')
        header.pack(fill=tk.X)

        match_id = match.get('match_id', '')

        tk.Label(header, text=f" {match_id} ", font=('Microsoft YaHei', max(11, int(13*s)), 'bold'),
                fg='#ffffff', bg='#0066cc', padx=8, pady=3).pack(side=tk.LEFT)

        league_round = match.get('league_round', '')
        league = match.get('league', '')
        display_league = league_round if league_round else league
        if display_league:
            league_label = tk.Label(header, text=f" {display_league} ", font=('Microsoft YaHei', max(9, int(11*s))),
                    fg='#ffdd44' if league_round else '#ffffff', bg='#0066cc', pady=3, cursor='hand2' if league_round else '')
            league_label.pack(side=tk.LEFT)
            standings_data = match.get('standings_data')
            if standings_data and league_round:
                home_team = match.get('home_team', '')
                away_team = match.get('away_team', '')
                StandingsTooltip(league_label, standings_data, s, home_team, away_team)

        match_date = match.get('match_date', '')
        match_time = match.get('match_time', '')
        match_day = match.get('match_day', '')
        date_parts = []
        if match_date:
            date_parts.append(match_date)
        if match_time:
            date_parts.append(match_time)
        if match_day:
            date_parts.append(match_day)
        if date_parts:
            tk.Label(header, text=f" {' '.join(date_parts)} ", font=('Microsoft YaHei', max(8, int(10*s))),
                    fg='#bbddff', bg='#0066cc', pady=3).pack(side=tk.RIGHT, padx=8)

        content_frame = tk.Frame(info_frame, bg='#ffffff')
        content_frame.pack(fill=tk.X, padx=8, pady=5)

        home_team = match.get('home_team', '')
        away_team = match.get('away_team', '')
        home_score = match.get('home_score', '')
        away_score = match.get('away_score', '')
        has_score = home_score != '' or away_score != ''

        home_frame = tk.Frame(content_frame, bg='#ffffff')
        home_frame.pack(side=tk.LEFT, expand=True)

        home_logo_url = match.get('home_logo', '')
        if home_logo_url:
            self._load_team_logo(home_frame, home_logo_url, s, '#ffffff', row=0, col=0)

        home_text_frame = tk.Frame(home_frame, bg='#ffffff')
        home_text_frame.grid(row=0, column=1, padx=3)
        tk.Label(home_text_frame, text=home_team, font=('Microsoft YaHei', max(10, int(12*s)), 'bold'),
                fg='#cc0000', bg='#ffffff').pack()

        center_frame = tk.Frame(content_frame, bg='#ffffff')
        center_frame.pack(side=tk.LEFT, padx=15)

        if has_score:
            score_text = f"{home_score} - {away_score}"
            tk.Label(center_frame, text=score_text, font=('Microsoft YaHei', max(12, int(16*s)), 'bold'),
                    fg='#ffd700', bg='#ffffff').pack()
            home_jc = match.get('home_jc_score', '')
            away_jc = match.get('away_jc_score', '')
            if home_jc != '' or away_jc != '':
                tk.Label(center_frame, text=f"({home_jc}:{away_jc})", font=('Microsoft YaHei', max(7, int(9*s))),
                        fg='#aaaaaa', bg='#ffffff').pack()
        else:
            tk.Label(center_frame, text="VS", font=('Microsoft YaHei', max(12, int(14*s)), 'bold'),
                    fg='#666666', bg='#ffffff').pack()

        away_frame = tk.Frame(content_frame, bg='#ffffff')
        away_frame.pack(side=tk.LEFT, expand=True)

        away_logo_url = match.get('away_logo', '')
        if away_logo_url:
            self._load_team_logo(away_frame, away_logo_url, s, '#ffffff', row=0, col=0)

        away_text_frame = tk.Frame(away_frame, bg='#ffffff')
        away_text_frame.grid(row=0, column=1, padx=3)
        tk.Label(away_text_frame, text=away_team, font=('Microsoft YaHei', max(10, int(12*s)), 'bold'),
                fg='#0066cc', bg='#ffffff').pack()

        status_frame = tk.Frame(info_frame, bg='#f5f5f5')
        status_frame.pack(fill=tk.X, padx=8, pady=(0, 5))

        status = match.get('status', '')
        match_time = match.get('match_time', '')

        status_color = '#009900' if '未开始' in status else '#ff6600' if '场' in status else '#cc0000'

        tk.Label(status_frame, text=f"状态: {status}", font=('Microsoft YaHei', max(8, int(10*s))),
                fg=status_color, bg='#f5f5f5').pack(side=tk.LEFT, padx=8, pady=3)
        tk.Label(status_frame, text=f"时间: {match_time}", font=('Microsoft YaHei', max(8, int(10*s))),
                fg='#666666', bg='#f5f5f5').pack(side=tk.LEFT, padx=8, pady=3)

        handicap = match.get('handicap', '')
        if handicap:
            handicap_text = goal2goal_cn(handicap)
            if handicap_text:
                prefix = "受让" if handicap_text.startswith("受让") else ""
                core = handicap_text.replace("受让", "")
                if prefix:
                    handicap_text = f"客受让 {core}"
                else:
                    try:
                        if float(handicap) > 0:
                            handicap_text = f"主让 {core}"
                        elif float(handicap) == 0:
                            handicap_text = core
                        else:
                            handicap_text = f"主受让 {core}"
                    except:
                        handicap_text = core
            tk.Label(status_frame, text=f"盘口: {handicap_text}", font=('Microsoft YaHei', max(8, int(10*s))),
                    fg='#cc0000', bg='#f5f5f5').pack(side=tk.LEFT, padx=8, pady=3)

        venue = match.get('venue', '')
        weather = match.get('weather', '')
        temperature = match.get('temperature', '')
        vw_parts = []
        if venue:
            vw_parts.append(f"场地: {venue}")
        if weather:
            vw_parts.append(f"天气: {weather}")
        if temperature:
            vw_parts.append(temperature)
        if vw_parts:
            tk.Label(status_frame, text='  '.join(vw_parts), font=('Microsoft YaHei', max(8, int(9*s))),
                    fg='#888888', bg='#f5f5f5').pack(side=tk.RIGHT, padx=8, pady=3)

    def _load_team_logo(self, parent, url, scale, bg_color, row=0, col=0):
        logo_size = max(24, int(30 * scale))

        placeholder = tk.Label(parent, text="\u26bd", font=('Microsoft YaHei', logo_size // 2),
                              bg=bg_color, width=2, height=1)
        placeholder.grid(row=row, column=col, padx=3, pady=3)

        def load_async():
            try:
                from PIL import Image, ImageTk
                import requests as req_lib

                cache_dir = os.path.join(os.path.expanduser('~'), '.jc_temp', 'logos')
                os.makedirs(cache_dir, exist_ok=True)
                cache_file = os.path.join(cache_dir, hashlib.md5(url.encode()).hexdigest() + '.png')

                if os.path.exists(cache_file):
                    img = Image.open(cache_file)
                else:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': 'https://zq.titan007.com/',
                    }
                    resp = req_lib.get(url, headers=headers, timeout=5)
                    if resp.status_code != 200:
                        return
                    img = Image.open(BytesIO(resp.content))
                    try:
                        img.save(cache_file)
                    except Exception:
                        pass

                img = img.resize((logo_size, logo_size), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                try:
                    parent.after(0, lambda: self._update_logo(placeholder, photo, bg_color, row, col))
                except tk.TclError:
                    pass
            except Exception as e:
                print(f"加载队徽失败: {e}")

        threading.Thread(target=load_async, daemon=True).start()

    def _update_logo(self, placeholder, photo, bg_color, row, col):
        try:
            master = placeholder.master
            placeholder.destroy()
            lbl = tk.Label(master, image=photo, bg=bg_color)
            lbl.image = photo
            lbl.grid(row=row, column=col, padx=3, pady=3)
        except tk.TclError:
            pass
