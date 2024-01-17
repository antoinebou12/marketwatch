import os
from datetime import datetime

import pytest

from marketwatch import MarketWatch
from marketwatch import MarketWatchException
from marketwatch.schemas import OrderType
from marketwatch.schemas import Position
from marketwatch.schemas import PriceType
from marketwatch.schemas import Term


GAME_OWNER = "marketwatchapiunittest"
GAME = "algoets-h2023"


def is_stock_market_open():
    # Get the current day and time
    now = datetime.now()
    weekday = now.weekday()
    if weekday >= 5:
        return False
    if now.hour < 9 or now.hour > 16:
        return False
    if now.hour == 9 and now.minute < 30:
        return False
    return True


@pytest.fixture
def authenticated_marketwatch():
    username = os.environ.get("MARKETWATCH_USERNAME")
    password = os.environ.get("MARKETWATCH_PASSWORD")
    email = username
    password = password
    try:
        return MarketWatch(email, password)
    except MarketWatchException as e:
        pytest.fail(f"Failed to authenticate: {e}")


def test_authenticated_marketwatch(authenticated_marketwatch):
    mw = authenticated_marketwatch
    # Verify that the login was successful
    assert mw.check_login() is True
    # Verify that we can get the user ID
    user_id = mw.get_user_id()
    assert user_id is not None
    assert isinstance(user_id, str)


def test_marketwatch_exception():
    with pytest.raises(MarketWatchException):
        raise MarketWatchException("Test")


def test_get_client_id(authenticated_marketwatch):
    mw = authenticated_marketwatch
    assert mw.get_client_id() == "5hssEAdMy0mJTICnJNvC9TXEw3Va7jfO"


def test_generate_csrf_token(authenticated_marketwatch):
    mw = authenticated_marketwatch
    assert mw.generate_csrf_token() is not None


def test_get_user_id(authenticated_marketwatch):
    mw = authenticated_marketwatch
    mw.get_user_id()


def test_get_games(authenticated_marketwatch):
    mw = authenticated_marketwatch
    games = mw.get_games()
    assert games is not None
    assert isinstance(games, list)
    assert len(games) > 0
    assert isinstance(games[0], dict)
    assert "name" in games[0]
    assert "url" in games[0]
    assert "id" in games[0]
    assert "return" in games[0]
    assert "total_return" in games[0]
    assert "rank" in games[0]
    assert "end" in games[0]
    assert "players" in games[0]


def test_get_game(authenticated_marketwatch):
    mw = authenticated_marketwatch
    game = mw.get_game(GAME_OWNER)
    assert game is not None
    assert isinstance(game, dict)
    assert "name" in game
    assert "title" in game
    assert "time" in game
    assert "url" in game
    assert "start_date" in game
    assert "end_date" in game
    assert "players" in game
    assert "creator" in game
    assert "rank" in game
    assert "portfolio_value" in game
    assert "gain_percentage" in game
    assert "gain" in game
    assert "return" in game
    assert "cash_remaining" in game
    assert "buying_power" in game
    assert "shorts_reserve" in game
    assert "cash_borrowed" in game
    assert "ledger_id" in game


def test_get_leaderboard(authenticated_marketwatch):
    mw = authenticated_marketwatch
    leaderboard = mw.get_leaderboard(GAME_OWNER)
    assert leaderboard is not None
    assert isinstance(leaderboard, list)
    assert len(leaderboard) > 0
    assert isinstance(leaderboard[0], dict)
    assert "rank" in leaderboard[0]
    assert "player" in leaderboard[0]
    assert "player_url" in leaderboard[0]
    assert "portfolio_value" in leaderboard[0]
    assert "gain_percentage" in leaderboard[0]
    assert "transactions" in leaderboard[0]
    assert "gain" in leaderboard[0]


def test_get_portfolio(authenticated_marketwatch):
    if not is_stock_market_open():
        pytest.skip("Stock market is closed, skipping test.")
    mw = authenticated_marketwatch
    portfolio = mw.get_portfolio(GAME_OWNER)
    assert portfolio is not None
    assert isinstance(portfolio, dict)
    assert "portfolio" in portfolio
    assert "portfolio_value" in portfolio
    assert "return" in portfolio
    assert "cash_remaining" in portfolio
    assert "buying_power" in portfolio
    assert "shorts_reserve" in portfolio
    assert "cash_borrowed" in portfolio
    assert "portfolio_allocation" in portfolio

    _extracted_from_test_get_portfolio(portfolio, "portfolio", "quantity")
    assert "sign" in portfolio["portfolio"][0]
    assert "holding" in portfolio["portfolio"][0]
    assert "holding_percentage" in portfolio["portfolio"][0]
    assert "price" in portfolio["portfolio"][0]
    assert "price_gain" in portfolio["portfolio"][0]
    assert "price_gain_percentage" in portfolio["portfolio"][0]
    assert "value" in portfolio["portfolio"][0]
    assert "value_point" in portfolio["portfolio"][0]
    assert "value_percentage" in portfolio["portfolio"][0]

    assert isinstance(portfolio["portfolio_value"], str)
    assert isinstance(portfolio["gain_percentage"], str)
    assert isinstance(portfolio["gain"], str)
    assert isinstance(portfolio["return"], str)
    assert isinstance(portfolio["cash_remaining"], str)
    assert isinstance(portfolio["buying_power"], str)
    assert isinstance(portfolio["shorts_reserve"], str)
    assert isinstance(portfolio["cash_borrowed"], str)

    _extracted_from_test_get_portfolio(portfolio, "portfolio_allocation", "amount")


def _extracted_from_test_get_portfolio(portfolio, arg1, arg2):
    assert isinstance(portfolio[arg1], list)
    assert len(portfolio[arg1]) >= 0


def test_get_price(authenticated_marketwatch):
    mw = authenticated_marketwatch
    price = mw.get_price("aapl")
    assert price is not None
    assert isinstance(price, str)
    assert price.__contains__("$")
    assert price.__contains__(".")
    assert price.__contains__("AAPL")
    assert price != ""


def test_get_search(authenticated_marketwatch):
    mw = authenticated_marketwatch
    search = mw.get_search("aapl")
    assert search is not None
    assert isinstance(search, dict)
    assert "chartingSymbol" in search
    assert "company" in search
    assert "country" in search
    assert "djnSymbol" in search
    assert "exchange" in search
    assert "exchangeIsoCode" in search
    assert "factivaCode" in search
    assert "isFuture" in search
    assert "quote" in search
    assert "ticker" in search
    assert "type" in search


def test_buy(authenticated_marketwatch):
    mw = authenticated_marketwatch
    payload = mw.buy(GAME_OWNER, "aapl", 1)
    assert payload is not None
    assert payload == "Submitted"


def test_short(authenticated_marketwatch):
    mw = authenticated_marketwatch
    payload = mw.short(GAME_OWNER, "aapl", 1)
    assert payload is not None
    assert payload is not None
    assert payload == "Submitted"


def test_sell(authenticated_marketwatch):
    mw = authenticated_marketwatch
    payload = mw.sell(GAME_OWNER, "aapl", 1)
    assert payload is not None
    assert payload is not None
    assert payload == "Submitted"


def test_cover(authenticated_marketwatch):
    mw = authenticated_marketwatch
    payload = mw.cover(GAME_OWNER, "aapl", 1)
    assert payload is not None
    assert payload is not None
    assert payload == "Submitted"


def test_submit(authenticated_marketwatch):
    mw = authenticated_marketwatch
    payload = mw._create_payload(
        GAME_OWNER,
        "aapl",
        1,
        PriceType.MARKET,
        0,
        OrderType.BUY,
        Term.INDEFINITE,
    )
    response = mw._submit(
        GAME_OWNER,
        {
            "djid": "13-3122",
            "ledgerId": "_7g9NEC9_Eqy",
            "tradeType": "Buy",
            "shares": 1,
            "expiresEndOfDay": False,
            "orderType": "Market",
        },
    )
    assert response is not None
    assert isinstance(response, str)
    assert response == "Submitted"


def test__get_order_type(authenticated_marketwatch):
    mw = authenticated_marketwatch
    order_type = mw._get_order_type("buy")
    assert order_type is not None
    assert isinstance(order_type, OrderType)
    assert order_type == OrderType.BUY

    order_type = mw._get_order_type("short")
    assert order_type is not None
    assert isinstance(order_type, OrderType)
    assert order_type == OrderType.SHORT

    order_type = mw._get_order_type("cover")
    assert order_type is not None
    assert isinstance(order_type, OrderType)
    assert order_type == OrderType.COVER

    order_type = mw._get_order_type("sell")
    assert order_type is not None
    assert isinstance(order_type, OrderType)
    assert order_type == OrderType.SELL


def test__get_price_type(authenticated_marketwatch):
    mw = authenticated_marketwatch
    price_type = mw._get_price_type("market")
    assert price_type is not None
    assert isinstance(price_type, PriceType)
    assert price_type == PriceType.MARKET

    price_type = mw._get_price_type("limit")
    assert price_type is not None
    assert isinstance(price_type, PriceType)
    assert price_type == PriceType.LIMIT

    price_type = mw._get_price_type("stop")
    assert price_type is not None
    assert isinstance(price_type, PriceType)
    assert price_type == PriceType.STOP


def test__get_order_price(authenticated_marketwatch):
    mw = authenticated_marketwatch
    price = mw._get_order_price("buy aapl 1")
    assert price is None

    price = mw._get_order_price("buy aapl 1 $1.0")
    assert price is not None
    assert isinstance(price, float)
    assert price == 1.0


def test_get_positions(authenticated_marketwatch):
    mw = authenticated_marketwatch
    positions = mw.get_positions(GAME)
    assert positions is not None
    assert isinstance(positions, list)
    assert len(positions) > 0
    assert isinstance(positions[0], Position)
    assert positions[0].ticker is not None
    assert positions[0].orderType is not None
    assert positions[0].quantity is not None
    assert positions[0].entry_price is not None


def test_get_game_settings(authenticated_marketwatch):
    mw = authenticated_marketwatch
    settings = mw.get_game_settings(GAME)
    assert settings is not None
    assert isinstance(settings, dict)
    assert settings["game_public"] is not None
    assert settings["portfolios_public"] is not None
    assert settings["start_balance"] is not None
    assert settings["commission"] is not None
    assert settings["credit_interest_rate"] is not None
    assert settings["leverage_debt_interest_rate"] is not None
    assert settings["minimum_stock_price"] is not None
    assert settings["maximum_stock_price"] is not None
    assert settings["short_selling_enabled"] is not None
    assert settings["margin_trading_enabled"] is not None
    assert settings["limit_orders_enabled"] is not None
    assert settings["stop_loss_orders_enabled"] is not None
    assert settings["partial_share_trading_enabled"] is not None


def test__clean_text(authenticated_marketwatch):
    mw = authenticated_marketwatch
    _extracted_from_test__clean_text(mw, "buy aapl 1 $1.0")
    _extracted_from_test__clean_text(mw, "buy aapl 1 $1.0 ")
    _extracted_from_test__clean_text(mw, " buy aapl 1 $1.0  ")


def _extracted_from_test__clean_text(mw, arg1):
    result = mw._clean_text(arg1)
    assert result is not None
    assert isinstance(result, str)
    assert result == "buyaapl1$1.0"

    return result

def test_check_error_game(authenticated_marketwatch):
    mw = authenticated_marketwatch
    mw.check_error_game()

def test__get_ticker_uid(authenticated_marketwatch):
    mw = authenticated_marketwatch
    ticker_uid = mw._get_ticker_uid("aapl")
    assert ticker_uid is not None
    assert isinstance(ticker_uid, str)
    assert ticker_uid == "STOCK/US/XNAS/AAPL"

def test_create_watchlist(authenticated_marketwatch):
    mw = authenticated_marketwatch
    watchlist = mw.create_watchlist("test")
    assert watchlist is not None
    assert isinstance(watchlist, dict)
    assert watchlist["Id"] is not None
    assert watchlist["Name"] == "test"
    assert watchlist["TotalItemCount"] == 0
    assert watchlist["Revision"] == 0
    assert watchlist["Items"] == []
    assert watchlist["CreateDateUtc"] is not None
    assert watchlist["LastModifiedDateUtc"] is not None
    mw.delete_watchlist(watchlist["Id"])

def test_delete_watchlist(authenticated_marketwatch):
    mw = authenticated_marketwatch
    watchlist = mw.create_watchlist("test")
    assert watchlist is not None
    mw.delete_watchlist(watchlist["Id"])
    watchlists = mw.get_watchlists()
    assert watchlists is not None
    assert isinstance(watchlists, list)
    assert len(watchlists) == 1

def test_get_watchlists(authenticated_marketwatch):
    mw = authenticated_marketwatch
    watchlist = mw.create_watchlist("test")
    assert watchlist is not None
    assert isinstance(watchlist, dict)
    assert watchlist["Id"] is not None
    assert watchlist["Name"] == "test"
    assert watchlist["TotalItemCount"] == 0
    assert watchlist["Revision"] == 0
    assert watchlist["Items"] == []
    assert watchlist["CreateDateUtc"] is not None
    assert watchlist["LastModifiedDateUtc"] is not None
    watchlists = mw.get_watchlists()
    assert watchlists is not None
    assert isinstance(watchlists, list)
    assert len(watchlists) == 2
    mw.delete_watchlist(watchlist["Id"])

def test_add_to_watchlist(authenticated_marketwatch):
    mw = authenticated_marketwatch
    timestamp = str(datetime.now().timestamp())
    watchlist = mw.create_watchlist(timestamp)
    watchlist = mw.add_to_watchlist(watchlist["Id"], ["AAPL"])
    assert watchlist is not None
    assert isinstance(watchlist, dict)
    assert watchlist["Id"] is not None
    assert watchlist["Name"] == timestamp
    assert watchlist["TotalItemCount"] == 1
    assert watchlist["Revision"] == 1
    assert watchlist["Items"] is not None
    assert isinstance(watchlist["Items"], list)
    assert len(watchlist["Items"]) == 1
    assert watchlist["Items"][0]["ChartingSymbol"] == "STOCK/US/XNAS/AAPL"
    mw.delete_watchlist_item(watchlist["Id"], "AAPL")
    mw.delete_watchlist(watchlist["Id"])

# def test_create_game(marketwatch):
#     # Créer un nouveau jeu avec les paramètres spécifiés
#     name = "Mon nouveau jeu"
#     start_balance = 100000
#     duration = 30
#     game_id = marketwatch.create_game(name, start_balance, duration)

#     # Vérifier que le jeu a été créé avec succès
#     assert isinstance(game_id, int)

#     # Supprimer le jeu nouvellement créé
#     marketwatch.delete_game(game_id)
