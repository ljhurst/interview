# LLM Token Budget Manager

A production-ready token budget management system for tracking and enforcing LLM API usage limits across teams with support for daily/monthly quotas, priority-based borrowing, and efficient analytics queries.

## Architecture & Design Decisions

### Scalability & Performance

**O(1) Team Lookups**: The implementation uses a `dict[str, TeamBudget]` for constant-time team access, critical for high-throughput API scenarios where budget checks occur on every request.

**Efficient Top-K Queries**: The `get_top_k_teams()` method leverages `heapq.nlargest()` for O(n log k) complexity instead of O(n log n) full sorting. This is optimal when k << n, which is typical for analytics dashboards showing top 10-20 teams.

**Lazy Refill Strategy**: Daily and monthly refills occur automatically during `can_make_request()` checks rather than requiring scheduled batch jobs. This ensures:
- Zero-overhead for teams that don't make requests
- Always-accurate limits without background processing
- Reduced operational complexity

### Type Safety & Domain Modeling

**Strong Typing Throughout**: The codebase uses Python type hints consistently, enabling static analysis and improving IDE support. This reduces runtime errors and improves maintainability.

**Domain-Driven Design**: The `TeamBudget` dataclass encapsulates all team budget state, ensuring data integrity through validation in `__post_init__()`. The `Priority` enum provides type-safe priority levels, preventing string-based errors.

**Structured Data Over Primitives**: Instead of raw dictionaries or tuples, the implementation uses typed dataclasses, making the API self-documenting and reducing cognitive load.

### Extensibility & Maintainability

**Open/Closed Principle**: The `PriorityTokenBudgetManager` extends `TokenBudgetManager` through inheritance, adding priority-based borrowing without modifying the base class. This demonstrates:
- Backward compatibility preservation
- Single Responsibility Principle adherence
- Easy addition of new priority behaviors

**Composition Over Duplication**: Public refill methods (`refill_daily()`, `refill_monthly()`) delegate to private `_if_needed` methods, eliminating code duplication and ensuring consistent behavior across manual and automatic refills.

**Separation of Concerns**: Clear boundaries between:
- Data models (`models.py`) - domain entities
- Core logic (`budget_manager.py`) - business rules
- Extended features (`priority_manager.py`) - specialized behaviors

### Error Handling & Validation

**Fail-Fast Validation**: Input validation occurs at method boundaries with clear `ValueError` messages. This prevents invalid state propagation and provides actionable error messages for debugging.

**Defensive Programming**: Methods validate team existence, non-negative tokens, and limit constraints before operations, preventing silent failures and ensuring predictable behavior.

## Key Features

### Core Budget Management

- **Dual-Limit Enforcement**: Simultaneous daily and monthly limits with independent tracking
- **Automatic Refills**: Daily and monthly quotas reset automatically based on date comparisons
- **Efficient Queries**: Top-K team analytics with optimal algorithmic complexity

### Priority-Based Borrowing

- **High-Priority Override**: Teams can borrow from tomorrow's daily quota for urgent requests
- **Borrowing Limits**: Prevents unbounded borrowing by capping at daily_limit
- **Debt Tracking**: Borrowed tokens are deducted from the next day's quota automatically

## Testing Strategy

The test suite demonstrates **Test-Driven Development** principles with comprehensive coverage:

- **20 test cases** covering happy paths, edge cases, and error conditions
- **Date mocking** for testing time-dependent refill logic without flakiness
- **Isolated unit tests** that verify individual behaviors independently
- **Integration-style tests** that validate multi-step workflows

Key test categories:
- Input validation and error handling
- Daily and monthly refill mechanics
- Priority borrowing logic
- Top-K query correctness
- Edge cases (empty teams, k > n, etc.)

## Production Readiness Considerations

### Observability

While not implemented here, production deployment would benefit from:
- **Metrics**: Track refill frequency, borrowing usage, limit violations
- **Logging**: Structured logs for budget checks, refills, and errors
- **Alerting**: Notifications when teams approach limits or borrowing thresholds

### Scalability Enhancements

For enterprise-scale deployment:
- **Persistence Layer**: Replace in-memory dict with Redis or database backend
- **Distributed Locking**: Ensure atomic refill operations across instances
- **Caching Strategy**: Cache team budgets with TTL for high-throughput scenarios
- **Batch Operations**: Optimize `refill_daily()`/`refill_monthly()` for thousands of teams

### Security & Compliance

- **Input Sanitization**: Current validation prevents injection, but production needs rate limiting
- **Audit Trail**: Log all budget modifications for compliance tracking
- **Access Control**: Integrate with enterprise auth (OAuth/OIDC) for team management

## Code Quality Highlights

### Clean Code Principles

- **Small, Focused Functions**: Each method has a single responsibility
- **Self-Documenting Names**: Method and variable names clearly express intent
- **DRY (Don't Repeat Yourself)**: Refill logic centralized in reusable private methods
- **Minimal Comments**: Code clarity eliminates need for explanatory comments

### Python Best Practices

- **Type Hints**: Full type coverage enables static analysis and better tooling
- **Dataclasses**: Modern Python features for clean data modeling
- **Enum Usage**: Type-safe constants prevent magic strings
- **Private Methods**: Proper encapsulation with `_` prefix convention

## Usage Example

```python
from llm_token_budget_manager import TokenBudgetManager, PriorityTokenBudgetManager, Priority

# Basic usage
manager = TokenBudgetManager()
manager.add_team("engineering", daily_limit=10000, monthly_limit=100000)
manager.add_team("product", daily_limit=5000, monthly_limit=50000)

if manager.can_make_request("engineering", 5000):
    manager.record_request("engineering", 5000)

# Priority-based borrowing
priority_manager = PriorityTokenBudgetManager()
priority_manager.add_team("critical", daily_limit=10000, monthly_limit=100000)

# High-priority request can borrow from tomorrow
if priority_manager.can_make_request("critical", 15000, Priority.HIGH):
    priority_manager.record_request("critical", 15000, Priority.HIGH)

# Analytics
top_teams = manager.get_top_k_teams(5)
```

## Development Setup

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src/llm_token_budget_manager --cov-report=html
```

## Future Enhancements

- **Rate Limiting**: Per-team rate limiting beyond token budgets
- **Budget Forecasting**: Predictive analytics for budget exhaustion
- **Multi-Region Support**: Geographic budget allocation
- **Webhook Integration**: Event notifications for budget events
- **GraphQL/REST API**: Expose functionality as microservice
