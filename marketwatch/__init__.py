"""
MarketWatch API using Python

This is a Python API for the MarketWatch game. It allows you to get your
portfolio, place orders, and get the leaderboard.

Example:
	>>> from marketwatch import MarketWatch
    >>> import os
	>>> mw = MarketWatch(os.environ["MARKETWATCH_USERNAME"], os.environ["MARKETWATCH_PASSWORD"])
	>>> mw.get_games()
	>>> mw.get_portfolio(1234)
	>>> mw.buy(1234, "AAPL", 1)
	>>> mw.get_leaderboard(1234)
"""
import platform
from time import sleep
import csv
import json
from typing import List

import httpx
from bs4 import BeautifulSoup
from rich.progress import track

from marketwatch.exceptions import MarketWatchException
from marketwatch.schemas import Order
from marketwatch.schemas import OrderType
from marketwatch.schemas import Position
from marketwatch.schemas import PriceType
from marketwatch.schemas import Term


class MarketWatch:
    """
    MarketWatch API

    :param email: Email
    :param password: Password
    """

    def __init__(self, email: str, password: str):
        """
        Initialize the MarketWatch API

        :param email: Email
        :param password: Password

        :return: None

        """
        self.session = httpx.Client()

        self.email = email
        self.password = password
        self.client_id = self.get_client_id()
        self.login()

        self.user_id = self.get_user_id()
        self.ledger_id = None
        self.games = None

    def generate_csrf_token(self) -> str:
        """
        Get the csrf token from the login page

        :return: CSRF Token
        """
        try:
            sleep(2)
            client = self.session.get("https://sso.accounts.dowjones.com/login-page")
            return client.cookies["csrf"]
        except KeyError as e:
            raise MarketWatchException("Failed to generate csrf token from cookies {e}")
        except httpx.HTTPError as e:
            raise MarketWatchException("Failed to generate csrf token from httpx {e}")
        except Exception as e:
            raise MarketWatchException(f"Failed to generate csrf token from unknown {e}")

    def get_client_id(self) -> str:
        """
        Generate a client id

        :return: Client ID
        """
        return "5hssEAdMy0mJTICnJNvC9TXEw3Va7jfO"

    def get_user_id(self):
        try: 
            user = self.session.post(
                "https://sso.accounts.dowjones.com/getuser",
                data={
                    "username": self.email,
                    "csrf": self.generate_csrf_token(),
                },
            )

            if user.status_code == 200:
                return user.json()["id"]
            else:
                raise MarketWatchException("Failed to get user id")

        except KeyError as e:
            raise MarketWatchException("Failed to get user id from cookies {e}")
        except httpx.HTTPError as e:
            raise MarketWatchException("Failed to get user id from httpx {e}")
        except Exception as e:
            raise MarketWatchException(f"Failed to get user id from unknown {e}")

    def get_ledger_id(self, game_id) -> str:
        """
        Get the ledger id

        :param game_id: Game ID
        """
        game_page = self.session.get(f"https://www.marketwatch.com/games/{game_id}")

        if game_page.status_code != 200:
            raise MarketWatchException("Game not found")
        soup = BeautifulSoup(game_page.text, "html.parser")

        return soup.find("canvas", {"id": "j-chartjs-performance"})["data-pub"]
    
    def get_user_agent(self):
        os_name = platform.system()
        if os_name == 'Windows':
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        elif os_name == 'Darwin':
            return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        elif os_name == 'Linux':
            return "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        else:
            return "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2)"

    def login(self):
        """
        Login to the MarketWatch API

        :return: None
        """

        # https://sso.accounts.dowjones.com/authorize?response_type=id_token&nonce=foobar&ui_locales=en-us-x-wsj-3-0&scope=email%2Cfirst_name%2Clast_name%2Croles%2Copenid%2Cuuid&client_id=5hssEAdMy0mJTICnJNvC9TXEw3Va7jfO&redirect_uri=${CALLBACK_URI}
        login_data = {
            "client_id": self.client_id,
            "connection": "DJldap",
            "headers": {
                "User-Agent": self.get_user_agent(),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/json;charset=utf-8",
                "Origin": "https://accounts.marketwatch.com",
                "Connection": "keep-alive",
                "Referer": "https://accounts.marketwatch.com/login-page/signin",
                "TE": "Trailers",
                "X-REMOTE-USER": self.email,
                "x-_dj-_client__id": self.client_id,
                "x-_oidc-_provider": "localop",
            },
            "nonce": "0590aaf2-c662-4fc4-9edc-81727f80798c",
            "ns": "prod/accounts-mw",
            "password": self.password,
            "protocol": "oauth2",
            "redirect_uri": "https://accounts.marketwatch.com/login-page/callback",
            "response_type": "code",
            "scope": "openid idp_id roles email given_name family_name djid djUsername djStatus trackid tags prts suuid updated_at",
            "tenant": "sso",
            "username": self.email,
            "ui_locales": "en-us-x-mw-11-8",
            "_csrf": self.generate_csrf_token(),
            "_intstate": "deprecated",
        }
        try:
            login = self.session.post(
                "https://sso.accounts.dowjones.com/authenticate", data=login_data
            )
        except httpx.HTTPError as e:
            raise MarketWatchException("Failed to login to MarketWatch {e}")
        except Exception as e:
            raise MarketWatchException(f"Failed to login to MarketWatch {e}")

        if login.status_code == 401:
            print(login.url)
            print(login.content)
            raise MarketWatchException("Login failed check your credentials")

        # Get the token value from the response
        response_data = BeautifulSoup(login.text, "html.parser")

        # Get the token value from the response
        token = response_data.find("input", {"name": "token"})["value"]
        params = response_data.find("input", {"name": "params"})["value"]

        data = {
            "token": token,
            "params": params,
        }

        try:
            response = self.session.post(
                "https://sso.accounts.dowjones.com/postauth/handler",
                data=data,
                follow_redirects=True,
            )
        except httpx.HTTPError as e:
            raise MarketWatchException("Failed to login to MarketWatch {e}")
        except Exception as e:
            raise MarketWatchException(f"Failed to login to MarketWatch {e}")
        
        try:
            response = self.session.post(
                "https://sso.accounts.dowjones.com/postauth/handler",
                data=data,
                follow_redirects=True,
            )
        except httpx.HTTPError as e:
            raise MarketWatchException("Failed to login to MarketWatch {e}")
        except Exception as e:
            raise MarketWatchException(f"Failed to login to MarketWatch {e}")

        if response.status_code in [200, 302]:
            print("Login successful")

        # check if the login was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            username = soup.find(
                "li", {"class": "profile__item profile--name divider"}
            ).text.strip()
            print(f"Logged in as {username}")

            # set all the response cookies to the session
            for cookie in response.cookies.items():
                self.session.cookies.set(cookie[0], cookie[1])

    def check_login(self):
        """
        Check if the user is logged in

        :return: True if logged in else False
        """
        # Check if the user is logged in
        response = self.session.get("https://www.marketwatch.com")
        if response.status_code != 200:
            return False
        soup = BeautifulSoup(response.text, "html.parser")
        return bool(
            username := soup.find(
                "li", {"class": "profile__item profile--name divider"}
            ).text.strip()
        )

    # auth decorator in class
    def auth(func):
        def wrapper(self, *args, **kwargs):
            if not self.check_login():
                self.login()
            return func(self, *args, **kwargs)

        return wrapper

    @auth
    def get_games(self):
        """
        Get all the games
        [{'name': 'ALGOETS-H2023', 'url': 'https://www.marketwatch.com/games/algoets-h2023', 'id': 'algoets-h2023',
                        'return': '0.00%', 'total_return': '-$3,710.85', 'rank': '15', 'end': '3/31/23', 'players': '27'}]

                        :return: List of games
        """
        games_page = self.session.get("https://www.marketwatch.com/games")

        if games_page.status_code != 200:
            raise MarketWatchException("Failed to get games")

        soup = BeautifulSoup(games_page.text, "html.parser")

        games = soup.find("table", {"class": "your-games"})
        if games is None:
            raise MarketWatchException("No games found")
        games = games.find("tbody").find_all("tr")

        games_data = []

        for game in games:
            game_data = game.find_all("td")
            game_name = game_data[0].find("a").text
            game_url = game_data[0].find("a")["href"]
            game_id = game_url.split("/")[-1]
            game_return = game_data[1].text
            game_total_return = game_data[2].text
            game_rank = game_data[3].text
            game_end = game_data[4].text
            game_players = game_data[5].text

            games_data.append(
                {
                    "name": game_name,
                    "url": game_url,
                    "id": game_id,
                    "return": game_return,
                    "total_return": game_total_return,
                    "rank": game_rank,
                    "end": game_end,
                    "players": game_players,
                }
            )
        return games_data

    @auth
    def create_game(self, name: str, start_date: int, end_date: int, **kwargs) -> dict:
        """
        Create a game on MarketWatch.

        Args:
            name (str): Name of the game to create.
            start_date (int): Start date of the game in epoch time.
            end_date (int): End date of the game in epoch time.
            **kwargs: Additional optional parameters to configure the game.

        Returns:
            dict: A dictionary containing information about the created game.

        Raises:
            MarketWatchException: If game creation fails.
        """
        url = 'https://vse-api.marketwatch.com/v1/games'
        headers = {'Content-Type': 'application/json'}

        # Construct payload with default and optional parameters
        payload = {
            "name": name,
            "uri": kwargs.get('uri', name),
            "startDateUtc": start_date,
            "endDateUtc": end_date,
            "allowJoinAfterStart": kwargs.get('allowJoinAfterStart', True),
            "privacyPortfolios": kwargs.get('privacyPortfolios', 'public'),
            "privacyGame": kwargs.get('privacyGame', 'public'),
            "allowComment": kwargs.get('allowComment', True),
            "description": kwargs.get('description', ''),
            "startingAmount": kwargs.get('startingAmount', 100000),
            "commissionPerTrade": kwargs.get('commissionPerTrade', 10),
            "creditInterestRate": kwargs.get('creditInterestRate', 0),
            "debitInterestRate": kwargs.get('debitInterestRate', 0),
            "minimumTradePrice": kwargs.get('minimumTradePrice', 2),
            "maximumTradePrice": kwargs.get('maximumTradePrice', 500000),
            "allowShortSelling": kwargs.get('allowShortSelling', True),
            "marginEnabled": kwargs.get('marginEnabled', True),
            "allowLimitOrders": kwargs.get('allowLimitOrders', False),
            "allowStopOrders": kwargs.get('allowStopOrders', False),
            "allowPartialShares": kwargs.get('allowPartialShares', False),
        }

        # Make request to create game
        response = self.session.post(
            url,
            headers=headers,
            json=payload,
        )

        # Raise exception if game creation fails
        if response.status_code != 200:
            raise MarketWatchException('Failed to create game')

        # Return information about created game
        return self.get_game(name)

    @auth
    def reset_game(self, game_id: str):
        """
        Reset the game.
        
        :param game_id: Game ID
        :return: None
        """
        url = f"https://vse-api.marketwatch.com/v1/reset/{game_id}"
        response = self.session.post(url)
            
        if response.status_code != 200:
            raise MarketWatchException("Failed to reset game")


    # @auth
    # def modify_game(self, game_id: str, **kwargs) -> dict:
    #     game_settings = self.get_game_settings(game_id)
    #     headers = {'Content-Type': 'application/json'}
    #     # Construct payload with default and optional parameters
    #     payload = {
    #         "name": kwargs.get('name', 'testgame'),
    #         "uri": kwargs.get('uri', 'testgame'),
    #         "startDateUtc": kwargs.get('startDateUtc', 1635619200),
    #         "endDateUtc": kwargs.get('endDateUtc', 1635619200),
    #         "allowJoinAfterStart": kwargs.get('allowJoinAfterStart', True),
    #         "privacyPortfolios": kwargs.get('privacyPortfolios', 'public'),
    #         "privacyGame": kwargs.get('privacyGame', 'public'),
    #         "allowComment": kwargs.get('allowComment', True),
    #         "description": kwargs.get('description', ''),
    #         "startingAmount": kwargs.get('startingAmount', 100000),
    #         "commissionPerTrade": kwargs.get('commissionPerTrade', 10),
    #         "creditInterestRate": kwargs.get('creditInterestRate', 0),
    #         "debitInterestRate": kwargs.get('debitInterestRate', 0),
    #         "minimumTradePrice": kwargs.get('minimumTradePrice', 2),
    #         "maximumTradePrice": kwargs.get('maximumTradePrice', 500000),
    #         "allowShortSelling": kwargs.get('allowShortSelling', True),
    #         "marginEnabled": kwargs.get('marginEnabled', True),
    #         "allowLimitOrders": kwargs.get('allowLimitOrders', False),
    #         "allowStopOrders": kwargs.get('allowStopOrders', False),
    #         "allowPartialShares": kwargs.get('allowPartialShares', False),
    #     }


    @auth
    def get_game(self, game_id: str) -> list:
        """
        Get a game
        {
        'name': 'algoets-h2023',
        'title': 'ALGOETS-H2023',
        'time': 'Game ends in 4 days',
        'url': 'https://www.marketwatch.com/games/algoets-h2023',
        'start_date': 'Mar 20, 2023', 'end_date': 'Mar 31, 2023',
        'players': '27', 'creator': 'Mohamed Ilias',
        'rank': '15', 'portfolio_value': '$996,289.15',
        'gain_percentage': '0.00%', 'gain': '-$3,710.85',
        'return': '-0.37%', 'cash_remaining': '$249,845.55',
        'buying_power': '$143,734.12',
        'shorts_reserve': '$0.00',
        'cash_borrowed': '$0.00'
        }

        :param game_id: Game id
        :return: Game data
        """
        game_page = self.session.get(f"https://www.marketwatch.com/games/{game_id}")

        if game_page.status_code != 200:
            raise MarketWatchException("Game not found")
        soup = BeautifulSoup(game_page.text, "html.parser")

        game_title = soup.find("h1", {"class": "game__title"}).text
        game_time = soup.find("div", {"class": "game__time"}).text
        game_url = game_page.url

        game_description = soup.find("div", {"class": "about-game"}).find_all(
            "li", {"class": "kv__item"}
        )
        descriptions = [
            description.find("span", {"class": "primary"}).text
            for description in game_description
        ]
        game_start_date = descriptions[0]
        game_end_date = descriptions[1]
        game_players = descriptions[2]
        game_creator = descriptions[3]

        game_rank = soup.find("div", {"class": "rank__number"}).text

        profile = soup.find("div", {"class": "element--profile"}).find_all(
            "li", {"class": "kv__item"}
        )
        elements = [
            element.find("span", {"class": "primary"}).text for element in profile
        ]
        game_portfolio_value = elements[0]
        game_gain_percentage = elements[1]
        game_gain = elements[2]
        game_return = elements[3]
        game_cash_remaining = elements[4]
        game_buying_power = elements[5]
        game_shorts_reserve = elements[6]
        game_cash_borrowed = elements[7]

        ledger_id = soup.find("canvas", {"id": "j-chartjs-performance"})["data-pub"]

        return {
            "name": game_id,
            "title": game_title.strip(),
            "time": game_time,
            "url": str(game_url),
            "start_date": game_start_date,
            "end_date": game_end_date,
            "players": game_players,
            "creator": game_creator,
            "rank": game_rank,
            "portfolio_value": game_portfolio_value,
            "gain_percentage": game_gain_percentage,
            "gain": game_gain,
            "return": game_return,
            "cash_remaining": game_cash_remaining,
            "buying_power": game_buying_power,
            "shorts_reserve": game_shorts_reserve,
            "cash_borrowed": game_cash_borrowed,
            "ledger_id": ledger_id,
        }

    def get_price(self, ticker: str) -> str:
        """
        Get the price of a stock from MarketWatch.

        :param ticker: Ticker symbol of the stock.
        :return: String in the format "TICKER : $PRICE" e.g., "AAPL : $137.00".
        """
        try:
            # Send a GET request to the MarketWatch URL for the given ticker
            url = f"https://www.marketwatch.com/investing/stock/{ticker.lower()}"
            response = self.session.get(url)
            response.raise_for_status()  # Will raise HTTPError for 4XX/5XX status

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Locate the price in the HTML
            # Adjust the selector as per the actual structure of the webpage
            price_container = soup.select_one('.intraday__price .value')
            if price_container:
                price = price_container.get_text(strip=True)
                return f"{ticker.upper()} : ${price}"
            else:
                raise MarketWatchException(f"Price not found for ticker {ticker}")

        except HTTPError as http_err:
            raise MarketWatchException(f"HTTP error occurred: {http_err}")
        except Exception as err:
            raise MarketWatchException(f"Other error occurred: {err}")

    @auth
    def get_portfolio(self, game_id: str):
        """
        Get the portfolio of a game
        {'portfolio': [{'ticker': 'AAPL', 'quantity': '200 Shares', 'holding': '\nBuy\n', 'holding_percentage': '4%', 'price': '$160.25', 'price_gain': '1.32', 'price_gain_percentage': '0.83%', 'value': '$32,050.00', 'gain': '$295.50', 'gain_percentage': '0.93%'}]

                        :param game_id: Game id

                        :return: Portfolio of the game
        """
        response = self.session.get(
            f"https://www.marketwatch.com/games/{game_id}/portfolio"
        )

        if response.status_code != 200:
            raise MarketWatchException("Game not found")

        soup = BeautifulSoup(response.text, "html.parser")

        profile = soup.find("div", {"class": "element--profile"}).find_all(
            "li", {"class": "kv__item"}
        )
        elements = [
            element.find("span", {"class": "primary"}).text for element in profile
        ]
        game_portfolio_value = elements[0]
        game_gain_percentage = elements[1]
        game_gain = elements[2]
        game_return = elements[3]
        game_cash_remaining = elements[4]
        game_buying_power = elements[5]
        game_shorts_reserve = elements[6]
        game_cash_borrowed = elements[7]

        table_element = soup.find("mw-table-dropdown")
        if table_element is None:
            
            return {}

        table = table_element.find("tbody").find_all("tr")

        portfolio = []

        for row in table:
            cells = row.find_all("td")
            sign = (
                "-"
                if cells[4]
                .find("small", {"class": "secondary"})
                .find("span", {"class": "point"})
                .text[0]
                == "-"
                else "+"
            )
            ticker = cells[1].find("a", {"class": "primary"}).find("mini-quote").text
            quantity = cells[1].find("div", {"class": "secondary"}).find("small").text
            holding = cells[2].find("div", {"class": "secondary"}).text
            holding_percentage = cells[2].find("div", {"class": "primary"}).text
            price = cells[3].find("div", {"class": "primary"}).text
            price_gain = (
                cells[3]
                .find("small", {"class": "secondary"})
                .find("span", {"class": "point"})
                .text
            )
            price_gain_percentage = (
                cells[3]
                .find("small", {"class": "secondary"})
                .find("span", {"class": "percent"})
                .text
            )
            value = cells[4].find("div", {"class": "primary"}).text
            value_point = (
                cells[4]
                .find("small", {"class": "secondary"})
                .find("span", {"class": "point"})
                .text
            )
            value_percentage = (
                cells[4]
                .find("small", {"class": "secondary"})
                .find("span", {"class": "percent"})
                .text
            )

            portfolio.append(
                {
                    "sign": sign,
                    "ticker": ticker,
                    "quantity": quantity,
                    "holding": holding,
                    "holding_percentage": holding_percentage,
                    "price": price,
                    "price_gain": price_gain,
                    "price_gain_percentage": price_gain_percentage,
                    "value": value,
                    "value_percentage": value_percentage,
                    "value_point": value_point,
                }
            )

        portfolio_allocation = soup.find(
            "div", {"class": "list list--allocation horizontal"}
        ).find_all("span", {"class": "list__item"})
        portfolio_allocation = []
        portfolio_allocation.extend(
            {
                "ticker": allocation.find("div", {"class": "tooltip left"})
                .find("span", {"class": "symbol"})
                .text,
                "amount": allocation.find("div", {"class": "tooltip left"})
                .find("span", {"class": "percent"})
                .text,
            }
            for allocation in track(portfolio_allocation)
        )

        return {
            "portfolio": portfolio,
            "portfolio_value": game_portfolio_value,
            "gain_percentage": game_gain_percentage,
            "gain": game_gain,
            "return": game_return,
            "cash_remaining": game_cash_remaining,
            "buying_power": game_buying_power,
            "shorts_reserve": game_shorts_reserve,
            "cash_borrowed": game_cash_borrowed,
            "portfolio_allocation": portfolio_allocation,
        }

    @auth
    def get_portfolio_performance(
        self, game_id: str, download: bool = False, next_page_url: str = None
    ):
        """
        Get the portfolio performance of a game

        :param game_id: Game id
        :param download: Download the portfolio performance
        :param next_page_url: Next page url

        :return: Portfolio performance of the game
        """
        if next_page_url is None:
            response = self.session.get(
                f"https://www.marketwatch.com/games/{game_id}/performance"
            )
        else:
            response = self.session.get(next_page_url)

        if response.status_code != 200:
            raise MarketWatchException("Game not found")

        soup = BeautifulSoup(response.text, "html.parser")

        ledger_id = self.get_ledger_id(game_id=game_id)
        table = (
            soup.find("div", {"class": "portfolio-performance"})
            .find("table", {"class": "table--primary"})
            .find("tbody")
            .find_all("tr")
        )

        if download:
            print("Downloaded")
            return self.session.get(
                f"https://www.marketwatch.com/games/{game_id}/download?view=performance&amp;pub={ledger_id}&amp;isDownload=true"
            )

        portfolio_performance = []

        for row in table:
            cells = row.find_all("td")
            portfolio_performance.append(
                {
                    "date": cells[0].text,
                    "cash": cells[1].text,
                    "market_value": cells[2].text,
                    "total_value": cells[3].text,
                    "return": cells[4].text,
                }
            )

        cursor_next = soup.find(
            "div", {"class": "element element--table portfolio-performance"}
        )["cursor-next"]

        if next_page := soup.find("a", {"class": "link align--right  j-next"}):
            portfolio_performance += self.get_portfolio_performance(
                game_id=game_id,
                download=download,
                next_page_url=f"https://www.marketwatch.com/games/{game_id}/performance?pub={ledger_id}&cursor={cursor_next}",
            )

        return portfolio_performance

    @auth
    def get_transactions(
        self, game_id: str, download: bool = False, next_page_url: str = None
    ):
        """
        Get the transactions of a game

        :param game_id: The game id
        :param download: Download the transactions as a csv file
        :param next_page_url: The next page url
        :return: A list of transactions
        """
        response = self.session.get(
            f"https://www.marketwatch.com/games/{game_id}/transactions"
        )

        if response.status_code != 200:
            raise MarketWatchException("Game not found")

        soup = BeautifulSoup(response.text, "html.parser")

        table = (
            soup.find("div", {"class": "element element--table transactions"})
            .find("tbody")
            .find_all("tr")
        )

        if download:
            return self.session.get(
                f"https://www.marketwatch.com/games/{game_id}/download?view=transactions&amp;pub=&amp;isDownload=true"
            )

        transactions = []

        for row in table:
            cells = row.find_all("td")
            transactions.append(
                {
                    "symbol": cells[0].text,
                    "buy_date": cells[1].text,
                    "sell_date": cells[2].text,
                    "type": cells[3].text,
                    "shares": cells[4].text,
                    "price": cells[5].text,
                }
            )

        cursor_next = soup.find(
            "div", {"class": "element element--table portfolio-performance"}
        )["cursor-next"]

        if next_page := soup.find("a", {"class": "link align--right  j-next"}):
            transactions += self.get_transactions(
                game_id=game_id,
                download=download,
                next_page_url=f"https://www.marketwatch.com/games/{game_id}/transactions?cursor={cursor_next}",
            )

        return transactions

    @auth
    def get_leaderboard(self, game_id: str, download: bool = False):
        """
        Get the leaderboard of a game
                        :param download: Download the leaderboard
        :param game_id: Game id

        :return: Leaderboard of the game
        """
        if download:
            return self.session.get(
                f"https://www.marketwatch.com/games/{game_id}/download?view=rankings&amp;pub=&amp;isDownload=true"
            )

        response = self.session.get(
            f"https://www.marketwatch.com/games/{game_id}/rankings"
        )
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"class": "table table--primary ranking"})
        rows = table.find_all("tr", {"class": "table__row"})
        players = []
        for row in track(rows):
            cells = row.find_all("td")
            rank = "N/A"
            player_name = "N/A"
            player_url = "N/A"
            portfolio_value = "N/A"
            gain_percentage = "N/A"
            transactions = "N/A"
            gain = "N/A"
            for cell in cells:
                if cell == cells[0]:
                    rank = cell.text
                elif cell == cells[1]:
                    player_name = cell.find("a", {"class": "link"}).text
                    player_url = cell.find("a", {"class": "link"})["href"]
                elif cell == cells[2]:
                    portfolio_value = cell.text
                elif cell == cells[3]:
                    gain_percentage = cell.text
                elif cell == cells[4]:
                    transactions = cell.text
                elif cell == cells[5]:
                    gain = cell.text
            players.append(
                {
                    "rank": rank,
                    "player": player_name,
                    "player_url": player_url,
                    "portfolio_value": portfolio_value,
                    "gain_percentage": gain_percentage,
                    "transactions": transactions,
                    "gain": gain,
                }
            )
        return players

    def get_search(self, search: str):
        """
        Get the search of a mw

        :param search: Search query

        :return: Search results
        """
        # https://api.wsj.net/api/autocomplete/search?q=AAPL&need=symbol&excludeExs=xmstar&maxRows=12&entitlementToken=cecc4267a0194af89ca343805a3e57af&it=stock,exchangetradedfund,fund&cc=us&xe=coindesk
        response = self.session.get(
            "https://api.wsj.net/api/autocomplete/search",
            params={
                "q": search,
                "need": "symbol",
                "excludeExs": "xmstar",
                "maxRows": 12,
                "entitlementToken": "cecc4267a0194af89ca343805a3e57af",
                "it": "stock,exchangetradedfund,fund",
                "cc": "us",
                "xe": "coindesk",
            },
        )
        if response.status_code != 200:
            raise MarketWatchException("Error while getting search")

        results = response.json()["symbols"][0]
        return {
            "chartingSymbol": results["chartingSymbol"],
            "company": results["company"],
            "country": results["country"],
            "djnSymbol": results["djnSymbol"],
            "exchange": results["exchange"],
            "exchangeIsoCode": results["exchangeIsoCode"],
            "factivaCode": results["factivaCode"],
            "isFuture": results["isFuture"],
            "quote": results["quote"],
            "ticker": results["ticker"],
            "type": results["type"],
        }

    def buy(
        self,
        game_id,
        ticker,
        shares,
        term=Term.INDEFINITE,
        priceType=PriceType.MARKET,
        price=None,
    ):
        """
        Buy a position

        :param ticker: Ticker
        :param shares: Number of shares
        :param term: Term
        :param priceType: Price type
        :param price: Price
        """
        return self._create_payload(
            game_id=game_id,
            ticker=ticker,
            shares=shares,
            term=term,
            priceType=priceType,
            price=price,
            orderType=OrderType.BUY,
        )

    def short(
        self,
        game_id,
        ticker,
        shares,
        term=Term.INDEFINITE,
        priceType=PriceType.MARKET,
        price=None,
    ):
        """
        Short a position

        :param ticker: Ticker
        :param shares: Number of shares
        :param term: Term
        :param priceType: Price type
        :param price: Price

        """
        return self._create_payload(
            game_id=game_id,
            ticker=ticker,
            shares=shares,
            term=term,
            priceType=priceType,
            price=price,
            orderType=OrderType.SHORT,
        )

    def sell(
        self,
        game_id,
        ticker,
        shares,
        term=Term.INDEFINITE,
        priceType=PriceType.MARKET,
        price=None,
    ):
        """
                        Sell a position

        :param ticker: Ticker
        :param shares: Number of shares
        :param term: Term
        :param priceType: Price type
        :param price: Price
        """
        return self._create_payload(
            game_id=game_id,
            ticker=ticker,
            shares=shares,
            term=term,
            priceType=priceType,
            price=price,
            orderType=OrderType.SELL,
        )

    def cover(
        self,
        game_id,
        ticker,
        shares,
        term=Term.INDEFINITE,
        priceType=PriceType.MARKET,
        price=None,
    ):
        """
        Cover a short position

        :param ticker: Ticker
        :param shares: Number of shares
        :param term: Term
        :param priceType: Price type
        :param price: Price

        """
        return self._create_payload(
            game_id=game_id,
            ticker=ticker,
            shares=shares,
            term=term,
            priceType=priceType,
            price=price,
            orderType=OrderType.COVER,
        )

    @auth
    def _create_payload(
        self,
        game_id: str,
        ticker: str,
        shares: int,
        priceType: PriceType,
        price,
        orderType: OrderType,
        term: Term,
    ):
        """
        Create the payload for a trade order

        :param game_id: Game id
        :param ticker: Ticker
        :param shares: Number of shares
        :param priceType: Price type
        :param price: Price
        :param orderType: Order type
        :param term: Term

        :return: Payload
        """
        ticker_uid = self._get_ticker_uid(ticker)
        response = self.session.post(
            f"https://www.marketwatch.com/games/{game_id}/tradeorder?chartingSymbol={ticker_uid}"
        )
        if response.status_code != 200:
            raise MarketWatchException("Error while getting search")
            # Parse form payload

        soup = BeautifulSoup(response.text, "html.parser")
        form = soup.findAll("form")[0]
        # with form payload
        payload = {
            "djid": form["data-djkey"],
            "ledgerId": form["data-pub"],
            "tradeType": orderType.value,
            "shares": shares,
            "expiresEndOfDay": term == Term.DAY,
            "orderType": priceType.value,
        }

        if priceType in [PriceType.LIMIT, PriceType.STOP]:
            payload["limitStopPrice"] = str(price)

        return self._submit(
            game_id=game_id,
            payload=payload,
        )

    # Get UID from ticker name
    def _get_ticker_uid(self, ticker):
        respond = self.session.get(
            f"https://www.marketwatch.com/investing/stock/{ticker}"
        )
        soup = BeautifulSoup(respond.text, "html.parser")
        try:
            return soup.find("mw-chart")["data-ticker"]
        except Exception:
            return None

    # Execture order
    def _submit(self, game_id: str, payload: dict):
        headers = {"Content-Type": "application/json"}

        ledger_id = payload["ledgerId"]

        url = f"https://vse-api.marketwatch.com/v1/games/{game_id}/ledgers/{ledger_id}/trades"
        response = json.loads(
            self.session.post(url=url, headers=headers, json=payload).text
        )
        return response["data"]["status"]

    def cancel_order(self, game_id, id):
        url = (
            f"http://www.marketwatch.com/games/{game_id}/trade/cancelorder?id={str(id)}"
        )
        self.session.get(url)

    def cancel_all_orders(self, game_id):
        for order in self.getPendingOrders():
            url = f"http://www.marketwatch.com/games/{game_id}/trade/cancelorder?id={str(order.id)}"
            self.session.get(url)

    def get_pending_orders(self, game_id: str):
        url = f"https://www.marketwatch.com/games/{game_id}/portfolio"
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        orders_table = soup.find(
            "table", {"class": "table table--primary table--condensed no-margin"}
        )
        if not orders_table:
            return []

        rows = orders_table.find_all("tr")[1:]
        orders = []
        for row in rows:
            order_id = row.get("data-order")
            if not order_id:
                order_id = None

            ticker = row.find("td", {"class": "ticker"}).text.strip()
            quantity = int(row.find("td", {"class": "shares"}).text.strip())
            order_type = self._get_order_type(
                row.find("td", {"class": "type"}).text.strip()
            )
            price_type = self._get_price_type(
                row.find("td", {"class": "type"}).text.strip()
            )
            price = self._get_order_price(
                row.find("td", {"class": "price"}).text.strip()
            )

            orders.append(
                Order(order_id, ticker, quantity, order_type, price_type, price)
            )

        return orders

    def _get_order_type(self, order):
        """
        Get order type from string

        :param order: Order string
        :return: OrderType
        """
        order = order.lower()
        if "buy" in order:
            return OrderType.BUY
        elif "short" in order:
            return OrderType.SHORT
        elif "cover" in order:
            return OrderType.COVER
        elif "sell" in order:
            return OrderType.SELL
        else:
            return None

    def _get_price_type(self, order):
        order = order.lower()
        if "market" in order:
            return PriceType.MARKET
        elif "limit" in order:
            return PriceType.LIMIT
        elif "stop" in order:
            return PriceType.STOP
        else:
            return None

    def _get_order_price(self, order):
        """
        Get order price from string

        :param order: Order string
        :return: Price

        Symbol	Shares	% Holdings	Type	Price	Price Change	Price Change %	Value	Value Gain/Loss	Value Gain/Loss %
        AAPD	12	< 1%	BUY	$24.90	0.27	1.08%	$298.74	$6.66	2.28%
        AAPL	623	12%	BUY	$156.54	-1.74	-1.10%	$97,524.42	-$1,786.29	-1.80%
        ANCTF	400	2%	BUY	$47.99	0.19	0.40%	$19,196.00	$374.05	1.99%
        BAC	100	< 1%	BUY	$28.38	-0.11	-0.38%	$2,838.24	$32.24	1.15%
        """
        return None if ("$" not in order) else float(order[(order.index("$") + 1) :])

    def get_positions(self, game_id: str, download: bool = False):
        soup = BeautifulSoup(
            self.session.get(
                f"https://www.marketwatch.com/games/{game_id}/portfolio"
            ).text,
            "html.parser",
        )

        if download:
            return self.session.get(
                "https://www.marketwatch.com"
                + soup.select("a[href*='download?view=holdings']")[0]["href"]
            )

        try:
            position_csv = self.session.get(
                "https://www.marketwatch.com"
                + soup.select("a[href*='download?view=holdings']")[0]["href"]
            ).text
        except IndexError:
            return []

        positions = []
        # extract all lines, skipping the header, in the given csv text
        reader = csv.reader(position_csv.split("\n")[1:])

        for row in reader:
            if len(row) == 0:
                continue

            ticker = row[0]
            quantity = int(row[1].replace(",", ""))
            price = float(row[4].replace("$", "").replace(",", ""))
            ep = float(row[8].replace("$", "").replace(",", "")) / quantity
            positions.append(Position(ticker, quantity, price, ep))

        return positions

    def get_game_settings(self, game_id: str):
        """
        Get game settings

        :param game_id: Game ID
        :return: GameSettings
        """
        url = f"https://www.marketwatch.com/games/{game_id}/settings"
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        option_tables = soup.find_all("table", {"class": "portfolio-options"})

        def clean_text(text):
            return text.replace("$", "").replace(",", "").replace("%", "")

        # Extract the game settings from the option tables
        settings = {
            "game_public": option_tables[0]
            .find_all("td", {"class": "table__cell"})[1]
            .text.strip()
            == "Public",
            "portfolios_public": option_tables[1]
            .find_all("td", {"class": "table__cell"})[1]
            .text.strip()
            == "Public",
            "start_balance": float(
                clean_text(
                    option_tables[2].find_all("td", {"class": "table__cell"})[1].text
                )
            ),
            "commission": float(
                clean_text(
                    option_tables[2].find_all("td", {"class": "table__cell"})[3].text
                )
            ),
            "credit_interest_rate": float(
                clean_text(
                    option_tables[2].find_all("td", {"class": "table__cell"})[5].text
                )
            )
            / 100,
            "leverage_debt_interest_rate": float(
                clean_text(
                    option_tables[2].find_all("td", {"class": "table__cell"})[7].text
                )
            )
            / 100,
            "minimum_stock_price": float(
                clean_text(
                    option_tables[2].find_all("td", {"class": "table__cell"})[9].text
                )
            ),
            "maximum_stock_price": float(
                clean_text(
                    option_tables[2].find_all("td", {"class": "table__cell"})[11].text
                )
            ),
            "short_selling_enabled": option_tables[3]
            .find_all("td", {"class": "table__cell"})[1]
            .text.strip()
            == "Enabled",
            "margin_trading_enabled": option_tables[3]
            .find_all("td", {"class": "table__cell"})[3]
            .text.strip()
            == "Enabled",
            "limit_orders_enabled": option_tables[3]
            .find_all("td", {"class": "table__cell"})[5]
            .text.strip()
            == "Enabled",
            "stop_loss_orders_enabled": option_tables[3]
            .find_all("td", {"class": "table__cell"})[7]
            .text.strip()
            == "Enabled",
            "partial_share_trading_enabled": option_tables[3]
            .find_all("td", {"class": "table__cell"})[9]
            .text.strip()
            == "Enabled",
        }

        return settings

        return settings

    def _clean_text(self, text):
        """
        Clean text

        :param text: Text to clean
        :return: Cleaned text
        """
        return (
            text.replace("\r\n", "").replace("\t", "").replace(" ", "").replace(",", "")
        )

    def check_error_game(self):
        """
        Check if the game is down

        :param game_id: Game ID
        :return: None
        """
        if self.session.get("https://www.marketwatch.com/games").status_code != 200:
            raise MarketWatchException("Marketwatch Stock Market Game Down")

    # decorator to check if the game is down
    def check_error(func):
        """
        Decorator to check if the game is down

        :param func: Function to decorate
        :return: Decorated function
        """

        def wrapper(*args, **kwargs):
            """
            Wrapper function

            :param args: Arguments
            :param kwargs: Keyword arguments
            :return: Decorated function
            """
            args[0].check_error_game()
            return func(*args, **kwargs)

        return wrapper

    def _get_ticker_uids(self, tickers: List[str]):
        """
        Get ticker IDs

        :param tickers: List of tickers
        :return: List of ticker IDs
        """
        return [self._get_ticker_uid(ticker) for ticker in tickers]

    def create_watchlist(self, name: str, tickers: List[str] = None):
        """
        Create a watchlist

        :param name: Watchlist name
        :param tickers: List of tickers
        :return: None
        """
        tickers = [] if tickers is None else self._get_ticker_uids(tickers)
        data = {"Name": name}

        if tickers:
            data["Items"] =  tickers

        response = self.session.post(
            "https://api.marketwatch.com/api/oskar/me/marketwatch-com",
            json=data,
        )

        if response.status_code != 201:
            raise MarketWatchException("Failed to create watchlist")

        response_json = response.json()

        return {
            "Id": response_json["Id"],
            "Name": name,
            "TotalItemCount": response_json["TotalItemCount"],
            "Revision": response_json["Revision"],
            "Items": response_json["Items"],
            "CreateDateUtc": response_json["CreateDateUtc"],
            "LastModifiedDateUtc": response_json["LastModifiedDateUtc"],
        }

    def add_to_watchlist(self, watchlist_id: str, tickers: list):
        """
        Add tickers to a watchlist

        :param watchlist_id: Watchlist ID
        :param tickers: List of tickers
        :return: None

        {
        "Items": [
            {
            "ChartingSymbol": "STOCK/US/XNAS/AAPL"
            }
        ]
        }
        """
        data = {"Items": [{"ChartingSymbol": f"{self._get_ticker_uid(ticker)}"} for ticker in tickers]}

        response = self.session.post(
            f"https://api.marketwatch.com/api/oskar/me/marketwatch-com/{watchlist_id}/items",
            headers={"Content-Type": "application/json"},
            data=json.dumps(data),
        )

        if response.status_code != 201:
            raise MarketWatchException("Failed to add to watchlist")

        return response.json()

    def get_watchlists(self):
        """
        Get all watchlists

        :return: List of watchlists
        """

        response = self.session.get(
            "https://api.marketwatch.com/api/oskar/me/marketwatch-com/"
        )

        if response.status_code != 200:
            raise MarketWatchException("Failed to get watchlists")

        return response.json()

    def get_watchlist(self, watchlist_id: str):
        """
        Get a watchlist

        :param watchlist_id: Watchlist ID
        :return: Watchlist
        """
        response = self.session.get(
            f"https://api.marketwatch.com/api/oskar/me/marketwatch-com/{watchlist_id}"
        )

        if response.status_code != 200:
            raise MarketWatchException("Failed to get watchlist")

        return response.json()

    def delete_watchlist(self, watchlist_id: str):
        """
        Delete a watchlist

        :param watchlist_id: Watchlist ID
        :return: None
        """
        response = self.session.delete(
            f"https://api.marketwatch.com/api/oskar/me/marketwatch-com/{watchlist_id}"
        )

        if response.status_code != 200:
            raise MarketWatchException("Failed to delete watchlist")


    def delete_watchlist_item(self, watchlist_id: str, ticker: str):
        """
        Delete a ticker from a watchlist

        :param watchlist_id: Watchlist ID
        :param ticker: Ticker to delete
        :return: None
        """
        ticker_uid = self._get_ticker_uid(ticker)
        items = self.get_watchlist(watchlist_id).get("Items")
        key = next(
            (
                item.get("Key")
                for item in items
                if item.get("ChartingSymbol") == ticker_uid
            ),
            None,
        )
        response = self.session.delete(
            f"https://api.marketwatch.com/api/oskar/me/marketwatch-com/{watchlist_id}/items/{key}"
        )

        if response.status_code != 200:
            raise MarketWatchException("Failed to delete ticker from watchlist")


if __name__ == "__main__":
    import os

    username = os.environ.get("MARKETWATCH_USERNAME")
    password = os.environ.get("MARKETWATCH_PASSWORD")

    marketwatch = MarketWatch(username, password)

    print(f"Price: {marketwatch.get_price('AAPL')} \n")
    print(f"Games: {marketwatch.get_games()} \n")

    games1 = marketwatch.get_games()[0]["name"].lower().replace(" ", "-")

    print(f"Game: {marketwatch.get_game(games1)} \n")
    print(f"Game Settings: {marketwatch.get_game_settings(games1)} \n")

    print(f"Leaderboard: {marketwatch.get_leaderboard(games1)} \n")
    print(f"Porfolio: {marketwatch.get_portfolio(games1)} \n")

    print(f"Position: {marketwatch.get_positions(games1)}")
    print(f"Orders Pending: {marketwatch.get_pending_orders(games1)}")
    marketwatch.buy(games1, "AAPL", 100)

    print(f"Position diff: {marketwatch.get_positions(games1)}")
