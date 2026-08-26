import json
from pathlib import Path
from stock_class import Stock

class StockMarket:
    def __init__(self):
        self.stocks = {}
        self.load_stocks()

    def load_stocks(self):
        data_file = Path(__file__).with_name("stocks.json")
        with data_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        for s in data["stocks"]:
            sector = s.get("sector", "Unknown")
            profile = data.get("fundamental_profiles", {}).get(sector, {})
            ticker = s["ticker"]
            name = s["name"]
            price = s["price"]
            trend = s["trend"]
            volatility = s["volatility"]

            self.stocks[ticker] = Stock(
                ticker=ticker,
                name=name,
                price=price,
                trend=trend,
                volatility=volatility,
                sector=sector,
                revenue=profile.get("revenue", 0),
                profit=profile.get("profit", 0),
                debt=profile.get("debt", 0),
                growth_rate=profile.get("growth_rate", 0.0),
            )

    def view_stocks(self):
        if not self.stocks:
            print("No stocks available.")
            return

        for stock in self.stocks.values():
            print(f"{stock.ticker} | {stock.name} | {stock.sector} | ${stock.price:.2f}")

    def next_day(self, player):
        for stock in self.stocks.values():
            stock.update_price()

            # Trigger a 2-for-1 split if price gets too high
            if stock.price > 500:
                self.apply_split(stock, 2, player)

    def apply_split(self, stock, ratio, player):
        """Apply a stock split while preserving the player's holding value."""
        stock.price = round(stock.price / ratio, 2)

        if stock.ticker in player.portfolio:
            holding = player.portfolio[stock.ticker]
            holding["shares"] *= ratio
            holding["avg_price"] = round(holding["avg_price"] / ratio, 2)

        return f"{stock.ticker} has split {ratio}-for-1!"

    def buy_stock(self, player, ticker, shares):
        if shares <= 0:
            return "Shares must be a positive whole number."

        if ticker not in self.stocks:
            return "Invalid ticker."

        stock = self.stocks[ticker]
        cost = stock.price * shares

        if player.bank < cost:
            return "You don't have enough money."

        player.bank -= cost

        if ticker in player.portfolio:
            old_shares = player.portfolio[ticker]["shares"]
            old_avg = player.portfolio[ticker]["avg_price"]

            new_total_shares = old_shares + shares
            new_avg_price = ((old_avg * old_shares) + cost) / new_total_shares

            player.portfolio[ticker]["shares"] = new_total_shares
            player.portfolio[ticker]["avg_price"] = round(new_avg_price, 2)

        else:
            player.portfolio[ticker] = {
                "shares": shares,
                "avg_price": stock.price
            }

        return f"Bought {shares} shares of {ticker} at ${stock.price} each."

    def sell_stock(self, player, ticker, shares):
        if shares <= 0:
            return "Shares must be a positive whole number."

        if ticker not in player.portfolio or player.portfolio[ticker]["shares"] < shares:
            return "You don't own enough shares."

        stock = self.stocks[ticker]
        revenue = stock.price * shares

        player.bank += revenue
        player.portfolio[ticker]["shares"] -= shares

        if player.portfolio[ticker]["shares"] == 0:
            del player.portfolio[ticker]

        return f"Sold {shares} shares of {ticker} at ${stock.price} each."

    def portfolio_value(self, player):
        total = 0

        if not player.portfolio:
            return 0

        for ticker, data in player.portfolio.items():
            shares = data["shares"]
            stock = self.stocks[ticker]
            total += stock.price * shares

        return total

    def net_worth(self, player):
        return player.cash + player.bank + self.portfolio_value(player)
