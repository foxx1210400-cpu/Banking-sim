from create_product import ProductCreator
from company_logic import simulate_company_year


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
        self.factory_capacity = 50000
        self.production_capacity = self.factory_capacity
        self.factory_cost = 100000
        self.bankrupt = False
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
        return f"Factory purchased. Production capacity is now {self.production_capacity:,} units."

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

    def run_year(self):
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
        }

    def value(self):
        return max(self.cash - self.debt, 0)