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

def test_get_price_fund(authenticated_marketwatch):
    mw = authenticated_marketwatch
    price = mw.get_price("AIQ")
    assert price is not None
    assert isinstance(price, str)
    assert "$" in price
    assert "." in price
    assert "AIQ" in price
    assert price != ""