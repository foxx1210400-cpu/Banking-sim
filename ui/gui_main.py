import tkinter as tk

from player_class import Player
from stock_market import StockMarket
from ui.gui_components import make_button, write_to_textbox
from ui.gui_ticker import build_ticker


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
        elif current_page == "stocks":
            if current_view == "portfolio":
                show_portfolio()
            else:
                populate_stocks(active_sector.get())

    # All stock controls live in this center panel, not the left navigation.
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
        stock_panel.pack(fill="both", expand=True)
        populate_stocks(active_sector.get())

    make_button(sidebar, "Finances", show_finances).pack(fill="x")
    make_button(sidebar, "Next Day", lambda: advance_days(1)).pack(fill="x")
    make_button(sidebar, "Next Year", lambda: advance_days(365)).pack(fill="x")
    make_button(sidebar, "View Stocks", show_stock_menu).pack(fill="x")

    refresh_header()
    show_text("Welcome to Banking Life Simulator.")
    root.mainloop()


if __name__ == "__main__":
    launch()
