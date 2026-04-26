import tkinter as tk
from tkinter import ttk
from typing import Dict, List


class StandingsTooltip:
    def __init__(self, widget, standings_data, scale, home_team='', away_team=''):
        self.widget = widget
        self.standings_data = standings_data
        self.scale = scale
        self.home_team = home_team
        self.away_team = away_team
        self.tooltip_window = None
        self.hide_after_id = None
        widget.bind('<Enter>', self.on_enter)
        widget.bind('<Leave>', self.on_leave)

    def on_enter(self, event=None):
        if self.hide_after_id:
            try:
                self.widget.after_cancel(self.hide_after_id)
            except:
                pass
            self.hide_after_id = None
        self.show_tooltip()

    def on_leave(self, event=None):
        self.hide_after_id = self.widget.after(300, self.hide_tooltip)

    def show_tooltip(self):
        if self.tooltip_window:
            return
        if not self.standings_data:
            return
        has_team_data = self.standings_data.get('home_team') or self.standings_data.get('away_team')
        has_league_data = any(self.standings_data.get(k) for k in ['total', 'home', 'away'])
        if not has_team_data and not has_league_data:
            return

        s = self.scale
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        try:
            tw.attributes('-topmost', True)
        except:
            pass

        tw.bind('<Enter>', self.on_tooltip_enter)
        tw.bind('<Leave>', self.on_tooltip_leave)

        outer = tk.Frame(tw, bg='#888888', bd=1)
        outer.pack()

        main_frame = tk.Frame(outer, bg='#ffffff')
        main_frame.pack(padx=1, pady=1)

        title_frame = tk.Frame(main_frame, bg='#0066cc')
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text=' 赛前积分榜 ', font=('Microsoft YaHei', max(10, int(12*s)), 'bold'),
                fg='#ffffff', bg='#0066cc', padx=10, pady=3).pack(side=tk.LEFT)

        if has_team_data:
            self._show_team_stats(main_frame, s)
        elif has_league_data:
            self._show_league_rankings(main_frame, s)

        self.tooltip_window = tw

    def _show_team_stats(self, parent, s):
        for team_key, color in [('home_team', '#cc0000'), ('away_team', '#0066cc')]:
            team_data = self.standings_data.get(team_key)
            if not team_data:
                continue

            team_name = team_data.get('name', '')

            header_frame = tk.Frame(parent, bg=color)
            header_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
            tk.Label(header_frame, text=f' {team_name} ', font=('Microsoft YaHei', max(10, int(12*s)), 'bold'),
                    fg='#ffffff', bg=color, padx=8, pady=3).pack(side=tk.LEFT)

            table_frame = tk.Frame(parent, bg='#ffffff')
            table_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

            headers = ['', '赛', '胜', '平', '负', '得', '失', '净', '积分', '排名', '胜率']
            col_widths = [4, 3, 3, 3, 3, 3, 3, 4, 4, 3, 5]

            char_width = max(8, int(10 * s))
            font = ('Microsoft YaHei', char_width)
            font_bold = ('Microsoft YaHei', char_width, 'bold')

            for i, hdr in enumerate(headers):
                bg = '#FDEFD2' if i == 0 else '#ECF4FB'
                tk.Label(table_frame, text=hdr, font=font_bold, fg='#666666', bg=bg,
                        width=col_widths[i], relief='solid', bd=1, padx=1, pady=1).grid(row=0, column=i, sticky='nsew')

            row_idx = 1
            for stat_type, stat_label in [('total', '总'), ('home', '主'), ('away', '客')]:
                stats = team_data.get(stat_type)
                if not stats:
                    continue

                bg = '#ffffff' if row_idx % 2 == 1 else '#F2F9FD'
                values = [stat_label, stats.get('played', ''), stats.get('won', ''), stats.get('drawn', ''),
                         stats.get('lost', ''), stats.get('gf', ''), stats.get('ga', ''), stats.get('gd', ''),
                         stats.get('points', ''), stats.get('rank', ''), stats.get('win_rate', '')]

                for col_idx, val in enumerate(values):
                    fg = '#cc0000' if col_idx == 8 and val else '#0055cc' if col_idx >= 1 else '#333333'
                    f = font_bold if col_idx in [0, 8] else font
                    tk.Label(table_frame, text=str(val), font=f, fg=fg, bg=bg,
                            width=col_widths[col_idx], relief='solid', bd=1, padx=1, pady=1
                            ).grid(row=row_idx, column=col_idx, sticky='nsew')

                row_idx += 1

    def _show_league_rankings(self, parent, s):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        for tab_name, key in [('总', 'total'), ('主', 'home'), ('客', 'away')]:
            data = self.standings_data.get(key, [])
            if not data:
                continue
            tab_frame = tk.Frame(notebook, bg='#ffffff')
            notebook.add(tab_frame, text=tab_name)
            self._create_standings_table(tab_frame, data, s)

    def _create_standings_table(self, parent, data, s):
        headers = ['排名', '球队', '积分']
        col_widths = [4, 10, 5]

        char_width = max(8, int(10 * s))
        font = ('Microsoft YaHei', char_width)
        font_bold = ('Microsoft YaHei', char_width, 'bold')

        for i, hdr in enumerate(headers):
            bg = '#FDEFD2' if i == 0 else '#ECF4FB'
            tk.Label(parent, text=hdr, font=font_bold, fg='#666666', bg=bg,
                    width=col_widths[i], relief='solid', bd=1, padx=1, pady=1).grid(row=0, column=i, sticky='nsew')

        for row_idx, item in enumerate(data):
            bg = '#ffffff' if row_idx % 2 == 0 else '#F2F9FD'
            team = item.get('team', '')
            is_home = (team == self.home_team)
            is_away = (team == self.away_team)
            if is_home:
                bg = '#ffe0e0'
            elif is_away:
                bg = '#e0e0ff'

            values = [item.get('rank', ''), item.get('team', ''), item.get('points', '')]
            for col_idx, val in enumerate(values):
                fg = '#cc0000' if is_home else '#0066cc' if is_away else '#0055cc' if col_idx >= 2 else '#333333'
                f = font_bold if (is_home or is_away or col_idx == 0) else font
                tk.Label(parent, text=str(val), font=f, fg=fg, bg=bg,
                        width=col_widths[col_idx], relief='solid', bd=1, padx=1, pady=1
                        ).grid(row=row_idx+1, column=col_idx, sticky='nsew')

    def on_tooltip_enter(self, event=None):
        if self.hide_after_id:
            try:
                self.widget.after_cancel(self.hide_after_id)
            except:
                pass
            self.hide_after_id = None

    def on_tooltip_leave(self, event=None):
        self.hide_after_id = self.widget.after(300, self.hide_tooltip)

    def hide_tooltip(self):
        if self.tooltip_window:
            try:
                self.tooltip_window.destroy()
            except:
                pass
            self.tooltip_window = None

    def destroy(self):
        self.hide_tooltip()
        try:
            self.widget.unbind('<Enter>')
            self.widget.unbind('<Leave>')
        except:
            pass


class StandingsPanel:
    def __init__(self, parent, scale=1.0):
        self.parent = parent
        self.scale = scale
        self.bg_color = '#f5f5f5'
        self.header_bg = '#FDEFD2'
        self.sub_bg = '#ECF4FB'
        self.row_bg1 = '#ffffff'
        self.row_bg2 = '#F2F9FD'
        self.border_color = '#cccccc'
        self.text_color = '#333333'
        self.title_color = '#0066cc'
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

        if not analysis_data:
            self._show_no_data()
            return

        standings = analysis_data.get('standings_data', {})
        if not standings:
            self._show_no_data()
            return

        has_team_data = standings.get('home_team') or standings.get('away_team')
        has_league_data = any(standings.get(k) for k in ['total', 'home', 'away'])

        if not has_team_data and not has_league_data:
            self._show_no_data()
            return

        s = self.scale

        canvas = tk.Canvas(self.parent, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)

        def on_canvas_config(event):
            canvas.itemconfig(canvas_window, width=event.width)
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_frame_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", on_canvas_config)
        scrollable_frame.bind("<Configure>", on_frame_config)

        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        if has_team_data:
            self._render_team_standings(scrollable_frame, standings, s)
        if has_league_data:
            self._render_league_standings(scrollable_frame, standings, s)

    def _show_no_data(self):
        s = self.scale
        tk.Label(
            self.parent,
            text="暂无赛前积分榜数据",
            font=('Microsoft YaHei', max(10, int(14*s))),
            fg='#aaaaaa',
            bg=self.bg_color
        ).pack(expand=True)

    def _create_section_title(self, parent, title: str):
        s = self.scale
        title_frame = tk.Frame(parent, bg='#0066cc', bd=0)
        title_frame.pack(fill=tk.X, pady=(10, 0), padx=5)
        tk.Label(
            title_frame,
            text=f" {title} ",
            font=('Microsoft YaHei', max(11, int(13*s)), 'bold'),
            fg='#ffffff',
            bg='#0066cc',
            padx=10,
            pady=5
        ).pack(anchor='w')

    def _render_team_standings(self, parent, standings_data: Dict, s):
        for team_key, label in [('home_team', '主队'), ('away_team', '客队')]:
            team_data = standings_data.get(team_key)
            if not team_data:
                continue

            team_name = team_data.get('name', label)
            title = f'{team_name} 积分排名'

            self._create_section_title(parent, title)

            table_outer = tk.Frame(parent, bg=self.border_color, bd=1)
            table_outer.pack(fill=tk.X, padx=5, pady=(0, 10))

            headers = ['', '赛', '胜', '平', '负', '得', '失', '净', '积分', '排名', '胜率']
            col_widths = [6, 5, 5, 5, 5, 5, 5, 6, 6, 5, 8]

            char_width = max(11, int(13 * s))
            font = ('Microsoft YaHei', char_width)
            font_bold = ('Microsoft YaHei', char_width, 'bold')

            for i, hdr in enumerate(headers):
                bg = self.header_bg if i == 0 else self.sub_bg
                tk.Label(table_outer, text=hdr, font=font_bold, fg='#666666', bg=bg,
                        width=col_widths[i], relief='solid', bd=1, padx=2, pady=3).grid(row=0, column=i, sticky='nsew')

            row_idx = 1
            for stat_type, stat_label in [('total', '总'), ('home', '主'), ('away', '客')]:
                stats = team_data.get(stat_type)
                if not stats:
                    continue
                bg = self.row_bg1 if row_idx % 2 == 1 else self.row_bg2
                values = [
                    stat_label,
                    stats.get('played', ''),
                    stats.get('won', ''),
                    stats.get('drawn', ''),
                    stats.get('lost', ''),
                    stats.get('gf', ''),
                    stats.get('ga', ''),
                    stats.get('gd', ''),
                    stats.get('points', ''),
                    stats.get('rank', ''),
                    stats.get('win_rate', '')
                ]
                for col_idx, val in enumerate(values):
                    fg = '#cc0000' if col_idx == 8 and val else '#0055cc' if col_idx >= 1 else '#333333'
                    f = font_bold if col_idx in [0, 8] else font
                    tk.Label(table_outer, text=str(val), font=f, fg=fg, bg=bg,
                            width=col_widths[col_idx], relief='solid', bd=1, padx=2, pady=2
                            ).grid(row=row_idx, column=col_idx, sticky='nsew')
                row_idx += 1

            for c in range(len(headers)):
                table_outer.grid_columnconfigure(c, weight=1)

    def _render_league_standings(self, parent, standings_data: Dict, s):
        for tab_name, key in [('总积分榜', 'total'), ('主场积分榜', 'home'), ('客场积分榜', 'away')]:
            data = standings_data.get(key, [])
            if not data:
                continue

            self._create_section_title(parent, tab_name)

            table_outer = tk.Frame(parent, bg=self.border_color, bd=1)
            table_outer.pack(fill=tk.X, padx=5, pady=(0, 10))

            headers = ['排名', '球队', '积分']
            col_widths = [6, 14, 8]

            char_width = max(11, int(13 * s))
            font = ('Microsoft YaHei', char_width)
            font_bold = ('Microsoft YaHei', char_width, 'bold')

            home_team = self.current_match.get('home_team', '') if self.current_match else ''
            away_team = self.current_match.get('away_team', '') if self.current_match else ''

            for i, hdr in enumerate(headers):
                bg = self.header_bg if i == 0 else self.sub_bg
                tk.Label(table_outer, text=hdr, font=font_bold, fg='#666666', bg=bg,
                        width=col_widths[i], relief='solid', bd=1, padx=2, pady=3).grid(row=0, column=i, sticky='nsew')

            for row_idx, item in enumerate(data):
                bg = self.row_bg1 if row_idx % 2 == 0 else self.row_bg2
                team = item.get('team', '')
                is_home = (team == home_team)
                is_away = (team == away_team)
                if is_home:
                    bg = '#ffe0e0'
                elif is_away:
                    bg = '#e0e0ff'

                values = [item.get('rank', ''), item.get('team', ''), item.get('points', '')]
                for col_idx, val in enumerate(values):
                    fg = '#cc0000' if is_home else '#0066cc' if is_away else '#0055cc' if col_idx >= 2 else '#333333'
                    f = font_bold if (is_home or is_away or col_idx == 0) else font
                    tk.Label(table_outer, text=str(val), font=f, fg=fg, bg=bg,
                            width=col_widths[col_idx], relief='solid', bd=1, padx=2, pady=2
                            ).grid(row=row_idx+1, column=col_idx, sticky='nsew')

            for c in range(len(headers)):
                table_outer.grid_columnconfigure(c, weight=1)
