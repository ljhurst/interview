import time

import pytest

from rate_limiter import RateLimiter, RateLimitExceededError


def test_within_limits():
    rate_limiter = RateLimiter(max_requests=5)

    for _ in range(5):
        rate_limiter.make_request("user_1")


def test_exceed_limits():
    rate_limiter = RateLimiter(max_requests=3)

    for _ in range(3):
        rate_limiter.make_request("user_1")

    with pytest.raises(RateLimitExceededError):
        rate_limiter.make_request("user_1")


def test_multiple_users():
    rate_limiter = RateLimiter(max_requests=2)

    for _ in range(2):
        rate_limiter.make_request("user_2")

    rate_limiter.make_request("user_1")

    with pytest.raises(RateLimitExceededError):
        rate_limiter.make_request("user_2")


def test_after_wait_time():
    time_window_seconds = 1
    rate_limiter = RateLimiter(max_requests=2, time_window_seconds=time_window_seconds)

    for _ in range(2):
        rate_limiter.make_request("user_1")

    with pytest.raises(RateLimitExceededError):
        rate_limiter.make_request("user_1")

    time.sleep(time_window_seconds + 0.1)

    rate_limiter.make_request("user_1")
