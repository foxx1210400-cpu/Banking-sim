from __future__ import annotations

from company_class import Company


class Player:
    def __init__(self):
        self.bank: float = 100000.0
        self.year = 2000
        self.month = 1
        self.day = 1

        self.portfolio = {}
        self.company: Company | None = None

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

    def advance_month(self):
        self.day = 1
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1

    def advance_year(self):
        self.month = 1
        self.day = 1
        self.year += 1
