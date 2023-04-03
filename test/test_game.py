import os

import pytest

from marketwatch.exceptions import MarketWatchException
from marketwatch.game import MarketWatchGame

GAME_OWNER = "marketwatchapiunittest"
GAME = "algoets-h2023"


@pytest.fixture
def auth_marketwatch():
    username = os.environ.get("MARKETWATCH_USERNAME")
    password = os.environ.get("MARKETWATCH_PASSWORD")
    email = username
    password = password
    try:
        return MarketWatchGame(email, password, GAME)
    except MarketWatchException as e:
        pytest.fail(f"Failed to authenticate: {e}")


@pytest.fixture
def auth_marketwatch_owner():
    username = os.environ.get("MARKETWATCH_USERNAME")
    password = os.environ.get("MARKETWATCH_PASSWORD")
    email = username
    password = password
    try:
        return MarketWatchGame(email, password, GAME_OWNER)
    except MarketWatchException as e:
        pytest.fail(f"Failed to authenticate: {e}")


def test_marketwatch_game_init(auth_marketwatch_owner, auth_marketwatch):
    assert auth_marketwatch_owner is not None
    assert auth_marketwatch is not None

def test_marketwatch_game_get_game(auth_marketwatch_owner, auth_marketwatch):
    assert auth_marketwatch_owner.game is not None
    assert auth_marketwatch.game is not None

def test_marketwatch_game_get_game_settings(auth_marketwatch_owner, auth_marketwatch):
    # assert auth_marketwatch_owner.settings is not None
    assert auth_marketwatch.settings is not None

def test_marketwatch_game_get_leaderboard(auth_marketwatch_owner, auth_marketwatch):
    assert auth_marketwatch_owner.leaderboard is not None
    assert auth_marketwatch.leaderboard is not None

def test_marketwatch_game_get_pending_orders(auth_marketwatch_owner, auth_marketwatch):
    assert auth_marketwatch_owner.orders is not None
    # assert auth_marketwatch.orders is not None

def test_marketwatch_game_get_portfolio(auth_marketwatch_owner, auth_marketwatch):
    assert auth_marketwatch_owner.portfolio is not None
    assert auth_marketwatch.portfolio is not None

def test_marketwatch_game_get_portfolio_performance(auth_marketwatch_owner, auth_marketwatch):
    # assert auth_marketwatch_owner.portfolio_performance is not None
    assert auth_marketwatch.portfolio_performance is not None

def test_marketwatch_game_get_ledger_id(auth_marketwatch_owner, auth_marketwatch):
    assert auth_marketwatch_owner.ledger_id is not None
    assert auth_marketwatch.ledger_id is not None


def test_marketwatch_game_get_game_id(auth_marketwatch_owner, auth_marketwatch):
    assert auth_marketwatch_owner.game_id is not None
    assert auth_marketwatch.game_id is not None