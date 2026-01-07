import heapq
from datetime import date

from .models import TeamBudget


class TokenBudgetManager:
    def __init__(self) -> None:
        self._teams: dict[str, TeamBudget] = {}
        self._current_date: date = date.today()

    def add_team(self, team_id: str, daily_limit: int, monthly_limit: int) -> None:
        if team_id in self._teams:
            raise ValueError(f"Team {team_id} already exists")
        if daily_limit < 0:
            raise ValueError("daily_limit must be non-negative")
        if monthly_limit < 0:
            raise ValueError("monthly_limit must be non-negative")

        self._teams[team_id] = TeamBudget(
            team_id=team_id,
            daily_limit=daily_limit,
            monthly_limit=monthly_limit,
            daily_usage=0,
            monthly_usage=0,
            last_refill_date=None,
            last_refill_month=None,
        )

    def can_make_request(self, team_id: str, tokens: int) -> bool:
        if tokens < 0:
            raise ValueError("tokens must be non-negative")

        self._ensure_team_exists(team_id)
        team_budget = self._teams[team_id]

        self._refill_team_if_needed(team_budget)

        available_daily = team_budget.daily_limit - team_budget.daily_usage
        available_monthly = team_budget.monthly_limit - team_budget.monthly_usage

        return tokens <= available_daily and tokens <= available_monthly

    def record_request(self, team_id: str, tokens: int) -> None:
        if tokens < 0:
            raise ValueError("tokens must be non-negative")

        if not self.can_make_request(team_id, tokens):
            team_budget = self._teams[team_id]
            available_daily = team_budget.daily_limit - team_budget.daily_usage
            available_monthly = team_budget.monthly_limit - team_budget.monthly_usage

            if tokens > available_daily:
                raise ValueError(
                    f"Request exceeds daily limit: {tokens} > {available_daily}"
                )
            if tokens > available_monthly:
                raise ValueError(
                    f"Request exceeds monthly limit: {tokens} > {available_monthly}"
                )

        team_budget = self._teams[team_id]
        team_budget.daily_usage += tokens
        team_budget.monthly_usage += tokens

    def refill_daily(self) -> None:
        self._current_date = date.today()
        for team_budget in self._teams.values():
            self._refill_daily_if_needed(team_budget)

    def refill_monthly(self) -> None:
        for team_budget in self._teams.values():
            self._refill_monthly_if_needed(team_budget)

    def get_top_k_teams(self, k: int) -> list[tuple[str, int]]:
        if k < 0:
            raise ValueError("k must be non-negative")

        if not self._teams:
            return []

        teams_with_usage = [
            (team_budget.monthly_usage, team_budget.team_id)
            for team_budget in self._teams.values()
        ]

        top_k = heapq.nlargest(k, teams_with_usage)

        return [(team_id, usage) for usage, team_id in top_k]

    def _ensure_team_exists(self, team_id: str) -> None:
        if team_id not in self._teams:
            raise ValueError(f"Team {team_id} does not exist")

    def _refill_team_if_needed(self, team_budget: TeamBudget) -> None:
        self._refill_daily_if_needed(team_budget)
        self._refill_monthly_if_needed(team_budget)

    def _refill_daily_if_needed(self, team_budget: TeamBudget) -> None:
        today = date.today()
        if team_budget.last_refill_date is None or team_budget.last_refill_date < today:
            team_budget.daily_usage = 0
            team_budget.last_refill_date = today
            self._current_date = today

    def _refill_monthly_if_needed(self, team_budget: TeamBudget) -> None:
        today = date.today()
        if team_budget.last_refill_month is None:
            team_budget.monthly_usage = 0
            team_budget.last_refill_month = today
        else:
            current_month = (today.year, today.month)
            last_month = (
                team_budget.last_refill_month.year,
                team_budget.last_refill_month.month,
            )
            if last_month < current_month:
                team_budget.monthly_usage = 0
                team_budget.last_refill_month = today
