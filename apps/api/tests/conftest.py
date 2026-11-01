import pytest

from api.core.rate_limit import limiter


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """The limiter is process-wide state; every test starts with empty counters."""
    limiter.reset()
    yield
    limiter.reset()
