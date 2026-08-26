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

    def update_price(self):
        # random daily movement
        daily_move = random.uniform(-self.volatility, self.volatility)

        # apply trend + randomness
        self.price += self.price * (self.trend + daily_move)

        # round for display
        self.price = max(round(self.price, 2), 0.01)
