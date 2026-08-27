from __future__ import annotations

import random
from config import (
    EMPLOYEE_ANNUAL_COST,
    EMPLOYEES_PER_FACTORY,
    EMPLOYEES_PER_PRODUCT,
    FACTORY_ANNUAL_MAINTENANCE,
    MARKETING_EFFECT_CAP,
    MARKETING_EFFECT_SCALE,
    OPERATING_EXPENSE_RATE,
    PRICE_ELASTICITY,
    TAX_RATE,
)
from logger import logger


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

    marketing_effect = min(
        MARKETING_EFFECT_CAP,
        product.marketing_budget / (product.marketing_budget + MARKETING_EFFECT_SCALE),
    )
    reputation_effect = 1.0 + getattr(product, "company_reputation", 0.0) / 200.0
    loyalty_effect = 1.0 + getattr(product, "customer_loyalty", 10.0) / 250.0
    demand_factor = clamp(
        (product.base_demand / 10.0)
        * (1.0 / (1.0 + product.competition * 0.15))
        * calculate_price_factor(product)
        * (1.0 + marketing_effect)
        * reputation_effect
        * loyalty_effect
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
        "marketing_effect": marketing_effect,
    }


def simulate_company_year(company):
    total_revenue = 0.0
    total_manufacturing_cost = 0.0
    total_units_sold = 0
    total_units_unsold = 0
    total_inventory = 0
    total_marketing = 0.0
    remaining_capacity = max(0, int(getattr(company, "production_capacity", 0)))

    for product in company.products:
        product.company_reputation = getattr(company, "reputation", 0.0)
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
        total_marketing += max(0.0, float(getattr(product, "marketing_budget", 0.0)))

        sell_through = metrics["units_sold"] / max(metrics["units_sold"] + metrics["units_unsold"], 1)
        loyalty_change = (sell_through - 0.5) * 12.0 + metrics["marketing_effect"] * 4.0
        product.customer_loyalty = clamp(getattr(product, "customer_loyalty", 10.0) + loyalty_change, 0.0, 100.0)

    employee_count = max(
        1,
        company.factory_count * EMPLOYEES_PER_FACTORY + len(company.products) * EMPLOYEES_PER_PRODUCT,
    )
    employee_cost = employee_count * EMPLOYEE_ANNUAL_COST
    factory_maintenance = company.factory_count * getattr(company, "factory_maintenance", FACTORY_ANNUAL_MAINTENANCE)
    operating_expenses = total_revenue * OPERATING_EXPENSE_RATE
    pre_tax_profit = total_revenue - total_manufacturing_cost - operating_expenses - total_marketing - employee_cost - factory_maintenance
    taxes = max(pre_tax_profit, 0.0) * TAX_RATE
    net_income = pre_tax_profit - taxes
    total_expenses = total_manufacturing_cost + operating_expenses + total_marketing + employee_cost + factory_maintenance + taxes

    average_sell_through = total_units_sold / max(total_units_sold + total_units_unsold, 1)
    reputation_change = clamp((average_sell_through - 0.5) * 8.0 + min(total_marketing / MARKETING_EFFECT_SCALE, 3.0), -5.0, 5.0)
    company.reputation = clamp(getattr(company, "reputation", 10.0) + reputation_change, 0.0, 100.0)

    company.revenue = total_revenue
    company.expenses = total_expenses
    company.operating_expenses = operating_expenses
    company.taxes = taxes
    company.marketing_expenses = total_marketing
    company.employee_count = employee_count
    company.employee_expenses = employee_cost
    company.factory_maintenance = factory_maintenance
    company.net_income = net_income
    company.cash += net_income
    company.total_revenue += total_revenue
    company.total_expenses += total_expenses
    company.total_net_income = company.total_revenue - company.total_expenses
    company.total_units_sold = getattr(company, "total_units_sold", 0) + total_units_sold
    company.total_units_unsold = getattr(company, "total_units_unsold", 0) + total_units_unsold
    company.total_inventory = total_inventory
    logger.info("Company %s annual simulation: revenue=%.2f net_income=%.2f", company.name, total_revenue, net_income)

    return {
        "revenue": total_revenue,
        "manufacturing_cost": total_manufacturing_cost,
        "operating_expenses": operating_expenses,
        "marketing_expenses": total_marketing,
        "employee_expenses": employee_cost,
        "factory_maintenance": factory_maintenance,
        "employee_count": employee_count,
        "reputation": company.reputation,
        "taxes": taxes,
        "expenses": total_expenses,
        "pre_tax_profit": pre_tax_profit,
        "net_income": net_income,
        "units_sold": total_units_sold,
        "units_unsold": total_units_unsold,
        "inventory": total_inventory,
    }
