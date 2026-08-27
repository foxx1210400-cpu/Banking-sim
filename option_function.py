def view_bank_account(player):
    while True:
        print("==========================")
        print("1. View bank balance")
        print("2. Exit")
        print("==========================")

        try:
            user_choice = int(input("Choose: "))
        except ValueError:
            print("Invalid input.")
            continue

        if user_choice == 1:
            print("Bank Balance:", player.bank)

        elif user_choice == 2:
            return

        else:
            print("Try again.")


def apply_to_jobs():
    while True:
        print("=============")
        print("1. View jobs")
        print("2. Exit")
        print("=============")

        try:
            user_choice = int(input("Choose: "))
        except ValueError:
            print("Invalid input.")
            continue

        if user_choice == 1:
            print("There are no jobs yet.")

        elif user_choice == 2:
            return

        else:
            print("Try again.")
