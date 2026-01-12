import time
from collections import defaultdict

DEFAULT_TIME_WINDOW_SECONDS = 60


class RateLimitExceededError(Exception):
    """Exception raised when a user exceeds the rate limit."""

    pass


Requests = list[float]


class RateLimiter:
    """
    A simple rate limiter that restricts the number of requests a user can make
    within a specified time window.

    Attributes:
        max_requests (int): Maximum number of requests allowed per user within the time window.
        time_window_seconds (int): Time window in seconds for rate limiting.
        user_request (defaultdict): A dictionary mapping user IDs to their request timestamps.

    Methods:
        make_request(user_id: str): Simulate making a request for a given user.
    """

    max_requests: int
    time_window_seconds: int
    user_request: defaultdict[str, Requests]

    def __init__(
        self, max_requests: int, time_window_seconds: int = DEFAULT_TIME_WINDOW_SECONDS
    ):
        self.max_requests = max_requests
        self.time_window_seconds = time_window_seconds
        self.user_request = defaultdict(Requests)

    def make_request(self, user_id: str):
        """
        Simulate making a request for a given user.

        Args:
            user_id (str): The ID of the user making the request.

        Raises:
            RateLimitExceededError: If the user has exceeded the allowed number of requests.
        """

        current_time = time.time()

        self._cleanup_old_requests(user_id, current_time)

        if self._will_exceed_limit(user_id):
            raise RateLimitExceededError(
                f"User {user_id} has exceeded the rate limit of {self.max_requests} requests."
            )

        self.user_request[user_id].append(time.time())

    def _cleanup_old_requests(self, user_id: str, current_time: float):
        self.user_request[user_id] = [
            timestamp
            for timestamp in self.user_request[user_id]
            if current_time - timestamp <= self.time_window_seconds
        ]

    def _will_exceed_limit(self, user_id: str) -> bool:
        return len(self.user_request[user_id]) >= self.max_requests
