import tkinter as tk
from tkinter import ttk
from typing import Dict


class JCIndexPanel:
    def __init__(self, parent, scale=1.0):
        self.parent = parent
        self.scale = scale
        self.bg_color = '#f5f5f5'
        self.header_bg = '#e8e8e8'
        self.row_bg1 = '#ffffff'
        self.row_bg2 = '#f9f9f9'
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

        self._create_european_odds_table(scrollable_frame, match, analysis_data, s)

    def _show_no_data(self):
        s = self.scale
        tk.Label(
            self.parent,
            text="暂无竞彩指数数据",
            font=('Microsoft YaHei', max(10, int(14*s))),
            fg='#aaaaaa',
            bg=self.bg_color
        ).pack(expand=True)

    def _create_section_title(self, parent, title: str):
        s = self.scale
        title_frame = tk.Frame(parent, bg='#0066cc', bd=0)
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

    def _jc_cell(self, parent, text, row, col, font, fg='#333333', bg='#FFFFFF',
                 width=6, rowspan=1, colspan=1, bold=False):
        f = ('Microsoft YaHei', font[1], 'bold') if bold else font
        lbl = tk.Label(parent, text=str(text) if text else '', font=f,
                       fg=fg, bg=bg, width=width, height=1, relief='solid', bd=1, padx=2, pady=3)
        if rowspan > 1 and colspan > 1:
            lbl.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan, sticky='nsew')
        elif rowspan > 1:
            lbl.grid(row=row, column=col, rowspan=rowspan, sticky='nsew')
        elif colspan > 1:
            lbl.grid(row=row, column=col, columnspan=colspan, sticky='nsew')
        else:
            lbl.grid(row=row, column=col, sticky='nsew')

    def _create_european_odds_table(self, parent, match: Dict, analysis_data: Dict, s):
        char_width = max(11, int(13 * s))
        font = ('Microsoft YaHei', char_width)
        font_bold = ('Microsoft YaHei', char_width, 'bold')

        is_jc = False
        jc = {}
        if analysis_data:
            jc = analysis_data.get('jc_odds', {})
            if jc and jc.get('eu_curr_home'):
                is_jc = True

        if not is_jc:
            init_home = init_draw = init_away = ''
            curr_home = curr_draw = curr_away = ''
            company = ''
            if analysis_data:
                instant = analysis_data.get('instant_eu_odds', {})
                if instant:
                    company = instant.get('company', '')
                    init_home = instant.get('init_home', '')
                    init_draw = instant.get('init_draw', '')
                    init_away = instant.get('init_away', '')
                    curr_home = instant.get('curr_home', '')
                    curr_draw = instant.get('curr_draw', '')
                    curr_away = instant.get('curr_away', '')
            if not curr_home and analysis_data:
                odds_trend = analysis_data.get('odds_trend', [])
                for item in odds_trend:
                    if item.get('company_id') == '3' or item.get('company') == 'Crow*':
                        init_home = item.get('eu_init_home', '')
                        init_draw = item.get('eu_init_draw', '')
                        init_away = item.get('eu_init_away', '')
                        curr_home = item.get('eu_curr_home', '')
                        curr_draw = item.get('eu_curr_draw', '')
                        curr_away = item.get('eu_curr_away', '')
                        company = item.get('company', '')
                        break
            has_data = any([init_home, init_draw, init_away, curr_home, curr_draw, curr_away])
            if not has_data:
                return
            title = f'即时赔率 ({company})' if company else '即时赔率'
            self._create_section_title(parent, title)
            table_outer = tk.Frame(parent, bg=self.border_color, bd=1)
            table_outer.pack(fill=tk.X, padx=5, pady=(0, 10))
            headers = ['', '主胜', '平局', '客胜']
            col_widths = [10, 12, 12, 12]
            rows = [
                ['初盘', init_home or '-', init_draw or '-', init_away or '-'],
                ['即时', curr_home or '-', curr_draw or '-', curr_away or '-']
            ]
            for i, hdr in enumerate(headers):
                tk.Label(table_outer, text=hdr, font=font_bold, fg='#333333', bg=self.header_bg,
                        width=col_widths[i], relief='solid', bd=1, padx=2, pady=3).grid(row=0, column=i, sticky='nsew')
            for row_idx, row_data in enumerate(rows):
                bg = self.row_bg1 if row_idx % 2 == 0 else self.row_bg2
                for col_idx, val in enumerate(row_data):
                    fg = '#0066cc' if col_idx == 0 else '#333333'
                    f = font_bold if col_idx == 0 else font
                    tk.Label(table_outer, text=str(val), font=f, fg=fg, bg=bg,
                            width=col_widths[col_idx], relief='solid', bd=1, padx=2, pady=2
                            ).grid(row=row_idx+1, column=col_idx, sticky='nsew')
            for c in range(len(headers)):
                table_outer.grid_columnconfigure(c, weight=1)
            return

        self._create_section_title(parent, '竞彩指数')

        header_bg = '#FDEFD2'
        sub_bg = '#ECF4FB'
        row_bg = '#FFFFFF'

        wl_home = jc.get('eu_curr_home', '')
        wl_draw = jc.get('eu_curr_draw', '')
        wl_away = jc.get('eu_curr_away', '')
        hcp = jc.get('asian_hcp', '')
        sf_home = jc.get('asian_curr_home', '')
        sf_draw = jc.get('asian_curr_draw', '')
        sf_away = jc.get('asian_curr_away', '')

        has_goal = jc.get('goal_curr_g0') is not None and jc.get('goal_curr_g0') != ''
        goal_vals = [jc.get(f'goal_curr_g{i}', '') for i in range(8)]

        has_wl_sf = any([wl_home, wl_draw, wl_away, sf_home, sf_draw, sf_away])
        if not has_wl_sf:
            return

        jc_scroll = tk.Frame(parent, bg=self.border_color)
        jc_scroll.pack(fill=tk.X, padx=5, pady=(0, 5))

        jc_canvas = tk.Canvas(jc_scroll, bg=self.border_color, highlightthickness=0)
        h_scroll = ttk.Scrollbar(jc_scroll, orient='horizontal', command=jc_canvas.xview)

        jc_inner = tk.Frame(jc_canvas, bg=self.border_color)
        jc_win_id = jc_canvas.create_window((0, 0), window=jc_inner, anchor='nw')

        def _on_inner_configure(event):
            jc_canvas.configure(scrollregion=jc_canvas.bbox('all'))
            inner_w = jc_inner.winfo_reqwidth()
            canvas_w = jc_canvas.winfo_width()
            if inner_w <= canvas_w:
                h_scroll.pack_forget()
            else:
                h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        def _on_canvas_configure(event):
            jc_canvas.itemconfig(jc_win_id, width=event.width)
            inner_h = jc_inner.winfo_reqheight()
            jc_canvas.configure(height=inner_h)

        jc_inner.bind('<Configure>', _on_inner_configure)
        jc_canvas.bind('<Configure>', _on_canvas_configure)
        jc_canvas.configure(xscrollcommand=h_scroll.set)

        jc_canvas.pack(fill=tk.X, side=tk.TOP)
        h_scroll.pack(fill=tk.X, side=tk.BOTTOM)
        h_scroll.pack_forget()

        table1 = tk.Frame(jc_inner, bg=self.border_color, bd=1)
        table1.pack(fill=tk.X, padx=0, pady=(0, 2))

        goal_count = 8 if has_goal else 0
        total_cols = 1 + 4 + goal_count

        self._jc_cell(table1, '胜平负/亚让', 0, 0, font_bold, bg=header_bg,
                      colspan=1 + 4, bold=True, width=6)
        if has_goal:
            self._jc_cell(table1, '进球数', 0, 1 + 4, font_bold, bg=header_bg,
                          colspan=goal_count, bold=True, width=6)

        self._jc_cell(table1, '全场', 1, 0, font_bold, fg='#333333', bg=sub_bg,
                      width=5, rowspan=3, bold=True)

        wl_header_labels = ['', '主胜', '平局', '客胜']
        for i in range(4):
            self._jc_cell(table1, wl_header_labels[i], 1, 1 + i, font,
                          fg='#666666', bg=sub_bg, width=6, bold=True)

        if has_goal:
            goal_labels = ['0球', '1球', '2球', '3球', '4球', '5球', '6球', '7+球']
            for i, gl in enumerate(goal_labels):
                self._jc_cell(table1, gl, 1, 5 + i, font, fg='#666666', bg=sub_bg, width=5, bold=True)

        self._jc_cell(table1, '', 2, 1, font, bg=row_bg, width=6)
        wl_vals = [wl_home, wl_draw, wl_away]
        for i, val in enumerate(wl_vals):
            self._jc_cell(table1, val if val else '', 2, 2 + i, font,
                          fg='#0055cc', bg=row_bg, width=6, bold=bool(val))

        hcp_text = ''
        if hcp != '':
            try:
                hcp_val = float(hcp)
                hcp_text = str(int(hcp_val)) if hcp_val == int(hcp_val) else str(hcp_val)
            except (ValueError, TypeError):
                hcp_text = str(hcp)

        sf_vals = [hcp_text, sf_home, sf_draw, sf_away]
        for i, val in enumerate(sf_vals):
            self._jc_cell(table1, val if val else '', 3, 1 + i, font,
                          fg='#0055cc', bg=row_bg, width=6,
                          bold=(i == 0 and bool(val)))

        if has_goal:
            for i, val in enumerate(goal_vals):
                self._jc_cell(table1, str(val) if val else '', 2, 5 + i, font,
                              fg='#0055cc', bg=row_bg, width=5)
            for i in range(goal_count):
                self._jc_cell(table1, '', 3, 5 + i, font, bg=row_bg, width=5)

        for col in range(total_cols):
            table1.grid_columnconfigure(col, weight=1)

        score_live = jc.get('score_live', {})
        if score_live and any(v for v in score_live.values() if v):
            self._create_jc_score_table(jc_inner, score_live, font, font_bold, header_bg, sub_bg, row_bg)

        hf_live = jc.get('hf_live', {})
        if hf_live and any(v for v in hf_live.values() if v):
            self._create_jc_hf_table(jc_inner, hf_live, font, font_bold, header_bg, sub_bg, row_bg)

    def _create_jc_score_table(self, parent, score_live, font, font_bold, header_bg, sub_bg, row_bg):
        table_outer = tk.Frame(parent, bg=self.border_color, bd=1)
        table_outer.pack(fill=tk.X, padx=0, pady=(0, 2))
        c = tk.Frame(table_outer, bg=self.border_color)
        c.pack(fill=tk.X)

        self._jc_cell(c, '比分', 0, 0, font_bold, bg=header_bg, width=14,
                      colspan=14, bold=True)

        win_scores = [
            ('1:0', '10'), ('2:0', '20'), ('2:1', '21'),
            ('3:0', '30'), ('3:1', '31'), ('3:2', '32'),
            ('4:0', '40'), ('4:1', '41'), ('4:2', '42'),
            ('5:0', '50'), ('5:1', '51'), ('5:2', '52'),
            ('胜其它', 'win_other'),
        ]
        draw_scores = [
            ('0:0', '00'), ('1:1', '11'), ('2:2', '22'),
            ('3:3', '33'), ('平其它', 'draw_other'),
        ]
        lose_scores = [
            ('0:1', '01'), ('0:2', '02'), ('1:2', '12'),
            ('0:3', '03'), ('1:3', '13'), ('2:3', '23'),
            ('0:4', '04'), ('1:4', '14'), ('2:4', '24'),
            ('0:5', '05'), ('1:5', '15'), ('2:5', '25'),
            ('负其它', 'lose_other'),
        ]

        self._jc_cell(c, '胜', 1, 0, font_bold, fg='#666666', bg=sub_bg, width=5, bold=True)
        for i, (label, key) in enumerate(win_scores):
            self._jc_cell(c, label, 1, 1 + i, font, fg='#666666', bg=sub_bg, width=5, bold=True)
        for i in range(len(win_scores), 13):
            self._jc_cell(c, '', 1, 1 + i, font, bg=sub_bg, width=5)

        self._jc_cell(c, '', 2, 0, font, bg=row_bg, width=5)
        for i, (label, key) in enumerate(win_scores):
            val = score_live.get(key, '')
            self._jc_cell(c, val if val else '', 2, 1 + i, font, fg='#0055cc', bg=row_bg, width=5)
        for i in range(len(win_scores), 13):
            self._jc_cell(c, '', 2, 1 + i, font, bg=row_bg, width=5)

        self._jc_cell(c, '平', 3, 0, font_bold, fg='#666666', bg=sub_bg, width=5, bold=True)
        for i, (label, key) in enumerate(draw_scores):
            self._jc_cell(c, label, 3, 1 + i, font, fg='#666666', bg=sub_bg, width=5, bold=True)
        for i in range(len(draw_scores), 13):
            self._jc_cell(c, '', 3, 1 + i, font, bg=sub_bg, width=5)

        self._jc_cell(c, '', 4, 0, font, bg=row_bg, width=5)
        for i, (label, key) in enumerate(draw_scores):
            val = score_live.get(key, '')
            self._jc_cell(c, val if val else '', 4, 1 + i, font, fg='#0055cc', bg=row_bg, width=5)
        for i in range(len(draw_scores), 13):
            self._jc_cell(c, '', 4, 1 + i, font, bg=row_bg, width=5)

        self._jc_cell(c, '负', 5, 0, font_bold, fg='#666666', bg=sub_bg, width=5, bold=True)
        for i, (label, key) in enumerate(lose_scores):
            self._jc_cell(c, label, 5, 1 + i, font, fg='#666666', bg=sub_bg, width=5, bold=True)
        for i in range(len(lose_scores), 13):
            self._jc_cell(c, '', 5, 1 + i, font, bg=sub_bg, width=5)

        self._jc_cell(c, '', 6, 0, font, bg=row_bg, width=5)
        for i, (label, key) in enumerate(lose_scores):
            val = score_live.get(key, '')
            self._jc_cell(c, val if val else '', 6, 1 + i, font, fg='#0055cc', bg=row_bg, width=5)
        for i in range(len(lose_scores), 13):
            self._jc_cell(c, '', 6, 1 + i, font, bg=row_bg, width=5)

        for col in range(14):
            c.grid_columnconfigure(col, weight=1)

    def _create_jc_hf_table(self, parent, hf_live, font, font_bold, header_bg, sub_bg, row_bg):
        table_outer = tk.Frame(parent, bg=self.border_color, bd=1)
        table_outer.pack(fill=tk.X, padx=0, pady=(0, 2))
        c = tk.Frame(table_outer, bg=self.border_color)
        c.pack(fill=tk.X)

        self._jc_cell(c, '半全场', 0, 0, font_bold, bg=header_bg, width=9 * 6,
                      colspan=9, bold=True)

        hf_labels = ['胜/胜', '胜/平', '胜/负', '平/胜', '平/平', '平/负', '负/胜', '负/平', '负/负']
        hf_keys = ['ww', 'wd', 'wl', 'dw', 'dd', 'dl', 'lw', 'ld', 'll']

        for i, lbl_text in enumerate(hf_labels):
            self._jc_cell(c, lbl_text, 1, i, font, fg='#666666', bg=sub_bg, width=6, bold=True)

        for i, key in enumerate(hf_keys):
            val = hf_live.get(key, '')
            self._jc_cell(c, val if val else '', 2, i, font, fg='#0055cc', bg=row_bg, width=6)

        for col in range(9):
            c.grid_columnconfigure(col, weight=1)
