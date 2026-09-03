import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from company_class import Company
from config import SAVE_FILE, SECTOR_STARTUP_COSTS
from create_product import ProductCreator
from logger import logger
from persistence import load_game, save_game
from player_class import Player
from stock_market import StockMarket

C = {"navy": "#10263d", "blue": "#183b5b", "ink": "#17212b", "muted": "#718096",
     "line": "#e5eaf0", "paper": "#f5f7fa", "white": "#ffffff", "green": "#16845b",
    "red": "#c84b4b", "gold": "#d69b2d", "blue_soft": "#eaf2fb"}


class BankingLifeSim(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Banking Life Sim")
        self.geometry("1240x780")
        self.minsize(1040, 680)
        self.configure(bg=C["paper"])
        self.player = Player()
        self.market = StockMarket()
        self.page = None
        self._styles()
        self._shell()
        self.show_dashboard()

    def _styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Body.TLabel", background=C["paper"], foreground=C["ink"], font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=C["paper"], foreground=C["muted"], font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=C["paper"], foreground=C["ink"], font=("Segoe UI", 24, "bold"))
        style.configure("Section.TLabel", background=C["white"], foreground=C["ink"], font=("Segoe UI", 13, "bold"))
        style.configure("Treeview", background=C["white"], fieldbackground=C["white"], foreground=C["ink"], rowheight=34, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=C["white"], foreground=C["muted"], font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#eaf2fb")], foreground=[("selected", C["ink"])])

    def _shell(self):
        nav = tk.Frame(self, bg=C["navy"], width=226)
        nav.pack(side="left", fill="y"); nav.pack_propagate(False)
        tk.Label(nav, text="BANKING", bg=C["navy"], fg="#8fb5d3", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=24, pady=(28, 0))
        tk.Label(nav, text="LIFE SIM", bg=C["navy"], fg=C["white"], font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=24, pady=(0, 42))
        tk.Label(nav, text="WORKSPACE", bg=C["navy"], fg="#7595ae", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=24, pady=(0, 10))
        self._nav(nav, "▦   Overview", self.show_dashboard, True)
        self._nav(nav, "▤   Company", self.show_company)
        self._nav(nav, "◈   Stock Market", self.show_stocks)
        self._nav(nav, "◫   Portfolio", self.show_portfolio)
        tk.Frame(nav, bg="#2c4b64", height=1).pack(fill="x", padx=24, pady=28)
        tk.Label(nav, text="CURRENT YEAR", bg=C["navy"], fg="#7595ae", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=24)
        self.year_label = tk.Label(nav, text="", bg=C["navy"], fg=C["white"], font=("Segoe UI", 26, "bold"))
        self.year_label.pack(anchor="w", padx=24, pady=(2, 0))
        tk.Label(nav, text="Annual strategy cycle", bg=C["navy"], fg="#9bb1c1", font=("Segoe UI", 9)).pack(anchor="w", padx=24)
        tk.Frame(nav, bg=C["navy"]).pack(fill="both", expand=True)
        tk.Label(nav, text="◉  Player account", bg=C["navy"], fg=C["white"], font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=24, pady=(0, 24))

        self.main = tk.Frame(self, bg=C["paper"])
        self.main.pack(side="left", fill="both", expand=True)
        header = tk.Frame(self.main, bg=C["paper"], height=105)
        header.pack(fill="x", padx=34, pady=(24, 0)); header.pack_propagate(False)
        title_box = tk.Frame(header, bg=C["paper"]); title_box.pack(side="left", fill="y")
        self.eyebrow = tk.Label(title_box, text="WELCOME BACK", bg=C["paper"], fg=C["muted"], font=("Segoe UI", 9, "bold")); self.eyebrow.pack(anchor="w")
        self.page_title = tk.Label(title_box, text="Your financial picture", bg=C["paper"], fg=C["ink"], font=("Segoe UI", 24, "bold")); self.page_title.pack(anchor="w", pady=(3, 0))
        self.advance_button = tk.Button(header, text="Advance Year  →", command=self.advance_year, bg=C["green"], fg=C["white"], activebackground="#116b4a", activeforeground=C["white"], relief="flat", padx=18, pady=11, font=("Segoe UI", 10, "bold")); self.advance_button.pack(side="right", pady=18)
        tk.Button(header, text="Save", command=self.save_current_game, bg=C["white"], fg=C["blue"], relief="flat", padx=12, pady=10, font=("Segoe UI", 9, "bold")).pack(side="right", padx=(0, 8), pady=18)
        tk.Button(header, text="Load", command=self.load_saved_game, bg=C["white"], fg=C["blue"], relief="flat", padx=12, pady=10, font=("Segoe UI", 9, "bold")).pack(side="right", padx=(0, 8), pady=18)
        self.content = tk.Frame(self.main, bg=C["paper"]); self.content.pack(fill="both", expand=True, padx=34, pady=(0, 28))

    def _nav(self, parent, text, command, active=False):
        tk.Button(parent, text=text, command=command, bg=C["blue"] if active else C["navy"], fg=C["white"] if active else "#b1c3d0", activebackground=C["blue"], activeforeground=C["white"], relief="flat", anchor="w", padx=24, pady=11, font=("Segoe UI", 10, "bold" if active else "normal")).pack(fill="x", padx=(10 if active else 0, 0), pady=1)

    def _clear(self, heading):
        for child in self.content.winfo_children(): child.destroy()
        self.eyebrow.config(text="BANKING LIFE SIM")
        self.page_title.config(text=heading)
        self.year_label.config(text=str(self.player.year))

    def _card(self, parent):
        return tk.Frame(parent, bg=C["white"], highlightbackground=C["line"], highlightthickness=1)

    def _focus_for_dialog(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _metric(self, parent, label, value, change, color, column):
        card = self._card(parent); card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 6, 6 if column < 3 else 0))
        parent.grid_columnconfigure(column, weight=1)
        tk.Frame(card, bg=color, width=4).pack(side="left", fill="y")
        body = tk.Frame(card, bg=C["white"]); body.pack(fill="both", expand=True, padx=14, pady=12)
        tk.Label(body, text=label, bg=C["white"], fg=C["muted"], font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(body, text=value, bg=C["white"], fg=C["ink"], font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(4, 0))
        tk.Label(body, text=change, bg=C["white"], fg=C["green"] if change.startswith("+") else C["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w")

    def show_dashboard(self):
        self._clear("Your financial picture")
        metrics = tk.Frame(self.content, bg=C["paper"]); metrics.pack(fill="x", pady=(0, 18))
        company = self.player.company
        company_capital = company.cash if company else 0
        company_value = company.value() if company else 0
        portfolio = self.market.portfolio_value(self.player)
        net_worth = self.market.net_worth(self.player)
        self._metric(metrics, "Bank balance", f"${self.player.bank:,.0f}", "Liquid funds", C["gold"], 0)
        self._metric(metrics, "Company capital", f"${company_capital:,.0f}", "Operating balance", C["green"], 1)
        self._metric(metrics, "Company value", f"${company_value:,.0f}", "Assets minus debt", C["blue"], 2)
        self._metric(metrics, "Portfolio value", f"${portfolio:,.0f}", "Current holdings", C["navy"], 3)
        self._metric(metrics, "Net worth", f"${net_worth:,.0f}", "All assets", C["red"], 4)
        row = tk.Frame(self.content, bg=C["paper"]); row.pack(fill="both", expand=True)
        left = tk.Frame(row, bg=C["paper"]); left.pack(side="left", fill="both", expand=True, padx=(0, 9))
        right = tk.Frame(row, bg=C["paper"], width=310); right.pack(side="right", fill="y", padx=(9, 0)); right.pack_propagate(False)
        self._company_overview(left, company)
        self._watchlist(left)
        self._next_move(right, company)
        self._activity(right)

    def _company_overview(self, parent, company):
        card = self._card(parent); card.pack(fill="x", pady=(0, 18))
        top = tk.Frame(card, bg=C["white"]); top.pack(fill="x", padx=22, pady=(18, 12))
        tk.Label(top, text="COMPANY OVERVIEW", bg=C["white"], fg=C["muted"], font=("Segoe UI", 9, "bold")).pack(side="left")
        status = "NO COMPANY" if not company else ("BANKRUPT" if company.bankrupt else "OPERATING")
        color = C["red"] if status == "BANKRUPT" else C["green"]
        tk.Label(top, text=status, bg="#fcebea" if status == "BANKRUPT" else "#e6f5ee", fg=color, font=("Segoe UI", 8, "bold"), padx=8, pady=4).pack(side="right")
        tk.Label(card, text=company.name if company else "Start your first company", bg=C["white"], fg=C["ink"], font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=22)
        subtitle = f"{company.sector}  ·  {company.factory_count} factories  ·  {company.production_capacity:,} units capacity" if company else "Build a company, launch a product, and make your first annual decision."
        tk.Label(card, text=subtitle, bg=C["white"], fg=C["muted"], font=("Segoe UI", 10)).pack(anchor="w", padx=22, pady=(3, 17))
        stats = tk.Frame(card, bg=C["white"]); stats.pack(fill="x", padx=22, pady=(0, 20))
        values = [
            ("Annual revenue", company.revenue if company else 0),
            ("Net income", company.net_income if company else 0),
            ("Inventory", company.total_inventory if company else 0),
            ("Debt", company.debt if company else 0),
            ("Company value", company.value() if company else 0),
        ]
        for i, (label, value) in enumerate(values):
            block = tk.Frame(stats, bg=C["white"]); block.grid(row=0, column=i, sticky="w", padx=(0, 20))
            tk.Label(block, text=label, bg=C["white"], fg=C["muted"], font=("Segoe UI", 9)).pack(anchor="w")
            shown = f"${value:,.0f}" if i in (0, 1, 3, 4) else f"{value:,}"
            tk.Label(block, text=shown, bg=C["white"], fg=C["ink"], font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(4, 0))

    def _watchlist(self, parent):
        card = self._card(parent); card.pack(fill="both", expand=True)
        tk.Label(card, text="MARKET WATCHLIST", bg=C["white"], fg=C["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=22, pady=(18, 12))
        table = ttk.Treeview(card, columns=("ticker", "name", "price", "growth", "risk"), show="headings", height=7)
        for key, heading, width in [("ticker", "TICKER", 70), ("name", "COMPANY", 180), ("price", "PRICE", 90), ("growth", "GROWTH", 80), ("risk", "RISK", 80)]: table.heading(key, text=heading); table.column(key, width=width, anchor="w")
        for stock in list(self.market.stocks.values())[:7]:
            debt_ratio = stock.debt / max(stock.revenue, 1); risk = "High" if debt_ratio > .7 else "Medium" if debt_ratio > .35 else "Low"
            table.insert("", "end", values=(stock.ticker, stock.name, f"${stock.price:,.2f}", f"{stock.growth_rate:.1%}", risk))
        table.pack(fill="x", padx=14, pady=(0, 18))

    def _next_move(self, parent, company):
        card = self._card(parent); card.pack(fill="x", pady=(0, 18))
        tk.Label(card, text="YOUR NEXT MOVE", bg=C["white"], fg=C["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=20, pady=(19, 9))
        message = "Create your company" if not company else "Set your annual plan"
        detail = "Choose a sector and begin building your financial story." if not company else "Review your products, prices, and quota before the next year."
        tk.Label(card, text=message, bg=C["white"], fg=C["ink"], font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=20)
        tk.Label(card, text=detail, bg=C["white"], fg=C["muted"], wraplength=260, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(7, 17))
        tk.Button(card, text="Open company  →", command=self.show_company, bg=C["blue"], fg=C["white"], relief="flat", padx=14, pady=10, font=("Segoe UI", 10, "bold")).pack(fill="x", padx=20, pady=(0, 20))

    def _activity(self, parent):
        card = self._card(parent); card.pack(fill="both", expand=True)
        tk.Label(card, text="RECENT ACTIVITY", bg=C["white"], fg=C["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=20, pady=(19, 14))
        for text in ["Welcome to Banking Life Sim", "Annual market cycle ready", "Choose your first move"]:
            tk.Label(card, text="•  " + text, bg=C["white"], fg=C["ink"], font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(0, 14))

    def show_company(self):
        self._clear("Company management")
        if not self.player.company:
            self._company_setup(); return
        company = self.player.company
        top = tk.Frame(self.content, bg=C["paper"]); top.pack(fill="x", pady=(0, 16))
        tk.Label(top, text=f"{company.name}  ·  {company.sector}", bg=C["paper"], fg=C["ink"], font=("Segoe UI", 16, "bold")).pack(side="left")
        tk.Button(top, text="Sell company", command=self.open_sell_company, bg="#fcebea", fg=C["red"], relief="flat", padx=12, pady=8, font=("Segoe UI", 9, "bold")).pack(side="right", padx=(8, 0))
        tk.Button(top, text="Buy factory", command=self.buy_factory, bg=C["blue"], fg=C["white"], relief="flat", padx=12, pady=8, font=("Segoe UI", 9, "bold")).pack(side="right")
        tk.Button(top, text="Manage employees", command=self.manage_employees, bg=C["white"], fg=C["blue"], relief="flat", padx=12, pady=8, font=("Segoe UI", 9, "bold")).pack(side="right", padx=(0, 8))
        tk.Label(self.content, text=f"Capital ${company.cash:,.0f}   |   Capacity {company.production_capacity:,} units   |   {company.factory_count} factories", bg=C["paper"], fg=C["muted"], font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 12))
        tk.Label(self.content, text=f"Reputation {company.reputation:.0f}/100   |   Employees {company.employee_count}/{company.required_employee_count} needed   |   Workforce efficiency {min(company.staffing_ratio, 1.10):.0%}", bg=C["paper"], fg=C["muted"], font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 12))
        tk.Label(self.content, text=f"Last annual costs: marketing ${company.marketing_expenses:,.0f}   |   employees ${company.employee_expenses:,.0f}   |   operating costs ${company.operating_expenses:,.0f}   |   taxes ${company.taxes:,.0f}", bg=C["paper"], fg=C["muted"], font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 12))
        card = self._card(self.content); card.pack(fill="both", expand=True)
        tk.Label(card, text="ANNUAL PRODUCTION PLAN", bg=C["white"], fg=C["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=22, pady=(18, 10))
        if not company.products:
            tk.Label(card, text="No products yet. Research a product to begin.", bg=C["white"], fg=C["ink"], font=("Segoe UI", 12)).pack(anchor="w", padx=22, pady=20)
        for product in company.products:
            self._product_row(card, product)
        actions = tk.Frame(card, bg=C["white"]); actions.pack(fill="x", padx=22, pady=18)
        tk.Button(actions, text="Research / launch product", command=self.research_product, bg=C["blue"], fg=C["white"], relief="flat", padx=12, pady=9, font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Button(actions, text="Invest capital", command=self.invest_in_company, bg=C["white"], fg=C["blue"], relief="flat", padx=12, pady=9, font=("Segoe UI", 9, "bold")).pack(side="left", padx=8)

    def _company_setup(self):
        card = self._card(self.content); card.pack(fill="both", expand=True)
        tk.Label(card, text="Start your company", bg=C["white"], fg=C["ink"], font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=28, pady=(24, 4))
        tk.Label(card, text="Choose your name and industry. Every sector has a different market opportunity.", bg=C["white"], fg=C["muted"], font=("Segoe UI", 10)).pack(anchor="w", padx=28, pady=(0, 16))

        name_row = tk.Frame(card, bg=C["white"]); name_row.pack(fill="x", padx=28, pady=(0, 18))
        tk.Label(name_row, text="Company name", bg=C["white"], fg=C["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w")
        name_entry = tk.Entry(name_row, bg="#f5f7fa", fg=C["ink"], relief="flat", font=("Segoe UI", 11))
        name_entry.pack(fill="x", pady=(5, 0), ipady=7)

        sectors = sorted(set(ProductCreator.load_catalog()) | set(SECTOR_STARTUP_COSTS))
        catalog = ProductCreator.load_catalog()
        selected_sector = tk.StringVar(value=sectors[0] if sectors else "")
        tk.Label(card, text="SELECT AN INDUSTRY", bg=C["white"], fg=C["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=28, pady=(0, 8))
        sector_list = tk.Frame(card, bg=C["white"]); sector_list.pack(fill="both", expand=True, padx=28)

        def market_stats(sector):
            products = catalog.get(sector, [])
            if not products:
                return "No product data", "No product data"
            demand = sum(product.base_demand for product in products) / len(products)
            competition = sum(product.competition for product in products) / len(products)
            return f"{demand:.1f}/10", f"{competition:.1f}/10"

        sector_buttons = {}
        def select_sector(sector):
            selected_sector.set(sector)
            for name, button in sector_buttons.items():
                button.configure(bg="#eaf2fb" if name == sector else C["white"])

        for sector in sectors:
            demand, competition = market_stats(sector)
            row = tk.Frame(sector_list, bg=C["white"], highlightbackground=C["line"], highlightthickness=1)
            row.pack(fill="x", pady=3)
            button = tk.Button(row, text=sector, command=lambda value=sector: select_sector(value), bg=C["blue_soft"] if sector == selected_sector.get() else C["white"], fg=C["ink"], activebackground=C["blue_soft"], relief="flat", anchor="w", padx=12, pady=9, font=("Segoe UI", 10, "bold"))
            button.pack(side="left", fill="x", expand=True)
            sector_buttons[sector] = button
            tk.Label(row, text=f"Demand {demand}   Competition {competition}   ${SECTOR_STARTUP_COSTS.get(sector, 50000):,.0f}", bg=C["white"], fg=C["muted"], font=("Segoe UI", 9)).pack(side="right", padx=14)

        def submit_company():
            name = name_entry.get().strip()
            sector = selected_sector.get()
            if not name:
                messagebox.showerror("Company name required", "Enter a name for your company.", parent=self)
                return
            self._create_company(name, sector)

        tk.Button(card, text="Create company", command=submit_company, bg=C["green"], fg=C["white"], relief="flat", padx=16, pady=11, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=28, pady=18)

    def _product_row(self, parent, product):
        row = tk.Frame(parent, bg="#fbfcfd", highlightbackground=C["line"], highlightthickness=1); row.pack(fill="x", padx=22, pady=5)
        tk.Label(row, text=product.name, bg="#fbfcfd", fg=C["ink"], font=("Segoe UI", 11, "bold"), width=18, anchor="w").pack(side="left", padx=12, pady=13)
        tk.Label(row, text=f"Price ${product.sale_price:,.2f}\nCost ${product.manufacturing_cost:,.2f}", bg="#fbfcfd", fg=C["muted"], justify="left", anchor="w", font=("Segoe UI", 9)).pack(side="left", padx=10)
        tk.Label(row, text=f"Supply: {product.annual_production_quota + product.inventory:,}\nDemand: {product.base_demand}/10  |  Competition: {product.competition}/10\nLoyalty: {product.customer_loyalty:.0f}/100", bg="#fbfcfd", fg=C["muted"], justify="left", anchor="w", font=("Segoe UI", 9)).pack(side="left", padx=20)
        tk.Button(row, text="Edit plan", command=lambda p=product: self.edit_product(p), bg=C["white"], fg=C["blue"], relief="flat", font=("Segoe UI", 9, "bold")).pack(side="right", padx=12)
        tk.Button(row, text="Remove", command=lambda p=product: self.remove_product(p), bg="#fbfcfd", fg=C["red"], relief="flat", font=("Segoe UI", 9, "bold")).pack(side="right")

    def create_company(self):
        self._focus_for_dialog()
        name = simpledialog.askstring("Create company", "Company name:", parent=self)
        if not name or not name.strip(): return
        sectors = sorted(set(ProductCreator.load_catalog()) | set(SECTOR_STARTUP_COSTS))
        choice = simpledialog.askstring("Choose sector", "Enter a sector:\n\n" + "\n".join(sectors), parent=self)
        if not choice or choice.strip().title() not in sectors: messagebox.showerror("Invalid sector", "Choose one of the listed sectors.", parent=self); return
        sector = choice.strip().title(); cost = SECTOR_STARTUP_COSTS.get(sector, 50000)
        if self.player.bank < cost: messagebox.showerror("Insufficient funds", f"You need ${cost:,.0f} in the bank.", parent=self); return
        self._create_company(name.strip(), sector)

    def _create_company(self, name, sector):
        cost = SECTOR_STARTUP_COSTS.get(sector, 50000)
        if self.player.bank < cost:
            messagebox.showerror("Insufficient funds", f"You need ${cost:,.0f} in the bank.", parent=self)
            return
        self.player.company = Company(name, sector)
        self.player.company.cash = cost
        self.player.company.capital_invested = cost
        self.player.bank -= cost
        logger.info("Created company %s in %s", name, sector)
        self.show_company()

    def research_product(self):
        company = self.player.company; options = ProductCreator.load_sector_products(company.sector)
        self._focus_for_dialog()
        if not options: messagebox.showinfo("No products", "No products are available for this sector.", parent=self); return
        text = "\n".join(
            f"{i + 1}. {p.name}  |  "
            f"{'demand ' + str(p.base_demand) + '/10  | competition ' + str(p.competition) + '/10' if p.researched else 'market data locked'}  | "
            f"research ${p.research_cost:,.0f}"
            for i, p in enumerate(options)
        )
        raw = simpledialog.askstring("Research product", text + "\n\nEnter a number:", parent=self)
        try: product = options[int(raw) - 1]
        except (TypeError, ValueError, IndexError): return
        result = company.research_and_launch(product)
        if result != f"{product.name} was added.":
            messagebox.showerror("Unable to launch product", result, parent=self)
            return
        messagebox.showinfo(
            "Market research complete",
            f"{product.name}\n\n"
            f"Demand: {product.base_demand}/10\n"
            f"Competition: {product.competition}/10\n"
            f"Manufacturing cost: ${product.manufacturing_cost:,.2f}\n\n"
            "The product has been added to your lineup.",
            parent=self,
        )
        self.show_company()

    def edit_product(self, product):
        self._focus_for_dialog()
        dialog = tk.Toplevel(self)
        dialog.title("Edit annual plan")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=C["white"])
        dialog.resizable(False, False)
        tk.Label(dialog, text=product.name, bg=C["white"], fg=C["ink"], font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=24, pady=(22, 4))
        tk.Label(dialog, text=f"Annual production quota (0 to {self.player.company.production_capacity:,})", bg=C["white"], fg=C["muted"], font=("Segoe UI", 9)).pack(anchor="w", padx=24)
        tk.Label(
            dialog,
            text=(
                f"Last year: sold {product.units_sold:,} units  |  "
                f"revenue ${product.annual_revenue:,.0f}  |  "
                f"profit ${product.annual_profit:,.0f}\n"
                f"Inventory: {product.inventory:,} units  |  "
                f"Manufacturing cost: ${product.manufacturing_cost:,.2f}  |  "
                f"Marketing: ${product.marketing_budget:,.0f}  |  "
                f"Loyalty: {product.customer_loyalty:.0f}/100"
            ),
            bg=C["white"],
            fg=C["muted"],
            justify="left",
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=24, pady=(10, 0))
        quota_value = tk.IntVar(value=min(product.annual_production_quota, self.player.company.production_capacity))
        marketing_value = tk.DoubleVar(value=product.marketing_budget)
        quota_label = tk.Label(dialog, text="", bg=C["white"], fg=C["blue"], font=("Segoe UI", 14, "bold"))
        quota_label.pack(pady=(16, 4))
        capital_label = tk.Label(dialog, text="", bg=C["white"], fg=C["muted"], font=("Segoe UI", 10))
        capital_label.pack(pady=(2, 4))
        def update_quota(value):
            quota = int(float(value))
            quota_label.config(text=f"Production quota: {quota:,} units")
            capital_remaining = self.player.company.cash - (quota * product.manufacturing_cost) - marketing_value.get()
            capital_color = C["green"] if capital_remaining >= 0 else C["red"]
            capital_label.config(text=f"Capital after production: ${capital_remaining:,.2f}", fg=capital_color)
        tk.Scale(dialog, from_=0, to=self.player.company.production_capacity, orient="horizontal", variable=quota_value, command=update_quota, length=320, resolution=1, showvalue=False, troughcolor="#dbe7f2", activebackground=C["blue"], bg=C["white"], highlightthickness=0).pack(padx=24)
        update_quota(quota_value.get())
        tk.Label(dialog, text="Sale price", bg=C["white"], fg=C["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=24, pady=(18, 4))
        price_limit = max(product.manufacturing_cost * 10, product.sale_price * 2, 1.0)
        price_value = tk.DoubleVar(value=product.sale_price)
        price_label = tk.Label(dialog, text="", bg=C["white"], fg=C["blue"], font=("Segoe UI", 12, "bold"))
        price_label.pack(pady=(0, 4))
        def update_price(value):
            price_label.config(text=f"${float(value):,.2f} per unit")
        tk.Scale(dialog, from_=0.01, to=price_limit, resolution=0.01, orient="horizontal", variable=price_value, command=update_price, length=320, showvalue=False, troughcolor="#dbe7f2", activebackground=C["blue"], bg=C["white"], highlightthickness=0).pack(padx=24)
        update_price(price_value.get())
        tk.Label(dialog, text="Marketing budget", bg=C["white"], fg=C["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=24, pady=(18, 4))
        marketing_label = tk.Label(dialog, text="", bg=C["white"], fg=C["blue"], font=("Segoe UI", 12, "bold"))
        marketing_label.pack(pady=(0, 4))
        def update_marketing(value):
            marketing_label.config(text=f"${float(value):,.0f} per year")
            update_quota(quota_value.get())
        tk.Scale(dialog, from_=0, to=max(self.player.company.cash, 1), resolution=100, orient="horizontal", variable=marketing_value, command=update_marketing, length=320, showvalue=False, troughcolor="#dbe7f2", activebackground=C["blue"], bg=C["white"], highlightthickness=0).pack(padx=24)
        update_marketing(marketing_value.get())
        buttons = tk.Frame(dialog, bg=C["white"]); buttons.pack(fill="x", padx=24, pady=(0, 22))
        def save_plan():
            price = price_value.get()
            if price <= 0: messagebox.showerror("Invalid price", "Sale price must be greater than zero.", parent=dialog); return
            product.set_year_plan(quota_value.get(), price)
            product.marketing_budget = marketing_value.get()
            dialog.destroy(); self.show_company()
        tk.Button(buttons, text="Cancel", command=dialog.destroy, bg=C["white"], fg=C["muted"], relief="flat", padx=12, pady=8).pack(side="right")
        tk.Button(buttons, text="Save plan", command=save_plan, bg=C["green"], fg=C["white"], relief="flat", padx=14, pady=8, font=("Segoe UI", 9, "bold")).pack(side="right", padx=(0, 8))
        dialog.update_idletasks()
        screen_x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        screen_y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{screen_x}+{screen_y}")

    def remove_product(self, product):
        if not messagebox.askyesno("Remove product", f"Remove {product.name} from your lineup? Existing inventory will be discarded.", parent=self):
            return
        self.player.company.products.remove(product)
        self.show_company()

    def open_sell_company(self):
        company = self.player.company
        valuation = company.value()
        base_value = max(valuation, 1)
        dialog = tk.Toplevel(self)
        dialog.title("Sell company")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=C["white"])
        dialog.resizable(False, False)
        tk.Label(dialog, text="Sell company", bg=C["white"], fg=C["ink"], font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=24, pady=(22, 4))
        tk.Label(dialog, text="List your company for sale?", bg=C["white"], fg=C["ink"], font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=(0, 4))
        tk.Label(dialog, text=f"Estimated value: ${valuation:,.0f}", bg=C["white"], fg=C["muted"], font=("Segoe UI", 9)).pack(anchor="w", padx=24, pady=(0, 14))
        prices = [int(base_value * factor) for factor in (0.8, 1.0, 1.2, 1.5, 2.0)]
        selected_price = tk.StringVar(value=f"${prices[1]:,}")
        price_box = ttk.Combobox(dialog, textvariable=selected_price, values=[f"${price:,}" for price in prices], state="readonly", width=24)
        price_box.pack(anchor="w", padx=24); price_box.set(f"${prices[1]:,}")
        buttons = tk.Frame(dialog, bg=C["white"]); buttons.pack(fill="x", padx=24, pady=22)
        def list_company():
            asking_price = int(selected_price.get().replace("$", "").replace(",", ""))
            if asking_price > valuation * 1.5:
                messagebox.showinfo("No sale", "No one was interested in buying your company.", parent=dialog)
                return
            self.player.bank += asking_price
            sold_name = company.name
            self.player.company = None
            dialog.destroy(); self.show_dashboard()
            messagebox.showinfo("Company sold", f"{sold_name} was sold for ${asking_price:,.0f}.", parent=self)
        tk.Button(buttons, text="Cancel", command=dialog.destroy, bg=C["white"], fg=C["muted"], relief="flat", padx=12, pady=8).pack(side="right")
        tk.Button(buttons, text="List for sale", command=list_company, bg=C["green"], fg=C["white"], relief="flat", padx=14, pady=8, font=("Segoe UI", 9, "bold")).pack(side="right", padx=(0, 8))

    def buy_factory(self):
        message = self.player.company.buy_factory(); messagebox.showinfo("Factory", message, parent=self); self.show_company()

    def manage_employees(self):
        company = self.player.company
        self._focus_for_dialog()
        action = simpledialog.askstring(
            "Manage employees",
            f"Current workforce: {company.employee_count}\n"
            f"Required for full staffing: {company.required_employee_count}\n\n"
            "Enter H to hire or L to lay off employees:",
            parent=self,
        )
        if action is None:
            return
        action = action.strip().lower()
        if action not in {"h", "hire", "l", "layoff"}:
            messagebox.showerror("Invalid action", "Enter H to hire or L to lay off employees.", parent=self)
            return
        count = simpledialog.askinteger("Manage employees", "Number of employees:", parent=self, minvalue=1)
        if count is None:
            return
        message = company.hire_employees(count) if action in {"h", "hire"} else company.fire_employees(count)
        messagebox.showinfo("Employees", message, parent=self)
        self.show_company()

    def advance_year(self):
        company = self.player.company
        bankruptcy_message = "You have gone bankrupt, the authorities have taken all of the company's possessions to make up for it."
        if company and company.bankrupt:
            self.player.company = None
            self.show_dashboard()
            messagebox.showinfo("Bankruptcy", bankruptcy_message, parent=self)
            return
        if company:
            total = sum(p.annual_production_quota for p in company.products)
            if total > company.production_capacity: messagebox.showwarning("Capacity exceeded", "Your annual plan is larger than factory capacity.", parent=self); return
            try:
                summary = company.run_year(self.player.year)
            except Exception as exc:
                logger.exception("Annual simulation failed")
                messagebox.showerror("Simulation failed", str(exc), parent=self)
                return
        else: summary = None
        became_bankrupt = company is not None and company.bankrupt
        self.market.next_year(self.player); self.player.advance_year()
        if became_bankrupt:
            self.player.company = None
        self.show_dashboard()
        if became_bankrupt:
            messagebox.showinfo("Bankruptcy", bankruptcy_message, parent=self)
            return
        if summary: messagebox.showinfo("Annual report", f"Sales: {summary['units_sold']:,} units\nUnsold: {summary['units_unsold']:,} units\nRevenue: ${summary['revenue']:,.0f}\nTaxes: ${summary['taxes']:,.0f}\nNet income: ${summary['net_income']:,.0f}", parent=self)

    def invest_in_company(self):
        if not self.player.company:
            messagebox.showinfo("Company required", "Create a company before investing.", parent=self)
            return
        self._focus_for_dialog()
        amount = simpledialog.askfloat("Invest in company", "Amount to invest from your bank:", minvalue=0.01, parent=self)
        if amount is None:
            return
        if amount > self.player.bank:
            messagebox.showerror("Insufficient funds", "Your bank balance is too low.", parent=self)
            return
        self.player.bank -= amount
        self.player.company.invest(amount)
        logger.info("Player invested %.2f into %s", amount, self.player.company.name)
        self.show_company()

    def save_current_game(self):
        try:
            save_game(self.player, self.market, SAVE_FILE)
        except (OSError, TypeError, ValueError) as exc:
            logger.exception("Unable to save game")
            messagebox.showerror("Save failed", str(exc), parent=self)
            return
        messagebox.showinfo("Game saved", f"Progress saved to {SAVE_FILE}.", parent=self)

    def load_saved_game(self):
        try:
            self.player, self.market = load_game(SAVE_FILE)
        except (OSError, KeyError, TypeError, ValueError) as exc:
            logger.exception("Unable to load game")
            messagebox.showerror("Load failed", str(exc), parent=self)
            return
        logger.info("Game loaded from %s", SAVE_FILE)
        self.show_dashboard()

    def show_stocks(self):
        self._clear("Stock market")
        card = self._card(self.content); card.pack(fill="both", expand=True)
        filters = tk.Frame(card, bg=C["white"])
        filters.pack(fill="x", padx=14, pady=(14, 4))
        tk.Label(filters, text="FILTER MARKET", bg=C["white"], fg=C["muted"], font=("Segoe UI", 9, "bold")).pack(side="left", padx=(8, 14))
        sector_filter = tk.StringVar(value="All sectors")
        debt_filter = tk.StringVar(value="Any debt")
        revenue_filter = tk.StringVar(value="Any revenue")
        ownership_filter = tk.StringVar(value="All stocks")
        sector_values = ["All sectors", *sorted({stock.sector for stock in self.market.stocks.values()})]
        ttk.Combobox(filters, textvariable=sector_filter, values=sector_values, state="readonly", width=16).pack(side="left", padx=3)
        ttk.Combobox(filters, textvariable=debt_filter, values=["Any debt", "Low debt", "Medium debt", "High debt"], state="readonly", width=14).pack(side="left", padx=3)
        ttk.Combobox(filters, textvariable=revenue_filter, values=["Any revenue", "Under $1B", "$1B-$10B", "$10B-$100B", "Over $100B"], state="readonly", width=14).pack(side="left", padx=3)
        ttk.Combobox(filters, textvariable=ownership_filter, values=["All stocks", "Owned stocks"], state="readonly", width=14).pack(side="left", padx=3)

        table = ttk.Treeview(card, columns=("ticker", "name", "price", "return", "owned", "revenue", "profit", "debt", "growth"), show="headings")
        self.stock_table = table
        for key, heading, width in [("ticker", "TICKER", 70), ("name", "COMPANY", 165), ("price", "PRICE", 85), ("return", "LAST RETURN", 95), ("owned", "OWNED", 65), ("revenue", "REVENUE", 115), ("profit", "PROFIT", 115), ("debt", "DEBT", 115), ("growth", "GROWTH", 80)]: table.heading(key, text=heading); table.column(key, width=width, anchor="w")

        def debt_level(stock):
            ratio = stock.debt / max(stock.revenue, 1)
            return "High debt" if ratio > 0.7 else "Medium debt" if ratio > 0.35 else "Low debt"

        def revenue_matches(stock):
            if revenue_filter.get() == "Any revenue":
                return True
            if revenue_filter.get() == "Under $1B":
                return stock.revenue < 1_000_000_000
            if revenue_filter.get() == "$1B-$10B":
                return 1_000_000_000 <= stock.revenue < 10_000_000_000
            if revenue_filter.get() == "$10B-$100B":
                return 10_000_000_000 <= stock.revenue < 100_000_000_000
            return stock.revenue >= 100_000_000_000

        def apply_filters(*_args):
            table.delete(*table.get_children())
            for stock in self.market.stocks.values():
                owned = self.player.portfolio.get(stock.ticker, {}).get("shares", 0)
                if sector_filter.get() != "All sectors" and stock.sector != sector_filter.get():
                    continue
                if debt_filter.get() != "Any debt" and debt_level(stock) != debt_filter.get():
                    continue
                if not revenue_matches(stock):
                    continue
                if ownership_filter.get() == "Owned stocks" and owned <= 0:
                    continue
                last_return = stock.annual_returns[-1] if stock.annual_returns else 0.0
                table.insert("", "end", iid=stock.ticker, values=(stock.ticker, stock.name, f"${stock.price:,.2f}", f"{last_return:+.2f}%", owned, f"${stock.revenue:,.0f}", f"${stock.profit:,.0f}", f"${stock.debt:,.0f}", f"{stock.growth_rate:.1%}"))

        table.pack(fill="both", expand=True, padx=14, pady=10); table.bind("<<TreeviewSelect>>", lambda _e: self.stock_details(table))
        for variable in (sector_filter, debt_filter, revenue_filter, ownership_filter):
            variable.trace_add("write", apply_filters)
        apply_filters()
        actions = tk.Frame(card, bg=C["white"]); actions.pack(fill="x", padx=14, pady=(0, 14))
        tk.Button(actions, text="Buy selected", command=lambda: self.trade_stock("buy"), bg=C["green"], fg=C["white"], relief="flat", padx=12, pady=9, font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        tk.Button(actions, text="Sell selected", command=lambda: self.trade_stock("sell"), bg=C["blue"], fg=C["white"], relief="flat", padx=12, pady=9, font=("Segoe UI", 9, "bold")).pack(side="left")

    def stock_details(self, table):
        selected = table.selection()
        if not selected: return
        stock = self.market.stocks[selected[0]]; owned = self.player.portfolio.get(stock.ticker, {}).get("shares", 0)
        messagebox.showinfo(stock.name, f"Price: ${stock.price:,.2f}\nRevenue: ${stock.revenue:,.0f}\nProfit: ${stock.profit:,.0f}\nDebt: ${stock.debt:,.0f}\nGrowth: {stock.growth_rate:.1%}\nOwned shares: {owned}")

    def trade_stock(self, action):
        selected = self.stock_table.selection()
        if not selected:
            messagebox.showwarning("Select a stock", "Select a stock before trading.", parent=self)
            return
        ticker = selected[0]
        self._focus_for_dialog()
        shares = simpledialog.askinteger("Trade shares", "Number of shares:", minvalue=1, parent=self)
        if shares is None:
            return
        result = self.market.buy_stock(self.player, ticker, shares) if action == "buy" else self.market.sell_stock(self.player, ticker, shares)
        messagebox.showinfo("Trade result", result, parent=self)
        self.show_stocks()

    def show_portfolio(self):
        self._clear("Your portfolio")
        card = self._card(self.content); card.pack(fill="both", expand=True)
        tk.Label(card, text=f"Portfolio value  ${self.market.portfolio_value(self.player):,.2f}", bg=C["white"], fg=C["ink"], font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=24, pady=22)
        for ticker, holding in self.player.portfolio.items():
            stock = self.market.stocks[ticker]; tk.Label(card, text=f"{ticker}  ·  {stock.name}    {holding['shares']} shares    Current value ${stock.price * holding['shares']:,.2f}", bg=C["white"], fg=C["ink"], font=("Segoe UI", 11)).pack(anchor="w", padx=24, pady=8)
        if not self.player.portfolio: tk.Label(card, text="No holdings yet. Visit the Stock Market to begin.", bg=C["white"], fg=C["muted"], font=("Segoe UI", 11)).pack(anchor="w", padx=24)


def launch():
    BankingLifeSim().mainloop()


if __name__ == "__main__":
    launch()
