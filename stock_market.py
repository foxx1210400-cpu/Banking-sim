import json
import random
from pathlib import Path
from stock_class import Stock
from logger import logger

class StockMarket:
    def __init__(self):
        self.stocks = {}
        self.market_return = 0.0
        self.load_stocks()

    def load_stocks(self):
        data_file = Path(__file__).with_name("stocks.json")
        try:
            with data_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            logger.exception("Failed to load stock data: %s", exc)
            return

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
            stock.update_price(self.market_return)

    def next_year(self, player):
        starting_prices = {ticker: stock.price for ticker, stock in self.stocks.items()}
        for stock in self.stocks.values():
            stock.update_financials()
        self.market_return = random.gauss(0.0, 0.08)
        for stock in self.stocks.values():
            stock.update_price(self.market_return, annual=True)
            start_price = starting_prices[stock.ticker]
            stock.annual_returns.append(round((stock.price / start_price - 1.0) * 100.0, 2))
            stock.price_history.append((player.year, stock.price))
        logger.info("Market completed annual update for year %s", player.year)
        self.market_return = 0.0

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

            logger.info("Bought %s shares of %s at %.2f", shares, ticker, stock.price)

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
        company_value = player.company.value() if player.company else 0
        return player.bank + self.portfolio_value(player) + company_value
