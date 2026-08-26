import tkinter as tk
from tkinter import simpledialog

from company_class import Company
from create_product import ProductCreator
from player_class import Player
from stock_market import StockMarket
from ui.gui_components import make_button, write_to_textbox
from ui.gui_ticker import build_ticker

SECTOR_STARTUP_COSTS = {
    "Technology": 250000,
    "Finance": 150000,
    "Healthcare": 200000,
    "Energy": 300000,
    "Retail": 75000,
    "Automotive": 275000,
    "Food": 50000,
    "Media": 100000,
    "Aerospace": 400000,
    "Industrial": 225000,
}


def launch():
    """Create and run the Banking Life Simulator window."""
    player = Player()
    market = StockMarket()
    root = tk.Tk()
    root.title("Banking Life Sim")
    root.geometry("1000x650")
    root.minsize(800, 500)
    root.configure(bg="#111111")

    build_ticker(root, market)

    # A canvas makes the left navigation usable even after more menu items are added.
    sidebar_shell = tk.Frame(root, bg="#1a1a1a", width=200)
    sidebar_shell.pack(side="left", fill="y")
    sidebar_shell.pack_propagate(False)
    sidebar_canvas = tk.Canvas(sidebar_shell, bg="#1a1a1a", highlightthickness=0)
    sidebar_scrollbar = tk.Scrollbar(sidebar_shell, orient="vertical", command=sidebar_canvas.yview)
    sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
    sidebar_scrollbar.pack(side="right", fill="y")
    sidebar_canvas.pack(side="left", fill="both", expand=True)
    sidebar = tk.Frame(sidebar_canvas, bg="#1a1a1a")
    sidebar_window = sidebar_canvas.create_window((0, 0), window=sidebar, anchor="nw")

    def update_sidebar_scroll(_event=None):
        if _event is not None:
            del _event
        sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all"))

    def resize_sidebar(event):
        sidebar_canvas.itemconfigure(sidebar_window, width=event.width)

    def scroll_sidebar(event):
        if event.delta:
            sidebar_canvas.yview_scroll(-int(event.delta / 120), "units")

    sidebar.bind("<Configure>", update_sidebar_scroll)
    sidebar_canvas.bind("<Configure>", resize_sidebar)
    sidebar_canvas.bind("<MouseWheel>", scroll_sidebar)
    sidebar.bind("<MouseWheel>", scroll_sidebar)

    content = tk.Frame(root, bg="#111111")
    content.pack(side="right", fill="both", expand=True)
    header = tk.Label(content, fg="white", bg="#111111", font=("Segoe UI", 18, "bold"))
    header.pack(pady=10)
    page = tk.Frame(content, bg="#111111")
    page.pack(fill="both", expand=True, padx=20, pady=(0, 10))

    textbox = tk.Text(page, bg="#000000", fg="#dddddd", font=("Segoe UI", 12), state="disabled")
    textbox.pack(fill="both", expand=True)
    current_page = "welcome"

    def refresh_header():
        header.config(text=f"{player.month}/{player.day}/{player.year}   |   Net Worth: ${market.net_worth(player):,.2f}")

    def show_text(message):
        stock_panel.pack_forget()
        company_panel.pack_forget()
        textbox.pack(fill="both", expand=True)
        write_to_textbox(textbox, message)

    def show_finances():
        nonlocal current_page
        current_page = "finances"
        portfolio = market.portfolio_value(player)
        show_text(
            f"Cash: ${player.cash:,.2f}\nBank: ${player.bank:,.2f}\n"
            f"Portfolio: ${portfolio:,.2f}\nNet worth: ${market.net_worth(player):,.2f}"
        )

    def advance_days(days):
        for _ in range(days):
            player.advance_day()
            market.next_day(player)
        refresh_header()
        if current_page == "finances":
            show_finances()
        elif current_page in {"company", "company_menu"}:
            show_company_summary()
        elif current_page == "stocks":
            if current_view == "portfolio":
                show_portfolio()
            else:
                populate_stocks(active_sector.get())

    def create_company_gui():
        if player.company is not None:
            show_text(f"You already own {player.company.name}.")
            return

        name = simpledialog.askstring("Create Company", "Enter company name:")
        if not name or not name.strip():
            show_text("Company name cannot be empty.")
            return

        sectors = sorted(set(ProductCreator.load_catalog().keys()) | set(SECTOR_STARTUP_COSTS.keys()))
        sector_list = "\n".join(f"{i + 1}. {sector}" for i, sector in enumerate(sectors))
        sector_choice = simpledialog.askstring("Create Company", f"Choose a sector:\n{sector_list}\n\nEnter a number:")
        if sector_choice is None:
            return

        try:
            sector_index = int(sector_choice.strip())
        except ValueError:
            sector_name = sector_choice.strip().title()
            if sector_name not in sectors:
                show_text("That sector is not available.")
                return
            sector = sector_name
        else:
            if sector_index < 1 or sector_index > len(sectors):
                show_text("Invalid sector selection.")
                return
            sector = sectors[sector_index - 1]

        startup_cost = SECTOR_STARTUP_COSTS.get(sector, 50000)
        if player.bank < startup_cost:
            show_text(f"You need at least ${startup_cost:,.2f} in your bank account to start a {sector} company.")
            return

        company = Company(name.strip(), sector)
        company.cash = startup_cost
        company.capital_invested = startup_cost
        player.company = company
        player.bank -= startup_cost
        show_company_summary()

    def show_company_summary():
        nonlocal current_page
        target_page = current_page
        current_page = "company"
        current_company = player.company
        if current_company is None:
            if target_page == "company_menu":
                refresh_company_summary_panel()
                return
            show_text("You do not own a company yet.\nUse the Create Company button in the sidebar.")
            return

        if target_page == "company_menu":
            refresh_company_summary_panel()
            return

        summary = current_company.get_financial_summary()
        lines = [
            f"Company: {current_company.name}",
            f"Sector: {current_company.sector}",
            f"Cash: ${summary['cash']:,.2f}",
            f"Revenue: ${summary['revenue']:,.2f}",
            f"Expenses: ${summary['expenses']:,.2f}",
            f"Net income: ${summary['net_income']:,.2f}",
            f"Debt: ${summary['debt']:,.2f}",
            f"Capital invested: ${summary['capital_invested']:,.2f}",
            f"Units sold: {summary['total_units_sold']}",
            f"Unsold units: {summary['total_units_unsold']}",
            f"Inventory: {summary['total_inventory']}",
            "",
            "Products:",
        ]
        if current_company.products:
            for product in current_company.products:
                lines.append(
                    f"- {product.name} | Price: ${product.sale_price:,.2f} | "
                    f"Production: {product.production_target} | Sold: {product.units_sold} | "
                    f"Inventory: {product.inventory} | Revenue: ${product.monthly_revenue:,.2f} | "
                    f"Profit: ${product.monthly_profit:,.2f}"
                )
        else:
            lines.append("- No products launched yet.")
        show_text("\n".join(lines))

    def confirm_yes_no(prompt_title, prompt_text):
        response = simpledialog.askstring(prompt_title, prompt_text, parent=root)
        if response is None:
            return False
        return response.strip().lower() == "y"

    def can_afford_production(company, product, units):
        if units <= 0:
            return True
        return company.cash >= (units * product.manufacturing_cost)

    def research_and_launch_product():
        if player.company is None:
            show_text("Create a company first.")
            return

        company = player.company
        sector_products = ProductCreator.load_sector_products(company.sector)
        if not sector_products:
            show_text("No products are available for this sector.")
            return

        options = "\n".join(
            f"{i + 1}. {product.name} | {'researched' if product.researched else f'research ${product.research_cost:,.2f}'}"
            for i, product in enumerate(sector_products)
        )
        selection = simpledialog.askstring("Research Product", f"Select a product:\n{options}\n\nEnter a number:")
        if selection is None:
            return

        try:
            index = int(selection.strip()) - 1
        except ValueError:
            show_text("Please enter a valid product number.")
            return

        if index < 0 or index >= len(sector_products):
            show_text("Invalid product selection.")
            return

        chosen = sector_products[index]
        if chosen.researched:
            if any(product.name == chosen.name for product in company.products):
                show_text(f"{chosen.name} is already in your product lineup.")
            elif confirm_yes_no("Launch Product", f"{chosen.name} is already researched. Launch it now? (y/n): "):
                company.add_product(chosen)
                show_company_summary()
            else:
                show_company_summary()
            return

        if company.cash < chosen.research_cost:
            show_text(f"You need ${chosen.research_cost:,.2f} to research {chosen.name}.")
            return

        company.cash -= chosen.research_cost
        chosen.research(company.cash)
        details = (
            f"{chosen.name} is now researched.\n"
            f"Demand: {chosen.base_demand}/10\n"
            f"Competition: {chosen.competition}/10\n"
            f"Manufacturing cost: ${chosen.manufacturing_cost:,.2f}"
        )
        if confirm_yes_no("Launch Product", f"{details}\n\nLaunch this product now? (y/n): "):
            company.add_product(chosen)
            show_text(f"{chosen.name} was added to your product lineup.\n\n{details}")
        else:
            show_text(details)

    def manage_company_products():
        if player.company is None:
            show_text("Create a company first.")
            return

        company = player.company
        if not company.products:
            show_text("You have no products added yet. Research a product first.")
            return

        options = "\n".join(
            f"{i + 1}. {product.name} | price ${product.sale_price:,.2f} | target {product.production_target} | inventory {product.inventory}"
            for i, product in enumerate(company.products)
        )
        action_raw = simpledialog.askstring("Manage Products", f"Select a product action:\n{options}\n\n1. Set production\n2. Set sale price\nEnter action number:")
        if action_raw is None:
            return

        action_value = action_raw.strip()
        if not action_value:
            show_text("Please enter a valid number.")
            return

        try:
            action_choice = int(action_value)
        except ValueError:
            show_text("Please enter a valid number.")
            return

        if 1 <= action_choice <= len(company.products):
            selected_product = company.products[action_choice - 1]
            method_raw = simpledialog.askstring("Manage Products", "1. Set production\n2. Set sale price\n\nChoose an option:")
            if method_raw is None:
                return

            method_value = method_raw.strip()
            if method_value == "1":
                amount_raw = simpledialog.askstring("Production Target", f"How many units of {selected_product.name} should be produced this month?")
                if amount_raw is None:
                    return
                try:
                    target = int(amount_raw)
                except (TypeError, ValueError):
                    show_text("Please enter a valid unit count.")
                    return
                if target < 0:
                    show_text("Production target cannot be negative.")
                    return
                required_capital = target * selected_product.manufacturing_cost
                if not can_afford_production(company, selected_product, target):
                    show_text(
                        f"Not enough capital to produce {target} units of {selected_product.name}. "
                        f"This would cost ${required_capital:,.2f}, but your company has ${company.cash:,.2f}."
                    )
                    return
                selected_product.set_month_plan(target)
                show_text(f"{selected_product.name} production target set to {selected_product.production_target} units.")
            elif method_value == "2":
                price_raw = simpledialog.askstring("Sale Price", f"Set the sale price for {selected_product.name}: ")
                if price_raw is None:
                    return
                try:
                    new_price = float(price_raw)
                except (TypeError, ValueError):
                    show_text("Please enter a valid price.")
                    return
                if new_price <= 0:
                    show_text("Sale price must be greater than zero.")
                    return
                selected_product.sale_price = new_price
                show_text(f"{selected_product.name} sale price set to ${selected_product.sale_price:,.2f}.")
            else:
                show_text("Invalid action.")
            return

        if action_choice == 1:
            product_number_raw = simpledialog.askstring("Production Target", "Enter product number to update production:")
            if product_number_raw is None:
                return
            try:
                product_index = int(product_number_raw) - 1
            except (TypeError, ValueError):
                show_text("Please enter a valid product number.")
                return
            if product_index < 0 or product_index >= len(company.products):
                show_text("Invalid product number.")
                return
            target_raw = simpledialog.askstring("Production Target", f"How many units of {company.products[product_index].name} should be produced this month?")
            if target_raw is None:
                return
            try:
                target = int(target_raw)
            except (TypeError, ValueError):
                show_text("Please enter a valid production target.")
                return
            if target < 0:
                show_text("Production target cannot be negative.")
                return
            product = company.products[product_index]
            required_capital = target * product.manufacturing_cost
            if not can_afford_production(company, product, target):
                show_text(
                    f"Not enough capital to produce {target} units of {product.name}. "
                    f"This would cost ${required_capital:,.2f}, but your company has ${company.cash:,.2f}."
                )
                return
            product.set_month_plan(target)
            show_text(f"{product.name} production target set to {product.production_target} units.")
        elif action_choice == 2:
            product_number_raw = simpledialog.askstring("Sale Price", "Enter product number to update sale price:")
            if product_number_raw is None:
                return
            try:
                product_index = int(product_number_raw) - 1
            except (TypeError, ValueError):
                show_text("Please enter a valid product number.")
                return
            if product_index < 0 or product_index >= len(company.products):
                show_text("Invalid product number.")
                return
            price_raw = simpledialog.askstring("Sale Price", f"Set the sale price for {company.products[product_index].name}: ")
            if price_raw is None:
                return
            try:
                new_price = float(price_raw)
            except (TypeError, ValueError):
                show_text("Please enter a valid price.")
                return
            if new_price <= 0:
                show_text("Sale price must be greater than zero.")
                return
            company.products[product_index].sale_price = new_price
            show_text(f"{company.products[product_index].name} sale price set to ${company.products[product_index].sale_price:,.2f}.")
        else:
            show_text("Invalid option.")

    def invest_in_company():
        if player.company is None:
            show_text("Create a company first.")
            return

        amount_raw = simpledialog.askstring("Investment", "How much would you like to invest into your company?")
        if amount_raw is None:
            return

        try:
            investment = float(amount_raw)
        except (TypeError, ValueError):
            show_text("Please enter a valid investment amount.")
            return

        if investment <= 0:
            show_text("Investment amount must be greater than zero.")
            return
        if player.bank < investment:
            show_text(f"You do not have enough in your bank account. You have ${player.bank:,.2f}.")
            return

        player.bank -= investment
        player.company.invest(investment)
        show_text(f"You invested ${investment:,.2f} into {player.company.name}.\nCompany cash: ${player.company.cash:,.2f}")

    def run_company_month():
        if player.company is None:
            show_text("Create a company first.")
            return

        company = player.company
        if not company.products:
            show_text("You have no products to sell this month.")
            return

        required_capital = sum(product.production_target * product.manufacturing_cost for product in company.products)
        if company.cash < required_capital:
            show_text(
                f"Not enough capital to run this month's production. "
                f"You need ${required_capital:,.2f} but only have ${company.cash:,.2f}. "
                f"Lower the production targets or invest more cash."
            )
            return

        company.run_month()
        player.advance_month()
        refresh_header()
        refresh_company_summary_panel()
        summary = company.get_financial_summary()
        show_text(
            f"Month complete.\n"
            f"Revenue: ${summary['revenue']:,.2f}\n"
            f"Expenses: ${summary['expenses']:,.2f}\n"
            f"Net income: ${summary['net_income']:,.2f}\n"
            f"Cash: ${summary['cash']:,.2f}\n"
            f"Date: {player.month}/{player.day}/{player.year}"
        )

    # All stock controls live in this center panel, not the left navigation.
    company_panel = tk.Frame(page, bg="#111111")
    company_title = tk.Label(company_panel, text="Company Management", fg="white", bg="#111111", font=("Segoe UI", 16, "bold"))
    company_title.pack(pady=(0, 8))

    company_action_bar = tk.Frame(company_panel, bg="#111111")
    company_action_bar.pack(fill="x", pady=(0, 10))
    company_summary_box = tk.Text(company_panel, bg="#000000", fg="#dddddd", font=("Segoe UI", 11), state="disabled", wrap="word", height=18)
    company_summary_box.pack(fill="both", expand=True)

    def refresh_company_summary_panel():
        company_summary_box.configure(state="normal")
        company_summary_box.delete("1.0", tk.END)
        if player.company is None:
            company_summary_box.insert("end", "No company created yet.\nUse Create Company to begin.")
        else:
            company = player.company
            summary = company.get_financial_summary()
            lines = [
                f"Company: {company.name}",
                f"Sector: {company.sector}",
                f"Cash: ${summary['cash']:,.2f}",
                f"Revenue: ${summary['revenue']:,.2f}",
                f"Expenses: ${summary['expenses']:,.2f}",
                f"Net income: ${summary['net_income']:,.2f}",
                f"Debt: ${summary['debt']:,.2f}",
                f"Capital invested: ${summary['capital_invested']:,.2f}",
                f"Units sold: {summary['total_units_sold']}",
                f"Unsold units: {summary['total_units_unsold']}",
                f"Inventory: {summary['total_inventory']}",
                "",
                "Products:",
            ]
            if company.products:
                for product in company.products:
                    lines.append(
                        f"- {product.name} | Price: ${product.sale_price:,.2f} | "
                        f"Production: {product.production_target} | Sold: {product.units_sold} | "
                        f"Inventory: {product.inventory} | Revenue: ${product.monthly_revenue:,.2f} | "
                        f"Profit: ${product.monthly_profit:,.2f}"
                    )
            else:
                lines.append("- No products launched yet.")
            company_summary_box.insert("end", "\n".join(lines))
        company_summary_box.configure(state="disabled")

    make_button(company_action_bar, "Create", create_company_gui).pack(side="left", fill="x", expand=True, padx=(0, 6))
    make_button(company_action_bar, "Summary", show_company_summary).pack(side="left", fill="x", expand=True, padx=(0, 6))
    make_button(company_action_bar, "Research", research_and_launch_product).pack(side="left", fill="x", expand=True, padx=(0, 6))
    make_button(company_action_bar, "Products", manage_company_products).pack(side="left", fill="x", expand=True, padx=(0, 6))
    make_button(company_action_bar, "Invest", invest_in_company).pack(side="left", fill="x", expand=True, padx=(0, 6))
    make_button(company_action_bar, "Run Month", run_company_month).pack(side="left", fill="x", expand=True)

    stock_panel = tk.Frame(page, bg="#111111")
    stock_title = tk.Label(stock_panel, text="Stock Market", fg="white", bg="#111111", font=("Segoe UI", 16, "bold"))
    stock_title.pack(pady=(0, 8))
    category_bar = tk.Frame(stock_panel, bg="#111111")
    category_bar.pack(fill="x", pady=(0, 8))
    body = tk.Frame(stock_panel, bg="#111111")
    body.pack(fill="both", expand=True)
    list_frame = tk.Frame(body, bg="#111111")
    list_frame.pack(side="left", fill="both", expand=True)
    stock_list = tk.Listbox(list_frame, bg="#000000", fg="#dddddd", selectbackground="#356b56", font=("Consolas", 11), activestyle="none")
    stock_scrollbar = tk.Scrollbar(list_frame, command=stock_list.yview)
    stock_list.configure(yscrollcommand=stock_scrollbar.set)
    stock_scrollbar.pack(side="right", fill="y")
    stock_list.pack(side="left", fill="both", expand=True)

    details = tk.Frame(body, bg="#1a1a1a", width=235)
    details.pack(side="right", fill="y", padx=(12, 0))
    details.pack_propagate(False)
    selected_ticker = tk.StringVar()
    detail_label = tk.Label(details, text="Select a stock", fg="white", bg="#1a1a1a", justify="left", anchor="nw", font=("Segoe UI", 11))
    detail_label.pack(fill="x", padx=12, pady=12)
    tk.Label(details, text="Shares", fg="white", bg="#1a1a1a", font=("Segoe UI", 11)).pack(anchor="w", padx=12, pady=(8, 2))
    shares_entry = tk.Entry(details, bg="#222222", fg="white", insertbackground="white")
    shares_entry.pack(fill="x", padx=12)
    trade_message = tk.Label(details, text="", fg="#dddddd", bg="#1a1a1a", wraplength=210, justify="left")
    trade_message.pack(fill="x", padx=12, pady=10)

    current_stocks = []
    current_view = "stocks"

    def select_stock(_event=None):
        if _event is not None:
            pass
        selection = stock_list.curselection()
        if not selection:
            return
        stock = current_stocks[selection[0]]
        selected_ticker.set(stock.ticker)
        holding = player.portfolio.get(stock.ticker, {})
        owned = holding.get("shares", 0)
        holding_details = f"\nYou own: {owned} shares"
        if owned:
            value = stock.price * owned
            gain = value - (holding["avg_price"] * owned)
            holding_details += f"\nAverage cost: ${holding['avg_price']:,.2f}\nMarket value: ${value:,.2f}\nGain/loss: ${gain:,.2f}"
        detail_label.config(text=f"{stock.name}\n\nTicker: {stock.ticker}\nSector: {stock.sector}\nPrice: ${stock.price:,.2f}{holding_details}")
        trade_message.config(text="")

    def populate_stocks(sector="All Stocks"):
        nonlocal current_stocks, current_view
        current_view = "stocks"
        stock_title.config(text=f"Stock Market — {sector}")
        current_stocks = [stock for stock in market.stocks.values() if sector == "All Stocks" or stock.sector == sector]
        stock_list.delete(0, tk.END)
        for stock in current_stocks:
            stock_list.insert(tk.END, f"{stock.ticker:<6} ${stock.price:>8,.2f}  {stock.name}")
        selected_ticker.set("")
        detail_label.config(text="Select a stock")
        trade_message.config(text="")

    def show_portfolio():
        nonlocal current_stocks, current_view
        current_view = "portfolio"
        stock_title.config(text=f"My Portfolio — ${market.portfolio_value(player):,.2f}")
        current_stocks = [market.stocks[ticker] for ticker in player.portfolio if ticker in market.stocks]
        stock_list.delete(0, tk.END)
        for stock in current_stocks:
            holding = player.portfolio[stock.ticker]
            value = stock.price * holding["shares"]
            stock_list.insert(tk.END, f"{stock.ticker:<6} {holding['shares']:>4} shares  ${value:>8,.2f}  {stock.name}")
        selected_ticker.set("")
        detail_label.config(text="Select a holding" if current_stocks else "You do not own any stocks yet.")
        trade_message.config(text="")

    def trade(action):
        ticker = selected_ticker.get()
        if not ticker:
            trade_message.config(text="Select a stock first.")
            return
        try:
            shares = int(shares_entry.get())
        except ValueError:
            trade_message.config(text="Shares must be a positive whole number.")
            return
        result = market.buy_stock(player, ticker, shares) if action == "buy" else market.sell_stock(player, ticker, shares)
        refresh_header()
        if current_view == "portfolio":
            show_portfolio()
        else:
            populate_stocks(active_sector.get())
        trade_message.config(text=result)

    make_button(details, "Buy Selected", lambda: trade("buy")).pack(fill="x", padx=12, pady=(4, 4))
    make_button(details, "Sell Selected", lambda: trade("sell")).pack(fill="x", padx=12)
    stock_list.bind("<<ListboxSelect>>", select_stock)

    active_sector = tk.StringVar(value="All Stocks")
    sectors = ["All Stocks", *sorted({stock.sector for stock in market.stocks.values()})]
    for index, sector in enumerate(sectors):
        tk.Radiobutton(category_bar, text=sector, value=sector, variable=active_sector, command=lambda s=sector: populate_stocks(s), fg="white", bg="#111111", selectcolor="#333333", activebackground="#111111", activeforeground="white").grid(row=index // 4, column=index % 4, sticky="w", padx=6, pady=2)
    make_button(category_bar, "My Portfolio", show_portfolio).grid(row=0, column=4, rowspan=2, sticky="nsew", padx=(14, 0))

    def show_stock_menu():
        nonlocal current_page
        current_page = "stocks"
        textbox.pack_forget()
        company_panel.pack_forget()
        stock_panel.pack(fill="both", expand=True)
        populate_stocks(active_sector.get())

    def show_company_menu():
        nonlocal current_page
        current_page = "company_menu"
        textbox.pack_forget()
        stock_panel.pack_forget()
        company_panel.pack(fill="both", expand=True)
        refresh_company_summary_panel()

    make_button(sidebar, "Finances", show_finances).pack(fill="x")
    make_button(sidebar, "Next Day", lambda: advance_days(1)).pack(fill="x")
    make_button(sidebar, "Next Year", lambda: advance_days(365)).pack(fill="x")
    make_button(sidebar, "View Stocks", show_stock_menu).pack(fill="x")
    make_button(sidebar, "Company Management", show_company_menu).pack(fill="x")

    refresh_header()
    show_text("Welcome to Banking Life Simulator.")
    root.mainloop()


if __name__ == "__main__":
    launch()
