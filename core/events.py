from __future__ import annotations

import json
import random
from pathlib import Path

from .config import DATA_DIR


CHOICES = {
    "childhood": (
        ("Listen to your parents", {"happiness": 2}),
        ("Try to handle it yourself", {"smarts": 1, "happiness": -1}),
    ),
    "school": (
        ("Study and learn from it", {"smarts": 3, "happiness": -1}),
        ("Ask a friend for help", {"relationships": 2}),
    ),
    "teen": (
        ("Talk it out", {"relationships": 2, "happiness": 1}),
        ("Keep it to yourself", {"smarts": 1, "happiness": -2}),
    ),
    "adult": (
        ("Handle it responsibly", {"happiness": 1, "bank": 500}),
        ("Brush it off", {"happiness": -1}),
    ),
    "family": (
        ("Spend time with family", {"relationships": 3, "happiness": 2}),
        ("Stay busy with your own life", {"smarts": 1, "relationships": -1}),
    ),
    "health": (
        ("Rest and take care of yourself", {"health": 3, "happiness": 1}),
        ("Push through it", {"health": -2, "smarts": 1}),
    ),
    "social": (
        ("Be friendly", {"relationships": 3, "happiness": 1}),
        ("Keep your distance", {"relationships": -1, "smarts": 1}),
    ),
    "work": (
        ("Put in the extra effort", {"bank": 1500, "smarts": 2, "happiness": -1}),
        ("Protect your free time", {"happiness": 2, "smarts": -1}),
    ),
    "pets": (
        ("Care for the animal", {"happiness": 3, "relationships": 1, "bank": -250}),
        ("Leave it alone", {"happiness": -1}),
    ),
    "crime": (
        ("Stay safe and report it", {"health": 1, "smarts": 2}),
        ("Keep out of it", {"happiness": -1, "smarts": 1}),
    ),
    "random": (
        ("Enjoy the moment", {"happiness": 2}),
        ("Think about what it means", {"smarts": 2}),
    ),
}


class EventManager:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else DATA_DIR / "events.json"
        self.events = self._load_events()

    def _load_events(self):
        with self.path.open("r", encoding="utf-8") as file:
            events = json.load(file)
        return [event for event in events if self._valid_event(event)]

    @staticmethod
    def _valid_event(event):
        age_range = event.get("age_range")
        return (
            isinstance(event.get("description"), str)
            and isinstance(event.get("category"), str)
            and isinstance(age_range, list)
            and len(age_range) == 2
        )

    def event_for_age(self, age: int):
        if age <= 12:
            event_chance = 1 / 3
        elif age < 18:
            event_chance = 1 / 5
        else:
            event_chance = 1 / 8
        if random.random() >= event_chance:
            return None
        eligible = [event for event in self.events if event["age_range"][0] <= age <= event["age_range"][1]]
        if not eligible:
            return None
        return random.choice(eligible)

    def choices_for(self, event):
        return CHOICES.get(event["category"], CHOICES["random"])

    @staticmethod
    def apply_choice(player, effects):
        for field, amount in effects.items():
            if field == "bank":
                player.bank = max(0, player.bank + amount)
                continue
            current = getattr(player, field, 50)
            setattr(player, field, max(0, min(100, current + amount)))

    def resolve(self, player, event, choice_index):
        choices = self.choices_for(event)
        label, effects = choices[choice_index]
        self.apply_choice(player, effects)
        result = {
            "event_id": event["id"],
            "age": player.age,
            "category": event["category"],
            "description": event["description"],
            "choice": label,
            "effects": effects,
        }
        player.event_history.append(result)
        return result
