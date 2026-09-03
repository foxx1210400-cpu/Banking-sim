from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from .config import DATA_DIR

if TYPE_CHECKING:
    from .player_class import Player


@dataclass(frozen=True)
class EnemyCompany:
    ticker: str
    name: str
    sector: str
    market_share: float
    annual_revenue: float
    products: tuple[str, ...]
    aggression: float
    stock_price: float

    @classmethod
    def from_dict(cls, data: dict) -> "EnemyCompany":
        return cls(
            ticker=data["ticker"],
            name=data["name"],
            sector=data["sector"],
            market_share=data["market_share"],
            annual_revenue=data["annual_revenue"],
            products=tuple(data["products"]),
            aggression=data["aggression"],
            stock_price=data["stock_price"],
        )


class CompetitorRegistry:
    """Loads rivals and selects those relevant to a player's company."""

    def __init__(self, data_file: Path | None = None):
        self.data_file = data_file or DATA_DIR / "Enemy_companies.json"
        self.companies_by_sector = self._load()

    def _load(self) -> dict[str, tuple[EnemyCompany, ...]]:
        with self.data_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return {
            sector: tuple(EnemyCompany.from_dict(company) for company in companies)
            for sector, companies in data["sectors"].items()
        }

    def for_player(self, player: "Player") -> tuple[EnemyCompany, ...]:
        """Return rivals only after the player has created a company."""
        if player.company is None:
            return ()
        return self.companies_by_sector.get(player.company.sector, ())