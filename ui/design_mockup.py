import tkinter as tk
from tkinter import ttk


COLORS = {
    "navy": "#10263d",
    "navy_light": "#183b5b",
    "ink": "#17212b",
    "muted": "#718096",
    "line": "#e5eaf0",
    "paper": "#f5f7fa",
    "white": "#ffffff",
    "green": "#16845b",
    "green_soft": "#e6f5ee",
    "red": "#c84b4b",
    "red_soft": "#fcebea",
    "gold": "#d69b2d",
    "gold_soft": "#fff5dc",
    "blue_soft": "#eaf2fb",
}


class DesignMockup(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Banking Life Sim | Product Direction")
        self.geometry("1240x780")
        self.minsize(1040, 680)
        self.configure(bg=COLORS["paper"])
        self._configure_styles()
        self._build_shell()

    def _configure_styles(self):
        styles = ttk.Style(self)
        styles.theme_use("clam")
        styles.configure("Body.TLabel", background=COLORS["paper"], foreground=COLORS["ink"], font=("Segoe UI", 10))
        styles.configure("Muted.TLabel", background=COLORS["paper"], foreground=COLORS["muted"], font=("Segoe UI", 9))
        styles.configure("Title.TLabel", background=COLORS["paper"], foreground=COLORS["ink"], font=("Segoe UI", 24, "bold"))
        styles.configure("Section.TLabel", background=COLORS["white"], foreground=COLORS["ink"], font=("Segoe UI", 13, "bold"))
        styles.configure("CardValue.TLabel", background=COLORS["white"], foreground=COLORS["ink"], font=("Segoe UI", 19, "bold"))
        styles.configure("Treeview", background=COLORS["white"], fieldbackground=COLORS["white"], foreground=COLORS["ink"], rowheight=36, font=("Segoe UI", 10))
        styles.configure("Treeview.Heading", background=COLORS["white"], foreground=COLORS["muted"], font=("Segoe UI", 9, "bold"), relief="flat")
        styles.map("Treeview", background=[("selected", COLORS["blue_soft"])], foreground=[("selected", COLORS["ink"])])

    def _label(self, parent, text, style="Body.TLabel", **kwargs):
        return ttk.Label(parent, text=text, style=style, **kwargs)

    def _card(self, parent, **kwargs):
        return tk.Frame(parent, bg=COLORS["white"], highlightbackground=COLORS["line"], highlightthickness=1, **kwargs)

    def _build_shell(self):
        nav = tk.Frame(self, bg=COLORS["navy"], width=226)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)

        brand = tk.Frame(nav, bg=COLORS["navy"])
        brand.pack(fill="x", padx=22, pady=(28, 42))
        tk.Label(brand, text="BANKING", bg=COLORS["navy"], fg="#8fb5d3", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(brand, text="LIFE SIM", bg=COLORS["navy"], fg=COLORS["white"], font=("Segoe UI", 20, "bold")).pack(anchor="w")

        tk.Label(nav, text="WORKSPACE", bg=COLORS["navy"], fg="#7595ae", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=24, pady=(0, 10))
        self._nav_button(nav, "▦   Overview", True)
        self._nav_button(nav, "▤   Company")
        self._nav_button(nav, "◈   Stock Market")
        self._nav_button(nav, "◫   Portfolio")
        self._nav_button(nav, "⌁   Activity")

        tk.Frame(nav, bg="#2c4b64", height=1).pack(fill="x", padx=24, pady=28)
        tk.Label(nav, text="CURRENT YEAR", bg=COLORS["navy"], fg="#7595ae", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=24)
        tk.Label(nav, text="2000", bg=COLORS["navy"], fg=COLORS["white"], font=("Segoe UI", 26, "bold")).pack(anchor="w", padx=24, pady=(2, 0))
        tk.Label(nav, text="Year 1 of your story", bg=COLORS["navy"], fg="#9bb1c1", font=("Segoe UI", 9)).pack(anchor="w", padx=24)

        tk.Frame(nav, bg=COLORS["navy"]).pack(fill="both", expand=True)
        tk.Label(nav, text="◉  Alex Morgan", bg=COLORS["navy"], fg=COLORS["white"], font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=24, pady=(0, 4))
        tk.Label(nav, text="Personal account", bg=COLORS["navy"], fg="#9bb1c1", font=("Segoe UI", 9)).pack(anchor="w", padx=24, pady=(0, 24))

        main = tk.Frame(self, bg=COLORS["paper"])
        main.pack(side="left", fill="both", expand=True)
        self._build_header(main)
        self._build_content(main)

    def _nav_button(self, parent, text, active=False):
        bg = COLORS["navy_light"] if active else COLORS["navy"]
        fg = COLORS["white"] if active else "#b1c3d0"
        tk.Label(parent, text=text, bg=bg, fg=fg, anchor="w", padx=24, pady=11, font=("Segoe UI", 10, "bold" if active else "normal")).pack(fill="x", padx=(10 if active else 0, 0), pady=1)

    def _build_header(self, parent):
        header = tk.Frame(parent, bg=COLORS["paper"], height=104)
        header.pack(fill="x", padx=34, pady=(26, 0))
        header.pack_propagate(False)
        left = tk.Frame(header, bg=COLORS["paper"])
        left.pack(side="left", fill="y")
        self._label(left, "Good morning, Alex", "Muted.TLabel").pack(anchor="w")
        self._label(left, "Your financial picture", "Title.TLabel").pack(anchor="w", pady=(3, 0))
        right = tk.Frame(header, bg=COLORS["paper"])
        right.pack(side="right", fill="y")
        tk.Button(right, text="?", bg=COLORS["white"], fg=COLORS["muted"], relief="flat", width=3, font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0, 10), pady=18)
        tk.Button(right, text="Advance Year  →", bg=COLORS["green"], fg=COLORS["white"], activebackground="#116b4a", activeforeground=COLORS["white"], relief="flat", padx=18, pady=11, font=("Segoe UI", 10, "bold")).pack(side="left", pady=18)

    def _build_content(self, parent):
        canvas = tk.Canvas(parent, bg=COLORS["paper"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLORS["paper"])
        scroll_frame.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(34, 0), pady=(0, 28))
        scrollbar.pack(side="right", fill="y", padx=(0, 22), pady=(0, 28))

        metrics = tk.Frame(scroll_frame, bg=COLORS["paper"])
        metrics.pack(fill="x", pady=(0, 18))
        self._metric(metrics, "Personal capital", "$12,480", "+$1,200 this year", COLORS["gold"], 0)
        self._metric(metrics, "Company capital", "$186,240", "+14.8% this year", COLORS["green"], 1)
        self._metric(metrics, "Portfolio value", "$42,680", "+6.2% this year", COLORS["navy_light"], 2)
        self._metric(metrics, "Total net worth", "$241,400", "+11.4% this year", COLORS["red"], 3)

        grid = tk.Frame(scroll_frame, bg=COLORS["paper"])
        grid.pack(fill="both", expand=True)
        left = tk.Frame(grid, bg=COLORS["paper"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 9))
        right = tk.Frame(grid, bg=COLORS["paper"], width=315)
        right.pack(side="right", fill="y", padx=(9, 0))
        right.pack_propagate(False)

        self._company_card(left)
        self._watchlist_card(left)
        self._next_move_card(right)
        self._activity_card(right)

    def _metric(self, parent, label, value, change, accent, column):
        card = self._card(parent, width=210, height=106)
        card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 6, 6 if column < 3 else 0))
        parent.grid_columnconfigure(column, weight=1)
        tk.Frame(card, bg=accent, width=4).pack(side="left", fill="y")
        body = tk.Frame(card, bg=COLORS["white"])
        body.pack(side="left", fill="both", expand=True, padx=15, pady=13)
        self._label(body, label, "Muted.TLabel").pack(anchor="w")
        self._label(body, value, "CardValue.TLabel").pack(anchor="w", pady=(4, 0))
        color = COLORS["green"] if change.startswith("+") else COLORS["red"]
        tk.Label(body, text=change, bg=COLORS["white"], fg=color, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 0))

    def _company_card(self, parent):
        card = self._card(parent)
        card.pack(fill="x", pady=(0, 18))
        top = tk.Frame(card, bg=COLORS["white"])
        top.pack(fill="x", padx=22, pady=(19, 15))
        self._label(top, "Company overview", "Section.TLabel").pack(side="left")
        tk.Label(top, text="OPERATING WELL", bg=COLORS["green_soft"], fg=COLORS["green"], font=("Segoe UI", 8, "bold"), padx=9, pady=4).pack(side="right")
        tk.Label(card, text="Northstar Foods", bg=COLORS["white"], fg=COLORS["ink"], font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=22)
        tk.Label(card, text="Food & Beverage  ·  2 factories  ·  100,000 units capacity", bg=COLORS["white"], fg=COLORS["muted"], font=("Segoe UI", 10)).pack(anchor="w", padx=22, pady=(3, 17))
        stats = tk.Frame(card, bg=COLORS["white"])
        stats.pack(fill="x", padx=22, pady=(0, 20))
        self._inline_stat(stats, "Annual revenue", "$384,600", 0)
        self._inline_stat(stats, "Net income", "$71,940", 1)
        self._inline_stat(stats, "Inventory", "18,240 units", 2)
        self._inline_stat(stats, "Factory capacity", "72% used", 3)

    def _inline_stat(self, parent, label, value, column):
        block = tk.Frame(parent, bg=COLORS["white"])
        block.grid(row=0, column=column, sticky="w", padx=(0, 30))
        self._label(block, label, "Muted.TLabel").pack(anchor="w")
        tk.Label(block, text=value, bg=COLORS["white"], fg=COLORS["ink"], font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(4, 0))

    def _watchlist_card(self, parent):
        card = self._card(parent)
        card.pack(fill="both", expand=True)
        top = tk.Frame(card, bg=COLORS["white"])
        top.pack(fill="x", padx=22, pady=(19, 12))
        self._label(top, "Market watchlist", "Section.TLabel").pack(side="left")
        self._label(top, "View market  →", "Muted.TLabel").pack(side="right")
        table = ttk.Treeview(card, columns=("ticker", "name", "price", "change", "growth", "risk"), show="headings", height=5)
        headings = (("ticker", "TICKER", 75), ("name", "COMPANY", 150), ("price", "PRICE", 90), ("change", "1Y CHANGE", 90), ("growth", "GROWTH", 75), ("risk", "RISK", 70))
        for key, title, width in headings:
            table.heading(key, text=title)
            table.column(key, width=width, anchor="w")
        rows = [("NOVA", "Nova Systems", "$42.18", "+8.4%", "12.0%", "Medium"), ("PRMB", "Prime Banking", "$88.04", "+2.1%", "6.0%", "Low"), ("VOLT", "Volt Energy", "$68.72", "-4.8%", "5.0%", "High"), ("BION", "BioNova", "$44.30", "+15.6%", "9.0%", "High"), ("SHOP", "ShopSmart", "$29.16", "+1.2%", "4.0%", "Low")]
        for row in rows:
            table.insert("", "end", values=row)
        table.pack(fill="x", padx=14, pady=(0, 18))

    def _next_move_card(self, parent):
        card = self._card(parent)
        card.pack(fill="x", pady=(0, 18))
        tk.Label(card, text="YOUR NEXT MOVE", bg=COLORS["white"], fg=COLORS["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=20, pady=(19, 9))
        tk.Label(card, text="Set your annual plan", bg=COLORS["white"], fg=COLORS["ink"], font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=20)
        tk.Label(card, text="Your company is ready for a new production decision.", bg=COLORS["white"], fg=COLORS["muted"], wraplength=265, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(7, 17))
        tk.Button(card, text="Open company plan  →", bg=COLORS["navy_light"], fg=COLORS["white"], activebackground=COLORS["navy"], activeforeground=COLORS["white"], relief="flat", anchor="w", padx=14, pady=10, font=("Segoe UI", 10, "bold")).pack(fill="x", padx=20, pady=(0, 20))

    def _activity_card(self, parent):
        card = self._card(parent)
        card.pack(fill="both", expand=True)
        tk.Label(card, text="RECENT ACTIVITY", bg=COLORS["white"], fg=COLORS["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=20, pady=(19, 14))
        activities = [("Company grew", "+$71,940", COLORS["green"]), ("Bought 3 NOVA", "-$126.54", COLORS["navy_light"]), ("Year advanced", "2000 → 2001", COLORS["gold"])]
        for title, detail, color in activities:
            row = tk.Frame(card, bg=COLORS["white"])
            row.pack(fill="x", padx=20, pady=(0, 15))
            tk.Frame(row, bg=color, width=7, height=30).pack(side="left", padx=(0, 10))
            body = tk.Frame(row, bg=COLORS["white"])
            body.pack(side="left", fill="x", expand=True)
            tk.Label(body, text=title, bg=COLORS["white"], fg=COLORS["ink"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(body, text=detail, bg=COLORS["white"], fg=COLORS["muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))


if __name__ == "__main__":
    DesignMockup().mainloop()
