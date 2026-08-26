class Player:
    def __init__(self):
        self.cash = 100
        self.bank = 100
        self.heat = 0
        self.year = 2000
        self.month = 1
        self.day = 1

        self.portfolio = {}

    def change_money(self, cash=0, bank=0):
        self.cash += cash
        self.bank += bank

    def advance_day(self):
        # Days in each month
        month_lengths = {
            1: 31,
            2: 28,  # We can add leap years later
            3: 31,
            4: 30,
            5: 31,
            6: 30,
            7: 31,
            8: 31,
            9: 30,
            10: 31,
            11: 30,
            12: 31
        }

        self.day += 1

        # If day exceeds the number of days in the current month
        if self.day > month_lengths[self.month]:
            self.day = 1
            self.month += 1

            # If month exceeds December
            if self.month > 12:
                self.month = 1
                self.year += 1
