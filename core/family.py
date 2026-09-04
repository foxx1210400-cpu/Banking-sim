from __future__ import annotations

import random


FIRST_NAMES = (
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Avery",
    "Cameron", "Drew", "Quinn", "Sam", "Robin", "Parker", "Reese",
)
LAST_NAMES = (
    "Bennett", "Carter", "Davis", "Foster", "Garcia", "Hayes", "Morgan",
    "Parker", "Reed", "Sullivan", "Turner", "Walker", "Wilson",
)


def generate_family():
    last_name = random.choice(LAST_NAMES)
    parent_names = random.sample(FIRST_NAMES, 2)
    annual_income = random.randint(35_000, 140_000)
    return {
        "last_name": last_name,
        "parents": [f"{name} {last_name}" for name in parent_names],
        "annual_income": annual_income,
        "assets": random.randint(25_000, 450_000),
        "home": random.choice(("Apartment", "Townhouse", "Family home")),
        "siblings": random.randint(0, 3),
    }