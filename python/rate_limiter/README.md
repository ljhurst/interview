# Rate Limiter

## Prompt

> Implement a rate limiter that allows N requests per minute per user.
> Design the API and implementation.

## Solution

A sliding window log rate limiter that tracks request timestamps per user.

### Algorithm

1. Store timestamp of each request per user
2. On new request, discard timestamps outside the time window
3. If remaining count ≥ limit, reject
4. Otherwise, record timestamp and allow

### Usage

```python
from rate_limiter import RateLimiter, RateLimitExceededError

limiter = RateLimiter(max_requests=100, time_window_seconds=60)

try:
    limiter.make_request(user_id="user_123")
except RateLimitExceededError:
    # Handle rate limit exceeded
    pass
```

## Trade-offs

| Choice | Trade-off |
|--------|-----------|
| Sliding window log | Precise limiting, but O(n) memory per user |
| In-memory storage | Fast, but single-node only |
| No locking | Simple, but not thread-safe |

## Limitations

- **Not thread-safe** — needs locking for concurrent access
- **Not distributed** — state lost on restart, doesn't scale horizontally
- **Unbounded memory** — no eviction of inactive users

## Alternatives Considered

| Algorithm | When to use |
|-----------|-------------|
| Token bucket | Need burst allowance, lower memory |
| Fixed window | Simplicity over precision |
| Redis + Lua | Distributed systems |

## Development

```bash
uv sync                 # Install dependencies
uv run pytest           # Run tests
uv run ruff check .     # Lint
uv run mypy src/        # Type check
```
