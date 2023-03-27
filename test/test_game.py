import pytest
from marketwatch import MarketWatch
from marketwatch.game import MarketWatchGame
from marketwatch.exceptions import MarketWatchException, MarketWatchGameException
import os

@pytest.fixture
def authenticated_marketwatch():
    username = os.environ.get("MARKETWATCH_USERNAME")
    password = os.environ.get("MARKETWATCH_PASSWORD")
    email = username
    password = password
    try:
        return MarketWatchGame(email, password, "algoets-h2023")
    except MarketWatchException as e:
        pytest.fail(f"Failed to authenticate: {e}")

def test_marketwatch_game_init(authenticated_marketwatch):
    assert authenticated_marketwatch is not None

