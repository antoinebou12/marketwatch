import os
from datetime import datetime

import pytest

from marketwatch import MarketWatch
from marketwatch import MarketWatchException

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

def test_get_price_stock(authenticated_marketwatch):
    mw = authenticated_marketwatch
    price = mw.get_price("MELI")
    assert price is not None
    assert isinstance(price, str)
    assert "$" in price
    assert "." in price
    assert "MELI" in price
    assert price != ""
    price = mw.get_price("AIQ")
    assert price is not None
    assert isinstance(price, str)
    assert "$" in price
    assert "." in price
    assert "AIQ" in price
    assert price != ""
    
def test_get_ticker_info(authenticated_marketwatch):
    mw = authenticated_marketwatch
    ticker_info = mw.get_ticker_info("MELI")
    assert ticker_info is not None
    assert isinstance(ticker_info, dict)
    
    # Check general fields
    assert "ticker" in ticker_info
    assert ticker_info["ticker"] == "MELI"
    assert "price" in ticker_info
    assert "change" in ticker_info
    assert "percent_change" in ticker_info

    # Check key data
    assert "Day Range" in ticker_info
    assert "Low" in ticker_info["Day Range"]
    assert "High" in ticker_info["Day Range"]

    assert "52 Week Range" in ticker_info
    assert "Low" in ticker_info["52 Week Range"]
    assert "High" in ticker_info["52 Week Range"]

    # Optionally check for after_hours if it exists
    if "after_hours" in ticker_info:
        after_hours = ticker_info["after_hours"]
        assert "price" in after_hours
        assert "change" in after_hours
        assert "percent_change" in after_hours

    # Optionally check for performance data if it exists
    if "performance" in ticker_info:
        performance = ticker_info["performance"]
        assert isinstance(performance, dict)
        assert "5 Day" in performance
        assert "1 Month" in performance
        assert "3 Month" in performance
        assert "YTD" in performance
        assert "1 Year" in performance