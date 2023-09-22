
import os

import pytest

from marketwatch.exceptions import MarketWatchException
from marketwatch.watchlist import MarketWatchWatchlist

WATCHLIST = "3762211977140901"

@pytest.fixture
def authenticated_marketwatch():
    username = os.environ.get("MARKETWATCH_USERNAME")
    password = os.environ.get("MARKETWATCH_PASSWORD")
    email = username
    password = password
    try:
        return MarketWatchWatchlist(email, password, WATCHLIST)
    except MarketWatchException as e:
        pytest.fail(f"Failed to authenticate: {e}")


def test_marketwatch_watchlist_init(authenticated_marketwatch):
    assert authenticated_marketwatch is not None

def test_marketwatch_watchlist_get_watchlists(authenticated_marketwatch):
    assert authenticated_marketwatch.watchlists is not None

def test_marketwatch_watchlist_get_watchlist(authenticated_marketwatch):
    assert authenticated_marketwatch.watchlist is not None
