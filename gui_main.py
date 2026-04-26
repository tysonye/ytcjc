import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional
import threading
import random

from modules.scraper import MatchScraper
from modules.match_list import MatchListPanel
from modules.match_info import MatchInfoPanel
from modules.standings import StandingsPanel
from modules.odds_trend import OddsTrendPanel
from modules.jc_index import JCIndexPanel


class MatchDisplayApp:

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
        self.root.bind('<Configure>', self._on_resize)

        self.matches = []
        self.scraper = MatchScraper()
        self.auto_refresh_after_id = None
        self._current_load_event = None
        self._current_detail_match_id = ''
        self._current_analysis_data = None

        self._setup_ui()
        self._refresh_data()
        self._start_auto_refresh()

    def _on_resize(self, event):
        if event.widget == self.root:
            new_scale = min(event.width / 1920, event.height / 1080)
            self.scale = max(0.5, new_scale)

    def _get_font(self, base_size, weight='normal'):
        size = max(8, int(base_size * self.scale))
        return ('Microsoft YaHei', size, weight)

    def _get_pad(self, base_pad):
        return max(2, int(base_pad * self.scale))

    def _setup_ui(self):
        pad = self._get_pad(10)
        title_height = int(80 * self.scale)

        title_frame = tk.Frame(self.root, bg='#16213e', height=title_height)
        title_frame.pack(fill=tk.X, padx=pad, pady=pad)

        title_font_size = max(12, int(24 * self.scale))
        title_label = tk.Label(
            title_frame,
            text="竞彩足球比赛数据大屏展示系统",
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
        self._update_time()

        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=pad, pady=pad)

        left_width = int(350 * self.scale)

        left_frame = tk.Frame(main_frame, bg='#16213e', width=left_width)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        left_frame.pack_propagate(False)

        self.match_list_panel = MatchListPanel(
            left_frame,
            scale=self.scale,
            on_match_selected=self._on_match_selected,
            on_refresh=lambda: self._refresh_data(date_str=self.match_list_panel.get_date())
        )

        right_frame = tk.Frame(main_frame, bg='#0f3460')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        match_info_frame = tk.Frame(right_frame, bg='#f5f5f5')
        match_info_frame.pack(fill=tk.X, padx=self._get_pad(5), pady=self._get_pad(5))
        self.match_info_panel = MatchInfoPanel(match_info_frame, scale=self.scale)

        style = ttk.Style()
        style.configure('Detail.TNotebook', background='#0f3460')
        style.configure('Detail.TNotebook.Tab', font=('Microsoft YaHei', max(9, int(11*self.scale)), 'bold'),
                        padding=[int(15*self.scale), int(8*self.scale)])

        self.notebook = ttk.Notebook(right_frame, style='Detail.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=self._get_pad(10), pady=self._get_pad(5))

        tab1_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(tab1_frame, text='赛前积分榜')
        self.standings_panel = StandingsPanel(tab1_frame, scale=self.scale)

        tab2_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(tab2_frame, text='即时走势')
        self.odds_trend_panel = OddsTrendPanel(tab2_frame, scale=self.scale)

        tab3_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(tab3_frame, text='竞彩指数')
        self.jc_index_panel = JCIndexPanel(tab3_frame, scale=self.scale)

        self._bind_mousewheel()

    def _bind_mousewheel(self):
        def on_global_mousewheel(event):
            x = event.x_root
            y = event.y_root

            try:
                list_canvas = self.match_list_panel.get_list_canvas()
                if list_canvas and list_canvas.winfo_exists():
                    lx = list_canvas.winfo_rootx()
                    ly = list_canvas.winfo_rooty()
                    lw = list_canvas.winfo_width()
                    lh = list_canvas.winfo_height()
                    if lx <= x <= lx + lw and ly <= y <= ly + lh:
                        self._on_mousewheel(event, list_canvas)
                        return
            except tk.TclError:
                pass

            try:
                nb = self.notebook
                if nb and nb.winfo_exists():
                    nx = nb.winfo_rootx()
                    ny = nb.winfo_rooty()
                    nw = nb.winfo_width()
                    nh = nb.winfo_height()
                    if nx <= x <= nx + nw and ny <= y <= ny + nh:
                        current_tab = nb.index(nb.select())
                        for widget in nb.winfo_children():
                            try:
                                if widget.winfo_viewable():
                                    for canvas in widget.winfo_children():
                                        if isinstance(canvas, tk.Canvas) and canvas.winfo_exists():
                                            self._on_mousewheel(event, canvas)
                                            return
                            except tk.TclError:
                                pass
            except tk.TclError:
                pass

        self.root.bind_all("<MouseWheel>", on_global_mousewheel)
        self.root.bind_all("<Button-4>", on_global_mousewheel)
        self.root.bind_all("<Button-5>", on_global_mousewheel)

    def _on_mousewheel(self, event, canvas=None):
        if canvas is None:
            return

        try:
            if not canvas.winfo_exists():
                return

            current_pos = canvas.yview()

            if event.num == 4 or event.num == 5:
                if event.num == 4:
                    if current_pos[0] > 0:
                        canvas.yview_scroll(-1, "units")
                else:
                    if current_pos[1] < 1:
                        canvas.yview_scroll(1, "units")
            else:
                delta = int(-1*(event.delta/120))
                if delta < 0:
                    if current_pos[0] > 0:
                        canvas.yview_scroll(delta, "units")
                else:
                    if current_pos[1] < 1:
                        canvas.yview_scroll(delta, "units")

        except tk.TclError:
            pass
        except Exception as e:
            print(f"滚动错误: {e}")

    def _update_time(self):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.time_label.config(text=f"当前时间：{current_time}")
        self.root.after(1000, self._update_time)

    def _start_auto_refresh(self):
        if self.auto_refresh_after_id:
            self.root.after_cancel(self.auto_refresh_after_id)
            self.auto_refresh_after_id = None

        interval_ms = random.randint(60, 180) * 1000
        print(f"下次自动刷新将在 {interval_ms // 1000} 秒后执行")

        def do_refresh():
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 自动刷新数据...")
            self._refresh_data(auto=True)

        self.auto_refresh_after_id = self.root.after(interval_ms, do_refresh)

    def _stop_auto_refresh(self):
        if self.auto_refresh_after_id:
            self.root.after_cancel(self.auto_refresh_after_id)
            self.auto_refresh_after_id = None

    def _refresh_data(self, date_str: Optional[str] = None, auto: bool = False):
        if not date_str:
            date_str = self.match_list_panel.get_date()

        self.match_list_panel.stats_label.config(text="加载中...")

        def fetch_thread():
            try:
                self.matches = self.scraper.get_all_matches(date_str)
                self.root.after(0, self._on_data_loaded)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"获取数据失败：{e}"))
                self.root.after(0, self._on_data_loaded)

        thread = threading.Thread(target=fetch_thread, daemon=True)
        thread.start()

        if not auto:
            self._start_auto_refresh()

    def _on_data_loaded(self):
        if not self.matches:
            messagebox.showerror("错误", "获取数据失败，请检查网络连接")
            self.match_list_panel.stats_label.config(text="0/0")
            return

        self.match_list_panel.update_matches(self.matches)
        if self.matches:
            self._on_match_selected(self.matches[0])
        self._start_auto_refresh()

    def _on_match_selected(self, match):
        if hasattr(self, '_current_load_event') and self._current_load_event:
            self._current_load_event.set()

        cancel_event = threading.Event()
        self._current_load_event = cancel_event

        self._current_detail_match_id = match.get('match_unique_id', '')

        self.match_info_panel.update_data(match, None)
        self.standings_panel.update_data(match, None)
        self.odds_trend_panel.update_data(match, None)
        self.jc_index_panel.update_data(match, None)

        def load_detail():
            analysis_data = self.scraper.fetch_match_analysis(match, cancel_event=cancel_event)
            if cancel_event.is_set():
                return
            if analysis_data:
                for key in ['venue', 'weather', 'temperature', 'league_round', 'match_date', 'match_day', 'home_logo', 'away_logo', 'standings_data']:
                    if key in analysis_data and key not in match:
                        match[key] = analysis_data[key]
            self._current_analysis_data = analysis_data
            try:
                self.root.after(0, lambda: self._safe_update_panels(match, analysis_data))
            except tk.TclError:
                pass

        thread = threading.Thread(target=load_detail, daemon=True)
        thread.start()

    def _safe_update_panels(self, match, analysis_data):
        try:
            if not self.root.winfo_exists():
                return
            self.match_info_panel.update_data(match, analysis_data)
            self.standings_panel.update_data(match, analysis_data)
            self.odds_trend_panel.update_data(match, analysis_data)
            self.jc_index_panel.update_data(match, analysis_data)
        except tk.TclError as e:
            print(f"显示详情时出错(窗口可能已关闭): {e}")
        except Exception as e:
            print(f"显示详情时出错: {e}")


def main():
    root = tk.Tk()
    app = MatchDisplayApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
