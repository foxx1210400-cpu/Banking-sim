class Product:
    def __init__(self, name, sale_price, unit_cost, base_demand=100):
        self.name = name
        self.sale_price = sale_price
        self.unit_cost = unit_cost
        self.base_demand = base_demand


class Company:
    def __init__(self, name, sector):
        self.name = name
        self.sector = sector
        self.cash = 0
        self.revenue = 0
        self.expenses = 0
        self.debt = 0
        self.capital_invested = 0
        self.products = []

    def invest(self, amount):
        if amount <= 0:
            return "Investment must be greater than zero."

        self.cash += amount
        self.capital_invested += amount
        return f"Invested ${amount:,.2f} into {self.name}."

    def create_product(self, name, sale_price, unit_cost):
        if not name.strip():
            return "Product needs a name."

        if sale_price <= 0 or unit_cost < 0:
            return "Price and cost must be valid."

        product = Product(name, sale_price, unit_cost)
        self.products.append(product)
        return f"{name} was created."

    def run_month(self):
        total_revenue = 0
        total_costs = 0

        for product in self.products:
            # Temporary demand rule: higher prices mean fewer sales.
            price_factor = max(0.25, min(1.75, 10 / product.sale_price))
            units_sold = int(product.base_demand * price_factor)

            total_revenue += units_sold * product.sale_price
            total_costs += units_sold * product.unit_cost

        profit = total_revenue - total_costs
        self.cash += profit
        self.revenue += total_revenue
        self.expenses += total_costs

        return profit

    def value(self):
        return max(self.cash - self.debt, 0)