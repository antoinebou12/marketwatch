import pytest

from marketwatch.exceptions import MarketWatchException
from marketwatch.exceptions import MarketWatchGameException


def test_market_watch_exception():
    with pytest.raises(MarketWatchException):
        raise MarketWatchException("Test MarketWatchException")


def test_market_watch_game_exception():
    with pytest.raises(MarketWatchGameException):
        raise MarketWatchGameException("Test MarketWatchGameException")
