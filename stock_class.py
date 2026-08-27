# ============================================================
# STOCK SYSTEM TODO (Future Features)
# ------------------------------------------------------------
# 1. Daily News System
#    - Random events affecting individual stocks or sectors
#    - Positive/negative headlines that shift daily volatility
#
# 2. Sector-Based Movement
#    - Group stocks into sectors (Tech, Energy, Food, AI, etc.)
#    - Sector-wide booms, crashes, and trend adjustments
#
# 3. Earnings Reports
#    - Quarterly performance updates (every ~90 days)
#    - Revenue, profit, guidance → major price jumps/drops
#
# 4. Market Crashes
#    - Rare global events causing large negative movement
#    - Panic selling, high volatility, multi-day downturns
#
# 5. Bankruptcy + IPO Replacement
#    - If price falls below threshold → company collapses
#    - Remove stock, wipe portfolios, introduce new IPO
#
# 6. Economic Cycles
#    - Long-term market phases (boom, recession, recovery)
#    - Trend adjustments across all stocks over time
#
# ============================================================







import random
import math

MAX_REVENUE = 1_000_000_000_000
MIN_REVENUE = 1_000_000

class Stock:
    def __init__(
        self,
        ticker,
        name,
        price,
        trend,
        volatility,
        sector="Unknown",
        revenue=0,
        profit=0,
        debt=0,
        growth_rate=0.0,
    ):
        self.ticker = ticker
        self.name = name
        self.price = price 
        self.price = max(self.price, 0.01) # Realism fix so stock prices dont go negitve but kinda unrealistic at the same time because stock prices dont go lower than 1 cent
        self.trend = trend        # long-term drift
        self.volatility = volatility  # daily randomness
        self.sector = sector
        self.revenue = revenue
        self.profit = profit
        self.debt = debt
        self.growth_rate = growth_rate
        self.starting_revenue = revenue
        self.starting_profit = profit
        self.starting_debt = debt
        self.performance = 0.0
        self.randomize_starting_financials()

    def randomize_starting_financials(self):
        """Give each stock its own plausible starting financial profile."""
        self.revenue = max(self.starting_revenue * random.uniform(0.8, 1.2), 1.0)
        self.profit = self.starting_profit * random.uniform(0.75, 1.25)
        self.debt = max(self.starting_debt * random.uniform(0.8, 1.2), 0.0)
        self.growth_rate = max(self.growth_rate * random.uniform(0.75, 1.25), -0.20)
        self.performance = self.calculate_performance()

    def calculate_performance(self):
        profit_margin = self.profit / max(self.revenue, 1.0)
        debt_ratio = self.debt / max(self.revenue, 1.0)
        profit_score = max(-0.10, min(0.10, profit_margin - 0.08))
        debt_penalty = max(-0.10, min(0.0, -debt_ratio * 0.05))
        growth_score = max(-0.10, min(0.10, (self.growth_rate - 0.06) * 0.5))
        return profit_score + debt_penalty + growth_score

    def update_financials(self):
        """Apply one year of company-specific financial performance."""
        revenue_change = max(-0.25, min(0.25, self.growth_rate + random.gauss(0.0, 0.03)))
        self.revenue = max(min(self.revenue * (1.0 + revenue_change), MAX_REVENUE), MIN_REVENUE)
        margin = self.profit / max(self.revenue / (1.0 + revenue_change), 1.0)
        margin += random.gauss(0.0, 0.01)
        margin = max(-0.25, min(0.35, margin))
        self.profit = self.revenue * margin
        self.debt = max(self.debt * (1.0 + random.gauss(0.0, 0.04)), 0.0)
        self.performance = self.calculate_performance()

    def update_price(self, market_return=0.0, annual=False):
        volatility = self.volatility * 8.0 if annual else self.volatility / 12.0
        random_move = random.gauss(0.0, volatility)

        annual_return = (self.trend * 5.0) + (self.performance * 0.5)
        period_return = annual_return + market_return if annual else (annual_return + market_return) / 365.0
        self.price *= math.exp(period_return + random_move - (volatility ** 2) / 2.0)

        # round for display
        self.price = max(round(self.price, 2), 0.01)
