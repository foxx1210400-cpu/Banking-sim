from __future__ import annotations

import json
from pathlib import Path

from .config import DATA_DIR

class JobCatalog:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else DATA_DIR / "jobs.json"
        self.jobs = self._load_jobs()

    def _load_jobs(self):
        raw = self.path.read_text(encoding="utf-8")
        jobs = json.loads(raw)["jobs"]
        for job in jobs:
            if "hourly_wage" not in job:
                job["hourly_wage"] = 10.50 if job["min_age"] < 18 else 15.00
        return jobs

    def available_for(self, age: int):
        return [job for job in self.jobs if job["min_age"] <= age]