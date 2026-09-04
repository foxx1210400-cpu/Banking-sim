import random
import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory

from core.company_class import Company
from core.config import APP_VERSION
from core.competitors import CompetitorRegistry
from core.create_product import Product
from core.events import EventManager
from core.jobs import JobCatalog
from core.persistence import load_game, save_game
from core.player_class import Player
from core.stock_market import StockMarket


class CoreGameTests(unittest.TestCase):
    def test_release_version_is_declared(self):
        self.assertEqual(APP_VERSION, "beta2.0.0")

    def test_understaffing_reduces_capacity_and_payroll_uses_actual_workforce(self):
        company = Company("Lean Co", "Food")
        company.cash = 1_000_000
        product = Product("Widget", 20, 10, base_demand=10, competition=1)
        product.annual_production_quota = company.production_capacity
        company.products.append(product)
        company.fire_employees(8)

        summary = company.run_year(2000)

        self.assertEqual(company.required_employee_count, 15)
        self.assertEqual(summary["employee_count"], 2)
        self.assertEqual(summary["employee_expenses"], 60_000)
        self.assertLess(summary["units_sold"] + summary["units_unsold"], 50_000)

    def test_extra_employees_improve_workforce_efficiency(self):
        company = Company("Growth Co", "Food")
        company.hire_employees(5)

        summary = company.run_year(2000)

        self.assertGreater(summary["workforce_efficiency"], 1.0)

    def test_competitors_are_available_only_for_a_player_company(self):
        player = Player()
        competitors = CompetitorRegistry()
        self.assertEqual(competitors.for_player(player), ())

        player.company = Company("Player Foods", "Food")
        rivals = competitors.for_player(player)

        self.assertTrue(rivals)
        self.assertTrue(all(rival.sector == "Food" for rival in rivals))
        self.assertTrue(all(rival.ticker and rival.stock_price > 0 for rival in rivals))

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
        self.assertEqual(player.bank, 0.0)

    def test_job_salary_is_paid_annually_after_taxes(self):
        player = Player()
        player.age = 14
        player.job = JobCatalog().available_for(14)[0]
        player.advance_year()
        salary = player.job["hourly_wage"] * 2_000
        self.assertEqual(player.last_salary, salary)
        self.assertEqual(player.bank, salary - player.last_taxes)
        self.assertGreaterEqual(player.last_taxes, 0)

    def test_activity_history_records_player_actions(self):
        player = Player()
        player.age = 10
        player.study_harder()
        player.advance_year()
        self.assertTrue(any("Studied harder" in item for item in player.activity_history))
        self.assertTrue(any("Aged up to 11" in item for item in player.activity_history))

    def test_activity_history_persists_through_save_load(self):
        player = Player()
        player.record_activity("Checked the activity feed.")
        with TemporaryDirectory() as folder:
            path = Path(folder) / "save.json"
            save_game(player, StockMarket(), path)
            loaded_player, _ = load_game(path)
        self.assertEqual(loaded_player.activity_history, player.activity_history)

    def test_college_tuition_and_graduation(self):
        player = Player()
        player.age = 18
        player.college_enrolled = True
        for _ in range(4):
            player.advance_year()
        self.assertFalse(player.college_enrolled)
        self.assertEqual(player.college_degree, "Bachelor's Degree")
        self.assertEqual(player.bank, -60_000)

    def test_player_starts_at_age_one_and_ages_with_years(self):
        player = Player()
        self.assertEqual(player.age, 1)
        player.advance_year()
        self.assertEqual(player.age, 2)

    def test_family_is_generated_with_expected_details(self):
        family = Player().family
        self.assertEqual(len(family["parents"]), 2)
        self.assertGreater(family["annual_income"], 0)
        self.assertGreater(family["assets"], 0)
        self.assertIn(family["home"], {"Apartment", "Townhouse", "Family home"})

    def test_jobs_catalog_unlocks_teen_jobs_at_fourteen(self):
        jobs = JobCatalog().available_for(14)
        titles = {job["title"] for job in jobs}
        self.assertIn("Game Tester", titles)
        self.assertIn("Paper Boy", titles)
        self.assertTrue(all(job["hourly_wage"] > 0 for job in jobs))

    def test_school_level_matches_age_range(self):
        player = Player()
        for age, school in ((4, None), (5, "Elementary School"), (10, "Elementary School"), (11, "Middle School"), (13, "Middle School"), (14, "High School"), (18, "High School"), (19, None)):
            player.age = age
            self.assertEqual(player.school_level(), school)

    def test_studying_improves_grades_without_exceeding_maximum(self):
        player = Player()
        player.age = 10
        player.grades = 98
        player.study_harder()
        self.assertEqual(player.grades, 100)
        player.study_harder()
        self.assertEqual(player.grades, 100)

    def test_studying_is_limited_to_once_per_year(self):
        player = Player()
        player.age = 10
        grades_before = player.grades
        self.assertTrue(player.study_harder())
        self.assertFalse(player.study_harder())
        self.assertEqual(player.grades, grades_before + 5)
        player.advance_year()
        self.assertTrue(player.study_harder())

    def test_studying_is_unavailable_outside_school_ages(self):
        player = Player()
        player.age = 4
        grades_before = player.grades
        self.assertFalse(player.study_harder())
        self.assertEqual(player.grades, grades_before)

    def test_events_are_filtered_by_age_and_apply_choice(self):
        manager = EventManager()
        player = Player()
        with patch("core.events.random.random", return_value=0.0):
            event = manager.event_for_age(3)
        self.assertIsNotNone(event)
        assert event is not None
        self.assertTrue(event["age_range"][0] <= 3 <= event["age_range"][1])
        before = {
            "bank": player.bank,
            "health": player.health,
            "happiness": player.happiness,
            "smarts": player.smarts,
            "relationships": player.relationships,
        }
        result = manager.resolve(player, event, 0)
        self.assertEqual(len(player.event_history), 1)
        self.assertEqual(result["choice"], manager.choices_for(event)[0][0])
        self.assertIn("You decided to", result["narrative"])
        self.assertIn(result["narrative"], player.activity_history[-1])
        self.assertTrue(any(getattr(player, field) != value for field, value in before.items()))

    def test_resolved_events_are_not_selected_again(self):
        manager = EventManager()
        player = Player()
        player.age = 3
        with patch("core.events.random.random", return_value=0.0), patch("core.events.random.choice", side_effect=lambda events: events[0]):
            first_event = manager.event_for_age(player.age, player.event_history)
            self.assertIsNotNone(first_event)
            assert first_event is not None
            manager.resolve(player, first_event, 0)
            next_event = manager.event_for_age(player.age, player.event_history)
        self.assertIsNotNone(next_event)
        assert next_event is not None
        self.assertNotEqual(next_event["id"], first_event["id"])

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
        player.age = 10
        player.year = 2005
        player.grades = 87
        player.study_harder()
        market = StockMarket()
        with TemporaryDirectory() as folder:
            path = Path(folder) / "save.json"
            save_game(player, market, path)
            loaded_player, _ = load_game(path)
        self.assertEqual(loaded_player.bank, 5000)
        self.assertEqual(loaded_player.year, 2005)
        self.assertEqual(loaded_player.grades, 92)
        self.assertEqual(loaded_player.last_study_year, player.year)

    def test_save_load_preserves_employee_count(self):
        player = Player()
        player.company = Company("Saved Co", "Food")
        player.company.hire_employees(7)
        market = StockMarket()
        with TemporaryDirectory() as folder:
            path = Path(folder) / "save.json"
            save_game(player, market, path)
            loaded_player, _ = load_game(path)
        assert loaded_player.company is not None
        self.assertEqual(loaded_player.company.employee_count, 17)

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
        company.hire_employees(5)
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
