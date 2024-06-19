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
        
def test_get_holdings_with_fund_ticker(authenticated_marketwatch):
    mw = authenticated_marketwatch
    ticker = "aiq"
    result = mw.get_holdings(ticker)
    
    # Verificar que el resultado es un diccionario
    assert result is not None
    assert isinstance(result, dict)
    
    # Verificar campos generales
    assert "ticker" in result
    assert result["ticker"] == "AIQ"
    assert "sector_allocation" in result
    assert isinstance(result["sector_allocation"], dict)
    assert "top_holdings" in result
    assert isinstance(result["top_holdings"], list)
    
    # Verificar contenido de sector_allocation
    sector_allocation = result["sector_allocation"]
    assert "Technology" in sector_allocation
    assert "Consumer Services" in sector_allocation
    assert "Industrials" in sector_allocation
    
    # Verificar contenido de top_holdings
    top_holdings = result["top_holdings"]
    assert len(top_holdings) > 0
    assert all(isinstance(item, dict) for item in top_holdings)
    assert all("company" in item for item in top_holdings)
    assert all("symbol" in item for item in top_holdings)
    assert all("net_assets" in item for item in top_holdings)

def test_get_holdings_with_stock_ticker(authenticated_marketwatch):
    mw = authenticated_marketwatch
    ticker = "meli"
    
    with pytest.raises(MarketWatchException) as exc_info:
        mw.get_holdings(ticker)
    
    assert str(exc_info.value) == "Other error occurred: The ticker MELI is not a fund, it is a stock or index."
    
    ticker_index = "spx"
    
    with pytest.raises(MarketWatchException) as exc_info:
        mw.get_holdings(ticker_index)
        
    assert str(exc_info.value) == "Other error occurred: The ticker SPX is not a fund, it is a stock or index."