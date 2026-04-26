import tkinter as tk
from tkinter import ttk
from typing import Dict, List
import threading
import re
from bs4 import BeautifulSoup


class OddsTrendPanel:
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
        self._popup_window = None

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

        odds_trend = analysis_data.get('odds_trend', [])
        if not odds_trend:
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

        self._create_odds_trend_table(scrollable_frame, odds_trend, s)

    def _show_no_data(self):
        s = self.scale
        tk.Label(
            self.parent,
            text="暂无即时走势数据",
            font=('Microsoft YaHei', max(10, int(14*s))),
            fg='#aaaaaa',
            bg=self.bg_color
        ).pack(expand=True)

    def _show_detail_popup(self, match_unique_id, company_id, company_name, s):
        if self._popup_window:
            try:
                self._popup_window.destroy()
            except:
                pass

        popup = tk.Toplevel(self.parent)
        popup.title(f'{company_name} 盘口变化详情')
        popup.configure(bg='#ffffff')
        popup.geometry(f"{int(850*s)}x{int(750*s)}")
        popup.attributes('-topmost', True)
        self._popup_window = popup

        header = tk.Frame(popup, bg='#0066cc')
        header.pack(fill=tk.X)
        tk.Label(header, text=f' {company_name} 盘口变化详情 ', font=('Microsoft YaHei', max(11, int(13*s)), 'bold'),
                fg='#ffffff', bg='#0066cc', padx=10, pady=5).pack(side=tk.LEFT)
        tk.Button(header, text='关闭', font=('Microsoft YaHei', max(9, int(11*s))),
                 bg='#cc0000', fg='#ffffff', relief=tk.FLAT, cursor='hand2',
                 command=popup.destroy).pack(side=tk.RIGHT, padx=10, pady=5)

        tab_bar = tk.Frame(popup, bg='#1a1a2e')
        tab_bar.pack(fill=tk.X)

        tabs = [
            ('亚让', 'handicap.aspx', 1),
            ('胜平负', '1x2.aspx', 0),
            ('进球数', 'overunder.aspx', 2),
            ('三合一', '3in1Odds.aspx', 0),
            ('半场亚让', 'handicapHalf.aspx', 3),
            ('半场进球数', 'overunderHalf.aspx', 4),
            ('角球指数', 'corner.aspx', 0),
        ]

        tab_buttons = []
        btn_font_size = max(8, int(11*s))

        content_canvas = tk.Canvas(popup, bg='#ffffff', highlightthickness=0)
        content_scrollbar = ttk.Scrollbar(popup, orient="vertical", command=content_canvas.yview)
        content_frame = tk.Frame(content_canvas, bg='#ffffff')

        content_window_id = content_canvas.create_window((0, 0), window=content_frame, anchor="nw")
        content_canvas.configure(yscrollcommand=content_scrollbar.set)

        def on_content_config(event):
            content_canvas.itemconfig(content_window_id, width=event.width)
            content_canvas.configure(scrollregion=content_canvas.bbox("all"))

        content_frame.bind("<Configure>", lambda e: content_canvas.configure(scrollregion=content_canvas.bbox("all")))
        content_canvas.bind("<Configure>", on_content_config)

        content_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def on_mousewheel(event):
            try:
                content_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass

        content_canvas.bind("<MouseWheel>", on_mousewheel)
        content_frame.bind("<MouseWheel>", on_mousewheel)
        popup.bind("<MouseWheel>", on_mousewheel)

        def _update_scroll():
            try:
                if content_canvas.winfo_exists():
                    content_canvas.update_idletasks()
                    content_canvas.configure(scrollregion=content_canvas.bbox("all"))
                    content_canvas.yview_moveto(0)
            except tk.TclError:
                pass

        def switch_tab(page_file, chart_type, active_btn):
            for btn in tab_buttons:
                btn.config(bg='#0f3460', fg='#ffffff')
            active_btn.config(bg='#e94560', fg='#ffffff')
            for w in content_frame.winfo_children():
                w.destroy()
            tk.Label(content_frame, text="加载中...", font=('Microsoft YaHei', max(10, int(14*s))),
                    fg='#aaaaaa', bg='#ffffff').pack(expand=True, pady=50)

            def fetch_page():
                try:
                    import requests
                    url = f"https://vip.titan007.com/changeDetail/{page_file}?id={match_unique_id}&companyid={company_id}"
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': 'https://zq.titan007.com/',
                    }
                    resp = requests.get(url, headers=headers, timeout=10)
                    if resp.status_code != 200:
                        popup.after(0, lambda: self._show_popup_error(content_frame, "请求失败"))
                        return
                    html = resp.content.decode('GB18030', errors='replace')
                    soup = BeautifulSoup(html, 'html.parser')

                    chart_data_str = None
                    if chart_type > 0:
                        iframe = soup.find('iframe', src=lambda x: x and 'chartFlash' in x)
                        if iframe:
                            chart_src = iframe.get('src', '')
                            if chart_src and not chart_src.startswith('http'):
                                chart_src = 'https://vip.titan007.com/changeDetail/' + chart_src
                            chart_data_str = self._fetch_chart_data(chart_src, headers)

                    popup.after(0, lambda: self._render_detail_content(
                        content_frame, soup, chart_data_str, chart_type, page_file, company_name, s, content_canvas))
                except Exception as e:
                    popup.after(0, lambda: self._show_popup_error(content_frame, str(e)))

            threading.Thread(target=fetch_page, daemon=True).start()

        for tab_name, page_file, chart_type in tabs:
            btn = tk.Button(tab_bar, text=tab_name, font=('Microsoft YaHei', btn_font_size),
                           bg='#0f3460', fg='#ffffff', relief=tk.FLAT, cursor='hand2',
                           padx=int(12*s), pady=int(6*s),
                           command=lambda pf=page_file, ct=chart_type, b=None: switch_tab(pf, ct, b))
            btn.pack(side=tk.LEFT, padx=2, pady=3)
            tab_buttons.append(btn)

        for i, (tab_name, page_file, chart_type) in enumerate(tabs):
            tab_buttons[i].config(command=lambda pf=page_file, ct=chart_type, b=tab_buttons[i]: switch_tab(pf, ct, b))

        switch_tab(tabs[0][1], tabs[0][2], tab_buttons[0])

    def _fetch_chart_data(self, chart_url, headers):
        if not chart_url:
            return None
        try:
            import requests
            resp = requests.get(chart_url, headers=headers, timeout=10)
            if resp.status_code != 200:
                return None
            html = resp.content.decode('GB18030', errors='replace')
            match = re.search(r"var\s+dataStr\s*=\s*'([^']+)'", html)
            if match:
                return match.group(1)
        except Exception as e:
            print(f"获取走势图数据失败: {e}")
        return None

    def _parse_chart_data(self, data_str):
        points = []
        if not data_str:
            return points
        for item in data_str.split(','):
            item = item.strip()
            if not item:
                continue
            parts = item.split('^')
            if len(parts) >= 5:
                try:
                    points.append({
                        'time': parts[0].strip(),
                        'val1': float(parts[1]) if parts[1].strip() else 0,
                        'handicap': parts[2].strip(),
                        'is_live': int(parts[3]) if parts[3].strip() else 0,
                        'val2': float(parts[4]) if parts[4].strip() else 0,
                    })
                except (ValueError, IndexError):
                    continue
        return points

    def _show_popup_error(self, parent, msg):
        for w in parent.winfo_children():
            w.destroy()
        tk.Label(parent, text=f"加载失败: {msg}", font=('Microsoft YaHei', 12),
                fg='#cc0000', bg='#ffffff').pack(expand=True)

    def _render_detail_content(self, parent, soup, chart_data_str, chart_type, page_file, company_name, s, scroll_canvas):
        for w in parent.winfo_children():
            w.destroy()

        if chart_type > 0:
            if chart_data_str:
                self._render_chart_canvas(parent, chart_data_str, chart_type, s, scroll_canvas)
            else:
                no_chart_frame = tk.LabelFrame(parent, text=' 走势图 ', font=('Microsoft YaHei', max(10, int(12*s)), 'bold'),
                                                fg='#0066cc', bg='#ffffff', padx=5, pady=5)
                no_chart_frame.pack(fill=tk.X, padx=5, pady=5)
                tk.Label(no_chart_frame, text="暂无走势图数据", font=('Microsoft YaHei', max(9, int(11*s))),
                        fg='#aaaaaa', bg='#ffffff').pack(pady=int(15*s))

        self._render_detail_tables(parent, soup, s, scroll_canvas)

        def _after_render():
            try:
                if scroll_canvas and scroll_canvas.winfo_exists():
                    scroll_canvas.update_idletasks()
                    scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
                    scroll_canvas.yview_moveto(0)
            except tk.TclError:
                pass

        if scroll_canvas:
            scroll_canvas.after_idle(_after_render)

    def _render_chart_canvas(self, parent, data_str, chart_type, s, scroll_canvas):
        points = self._parse_chart_data(data_str)
        if not points:
            return

        chart_w = int(750 * s)
        chart_h = int(250 * s)

        chart_frame = tk.LabelFrame(parent, text=' 走势图 ', font=('Microsoft YaHei', max(10, int(12*s)), 'bold'),
                                     fg='#0066cc', bg='#ffffff', padx=5, pady=5)
        chart_frame.pack(fill=tk.X, padx=5, pady=5)

        canvas = tk.Canvas(chart_frame, width=chart_w, height=chart_h, bg='#fafafa',
                          highlightthickness=1, highlightbackground='#cccccc')
        canvas.pack(fill=tk.X, padx=2, pady=2)

        ml = int(55 * s)
        mr = int(20 * s)
        mt = int(30 * s)
        mb = int(35 * s)
        pw = chart_w - ml - mr
        ph = chart_h - mt - mb

        vals1 = [p['val1'] for p in points if p['val1'] > 0]
        vals2 = [p['val2'] for p in points if p['val2'] > 0]
        if not vals1 and not vals2:
            return

        all_vals = vals1 + vals2
        vmin = min(all_vals)
        vmax = max(all_vals)
        vpad = (vmax - vmin) * 0.15 or 0.1
        vmin -= vpad
        vmax += vpad
        vrange = vmax - vmin

        def vy(v):
            return mt + ph * (1 - (v - vmin) / vrange)

        def vx(i):
            if len(points) <= 1:
                return ml
            return ml + pw * i / (len(points) - 1)

        canvas.create_rectangle(ml, mt, ml + pw, mt + ph, fill='#ffffff', outline='#dddddd')

        for i in range(6):
            y = mt + ph * i / 5
            v = vmax - vrange * i / 5
            canvas.create_line(ml, y, ml + pw, y, fill='#eeeeee', dash=(2, 2))
            canvas.create_text(ml - 5, y, text=f'{v:.2f}', anchor='e',
                             font=('Arial', max(7, int(8*s))), fill='#888888')

        live_start = None
        for i, p in enumerate(points):
            if p['is_live'] == 1:
                if live_start is None:
                    live_start = i

        if live_start is not None:
            x1 = vx(live_start)
            x2 = vx(len(points) - 1)
            canvas.create_rectangle(x1, mt, x2, mt + ph, fill='#fffde8', outline='')

        coords1 = []
        coords2 = []
        for i, p in enumerate(points):
            x = vx(i)
            if p['val1'] > 0:
                coords1.extend([x, vy(p['val1'])])
            if p['val2'] > 0:
                coords2.extend([x, vy(p['val2'])])

        if len(coords1) >= 4:
            canvas.create_line(coords1, fill='#e03030', width=max(1, int(2*s)), smooth=True)
        if len(coords2) >= 4:
            canvas.create_line(coords2, fill='#2060c0', width=max(1, int(2*s)), smooth=True)

        step = max(1, len(points) // 8)
        for i in range(0, len(points), step):
            x = vx(i)
            time_str = points[i]['time']
            if len(time_str) > 5:
                time_str = time_str[-5:]
            canvas.create_text(x, mt + ph + int(12*s), text=time_str, anchor='n',
                             font=('Arial', max(6, int(7*s))), fill='#888888')

        if chart_type in (1, 3):
            label1 = '主队'
            label2 = '客队'
        else:
            label1 = '大球'
            label2 = '小球'

        legend_y = mt - int(10*s)
        canvas.create_line(ml, legend_y, ml + int(20*s), legend_y, fill='#e03030', width=2)
        canvas.create_text(ml + int(25*s), legend_y, text=label1, anchor='w',
                         font=('Microsoft YaHei', max(7, int(9*s))), fill='#e03030')
        canvas.create_line(ml + int(65*s), legend_y, ml + int(85*s), legend_y, fill='#2060c0', width=2)
        canvas.create_text(ml + int(90*s), legend_y, text=label2, anchor='w',
                         font=('Microsoft YaHei', max(7, int(9*s))), fill='#2060c0')

        def _on_chart_wheel(event):
            if scroll_canvas:
                try:
                    scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                except:
                    pass

        canvas.bind("<MouseWheel>", _on_chart_wheel)
        chart_frame.bind("<MouseWheel>", _on_chart_wheel)

    def _render_detail_tables(self, parent, soup, s, scroll_canvas):
        tables = soup.find_all('table')
        if not tables:
            tk.Label(parent, text="无数据", font=('Microsoft YaHei', 12),
                    fg='#aaaaaa', bg='#ffffff').pack(expand=True)
            return

        data_tables = []
        for table in tables:
            rows = table.find_all('tr')
            if not rows:
                continue
            first_cells = rows[0].find_all(['td', 'th'], recursive=False)
            if len(first_cells) >= 5:
                header_texts = [c.get_text(strip=True) for c in first_cells]
                total_cols = sum(int(c.get('colspan', 1)) for c in first_cells)
                if total_cols < len(first_cells):
                    total_cols = len(first_cells)
                data_tables.append((table, header_texts, total_cols))

        if not data_tables:
            tk.Label(parent, text="无数据", font=('Microsoft YaHei', 12),
                    fg='#aaaaaa', bg='#ffffff').pack(expand=True)
            return

        for table, header_texts, total_cols in data_tables:
            title = '盘口变化'
            header_str = ' '.join(header_texts)

            if '主' in header_str and '盘' in header_str and '客' in header_str:
                if '角' in header_str or any('角' in h for h in header_texts):
                    title = '角球亚让盘口变化'
                else:
                    title = '亚让盘口变化'
            elif '大' in header_str and '盘' in header_str and '小' in header_str:
                if '角' in header_str:
                    title = '角球大小球盘口变化'
                else:
                    title = '进球数盘口变化'
            elif '主' in header_str and ('平' in header_str or '和' in header_str) and '客' in header_str:
                title = '胜平负盘口变化'

            self._render_single_table(parent, table, title, s, scroll_canvas, total_cols)

    def _render_single_table(self, parent, table, title, s, scroll_canvas, total_cols=None):
        rows = table.find_all('tr')
        if not rows:
            return

        first_cells = rows[0].find_all(['td', 'th'], recursive=False)
        num_cells = len(first_cells)
        if num_cells < 5:
            return

        if total_cols is None:
            total_cols = sum(int(c.get('colspan', 1)) for c in first_cells)
            if total_cols < num_cells:
                total_cols = num_cells

        table_frame = tk.LabelFrame(parent, text=f' {title} ', font=('Microsoft YaHei', max(10, int(12*s)), 'bold'),
                                     fg='#0066cc', bg='#ffffff', padx=5, pady=5)
        table_frame.pack(fill=tk.X, padx=5, pady=5)

        char_width = max(9, int(11 * s))
        font = ('Microsoft YaHei', char_width)
        font_bold = ('Microsoft YaHei', char_width, 'bold')

        if total_cols >= 7:
            col_widths = [6, 6, 9, 9, 9, 12, 5]
        elif total_cols == 6:
            col_widths = [6, 6, 9, 9, 12, 5]
        else:
            col_widths = [8] * total_cols

        while len(col_widths) < total_cols:
            col_widths.append(6)

        display_row = 0
        for row_idx, tr in enumerate(rows):
            cells = tr.find_all(['td', 'th'], recursive=False)
            if not cells:
                continue

            is_header = (display_row == 0)
            row_bg = '#FDEFD2' if is_header else ('#ffffff' if display_row % 2 == 1 else '#F2F9FD')

            col_pos = 0
            for cell_idx, td in enumerate(cells):
                colspan = int(td.get('colspan', 1))
                text = td.get_text(strip=True)

                if not is_header and colspan == 1 and cell_idx == len(cells) - 1:
                    status_match = re.search(r'(滚|即|早)$', text)
                    if status_match and total_cols == 7 and col_pos == total_cols - 2:
                        time_text = text[:status_match.start()]
                        status_text = status_match.group(1)

                        w = col_widths[col_pos] if col_pos < len(col_widths) else 8
                        lbl = tk.Label(table_frame, text=time_text, font=font, fg='#333333', bg=row_bg,
                                      width=w, relief='solid', bd=1, padx=2, pady=2)
                        lbl.grid(row=display_row, column=col_pos, sticky='nsew')
                        if scroll_canvas:
                            lbl.bind("<MouseWheel>", lambda e: scroll_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
                        col_pos += 1

                        status_fg = '#333333'
                        status_f = font
                        status_bg = row_bg
                        if status_text == '滚':
                            status_bg = '#fffde8'
                            status_fg = '#cc6600'
                            status_f = font_bold
                        elif status_text == '即':
                            status_fg = '#ff6600'
                            status_f = font_bold
                        elif status_text == '早':
                            status_fg = '#888888'

                        w = col_widths[col_pos] if col_pos < len(col_widths) else 5
                        lbl = tk.Label(table_frame, text=status_text, font=status_f, fg=status_fg, bg=status_bg,
                                      width=w, relief='solid', bd=1, padx=2, pady=2)
                        lbl.grid(row=display_row, column=col_pos, sticky='nsew')
                        if scroll_canvas:
                            lbl.bind("<MouseWheel>", lambda e: scroll_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
                        col_pos += colspan
                        continue

                fg = '#666666' if is_header else '#333333'
                f = font_bold if is_header else font
                bg = row_bg

                font_tag = td.find('font')
                if font_tag and not is_header:
                    color = font_tag.get('color', '')
                    if color in ('red', '#ff0000'):
                        fg = '#cc0000'
                    elif color in ('green', '#008000'):
                        fg = '#008800'

                cls_attr = td.get('class', [])
                if isinstance(cls_attr, list) and 'hg_red' in cls_attr and not is_header:
                    fg = '#cc0000'
                    f = font_bold

                if not is_header and text in ('滚', '即', '早') and col_pos + colspan >= total_cols:
                    if text == '滚':
                        bg = '#fffde8'
                        fg = '#cc6600'
                        f = font_bold
                    elif text == '即':
                        fg = '#ff6600'
                        f = font_bold
                    elif text == '早':
                        fg = '#888888'

                if colspan > 1:
                    w = sum(col_widths[col_pos:col_pos + colspan]) if col_pos + colspan <= len(col_widths) else 8 * colspan
                else:
                    w = col_widths[col_pos] if col_pos < len(col_widths) else 8

                lbl = tk.Label(table_frame, text=text, font=f, fg=fg, bg=bg,
                              width=w, relief='solid', bd=1, padx=2, pady=2)
                lbl.grid(row=display_row, column=col_pos, columnspan=colspan, sticky='nsew')

                if scroll_canvas:
                    lbl.bind("<MouseWheel>", lambda e: scroll_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

                col_pos += colspan

            display_row += 1

        for c in range(total_cols):
            table_frame.grid_columnconfigure(c, weight=1)

    def _create_odds_trend_table(self, parent, odds_trend: List[Dict], s):
        title_frame = tk.Frame(parent, bg='#0066cc', bd=0)
        title_frame.pack(fill=tk.X, pady=(10, 0), padx=5)

        tk.Label(title_frame, text=' 即时走势', font=('Microsoft YaHei', max(11, int(13*s)), 'bold'),
                fg='#ffffff', bg='#0066cc', padx=10, pady=5).pack(side=tk.LEFT)

        company_vars = {}
        for idx, item in enumerate(odds_trend):
            company = item.get('company', '')
            company_id = item.get('company_id', '')
            if company:
                var = tk.BooleanVar(value=(idx < 3))
                company_vars[company_id] = var
                cb = tk.Checkbutton(title_frame, text=company, variable=var,
                                    font=('Microsoft YaHei', max(10, int(12*s))),
                                    fg='#ffffff', bg='#0066cc', selectcolor='#0066cc',
                                    activebackground='#0066cc', activeforeground='#ffdd44',
                                    highlightthickness=0, bd=0, padx=5, pady=2)
                cb.pack(side=tk.LEFT, padx=2)

        table_outer = tk.Frame(parent, bg=self.border_color, bd=1)
        table_outer.pack(fill=tk.X, padx=5, pady=(0, 10))

        table_canvas = tk.Canvas(table_outer, bg=self.border_color, highlightthickness=0)
        h_scrollbar = ttk.Scrollbar(table_outer, orient="horizontal", command=table_canvas.xview)
        table_canvas.configure(xscrollcommand=h_scrollbar.set)

        table_container = tk.Frame(table_canvas, bg=self.border_color)
        table_window = table_canvas.create_window((0, 0), window=table_container, anchor="nw")

        def on_table_config(event):
            table_canvas.configure(scrollregion=table_canvas.bbox("all"))
            inner_w = table_container.winfo_reqwidth()
            inner_h = table_container.winfo_reqheight()
            canvas_w = table_canvas.winfo_width()
            table_canvas.configure(height=inner_h)
            if inner_w <= canvas_w:
                h_scrollbar.pack_forget()
            else:
                h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            table_canvas.itemconfig(table_window, width=event.width)

        table_container.bind("<Configure>", on_table_config)
        table_canvas.bind("<Configure>", lambda e: table_canvas.itemconfig(table_window, width=e.width))
        table_canvas.pack(side=tk.TOP, fill=tk.X, expand=True)

        char_width = max(11, int(13 * s))
        font = ('Microsoft YaHei', char_width)
        font_bold = ('Microsoft YaHei', char_width, 'bold')

        header_bg = '#FDEFD2'
        sub_bg = '#ECF4FB'
        init_bg = '#ffffff'
        final_bg = '#F2F9FD'
        live_bg = '#fffff0'
        eua_bg = '#FEFFEE'
        goal_bg = '#FEFFEE'

        col_widths = [8, 4, 6, 6, 6, 6, 7, 6, 7, 6, 7, 6, 7, 6, 6, 6, 4]
        headers_row1 = ['公司', '', '欧指', '', '', '欧转亚盘', '', '', '', '实际亚盘', '', '', '', '进球数', '', '', '']
        headers_row2 = ['', '', '主胜', '和局', '客胜', '主队', '亚让', '客队', '总水位', '主队', '亚让', '客队', '总水位', '大球', '盘口', '小球', '详']
        spans_row1 = {0: 2, 2: 3, 5: 4, 9: 4, 13: 3}

        row = 0
        for col_idx, hdr in enumerate(headers_row1):
            if col_idx in spans_row1:
                w = sum(col_widths[col_idx:col_idx + spans_row1[col_idx]])
                lbl = tk.Label(table_container, text=hdr, font=font_bold, fg='#666666',
                               bg=header_bg, width=w, height=1, relief='solid', bd=1, padx=2, pady=3)
                lbl.grid(row=row, column=col_idx, columnspan=spans_row1[col_idx], sticky='nsew')
            elif col_idx == 16:
                lbl = tk.Label(table_container, text='', font=font_bold, fg='#666666',
                               bg=header_bg, width=col_widths[col_idx], height=1, relief='solid', bd=1, padx=2, pady=3)
                lbl.grid(row=row, column=col_idx, sticky='nsew')

        row = 1
        for col_idx, hdr in enumerate(headers_row2):
            w = col_widths[col_idx]
            bg = sub_bg if col_idx < 16 else header_bg
            lbl = tk.Label(table_container, text=hdr, font=font_bold, fg='#666666',
                           bg=bg, width=w, height=1, relief='solid', bd=1, padx=2, pady=3)
            lbl.grid(row=row, column=col_idx, sticky='nsew')

        def get_vals(d, prefix):
            return [
                d.get(f'eu_{prefix}_home', ''),
                d.get(f'eu_{prefix}_draw', ''),
                d.get(f'eu_{prefix}_away', ''),
                d.get(f'eua_{prefix}_home', ''),
                d.get(f'eua_{prefix}_handicap', ''),
                d.get(f'eua_{prefix}_away', ''),
                d.get(f'eua_{prefix}_total', ''),
                d.get(f'real_{prefix}_home', ''),
                d.get(f'real_{prefix}_handicap', ''),
                d.get(f'real_{prefix}_away', ''),
                d.get(f'real_{prefix}_total', ''),
                d.get(f'goal_{prefix}_big', ''),
                d.get(f'goal_{prefix}_line', ''),
                d.get(f'goal_{prefix}_small', ''),
            ]

        match_unique_id = self.current_match.get('match_unique_id', '') if self.current_match else ''

        _build_lock = threading.Lock()
        _pending_build = [False]

        def build_table(*args):
            with _build_lock:
                if _pending_build[0]:
                    return
                _pending_build[0] = True

            try:
                for w in table_container.winfo_children():
                    try:
                        gi = w.grid_info()
                        if gi and int(gi.get('row', 0)) >= 2:
                            w.destroy()
                    except (tk.TclError, ValueError, KeyError):
                        pass

                filtered_trend = [item for item in odds_trend
                                  if company_vars.get(item.get('company_id', ''), tk.BooleanVar(value=True)).get()]

                r = 2
                for item in filtered_trend:
                    company = item.get('company', '')
                    company_id = item.get('company_id', '')

                    has_live = any([
                        item.get('eu_live_home'), item.get('eua_live_home'),
                        item.get('real_live_home'), item.get('goal_live_big')
                    ])

                    num_rows = 3 if has_live else 2

                    lbl = tk.Label(table_container, text=company, font=font_bold, fg='#0066cc',
                                   bg=init_bg, width=8, height=1, relief='solid', bd=1, padx=2, pady=3)
                    lbl.grid(row=r, column=0, rowspan=num_rows, sticky='nsew')

                    init_vals = get_vals(item, 'init')
                    curr_vals = get_vals(item, 'curr')
                    live_vals = get_vals(item, 'live')

                    def render_data_row(dr, label, vals, bg_color, is_bold=False):
                        type_bg = final_bg if label == '即' else (live_bg if label == '滚' else init_bg)
                        type_fg = '#ff6600' if label in ('即', '滚') else '#666666'
                        lbl_type = tk.Label(table_container, text=label, font=font_bold,
                                            fg=type_fg, bg=type_bg, width=4, height=1, relief='solid', bd=1, padx=2, pady=3)
                        lbl_type.grid(row=dr, column=1, sticky='nsew')

                        cell_bgs = [
                            init_bg, init_bg, init_bg,
                            eua_bg, eua_bg, eua_bg, eua_bg,
                            bg_color, bg_color, bg_color, bg_color,
                            goal_bg, goal_bg, goal_bg,
                        ]

                        for i, text in enumerate(vals):
                            display_text = text if text else ''
                            is_handicap = i in (4, 9, 12)
                            fg_c = '#cc3300' if is_handicap and display_text else '#0055cc'
                            f = font_bold if is_handicap and display_text else font
                            lbl = tk.Label(table_container, text=display_text, font=f,
                                           fg=fg_c, bg=cell_bgs[i], width=col_widths[i + 2],
                                           height=1, relief='solid', bd=1, padx=2, pady=3)
                            lbl.grid(row=dr, column=i + 2, sticky='nsew')

                    render_data_row(r, '初', init_vals, init_bg)
                    render_data_row(r + 1, '即', curr_vals, final_bg)

                    if has_live:
                        render_data_row(r + 2, '滚', live_vals, live_bg, is_bold=True)

                    detail_btn = tk.Label(table_container, text='详', font=font_bold,
                                         fg='#ffffff', bg='#0066cc', width=4, height=1,
                                         relief='solid', bd=1, padx=2, pady=3, cursor='hand2')
                    detail_btn.grid(row=r, column=16, rowspan=num_rows, sticky='nsew')

                    def on_detail(cid=company_id, cname=company):
                        self._show_detail_popup(match_unique_id, cid, cname, s)

                    detail_btn.bind('<Button-1>', lambda e, fn=on_detail: fn())

                    r += num_rows

                def update_canvas():
                    try:
                        if table_canvas.winfo_exists():
                            table_canvas.configure(scrollregion=table_canvas.bbox("all"),
                                                   height=table_container.winfo_reqheight())
                    except tk.TclError:
                        pass
                table_canvas.after_idle(update_canvas)
            finally:
                _pending_build[0] = False

        for var in company_vars.values():
            var.trace_add('write', lambda *args: table_container.after_idle(build_table))

        table_container.after_idle(build_table)

        for c in range(17):
            table_container.grid_columnconfigure(c, weight=1)
