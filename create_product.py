import json
from functools import lru_cache
from pathlib import Path

from logger import logger


RESEARCH_COST_MULTIPLIER = 0.2


class Product:
    def __init__(
        self,
        name,
        sale_price,
        unit_cost,
        base_demand=5,
        sector="Unknown",
        manufacturing_cost=None,
        research_cost=0,
        researched=False,
        competition=5,
    ):
        if not name or not str(name).strip():
            raise ValueError("Product name cannot be empty.")
        if sale_price <= 0:
            raise ValueError("Sale price must be greater than zero.")
        if unit_cost < 0:
            raise ValueError("Unit cost cannot be negative.")
        if not 1 <= int(base_demand) <= 10:
            raise ValueError("Demand must be between 1 and 10.")
        if not 1 <= int(competition) <= 10:
            raise ValueError("Competition must be between 1 and 10.")

        self.name = str(name).strip()
        self.sale_price = sale_price
        self.unit_cost = unit_cost
        self.base_demand = int(base_demand)
        self.sector = sector
        self.manufacturing_cost = unit_cost if manufacturing_cost is None else manufacturing_cost
        self.research_cost = research_cost
        self.researched = researched
        self.competition = int(competition)
        self.annual_production_quota = 0
        self.inventory = 0
        self.units_sold = 0
        self.units_unsold = 0
        self.annual_revenue = 0.0
        self.annual_cost = 0.0
        self.annual_profit = 0.0
        self.market_share = 0.0

    @classmethod
    def from_json(cls, data):
        manufacturing_cost = data.get("manufacturing_cost", data.get("unit_cost", 0))
        unit_cost = data.get("unit_cost", manufacturing_cost)
        sale_price = data.get("sale_price")
        if sale_price is None:
            sale_price = max(float(manufacturing_cost) * 1.75, 1.0)

        research_cost = data.get("research_cost", 0)
        if research_cost:
            research_cost = int(round(float(research_cost) * RESEARCH_COST_MULTIPLIER))
            if research_cost < 2500:
                research_cost = 2500

        demand = data.get("demand", data.get("base_demand", 5))
        competition = data.get("competition", 5)

        return cls(
            name=data.get("name"),
            sale_price=float(sale_price),
            unit_cost=float(unit_cost),
            base_demand=demand,
            sector=data.get("sector", "Unknown"),
            manufacturing_cost=float(manufacturing_cost),
            research_cost=research_cost,
            researched=False,
            competition=competition,
        )

    def research(self, company_cash):
        if self.researched:
            return f"{self.name} has already been researched."
        if company_cash < self.research_cost:
            return f"You need ${self.research_cost:,.2f} to research {self.name}."
        self.researched = True
        return f"{self.name} is now researched. Demand and manufacturing cost are unlocked."

    def summary(self):
        if self.researched:
            return (
                f"Research complete | Demand: {self.base_demand}/10 | "
                f"Competition: {self.competition}/10 | "
                f"Manufacturing cost: ${self.manufacturing_cost:,.2f}"
            )
        return f"Research cost: ${self.research_cost:,.2f} | Hidden market stats until researched"

    def set_year_plan(self, production_quota, sale_price=None):
        self.annual_production_quota = max(0, int(production_quota))
        if sale_price is not None:
            self.sale_price = max(float(sale_price), 1.0)
        return self.annual_production_quota

    def product_status(self):
        return {
            "name": self.name,
            "sale_price": self.sale_price,
            "annual_production_quota": self.annual_production_quota,
            "inventory": self.inventory,
            "units_sold": self.units_sold,
            "units_unsold": self.units_unsold,
            "annual_revenue": self.annual_revenue,
            "annual_cost": self.annual_cost,
            "annual_profit": self.annual_profit,
            "market_share": self.market_share,
        }

    @staticmethod
    @lru_cache(maxsize=4)
    def load_catalog(path="company_products.json"):
        data_file = Path(path)
        if not data_file.exists():
            return {}

        with data_file.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        catalog = {}
        for sector, entries in payload.get("products", {}).items():
            try:
                catalog[sector] = [Product.from_json(entry) for entry in entries]
            except (KeyError, TypeError, ValueError) as exc:
                logger.warning("Skipping invalid products in sector %s: %s", sector, exc)
                catalog[sector] = []
        return catalog

    def to_dict(self):
        return {
            "name": self.name,
            "sector": self.sector,
            "demand": self.base_demand,
            "competition": self.competition,
            "manufacturing_cost": self.manufacturing_cost,
            "research_cost": self.research_cost,
            "sale_price": self.sale_price,
            "unit_cost": self.unit_cost,
        }

    def __repr__(self):
        return (
            f"Product(name={self.name!r}, sector={self.sector!r}, sale_price={self.sale_price}, "
            f"unit_cost={self.unit_cost}, demand={self.base_demand}, competition={self.competition})"
        )


class ProductCreator:
    @staticmethod
    def create(name, sale_price, unit_cost, base_demand=5, sector="Unknown", manufacturing_cost=None, research_cost=0, competition=5):
        return Product(
            name=name,
            sale_price=sale_price,
            unit_cost=unit_cost,
            base_demand=base_demand,
            sector=sector,
            manufacturing_cost=manufacturing_cost,
            research_cost=research_cost,
            competition=competition,
        )

    @staticmethod
    def load_catalog(path="company_products.json"):
        return Product.load_catalog(path)

    @staticmethod
    def load_sector_products(sector, path="company_products.json"):
        catalog = Product.load_catalog(path)
        return catalog.get(sector, [])
