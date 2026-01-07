from datetime import date
from unittest.mock import patch

import pytest

from llm_token_budget_manager.budget_manager import TokenBudgetManager


def test_add_team():
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)

    assert "team1" in manager._teams
    team = manager._teams["team1"]
    assert team.team_id == "team1"
    assert team.daily_limit == 1000
    assert team.monthly_limit == 10000
    assert team.daily_usage == 0
    assert team.monthly_usage == 0


def test_add_team_duplicate_raises_error():
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)

    with pytest.raises(ValueError, match="Team team1 already exists"):
        manager.add_team("team1", daily_limit=2000, monthly_limit=20000)


def test_add_team_negative_limits_raises_error():
    manager = TokenBudgetManager()

    with pytest.raises(ValueError, match="daily_limit must be non-negative"):
        manager.add_team("team1", daily_limit=-100, monthly_limit=10000)

    with pytest.raises(ValueError, match="monthly_limit must be non-negative"):
        manager.add_team("team1", daily_limit=1000, monthly_limit=-10000)


def test_can_make_request_within_limits():
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)

    assert manager.can_make_request("team1", 500) is True
    assert manager.can_make_request("team1", 1000) is True
    assert manager.can_make_request("team1", 10000) is False


def test_can_make_request_exceeds_daily_limit():
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)

    manager.record_request("team1", 600)
    assert manager.can_make_request("team1", 400) is True
    assert manager.can_make_request("team1", 401) is False


@patch("llm_token_budget_manager.budget_manager.date")
def test_can_make_request_exceeds_monthly_limit(mock_date):
    mock_date.today.return_value = date(2024, 1, 1)
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)

    for day in range(1, 11):
        mock_date.today.return_value = date(2024, 1, day)
        manager.record_request("team1", 1000)

    assert manager.can_make_request("team1", 0) is True
    assert manager.can_make_request("team1", 1) is False


def test_can_make_request_nonexistent_team():
    manager = TokenBudgetManager()

    with pytest.raises(ValueError, match="Team team1 does not exist"):
        manager.can_make_request("team1", 100)


def test_can_make_request_negative_tokens():
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)

    with pytest.raises(ValueError, match="tokens must be non-negative"):
        manager.can_make_request("team1", -100)


def test_record_request():
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)

    manager.record_request("team1", 500)
    team = manager._teams["team1"]
    assert team.daily_usage == 500
    assert team.monthly_usage == 500

    manager.record_request("team1", 300)
    assert team.daily_usage == 800
    assert team.monthly_usage == 800


def test_record_request_exceeds_daily_limit():
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)

    manager.record_request("team1", 600)

    with pytest.raises(ValueError, match="Request exceeds daily limit"):
        manager.record_request("team1", 401)


@patch("llm_token_budget_manager.budget_manager.date")
def test_record_request_exceeds_monthly_limit(mock_date):
    mock_date.today.return_value = date(2024, 1, 1)
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)

    for day in range(1, 11):
        mock_date.today.return_value = date(2024, 1, day)
        manager.record_request("team1", 1000)

    mock_date.today.return_value = date(2024, 1, 11)
    with pytest.raises(ValueError, match="Request exceeds monthly limit"):
        manager.record_request("team1", 1)


@patch("llm_token_budget_manager.budget_manager.date")
def test_daily_refill_resets_usage(mock_date):
    mock_date.today.return_value = date(2024, 1, 1)
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)

    manager.record_request("team1", 500)
    assert manager._teams["team1"].daily_usage == 500

    mock_date.today.return_value = date(2024, 1, 2)
    manager.refill_daily()

    assert manager._teams["team1"].daily_usage == 0
    assert manager._teams["team1"].last_refill_date == date(2024, 1, 2)
    assert manager._teams["team1"].monthly_usage == 500


@patch("llm_token_budget_manager.budget_manager.date")
def test_daily_refill_auto_on_request(mock_date):
    mock_date.today.return_value = date(2024, 1, 1)
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)

    manager.record_request("team1", 500)
    assert manager._teams["team1"].daily_usage == 500

    mock_date.today.return_value = date(2024, 1, 2)
    assert manager.can_make_request("team1", 1000) is True
    assert manager._teams["team1"].daily_usage == 0


@patch("llm_token_budget_manager.budget_manager.date")
def test_monthly_refill_resets_usage(mock_date):
    mock_date.today.return_value = date(2024, 1, 15)
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)

    for day in range(15, 20):
        mock_date.today.return_value = date(2024, 1, day)
        manager.record_request("team1", 1000)
    assert manager._teams["team1"].monthly_usage == 5000

    mock_date.today.return_value = date(2024, 2, 1)
    manager.refill_monthly()

    assert manager._teams["team1"].monthly_usage == 0
    assert manager._teams["team1"].last_refill_month == date(2024, 2, 1)
    assert manager._teams["team1"].daily_usage == 1000


@patch("llm_token_budget_manager.budget_manager.date")
def test_monthly_refill_auto_on_request(mock_date):
    mock_date.today.return_value = date(2024, 1, 15)
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)

    for day in range(15, 20):
        mock_date.today.return_value = date(2024, 1, day)
        manager.record_request("team1", 1000)
    assert manager._teams["team1"].monthly_usage == 5000

    mock_date.today.return_value = date(2024, 2, 1)
    assert manager.can_make_request("team1", 1000) is True
    assert manager._teams["team1"].monthly_usage == 0


@patch("llm_token_budget_manager.budget_manager.date")
def test_both_refills_on_new_month(mock_date):
    mock_date.today.return_value = date(2024, 1, 31)
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)

    manager.record_request("team1", 500)
    assert manager._teams["team1"].daily_usage == 500
    assert manager._teams["team1"].monthly_usage == 500

    mock_date.today.return_value = date(2024, 2, 1)
    manager.refill_daily()
    manager.refill_monthly()

    assert manager._teams["team1"].daily_usage == 0
    assert manager._teams["team1"].monthly_usage == 0


@patch("llm_token_budget_manager.budget_manager.date")
def test_get_top_k_teams(mock_date):
    mock_date.today.return_value = date(2024, 1, 1)
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)
    manager.add_team("team2", daily_limit=1000, monthly_limit=10000)
    manager.add_team("team3", daily_limit=1000, monthly_limit=10000)

    mock_date.today.return_value = date(2024, 1, 1)
    manager.record_request("team1", 1000)
    for day in range(1, 4):
        mock_date.today.return_value = date(2024, 1, day)
        manager.record_request("team2", 1000)
    for day in range(1, 3):
        mock_date.today.return_value = date(2024, 1, day)
        manager.record_request("team3", 1000)

    top_2 = manager.get_top_k_teams(2)
    assert top_2 == [("team2", 3000), ("team3", 2000)]

    top_1 = manager.get_top_k_teams(1)
    assert top_1 == [("team2", 3000)]


@patch("llm_token_budget_manager.budget_manager.date")
def test_get_top_k_teams_k_greater_than_teams(mock_date):
    mock_date.today.return_value = date(2024, 1, 1)
    manager = TokenBudgetManager()
    manager.add_team("team1", daily_limit=1000, monthly_limit=10000)
    manager.add_team("team2", daily_limit=1000, monthly_limit=10000)

    mock_date.today.return_value = date(2024, 1, 1)
    manager.record_request("team1", 1000)
    for day in range(1, 3):
        mock_date.today.return_value = date(2024, 1, day)
        manager.record_request("team2", 1000)

    top_5 = manager.get_top_k_teams(5)
    assert len(top_5) == 2
    assert top_5 == [("team2", 2000), ("team1", 1000)]


def test_get_top_k_teams_empty():
    manager = TokenBudgetManager()

    assert manager.get_top_k_teams(5) == []


def test_get_top_k_teams_negative_k():
    manager = TokenBudgetManager()

    with pytest.raises(ValueError, match="k must be non-negative"):
        manager.get_top_k_teams(-1)
