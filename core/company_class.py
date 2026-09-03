from typing import Any

from .create_product import ProductCreator
from .company_logic import simulate_company_year
from .config import (
    EMPLOYEES_PER_FACTORY,
    EMPLOYEES_PER_PRODUCT,
    FACTORY_ANNUAL_MAINTENANCE,
    FACTORY_CAPACITY,
    FACTORY_COST,
)
from .logger import logger


class Company:
    def __init__(self, name, sector):
        self.name = name
        self.sector = sector
        self.cash = 0
        self.revenue = 0
        self.expenses = 0
        self.operating_expenses = 0
        self.taxes = 0
        self.net_income = 0
        self.debt = 0
        self.capital_invested = 0
        self.total_revenue = 0
        self.total_expenses = 0
        self.total_net_income = 0
        self.total_units_sold = 0
        self.total_units_unsold = 0
        self.total_inventory = 0
        self.factory_count = 1
        self.factory_capacity = FACTORY_CAPACITY
        self.production_capacity = self.factory_capacity
        self.factory_cost = FACTORY_COST
        self.bankrupt = False
        self.reputation = 10.0
        self.factory_maintenance = FACTORY_ANNUAL_MAINTENANCE
        self.marketing_expenses = 0.0
        self.employee_count = EMPLOYEES_PER_FACTORY
        self.employee_expenses = 0.0
        self.last_year_run = None
        self.last_year_summary: dict[str, Any] | None = None
        self.products = []

    def invest(self, amount):
        if amount <= 0:
            return "Investment must be greater than zero."

        self.cash += amount
        self.capital_invested += amount
        return f"Invested ${amount:,.2f} into {self.name}."

    def buy_factory(self):
        if self.bankrupt:
            return "This company is bankrupt."
        if self.cash < self.factory_cost:
            return f"You need ${self.factory_cost:,.2f} to buy a factory."

        self.cash -= self.factory_cost
        self.factory_count += 1
        self.production_capacity = self.factory_count * self.factory_capacity
        logger.info("Factory purchased for %s; capacity=%s", self.name, self.production_capacity)
        return f"Factory purchased. Production capacity is now {self.production_capacity:,} units."

    @property
    def required_employee_count(self):
        return max(
            1,
            self.factory_count * EMPLOYEES_PER_FACTORY
            + len(self.products) * EMPLOYEES_PER_PRODUCT,
        )

    @property
    def staffing_ratio(self):
        return self.employee_count / self.required_employee_count

    def hire_employees(self, count):
        count = int(count)
        if count <= 0:
            return "Hire count must be greater than zero."
        self.employee_count += count
        return f"Hired {count} employees. Workforce is now {self.employee_count}."

    def fire_employees(self, count):
        count = int(count)
        if count <= 0:
            return "Layoff count must be greater than zero."
        if count > self.employee_count:
            return f"You only employ {self.employee_count} people."
        self.employee_count -= count
        return f"Laid off {count} employees. Workforce is now {self.employee_count}."

    def create_product(self, name, sale_price, unit_cost, base_demand=100, sector=None, manufacturing_cost=None, research_cost=0):
        try:
            product = ProductCreator.create(
                name=name,
                sale_price=sale_price,
                unit_cost=unit_cost,
                base_demand=base_demand,
                sector=sector or self.sector,
                manufacturing_cost=manufacturing_cost,
                research_cost=research_cost,
            )
        except ValueError as exc:
            return str(exc)

        self.products.append(product)
        return f"{product.name} was created."

    def add_product(self, product):
        if product is None:
            return "No product was provided."
        self.products.append(product)
        return f"{product.name} was added."

    def research_and_launch(self, product):
        if product is None:
            return "No product was provided."
        if any(existing.name == product.name for existing in self.products):
            return f"{product.name} is already in your lineup."
        if self.cash < product.research_cost:
            return f"You need ${product.research_cost:,.2f} to research {product.name}."
        product.researched = True
        self.cash -= product.research_cost
        return self.add_product(product)

    def run_year(self, current_year: int | None = None) -> dict[str, Any]:
        if current_year is not None and self.last_year_run == current_year and self.last_year_summary is not None:
            return self.last_year_summary
        if self.bankrupt:
            return {
                "revenue": 0,
                "expenses": 0,
                "net_income": 0,
                "units_sold": 0,
                "units_unsold": self.total_inventory,
                "inventory": self.total_inventory,
            }
        summary = simulate_company_year(self)
        if self.cash <= 0:
            self.bankrupt = True
        self.last_year_run = current_year
        self.last_year_summary = summary
        logger.info("Company %s completed year %s with net income %.2f", self.name, current_year, summary["net_income"])
        return summary

    def get_financial_summary(self):
        return {
            "cash": self.cash,
            "revenue": self.revenue,
            "expenses": self.expenses,
            "operating_expenses": self.operating_expenses,
            "taxes": self.taxes,
            "net_income": self.net_income,
            "debt": self.debt,
            "capital_invested": self.capital_invested,
            "lifetime_revenue": self.total_revenue,
            "lifetime_expenses": self.total_expenses,
            "lifetime_net_income": self.total_net_income,
            "total_units_sold": self.total_units_sold,
            "total_units_unsold": self.total_units_unsold,
            "total_inventory": self.total_inventory,
            "factory_count": self.factory_count,
            "production_capacity": self.production_capacity,
            "bankrupt": self.bankrupt,
            "reputation": self.reputation,
            "marketing_expenses": self.marketing_expenses,
            "employee_count": self.employee_count,
            "required_employee_count": self.required_employee_count,
            "staffing_ratio": self.staffing_ratio,
            "employee_expenses": self.employee_expenses,
            "factory_maintenance": self.factory_maintenance,
        }

    def value(self):
        inventory_value = sum(product.inventory * product.manufacturing_cost for product in self.products)
        factory_value = self.factory_count * self.factory_cost
        return max(self.cash + inventory_value + factory_value - self.debt, 0)