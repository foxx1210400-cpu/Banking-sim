from __future__ import annotations

import random

TAX_RATE = 0.20
OPERATING_EXPENSE_RATE = 0.05
PRICE_ELASTICITY = 1.10


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def calculate_effective_demand(product):
    demand_score = clamp(product.base_demand / 10.0, 0.1, 1.0)
    competition_penalty = product.competition * 0.1
    effective_demand = demand_score - competition_penalty
    return clamp(effective_demand, 0.05, 1.0)


def calculate_price_factor(product):
    reference_price = max(product.manufacturing_cost * 2.0, 1.0)
    price_ratio = reference_price / max(product.sale_price, 1.0)
    return clamp(price_ratio ** PRICE_ELASTICITY, 0.05, 1.5)


def calculate_product_year(product, planned_production, noise=None):
    planned_production = max(0, int(planned_production))
    current_inventory = max(0, int(getattr(product, "inventory", 0)))
    available_inventory = current_inventory + planned_production
    if noise is None:
        noise = clamp(random.gauss(1.0, 0.03), 0.9, 1.1)

    demand_factor = clamp(
        (product.base_demand / 10.0)
        * (1.0 / (1.0 + product.competition * 0.15))
        * calculate_price_factor(product)
        * noise,
        0.0,
        1.0,
    )
    demand_limit = int(available_inventory * demand_factor)
    units_sold = min(available_inventory, demand_limit)
    units_unsold = max(0, available_inventory - units_sold)
    revenue = units_sold * product.sale_price
    manufacturing_cost = planned_production * product.manufacturing_cost

    return {
        "units_sold": units_sold,
        "units_unsold": units_unsold,
        "inventory": units_unsold,
        "revenue": revenue,
        "manufacturing_cost": manufacturing_cost,
        "demand_limit": demand_limit,
        "price_factor": calculate_price_factor(product),
    }


def simulate_company_year(company):
    total_revenue = 0.0
    total_manufacturing_cost = 0.0
    total_units_sold = 0
    total_units_unsold = 0
    total_inventory = 0
    remaining_capacity = max(0, int(getattr(company, "production_capacity", 0))) * 12

    for product in company.products:
        planned_production = min(
            max(0, int(getattr(product, "annual_production_quota", 0))),
            remaining_capacity,
        )
        remaining_capacity -= planned_production
        metrics = calculate_product_year(product, planned_production)

        product.units_sold = metrics["units_sold"]
        product.units_unsold = metrics["units_unsold"]
        product.inventory = metrics["inventory"]
        product.annual_revenue = metrics["revenue"]
        product.annual_cost = metrics["manufacturing_cost"]
        product.annual_profit = metrics["revenue"] - metrics["manufacturing_cost"]
        product.market_share = clamp(
            metrics["units_sold"] / max(planned_production, 1),
            0.0,
            1.0,
        )

        total_revenue += metrics["revenue"]
        total_manufacturing_cost += metrics["manufacturing_cost"]
        total_units_sold += metrics["units_sold"]
        total_units_unsold += metrics["units_unsold"]
        total_inventory += metrics["inventory"]

    operating_expenses = total_revenue * OPERATING_EXPENSE_RATE
    pre_tax_profit = total_revenue - total_manufacturing_cost - operating_expenses
    taxes = max(pre_tax_profit, 0.0) * TAX_RATE
    net_income = pre_tax_profit - taxes
    total_expenses = total_manufacturing_cost + operating_expenses + taxes

    company.revenue = total_revenue
    company.expenses = total_expenses
    company.operating_expenses = operating_expenses
    company.taxes = taxes
    company.net_income = net_income
    company.cash += net_income
    company.total_revenue += total_revenue
    company.total_expenses += total_expenses
    company.total_net_income = company.total_revenue - company.total_expenses
    company.total_units_sold = getattr(company, "total_units_sold", 0) + total_units_sold
    company.total_units_unsold = getattr(company, "total_units_unsold", 0) + total_units_unsold
    company.total_inventory = total_inventory

    return {
        "revenue": total_revenue,
        "manufacturing_cost": total_manufacturing_cost,
        "operating_expenses": operating_expenses,
        "taxes": taxes,
        "expenses": total_expenses,
        "pre_tax_profit": pre_tax_profit,
        "net_income": net_income,
        "units_sold": total_units_sold,
        "units_unsold": total_units_unsold,
        "inventory": total_inventory,
    }
