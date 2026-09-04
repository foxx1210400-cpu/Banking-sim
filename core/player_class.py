from __future__ import annotations

from .company_class import Company
from .family import generate_family


class Player:
    def __init__(self):
        self.bank: float = 0.0
        self.age = 1
        self.health = 100
        self.happiness = 50
        self.smarts = 50
        self.grades = 70
        self.last_study_year: int | None = None
        self.relationships = 50
        self.family = generate_family()
        self.job = None
        self.job_experience = 0
        self.last_salary = 0.0
        self.last_taxes = 0.0
        self.college_enrolled = False
        self.college_years = 0
        self.college_degree = None
        self.activity_history = ["Age 1: Your life begins."]
        self.event_history = []
        self.year = 2000
        self.month = 1
        self.day = 1

        self.portfolio = {}
        self.company: Company | None = None

    def school_level(self):
        if 5 <= self.age <= 10:
            return "Elementary School"
        if 11 <= self.age <= 13:
            return "Middle School"
        if 14 <= self.age <= 18:
            return "High School"
        return None

    def record_activity(self, message):
        self.activity_history.append(f"Age {self.age}: {message}")

    def study_harder(self):
        if self.school_level() is None or self.last_study_year == self.year:
            return False
        self.grades = min(100, self.grades + 5)
        self.smarts = min(100, self.smarts + 1)
        self.last_study_year = self.year
        self.record_activity(f"Studied harder and improved grades to {self.grades}/100.")
        return True

    @staticmethod
    def _income_tax(income):
        if income <= 15_000:
            return 0.0
        if income <= 50_000:
            return (income - 15_000) * 0.10
        if income <= 100_000:
            return 3_500 + (income - 50_000) * 0.20
        return 13_500 + (income - 100_000) * 0.30

    def annual_salary(self):
        if not self.job or self.age < self.job.get("min_age", 0):
            return 0.0
        return self.job.get("hourly_wage", 0.0) * 2_000

    def advance_year(self):
        self.last_salary = self.annual_salary()
        self.last_taxes = self._income_tax(self.last_salary)
        self.bank += self.last_salary - self.last_taxes
        if self.college_enrolled:
            self.bank -= 15_000
            self.college_years += 1
            self.record_activity("Paid $15,000 college tuition.")
            if self.college_years >= 4:
                self.college_enrolled = False
                self.college_degree = "Bachelor's Degree"
                self.record_activity("Graduated college with a Bachelor's Degree.")
        if self.job:
            self.job_experience += 1
        self.month = 1
        self.day = 1
        self.age += 1
        self.year += 1
        self.record_activity(f"Aged up to {self.age}.")
        if self.last_salary:
            self.record_activity(f"Earned ${self.last_salary:,.0f} salary and paid ${self.last_taxes:,.0f} in taxes.")

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

