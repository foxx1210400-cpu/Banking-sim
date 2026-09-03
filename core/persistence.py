import json
from pathlib import Path

from .company_class import Company
from .create_product import Product
from .player_class import Player
from .stock_class import Stock


def _product_to_dict(product):
    return {
        "name": product.name,
        "sale_price": product.sale_price,
        "unit_cost": product.unit_cost,
        "base_demand": product.base_demand,
        "sector": product.sector,
        "manufacturing_cost": product.manufacturing_cost,
        "research_cost": product.research_cost,
        "researched": product.researched,
        "competition": product.competition,
        "annual_production_quota": product.annual_production_quota,
        "inventory": product.inventory,
        "units_sold": product.units_sold,
        "units_unsold": product.units_unsold,
        "annual_revenue": product.annual_revenue,
        "annual_cost": product.annual_cost,
        "annual_profit": product.annual_profit,
        "market_share": product.market_share,
        "marketing_budget": product.marketing_budget,
        "customer_loyalty": product.customer_loyalty,
    }


def _company_to_dict(company):
    return {
        "name": company.name,
        "sector": company.sector,
        "cash": company.cash,
        "revenue": company.revenue,
        "expenses": company.expenses,
        "operating_expenses": company.operating_expenses,
        "taxes": company.taxes,
        "net_income": company.net_income,
        "debt": company.debt,
        "capital_invested": company.capital_invested,
        "total_revenue": company.total_revenue,
        "total_expenses": company.total_expenses,
        "total_net_income": company.total_net_income,
        "total_units_sold": company.total_units_sold,
        "total_units_unsold": company.total_units_unsold,
        "total_inventory": company.total_inventory,
        "factory_count": company.factory_count,
        "factory_capacity": company.factory_capacity,
        "employee_count": company.employee_count,
        "reputation": company.reputation,
        "factory_maintenance": company.factory_maintenance,
        "bankrupt": company.bankrupt,
        "products": [_product_to_dict(product) for product in company.products],
    }


def _stock_to_dict(stock):
    return {
        "ticker": stock.ticker,
        "name": stock.name,
        "price": stock.price,
        "trend": stock.trend,
        "volatility": stock.volatility,
        "sector": stock.sector,
        "revenue": stock.revenue,
        "profit": stock.profit,
        "debt": stock.debt,
        "growth_rate": stock.growth_rate,
        "price_history": stock.price_history,
        "annual_returns": stock.annual_returns,
    }


def save_game(player, market, filename: str | Path = "savegame.json"):
    data = {
        "version": 1,
        "player": {
            "bank": player.bank,
            "age": player.age,
            "health": player.health,
            "happiness": player.happiness,
            "smarts": player.smarts,
            "relationships": player.relationships,
            "event_history": player.event_history,
            "year": player.year,
            "month": player.month,
            "day": player.day,
            "portfolio": player.portfolio,
            "company": _company_to_dict(player.company) if player.company else None,
        },
        "stocks": {ticker: _stock_to_dict(stock) for ticker, stock in market.stocks.items()},
    }
    Path(filename).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_game(filename: str | Path = "savegame.json"):
    data = json.loads(Path(filename).read_text(encoding="utf-8"))
    player_data = data["player"]
    player = Player()
    for field in ("bank", "age", "health", "happiness", "smarts", "relationships", "event_history", "year", "month", "day", "portfolio"):
        if field in player_data:
            setattr(player, field, player_data[field])
    if "age" not in player_data:
        player.age = max(1, player.year - 1999)

    company_data = player_data.get("company")
    if company_data:
        company = Company(company_data["name"], company_data["sector"])
        for field in company_data:
            if field not in {"products", "last_year_run"}:
                setattr(company, field, company_data[field])
        company.production_capacity = company.factory_count * company.factory_capacity
        company.last_year_run = None
        company.last_year_summary = None
        for item in company_data.get("products", []):
            product = Product(
                item["name"], item["sale_price"], item["unit_cost"], item["base_demand"],
                item["sector"], item["manufacturing_cost"], item["research_cost"],
                item["researched"], item["competition"],
            )
            for field in item:
                if hasattr(product, field):
                    setattr(product, field, item[field])
            company.products.append(product)
        player.company = company

    from .stock_market import StockMarket
    market = StockMarket()
    for ticker, item in data.get("stocks", {}).items():
        if ticker not in market.stocks:
            continue
        stock = market.stocks[ticker]
        for field in ("price", "revenue", "profit", "debt", "growth_rate", "trend", "volatility"):
            if field in item:
                setattr(stock, field, item[field])
        stock.price_history = item.get("price_history", stock.price_history)
        stock.annual_returns = item.get("annual_returns", stock.annual_returns)
        stock.performance = stock.calculate_performance()
    return player, market
