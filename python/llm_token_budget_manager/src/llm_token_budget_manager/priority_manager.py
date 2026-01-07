from datetime import date

from .budget_manager import TokenBudgetManager
from .models import Priority, TeamBudget


class PriorityTokenBudgetManager(TokenBudgetManager):
    def can_make_request(
        self, team_id: str, tokens: int, priority: Priority = Priority.NORMAL
    ) -> bool:
        if tokens < 0:
            raise ValueError("tokens must be non-negative")

        self._ensure_team_exists(team_id)
        team_budget = self._teams[team_id]

        self._refill_team_if_needed(team_budget)

        available_daily = team_budget.daily_limit - team_budget.daily_usage
        available_monthly = team_budget.monthly_limit - team_budget.monthly_usage

        if priority == Priority.HIGH:
            if tokens <= available_daily and tokens <= available_monthly:
                return True

            if tokens > available_monthly:
                return False

            if tokens > available_daily:
                borrowable = team_budget.daily_limit
                already_borrowed = team_budget.borrowed_tokens
                remaining_borrowable = borrowable - already_borrowed

                needed_borrow = tokens - available_daily
                return needed_borrow <= remaining_borrowable

        return tokens <= available_daily and tokens <= available_monthly

    def record_request(
        self, team_id: str, tokens: int, priority: Priority = Priority.NORMAL
    ) -> None:
        if tokens < 0:
            raise ValueError("tokens must be non-negative")

        if not self.can_make_request(team_id, tokens, priority):
            team_budget = self._teams[team_id]
            available_daily = team_budget.daily_limit - team_budget.daily_usage
            available_monthly = team_budget.monthly_limit - team_budget.monthly_usage

            if tokens > available_monthly:
                raise ValueError(
                    f"Request exceeds monthly limit: {tokens} > {available_monthly}"
                )

            if priority == Priority.HIGH and tokens > available_daily:
                borrowable = team_budget.daily_limit
                already_borrowed = team_budget.borrowed_tokens
                remaining_borrowable = borrowable - already_borrowed
                needed_borrow = tokens - available_daily

                if needed_borrow > remaining_borrowable:
                    raise ValueError(
                        f"Request exceeds borrowable limit: {needed_borrow} > {remaining_borrowable}"
                    )
            elif tokens > available_daily:
                raise ValueError(
                    f"Request exceeds daily limit: {tokens} > {available_daily}"
                )

        team_budget = self._teams[team_id]

        available_daily = team_budget.daily_limit - team_budget.daily_usage

        if priority == Priority.HIGH and tokens > available_daily:
            borrowed_amount = tokens - available_daily
            team_budget.borrowed_tokens += borrowed_amount

        team_budget.daily_usage += tokens
        team_budget.monthly_usage += tokens

    def _refill_daily_if_needed(self, team_budget: TeamBudget) -> None:
        today = date.today()
        if team_budget.last_refill_date is None or team_budget.last_refill_date < today:
            if team_budget.borrowed_tokens > 0:
                team_budget.daily_usage = team_budget.borrowed_tokens
                team_budget.borrowed_tokens = 0
            else:
                team_budget.daily_usage = 0
            team_budget.last_refill_date = today
            self._current_date = today
