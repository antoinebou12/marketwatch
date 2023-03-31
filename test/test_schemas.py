import pytest

from marketwatch.schemas import *


@pytest.fixture
def game_settings():
    return GameSettings()


def test_game_settings_init(game_settings):
    assert game_settings.game is None
    assert game_settings.private is None
    assert game_settings.player_portfolios is None
    assert game_settings.starting_balance is None
    assert game_settings.commission is None
    assert game_settings.credit_interest_rate is None
    assert game_settings.leverage_debt_interest_rate is None
    assert game_settings.minimum_stock_price is None
    assert game_settings.maximum_stock_price is None
    assert game_settings.short_selling is None
    assert game_settings.margin_trading is None
    assert game_settings.limit_orders is None
    assert game_settings.stop_loss_trades is None
    assert game_settings.partial_share_trading is None


def test_game_settings_str(game_settings):
    game_settings.game = "My Game"
    game_settings.private = True
    game_settings.player_portfolios = ["player1", "player2"]
    game_settings.starting_balance = 10000
    game_settings.commission = 0.01
    game_settings.credit_interest_rate = 0.05
    game_settings.leverage_debt_interest_rate = 0.1
    game_settings.minimum_stock_price = 1
    game_settings.maximum_stock_price = 100
    game_settings.short_selling = True
    game_settings.margin_trading = True
    game_settings.limit_orders = True
    game_settings.stop_loss_trades = True
    game_settings.partial_share_trading = True

    assert (
        str(game_settings)
        == "GameSettings(game=My Game, private=True, player_portfolios=['player1', 'player2'], starting_balance=10000, commission=0.01, credit_interest_rate=0.05, leverage_debt_interest_rate=0.1, minimum_stock_price=1, maximum_stock_price=100, short_selling=True, margin_trading=True, limit_orders=True, stop_loss_trades=True, partial_share_trading=True)"
    )


def test_order():
    # Create an order
    order = Order(1, "AAPL", 10, "buy", "limit", 100.0)

    # Test that the properties are set correctly
    assert order.id == 1
    assert order.ticker == "AAPL"
    assert order.quantity == 10
    assert order.orderType == "buy"
    assert order.priceType == "limit"
    assert order.price == 100.0

    # Test the __str__ and __repr__ methods
    assert (
        str(order)
        == "Order(id=1, ticker=AAPL, quantity=10, orderType=buy, priceType=limit, price=100.0)"
    )
    assert (
        repr(order)
        == "Order(id=1, ticker=AAPL, quantity=10, orderType=buy, priceType=limit, price=100.0)"
    )


@pytest.fixture
def position():
    return Position("AAPL", "buy", 10, 100)


def test_position_creation(position):
    assert position.ticker == "AAPL"
    assert position.orderType == "buy"
    assert position.quantity == 10
    assert position.entry_price == 100


def test_position_string_representation(position):
    assert (
        str(position)
        == "Position(ticker=AAPL, orderType=buy, quantity=10, entry_price=100)"
    )


def test_position_repr_representation(position):
    assert (
        repr(position)
        == "Position(ticker=AAPL, orderType=buy, quantity=10, entry_price=100)"
    )
