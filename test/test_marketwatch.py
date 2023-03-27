import pytest

from marketwatch import MarketWatch
from marketwatch import MarketWatchException


@pytest.fixture
def authenticated_marketwatch():
    email = "user@example.com"
    password = "password"
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


# def test_get_games():
#     mw = MarketWatch("","" )
#     mw.get_games()
