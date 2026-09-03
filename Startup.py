from option_function import view_bank_account, apply_to_jobs
from player_class import Player
from stock_market import StockMarket
from company_class import Company
from create_product import ProductCreator
from config import SECTOR_STARTUP_COSTS
from logger import logger

market = StockMarket()
STARTUP_COSTS = SECTOR_STARTUP_COSTS


def create_company(player):
    name = input("Enter company name: ").strip()
    if not name:
        print("Company name cannot be empty.")
        return

    catalog_sectors = ProductCreator.load_catalog().keys()
    valid_sectors = sorted(set(catalog_sectors) | set(STARTUP_COSTS.keys()))
    print("Available sectors:")
    for i, sector in enumerate(valid_sectors, 1):
        cost = STARTUP_COSTS.get(sector, 50000)
        print(f"{i}. {sector} — ${cost:,.0f}")

    sector_choice = input("Choose a sector: ").strip()
    valid_lookup = {str(i): sector for i, sector in enumerate(valid_sectors, 1)}
    sector = valid_lookup.get(sector_choice, sector_choice.title())

    if sector not in valid_sectors:
        print("That sector is not available yet.")
        return

    startup_cost = STARTUP_COSTS.get(sector, 50000)
    if player.bank < startup_cost:
        print(f"You need at least ${startup_cost:,.0f} in the bank to start a {sector} company.")
        return

    company = Company(name, sector)
    company.cash = startup_cost
    company.capital_invested = startup_cost
    player.company = company
    player.bank -= startup_cost
    print(f"Company {name} created successfully in {sector}.")
    print(f"You paid a ${startup_cost:,.0f} startup cost and your company has ${startup_cost:,.0f} to work with.")


def manage_products(company):
    while True:
        if not company.products:
            print("You do not have any products yet.")
            return

        print("=========================")
        print("Product Management")
        print("1. View product performance")
        print("2. Set production for a product")
        print("3. Set sale price for a product")
        print("4. Back")
        print("=========================")

        try:
            choice = int(input("Choose: "))
        except ValueError:
            print("Please enter a number.")
            continue

        if choice == 1:
            for index, product in enumerate(company.products, 1):
                print(
                    f"{index}. {product.name} | "
                    f"Price: ${product.sale_price:,.2f} | "
                    f"Annual quota: {product.annual_production_quota} | "
                    f"Sold: {product.units_sold} | "
                    f"Unsold: {product.units_unsold} | "
                    f"Inventory: {product.inventory} | "
                    f"Revenue: ${product.annual_revenue:,.2f} | "
                    f"Profit: ${product.annual_profit:,.2f}"
                )

        elif choice == 2:
            try:
                product_index = int(input("Select a product number: "))
            except ValueError:
                print("Please enter a number.")
                continue

            if product_index < 1 or product_index > len(company.products):
                print("Invalid product selection.")
                continue

            product = company.products[product_index - 1]
            try:
                planned_units = int(input(f"How many units of {product.name} should be produced this year? "))
            except ValueError:
                print("Please enter a valid unit count.")
                continue

            product.set_year_plan(planned_units)
            print(f"{product.name} annual production quota set to {product.annual_production_quota} units.")

        elif choice == 3:
            try:
                product_index = int(input("Select a product number: "))
            except ValueError:
                print("Please enter a number.")
                continue

            if product_index < 1 or product_index > len(company.products):
                print("Invalid product selection.")
                continue

            product = company.products[product_index - 1]
            try:
                new_price = float(input(f"Set the sale price for {product.name}: $"))
            except ValueError:
                print("Please enter a valid price.")
                continue

            if new_price <= 0:
                print("Sale price must be greater than zero.")
                continue

            product.sale_price = new_price
            print(f"{product.name} sale price set to ${product.sale_price:,.2f}.")

        elif choice == 4:
            return
        else:
            print("Wrong key")


def company_menu(player):
    if not hasattr(player, "company") or player.company is None:
        create_company(player)
        if not hasattr(player, "company") or player.company is None:
            return

    while True:
        company = player.company
        print("=========================")
        print("1. View company details")
        print("2. Manage products")
        print("3. Research and launch a product")
        print("4. Invest in company")
        print("5. Manage employees")
        print("6. Buy factory")
        print("7. Exit company menu")
        print("=========================")

        try:
            choice = int(input("Choose: "))
        except ValueError:
            print("Please enter a number.")
            continue

        if choice == 1:
            summary = company.get_financial_summary()
            print(f"Company Name: {company.name}")
            print(f"Company Sector: {company.sector}")
            print(f"Cash: ${summary['cash']:,.2f}")
            print(f"Revenue: ${summary['revenue']:,.2f}")
            print(f"Expenses: ${summary['expenses']:,.2f}")
            print(f"Net income: ${summary['net_income']:,.2f}")
            print(f"Debt: ${summary['debt']:,.2f}")
            print(f"Units sold: {summary['total_units_sold']}")
            print(f"Unsold units: {summary['total_units_unsold']}")
            print(f"Inventory: {summary['total_inventory']}")
            if company.products:
                print("Products:")
                for product in company.products:
                    print(
                        f"- {product.name} | Sale: ${product.sale_price:,.2f} | "
                        f"Cost: ${product.manufacturing_cost:,.2f} | "
                        f"Demand: {product.base_demand}/10 | "
                        f"Competition: {product.competition}/10"
                    )
            else:
                print("Products: No products yet.")

        elif choice == 2:
            manage_products(company)

        elif choice == 3:
            sector_products = ProductCreator.load_sector_products(company.sector)
            if not sector_products:
                print("No products are available for this sector yet.")
                continue

            print(f"Research products for {company.sector}:")
            for i, product in enumerate(sector_products, 1):
                if product.researched:
                    status = (
                        f"Research complete | Demand: {product.base_demand}/10 | "
                        f"Competition: {product.competition}/10 | "
                        f"Manufacturing cost: ${product.manufacturing_cost:,.2f}"
                    )
                else:
                    status = (
                        f"Research cost: ${product.research_cost:,.2f} | "
                        "Market stats hidden until researched"
                    )
                print(f"{i}. {product.name} | {status}")

            try:
                picked = int(input("Select a product to research: "))
            except ValueError:
                print("Please enter a number.")
                continue

            if picked < 1 or picked > len(sector_products):
                print("Invalid choice.")
                continue

            chosen = sector_products[picked - 1]
            if chosen.researched:
                print(f"{chosen.name} is already researched.")
                print(
                    f"Unlocked stats: Demand {chosen.base_demand}/10 | "
                    f"Competition {chosen.competition}/10 | "
                    f"Manufacturing cost ${chosen.manufacturing_cost:,.2f}"
                )
                launch_choice = input("Would you like to launch this product now? (y/n): ").strip().lower()
                if launch_choice == "y":
                    if any(product.name == chosen.name for product in company.products):
                        print(f"{chosen.name} is already in your product lineup.")
                    else:
                        result = company.add_product(chosen)
                        print(result)
                continue

            cost = chosen.research_cost
            if company.cash < cost:
                print(f"You need ${cost:,.2f} to research {chosen.name}.")
                continue

            company.cash -= cost
            message = chosen.research(company.cash)
            print(message)
            print(
                f"Unlocked stats: Demand {chosen.base_demand}/10 | "
                f"Competition {chosen.competition}/10 | "
                f"Manufacturing cost ${chosen.manufacturing_cost:,.2f}"
            )

            launch_choice = input("Would you like to launch this product now? (y/n): ").strip().lower()
            if launch_choice == "y":
                if any(product.name == chosen.name for product in company.products):
                    print(f"{chosen.name} is already in your product lineup.")
                else:
                    result = company.add_product(chosen)
                    print(result)

        elif choice == 4:
            try:
                amount = float(input("How much do you want to invest into the company? $"))
            except ValueError:
                print("Please enter a valid amount.")
                continue

            if amount <= 0:
                print("Investment amount must be greater than zero.")
                continue
            if player.bank < amount:
                print(f"You do not have enough cash in your bank account for that investment. You have ${player.bank:,.2f}.")
                continue

            player.bank -= amount
            company.invest(amount)
            print(f"You invested ${amount:,.2f} into {company.name}.")
            print(f"Company cash: ${company.cash:,.2f}")

        elif choice == 5:
            print(
                f"Employees: {company.employee_count} | "
                f"Required: {company.required_employee_count} | "
                f"Workforce efficiency: {min(company.staffing_ratio, 1.10):.0%}"
            )
            action = input("Hire or lay off employees? (h/l): ").strip().lower()
            try:
                count = int(input("Number of employees: "))
            except ValueError:
                print("Please enter a whole number.")
                continue
            if action == "h":
                print(company.hire_employees(count))
            elif action == "l":
                print(company.fire_employees(count))
            else:
                print("Choose h to hire or l to lay off employees.")

        elif choice == 6:
            print(company.buy_factory())

        elif choice == 7:
            break
        else:
            print("Wrong key")


def advance_time(player, market, days=1):
    for _ in range(days):
        player.advance_day()
        market.next_day(player)

def options(player):
    while True:
        print("=========================")
        print("1. View your finances")
        print("2. Apply for a job")
        print("3. Move to next day")
        print("4. Move to next year")
        print("5. View stock market")
        print("6. Buy stocks")
        print("7. Sell stocks")
        print("8. View your portfolio")
        print("9. View net worth")
        print("10. Manage company")
        print("11. Exit")
        print("=========================")

        try:
            user_choice = int(input("Choose: "))
        except ValueError:
            print("Please enter a number.")
            continue

        if user_choice == 1:
            view_bank_account(player)

        elif user_choice == 2:
            apply_to_jobs()

        elif user_choice == 3:
            advance_time(player, market, days=1)
            print(f"Date: {player.month}/{player.day}/{player.year}")

        elif user_choice == 4:
            advance_time(player, market, days=365)
            print(f"Date: {player.month}/{player.day}/{player.year}")

        elif user_choice == 5:
            market.view_stocks()
            input("\nPress Enter to continue...")

        elif user_choice == 6:
            ticker = input("Ticker: ").upper()
            try:
                shares = int(input("Shares to buy: "))
            except ValueError:
                print("Please enter a number.")
                continue
            market.buy_stock(player, ticker, shares)

        elif user_choice == 7:
            ticker = input("Ticker: ").upper()
            try:
                shares = int(input("Shares to sell: "))
            except ValueError:
                print("Please enter a number.")
                continue
            market.sell_stock(player, ticker, shares)

        elif user_choice == 8:
            market.portfolio_value(player)

        elif user_choice == 9:
            worth = market.net_worth(player)
            print(f"Total Net Worth: ${worth:.2f}")

        elif user_choice == 10:
            company_menu(player)

        elif user_choice == 11:
            break

        else:
            print("Wrong key")

def game_loop(player):
    print("This is build one of banking sim")
    print("Press enter to continue")
    input()

    while True:
        options(player)
