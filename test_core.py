import random
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from company_class import Company
from create_product import Product
from persistence import load_game, save_game
from player_class import Player
from stock_market import StockMarket


class CoreGameTests(unittest.TestCase):
    def test_stock_purchase_keeps_exact_share_count(self):
        player = Player()
        player.bank = 10000
        market = StockMarket()
        ticker = next(iter(market.stocks))
        market.buy_stock(player, ticker, 3)
        self.assertEqual(player.portfolio[ticker]["shares"], 3)

    def test_player_uses_one_bank_balance(self):
        player = Player()
        self.assertFalse(hasattr(player, "cash"))
        self.assertEqual(player.bank, 100000.0)

    def test_annual_run_is_idempotent_for_same_year(self):
        random.seed(7)
        company = Company("Test Co", "Food")
        company.cash = 100000
        product = Product("Widget", 100, 10, base_demand=8, competition=1)
        product.annual_production_quota = 100
        company.products.append(product)
        first = company.run_year(2000)
        cash_after_first = company.cash
        second = company.run_year(2000)
        self.assertEqual(first, second)
        self.assertEqual(company.cash, cash_after_first)

    def test_save_load_preserves_player_state(self):
        player = Player()
        player.bank = 5000
        player.year = 2005
        market = StockMarket()
        with TemporaryDirectory() as folder:
            path = Path(folder) / "save.json"
            save_game(player, market, path)
            loaded_player, _ = load_game(path)
        self.assertEqual(loaded_player.bank, 5000)
        self.assertEqual(loaded_player.year, 2005)

    def test_inventory_can_sell_without_new_production(self):
        random.seed(3)
        company = Company("Inventory Co", "Food")
        company.cash = 100000
        product = Product("Widget", 100, 10, base_demand=8, competition=1)
        product.inventory = 1000
        company.products.append(product)
        summary = company.run_year(2000)
        self.assertGreater(summary["units_sold"], 0)
        self.assertEqual(summary["manufacturing_cost"], 0)

    def test_annual_quota_respects_capacity(self):
        company = Company("Capacity Co", "Food")
        company.cash = 100000
        product = Product("Widget", 100, 10, base_demand=8, competition=1)
        product.annual_production_quota = company.production_capacity + 1
        company.products.append(product)
        summary = company.run_year(2000)
        self.assertLessEqual(summary["manufacturing_cost"], company.production_capacity * product.manufacturing_cost)

    def test_bankruptcy_after_annual_loss(self):
        company = Company("Loss Co", "Food")
        company.cash = 1
        product = Product("Failure", 1, 100, base_demand=5, competition=5)
        product.annual_production_quota = 100
        company.products.append(product)
        company.run_year(2000)
        self.assertTrue(company.bankrupt)

    def test_annual_financial_formula(self):
        company = Company("Formula Co", "Food")
        company.cash = 1000000
        product = Product("Widget", 20, 10, base_demand=10, competition=1)
        product.annual_production_quota = 100
        company.products.append(product)
        summary = company.run_year(2000)
        expected_manufacturing = 100 * 10
        expected_operating = summary["revenue"] * 0.05
        expected_employee = 15 * 30000
        expected_factory = 1 * 15000
        expected_pre_tax = summary["revenue"] - expected_manufacturing - expected_operating - expected_employee - expected_factory
        expected_taxes = max(expected_pre_tax, 0) * 0.20
        self.assertEqual(summary["manufacturing_cost"], expected_manufacturing)
        self.assertAlmostEqual(summary["operating_expenses"], expected_operating)
        self.assertEqual(summary["employee_expenses"], expected_employee)
        self.assertEqual(summary["factory_maintenance"], expected_factory)
        self.assertAlmostEqual(summary["taxes"], expected_taxes)
        self.assertAlmostEqual(summary["net_income"], expected_pre_tax - expected_taxes)

    def test_later_product_inventory_sells_when_capacity_is_used(self):
        company = Company("Inventory Co", "Food")
        company.cash = 100000
        first = Product("First", 100, 10, base_demand=10, competition=1)
        first.annual_production_quota = company.production_capacity
        second = Product("Second", 100, 10, base_demand=10, competition=1)
        second.inventory = 1000
        company.products.extend((first, second))
        summary = company.run_year(2000)
        self.assertGreater(second.units_sold, 0)
        self.assertGreater(summary["units_sold"], second.units_sold)

    def test_marketing_increases_demand_and_is_expensed(self):
        company = Company("Marketing Co", "Food")
        company.cash = 1000000
        product = Product("Widget", 20, 10, base_demand=8, competition=1)
        product.annual_production_quota = 1000
        product.marketing_budget = 10000
        company.products.append(product)
        summary = company.run_year(2000)
        self.assertEqual(summary["marketing_expenses"], 10000)
        self.assertGreater(product.customer_loyalty, 10)
        self.assertGreater(company.reputation, 10)

    def test_stock_transactions_apply_tax(self):
        player = Player()
        market = StockMarket()
        ticker = next(iter(market.stocks))
        stock = market.stocks[ticker]
        player.bank = stock.price * 3 * 1.01
        market.buy_stock(player, ticker, 3)
        self.assertAlmostEqual(player.bank, 0)
        proceeds = stock.price * 3 * 0.99
        market.sell_stock(player, ticker, 3)
        self.assertAlmostEqual(player.bank, proceeds)


if __name__ == "__main__":
    unittest.main()
