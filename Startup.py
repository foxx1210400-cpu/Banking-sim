from option_function import view_bank_account, apply_to_jobs
from player_class import Player
from stock_market import StockMarket

market = StockMarket()

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
        print("10. Exit")
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
            break

        else:
            print("Wrong key")

def game_loop(player):
    print("This is build one of banking sim")
    print("Press enter to continue")
    input()

    while True:
        options(player)
