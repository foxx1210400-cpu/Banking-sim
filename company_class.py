from create_product import ProductCreator
from company_logic import simulate_company_month


class Company:
    def __init__(self, name, sector):
        self.name = name
        self.sector = sector
        self.cash = 0
        self.revenue = 0
        self.expenses = 0
        self.net_income = 0
        self.debt = 0
        self.capital_invested = 0
        self.total_revenue = 0
        self.total_expenses = 0
        self.total_net_income = 0
        self.total_units_sold = 0
        self.total_units_unsold = 0
        self.total_inventory = 0
        self.products = []

    def invest(self, amount):
        if amount <= 0:
            return "Investment must be greater than zero."

        self.cash += amount
        self.capital_invested += amount
        return f"Invested ${amount:,.2f} into {self.name}."

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

    def run_month(self):
        summary = simulate_company_month(self)
        self.net_income = summary["net_income"]
        return summary["net_income"]

    def get_financial_summary(self):
        return {
            "cash": self.cash,
            "revenue": self.revenue,
            "expenses": self.expenses,
            "net_income": self.net_income,
            "debt": self.debt,
            "capital_invested": self.capital_invested,
            "lifetime_revenue": self.total_revenue,
            "lifetime_expenses": self.total_expenses,
            "lifetime_net_income": self.total_net_income,
            "total_units_sold": self.total_units_sold,
            "total_units_unsold": self.total_units_unsold,
            "total_inventory": self.total_inventory,
        }

    def value(self):
        return max(self.cash - self.debt, 0)