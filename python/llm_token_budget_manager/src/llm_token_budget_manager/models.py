from dataclasses import dataclass
from datetime import date
from enum import Enum


class Priority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


@dataclass
class TeamBudget:
    team_id: str
    daily_limit: int
    monthly_limit: int
    daily_usage: int = 0
    monthly_usage: int = 0
    last_refill_date: date | None = None
    last_refill_month: date | None = None
    borrowed_tokens: int = 0

    def __post_init__(self) -> None:
        if self.daily_limit < 0:
            raise ValueError("daily_limit must be non-negative")
        if self.monthly_limit < 0:
            raise ValueError("monthly_limit must be non-negative")
        if self.daily_usage < 0:
            raise ValueError("daily_usage must be non-negative")
        if self.monthly_usage < 0:
            raise ValueError("monthly_usage must be non-negative")
        if self.borrowed_tokens < 0:
            raise ValueError("borrowed_tokens must be non-negative")
