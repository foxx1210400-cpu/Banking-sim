from __future__ import annotations


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def calculate_effective_demand(product):
    demand_score = clamp(product.base_demand / 10.0, 0.1, 1.0)
    competition_penalty = product.competition * 0.1
    effective_demand = demand_score - competition_penalty
    return clamp(effective_demand, 0.05, 1.0)


def calculate_product_month(product, planned_production=None):
    if planned_production is None:
        planned_production = getattr(product, "production_target", 0)

    planned_production = max(0, int(planned_production))
    current_inventory = getattr(product, "inventory", 0)

    inventory_before_sale = current_inventory + planned_production
    effective_demand = calculate_effective_demand(product)
    demand_limit = max(0, planned_production * effective_demand)
    available_inventory = max(0, inventory_before_sale)
    units_sold = min(available_inventory, int(demand_limit))
    units_unsold = max(0, available_inventory - units_sold)

    total_revenue = units_sold * product.sale_price
    total_manufacturing_cost = planned_production * product.manufacturing_cost
    product_profit = units_sold * (product.sale_price - product.manufacturing_cost)

    return {
        "units_sold": units_sold,
        "units_unsold": units_unsold,
        "inventory": units_unsold,
        "revenue": total_revenue,
        "manufacturing_cost": total_manufacturing_cost,
        "product_profit": product_profit,
        "market_share": clamp((units_sold / max(planned_production, 1)) if planned_production > 0 else 0.0, 0.0, 1.0),
        "demand_limit": int(demand_limit),
    }


def simulate_company_month(company):
    total_revenue = 0.0
    total_expenses = 0.0
    total_product_profit = 0.0
    total_units_sold = 0
    total_units_unsold = 0
    total_inventory = 0

    for product in company.products:
        metrics = calculate_product_month(product)

        product.units_sold = metrics["units_sold"]
        product.units_unsold = metrics["units_unsold"]
        product.inventory = metrics["inventory"]
        product.monthly_revenue = metrics["revenue"]
        product.monthly_cost = metrics["manufacturing_cost"]
        product.monthly_profit = metrics["product_profit"]
        product.market_share = metrics["market_share"]

        total_revenue += metrics["revenue"]
        total_expenses += metrics["manufacturing_cost"]
        total_product_profit += metrics["product_profit"]
        total_units_sold += metrics["units_sold"]
        total_units_unsold += metrics["units_unsold"]
        total_inventory += metrics["inventory"]

    company.revenue = total_revenue
    company.expenses = total_expenses
    company.net_income = total_revenue - total_expenses
    company.cash += company.net_income

    company.total_revenue += total_revenue
    company.total_expenses += total_expenses
    company.total_net_income = company.total_revenue - company.total_expenses
    company.total_units_sold = getattr(company, "total_units_sold", 0) + total_units_sold
    company.total_units_unsold = getattr(company, "total_units_unsold", 0) + total_units_unsold
    company.total_inventory = total_inventory

    return {
        "revenue": total_revenue,
        "expenses": total_expenses,
        "net_income": company.net_income,
        "product_profit": total_product_profit,
        "units_sold": total_units_sold,
        "units_unsold": total_units_unsold,
        "inventory": total_inventory,
    }
