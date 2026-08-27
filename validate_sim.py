import sys
import random
import py_compile
from company_class import Company
from create_product import Product

def run_validation():
    print("--- 1. Compilation Verification ---")
    files_to_compile = ["company_logic.py", "company_class.py", "ui/gui_main.py"]
    for file in files_to_compile:
        try:
            py_compile.compile(file, doraise=True)
            print(f"PASS: {file} compiled successfully.")
        except Exception as e:
            print(f"FAIL: {file} failed to compile: {e}")
            sys.exit(1)

    print("\n--- 2. Product Pricing & Demand Validation ---")
    comp_a = Company("CompanyA", "Tech")
    comp_a.cash = 1000000.0
    prod_a = Product(
        name="ProdA_2x",
        sale_price=20.0,
        unit_cost=10.0,
        base_demand=5,
        sector="Tech",
        manufacturing_cost=10.0,
        competition=5
    )
    prod_a.annual_production_quota = 1000
    comp_a.add_product(prod_a)

    comp_b = Company("CompanyB", "Tech")
    comp_b.cash = 1000000.0
    prod_b = Product(
        name="ProdB_8x",
        sale_price=80.0,
        unit_cost=10.0,
        base_demand=5,
        sector="Tech",
        manufacturing_cost=10.0,
        competition=5
    )
    prod_b.annual_production_quota = 1000
    comp_b.add_product(prod_b)

    # Seed and run year on A
    random.seed(42)
    cash_before_a = comp_a.cash
    summary_a = comp_a.run_year()
    net_income_a = summary_a["net_income"]
    cash_after_a = comp_a.cash

    # Seed and run year on B
    random.seed(42)
    cash_before_b = comp_b.cash
    summary_b = comp_b.run_year()
    net_income_b = summary_b["net_income"]
    cash_after_b = comp_b.cash

    units_sold_a = summary_a["units_sold"]
    units_sold_b = summary_b["units_sold"]
    print(f"Product A (2x price) units sold: {units_sold_a}")
    print(f"Product B (8x price) units sold: {units_sold_b}")

    if units_sold_b < units_sold_a:
        print("PASS: The higher-priced product (8x cost) sold fewer units than the lower-priced product (2x cost).")
    else:
        print("FAIL: The higher-priced product did NOT sell fewer units.")

    print("\n--- 3. Annual Summary Keys Verification ---")
    required_keys = ["manufacturing_cost", "operating_expenses", "taxes", "expenses", "net_income"]
    all_keys_exist = True
    for key in required_keys:
        if key in summary_a:
            print(f"PASS: '{key}' key exists in annual summary.")
        else:
            print(f"FAIL: '{key}' key is missing in annual summary.")
            all_keys_exist = False

    print("\n--- 4. Cash Change Equals Net Income Verification ---")
    cash_diff_a = cash_after_a - cash_before_a
    cash_diff_b = cash_after_b - cash_before_b
    
    # We use abs(val - val) < 1e-9 for floating point precision checks
    if abs(cash_diff_a - net_income_a) < 1e-9 and abs(cash_diff_b - net_income_b) < 1e-9:
        print(f"PASS: Cash change equals annual net income (Company A: {cash_diff_a} == {net_income_a}, Company B: {cash_diff_b} == {net_income_b}).")
    else:
        print(f"FAIL: Cash change does not equal net income. Company A diff: {cash_diff_a} vs {net_income_a}; Company B diff: {cash_diff_b} vs {net_income_b}")

    print("\n--- 5. Bankruptcy Verification on <= 0 Cash ---")
    comp_c = Company("CompanyC", "Tech")
    # Low production target and high expenses, or just set cash such that after simulation it is negative
    # Alternatively, set cash to negative or 0 after simulate_company_year, but since run_year checks self.cash <= 0,
    # let's set cash to 10 initially but with a product that has very high manufacturing cost, so the cash drops below <= 0.
    comp_c.cash = 1.0
    prod_c = Product(
        name="ProdC",
        sale_price=1.0,
        unit_cost=100.0,
        base_demand=5,
        sector="Tech",
        manufacturing_cost=100.0,
        competition=5
    )
    prod_c.annual_production_quota = 100
    comp_c.add_product(prod_c)
    
    comp_c.run_year()
    print(f"Company C cash after run_year: {comp_c.cash}")
    print(f"Company C bankrupt status: {comp_c.bankrupt}")
    if comp_c.cash <= 0 and comp_c.bankrupt:
        print("PASS: Company with cash <= 0 is marked bankrupt.")
    else:
        print("FAIL: Company with cash <= 0 was NOT marked bankrupt.")

if __name__ == '__main__':
    run_validation()