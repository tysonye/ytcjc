import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable


class MatchListPanel:
    def __init__(self, parent, scale=1.0, on_match_selected: Callable = None, on_refresh: Callable = None):
        self.parent = parent
        self.scale = scale
        self.on_match_selected = on_match_selected
        self.on_refresh = on_refresh
        self.matches = []
        self.filtered_matches = []
        self.list_canvas = None
        self.matches_list_frame = None
        self.list_window_id = None
        self.league_combo = None
        self.status_combo = None
        self.date_combo = None
        self.league_var = tk.StringVar(value="全部")
        self.status_var = tk.StringVar(value="全部")
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.progress_var = tk.StringVar(value="全部")
        self.stats_label = None
        self.progress_buttons = []
        self._setup_ui()

    def _setup_ui(self):
        s = self.scale
        pad = max(2, int(10 * s))

        control_frame = tk.Frame(self.parent, bg='#1a1a2e')
        control_frame.pack(fill=tk.X, padx=pad, pady=pad)

        btn_font_size = max(8, int(12 * s))
        label_font_size = max(8, int(12 * s))
        combo_font_size = max(8, int(11 * s))

        row1 = tk.Frame(control_frame, bg='#1a1a2e')
        row1.pack(fill=tk.X, pady=(0, max(2, int(5*s))))

        tk.Label(
            row1,
            text="日期:",
            font=('Microsoft YaHei', label_font_size),
            fg='#ffffff',
            bg='#1a1a2e'
        ).pack(side=tk.LEFT, padx=max(2, int(5*s)))

        today = datetime.now()
        date_list = [(today + timedelta(days=-i)).strftime('%Y-%m-%d') for i in range(7)]
        self.date_var = tk.StringVar(value=today.strftime('%Y-%m-%d'))
        self.date_combo = ttk.Combobox(
            row1,
            textvariable=self.date_var,
            state="readonly",
            width=12,
            font=('Microsoft YaHei', combo_font_size),
            values=date_list
        )
        self.date_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=max(2, int(5*s)))
        self.date_combo.bind('<<ComboboxSelected>>', self._do_refresh)

        self.stats_label = tk.Label(
            row1,
            text="0/0",
            font=('Microsoft YaHei', btn_font_size, 'bold'),
            fg='#00ff88',
            bg='#1a1a2e'
        )
        self.stats_label.pack(side=tk.RIGHT, padx=max(2, int(5*s)))

        row2 = tk.Frame(control_frame, bg='#1a1a2e')
        row2.pack(fill=tk.X, pady=(0, 0))

        progress_options = [
            ("全部", "全部"),
            ("进行中", "进行中"),
            ("未开始", "未开始"),
            ("已结束", "已结束"),
        ]
        for text, val in progress_options:
            btn = tk.Button(
                row2,
                text=text,
                font=('Microsoft YaHei', btn_font_size),
                bg='#0f3460',
                fg='#ffffff' if val != "全部" else '#00ff88',
                relief=tk.FLAT,
                cursor='hand2',
                padx=int(15*s),
                pady=int(8*s),
                command=lambda v=val: self._set_progress(v)
            )
            btn.pack(side=tk.LEFT, padx=max(1, int(3*s)))
            self.progress_buttons.append((btn, val))

        row3 = tk.Frame(control_frame, bg='#1a1a2e')
        row3.pack(fill=tk.X, pady=(0, 0))

        tk.Label(
            row3,
            text="联赛:",
            font=('Microsoft YaHei', label_font_size),
            fg='#ffffff',
            bg='#1a1a2e'
        ).pack(side=tk.LEFT, padx=max(2, int(5*s)))

        self.league_var = tk.StringVar(value="全部")
        self.league_combo = ttk.Combobox(
            row3,
            textvariable=self.league_var,
            state="readonly",
            width=16,
            font=('Microsoft YaHei', combo_font_size)
        )
        self.league_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=max(2, int(5*s)))
        self.league_combo.bind('<<ComboboxSelected>>', self._filter_matches)

        tk.Label(
            row3,
            text="状态:",
            font=('Microsoft YaHei', label_font_size),
            fg='#ffffff',
            bg='#1a1a2e'
        ).pack(side=tk.LEFT, padx=(max(2, int(10*s)), 0))

        self.status_var = tk.StringVar(value="全部")
        self.status_combo = ttk.Combobox(
            row3,
            textvariable=self.status_var,
            state="readonly",
            width=10,
            font=('Microsoft YaHei', combo_font_size),
            values=["全部", "未开始", "上半场", "中场", "下半场", "已完场"]
        )
        self.status_combo.set("全部")
        self.status_combo.pack(side=tk.LEFT, padx=max(2, int(5*s)))
        self.status_combo.bind('<<ComboboxSelected>>', self._filter_matches)

        list_canvas_frame = tk.Frame(self.parent, bg='#16213e')
        list_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=max(2, int(10*s)), pady=max(2, int(5*s)))

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

        def on_canvas_config(event):
            if self.list_window_id:
                self.list_canvas.itemconfig(self.list_window_id, width=event.width)
            self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))

        def on_frame_config(event):
            self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))

        self.list_canvas.bind("<Configure>", on_canvas_config)
        self.matches_list_frame.bind("<Configure>", on_frame_config)

        self.list_window_id = self.list_canvas.create_window((0, 0), window=self.matches_list_frame, anchor="nw")
        self.list_canvas.configure(yscrollcommand=scrollbar.set)

        self.list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _set_progress(self, value):
        self.progress_var.set(value)
        for btn, val in self.progress_buttons:
            if val == value:
                btn.config(bg='#e94560', fg='#ffffff')
            else:
                btn.config(bg='#0f3460', fg='#ffffff')
        self._filter_matches()

    def _do_refresh(self, event=None):
        if self.on_refresh:
            self.on_refresh()

    def get_date(self) -> str:
        return self.date_var.get()

    def get_list_canvas(self):
        return self.list_canvas

    def update_matches(self, matches: List[Dict]):
        self.matches = matches
        leagues = sorted(list(set([m['league'] for m in matches if m.get('league')])))
        self.league_combo['values'] = ["全部"] + leagues
        self.stats_label.config(text=f"0/{len(matches)}")
        self._filter_matches()

    def _filter_matches(self, event=None):
        league = self.league_var.get()
        status = self.status_var.get()
        progress = self.progress_var.get()

        self.filtered_matches = []
        for match in self.matches:
            if league != "全部":
                match_league = match.get('league', '').strip()
                if match_league != league.strip():
                    continue
            if status != "全部":
                match_status = match.get('status', '')
                if match_status != status:
                    continue
            if progress != "全部":
                match_status = match.get('status', '')
                if progress == "进行中":
                    if match_status not in ("上半场", "中场", "下半场"):
                        continue
                elif progress == "未开始":
                    if match_status != "未开始":
                        continue
                elif progress == "已结束":
                    if match_status != "已完场":
                        continue
            self.filtered_matches.append(match)

        self.stats_label.config(text=f"{len(self.filtered_matches)}/{len(self.matches)}")
        self._display_matches_list()

    def _display_matches_list(self):
        for widget in self.matches_list_frame.winfo_children():
            widget.destroy()

        for i, match in enumerate(self.filtered_matches):
            match_card = self._create_match_card(match, i)
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

    def _create_match_card(self, match: Dict, index: int):
        s = self.scale
        card = tk.Frame(self.matches_list_frame, bg='#1a1a2e', cursor='hand2')

        def on_click(event):
            if self.on_match_selected:
                self.on_match_selected(match)

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

        home_score = match.get('home_score', '')
        away_score = match.get('away_score', '')
        home_jc = match.get('home_jc_score', '')
        away_jc = match.get('away_jc_score', '')
        has_score = False
        if home_score != '' or away_score != '':
            has_score = True

        home_team = match.get('home_team', '')
        if home_team:
            home_label = tk.Label(info_frame, text=home_team, font=('Microsoft YaHei', max(10, int(13*s)), 'bold'), fg='#00ff88', bg='#1a1a2e', anchor='w')
            home_label.grid(row=0, column=0, sticky='w', padx=(0, 10))
            home_label.bind('<Button-1>', on_click)

        if has_score:
            score_frame = tk.Frame(info_frame, bg='#1a1a2e')
            score_frame.grid(row=0, column=1, rowspan=2, padx=10)

            score_text = f"{home_score} - {away_score}"
            score_label = tk.Label(score_frame, text=score_text, font=('Microsoft YaHei', max(12, int(18*s)), 'bold'), fg='#ffd700', bg='#1a1a2e')
            score_label.pack()
            score_label.bind('<Button-1>', on_click)

            if home_jc != '' or away_jc != '':
                jc_text = f"({home_jc}:{away_jc})"
                jc_label = tk.Label(score_frame, text=jc_text, font=('Microsoft YaHei', max(8, int(10*s))), fg='#aaaaaa', bg='#1a1a2e')
                jc_label.pack()
                jc_label.bind('<Button-1>', on_click)

        away_team = match.get('away_team', '')
        if away_team:
            away_label = tk.Label(info_frame, text=away_team, font=('Microsoft YaHei', max(10, int(13*s)), 'bold'), fg='#ff6b6b', bg='#1a1a2e', anchor='w')
            away_label.grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(5, 0))
            away_label.bind('<Button-1>', on_click)

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

        if status_code in ['1', '3']:
            display_time = None
            try:
                from datetime import datetime

                if status_code == '1':
                    time_str = match.get('start_time', '')
                else:
                    time_str = match.get('update_time', '')

                if time_str:
                    parts = time_str.split(',')
                    if len(parts) >= 6:
                        dt = datetime(int(parts[0]), int(parts[1])+1,
                                     int(parts[2]), int(parts[3]),
                                     int(parts[4]), int(parts[5]))
                        now_dt = datetime.now()
                        elapsed = int((now_dt - dt).total_seconds() // 60)

                        if status_code == '1':
                            if elapsed > 45:
                                display_time = "45+"
                            elif elapsed < 1:
                                display_time = "1'"
                            else:
                                display_time = f"{elapsed}'"
                        elif status_code == '3':
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
