"""
MarketWatch API using Python

This is a Python API for the MarketWatch game. It allows you to get your
portfolio, place orders, and get the leaderboard.

Example:
	>>> from marketwatch import MarketWatch
	>>> mw = MarketWatch("email", "password")
	>>> mw.get_games()
	>>> mw.get_portfolio(1234)
	>>> mw.place_order(1234, "AAPL", 10, "buy", "market")
	>>> mw.get_leaderboard(1234)
"""
import csv
import json

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

    def __init__(self, email, password):
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

    def generate_csrf_token(self):
        """
        Get the csrf token from the login page

        :return: CSRF Token
        """
        client = self.session.get("https://sso.accounts.dowjones.com/login-page")
        return client.cookies["csrf"]

    def get_client_id(self):
        """
        Generate a client id

        :return: Client ID
        """
        return "5hssEAdMy0mJTICnJNvC9TXEw3Va7jfO"

    def get_user_id(self):
        user = self.session.post(
            "https://sso.accounts.dowjones.com/getuser",
            data={
                "username": self.email,
                "csrf": self.generate_csrf_token(),
            },
        )

        if user.status_code == 200:
            return user.json()["id"]

    def get_ledger_id(self, game_id):
        """
        Get the ledger id

        :param game_id: Game ID
        """
        game_page = self.session.get(f"https://www.marketwatch.com/games/{game_id}")

        if game_page.status_code != 200:
            raise MarketWatchException("Game not found")
        soup = BeautifulSoup(game_page.text, "html.parser")

        return soup.find("canvas", {"id": "j-chartjs-performance"})["data-pub"]

    def login(self):
        """
        Login to the MarketWatch API

        :return: None
        """
        login_data = {
            "client_id": self.client_id,
            "connection": "DJldap",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
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

        login = self.session.post(
            "https://sso.accounts.dowjones.com/authenticate", data=login_data
        )

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

        response = self.session.post(
            "https://sso.accounts.dowjones.com/postauth/handler",
            data=data,
            follow_redirects=True,
        )
        response = self.session.post(
            "https://sso.accounts.dowjones.com/postauth/handler",
            data=data,
            follow_redirects=True,
        )

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

    def get_games(self):
        """
        Get all the games
        [{'name': 'ALGOETS-H2023', 'url': 'https://www.marketwatch.com/games/algoets-h2023', 'id': 'algoets-h2023',
                        'return': '0.00%', 'total_return': '-$3,710.85', 'rank': '15', 'end': '3/31/23', 'players': '27'}]

                        :return: List of games
        """
        self.check_login()
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

    def get_game(self, game_id: str) -> list:
        """
        Get a game
        {'name': 'algoets-h2023', 'title': 'ALGOETS-H2023', 'time': 'Game ends in 4 days', 'url': 'https://www.marketwatch.com/games/algoets-h2023', 'start_date': 'Mar 20, 2023', 'end_date': 'Mar 31, 2023', 'players': '27', 'creator': 'Mohamed Ilias',
                        'rank': '15', 'portfolio_value': '$996,289.15', 'gain_percentage': '0.00%', 'gain': '-$3,710.85', 'return': '-0.37%', 'cash_remaining': '$249,845.55', 'buying_power': '$143,734.12', 'shorts_reserve': '$0.00', 'cash_borrowed': '$0.00'}

                        :param game_id: Game id
        :return: Game data
        """
        self.check_login()
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
        Get the price of a stock
        Return: AAPL : $137.00

        :param ticker: Ticker of the stock

        :return: Price of the stock
        """
        # Get the price of a stock
        response = self.session.get(
            f"https://www.marketwatch.com/investing/stock/{ticker}"
        )
        if response.status_code != 200:
            raise MarketWatchException("Failed to get price")
        soup = BeautifulSoup(response.text, "html.parser")
        # //*[@id="maincontent"]/div[2]/div[3]/div/div[2]/h2/bg-quote
        regions = (
            soup.find("div", {"class": "region--intraday"})
            .find("h2", {"class": "intraday__price"})
            .find("bg-quote")
        )
        if regions is None:
            raise MarketWatchException("Failed to get price")
        return f"{ticker} : ${regions.text}"

    def get_portfolio(self, game_id: str):
        """
        Get the portfolio of a game
        {'portfolio': [{'ticker': 'AAPL', 'quantity': '200 Shares', 'holding': '\nBuy\n', 'holding_percentage': '4%', 'price': '$160.25', 'price_gain': '1.32', 'price_gain_percentage': '0.83%', 'value': '$32,050.00', 'gain': '$295.50', 'gain_percentage': '0.93%'}]

                        :param game_id: Game id

                        :return: Portfolio of the game
        """
        self.check_login()
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

        table = soup.find("mw-table-dropdown").find("tbody").find_all("tr")

        portfolio = []

        for row in table:
            cells = row.find_all("td")
            ticker = cells[1].find("a", {"class": "primary"}).find("mini-quote").text
            quantity = (
                cells[1]
                .find("div", {"class": "secondary"})
                .find("small", {"class": "text"})
                .text
            )
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
            gain = (
                cells[4]
                .find("small", {"class": "secondary"})
                .find("span", {"class": "point"})
                .text
            )
            gain_percentage = (
                cells[4]
                .find("small", {"class": "secondary"})
                .find("span", {"class": "percent"})
                .text
            )

            portfolio.append(
                {
                    "ticker": ticker,
                    "quantity": quantity,
                    "holding": holding,
                    "holding_percentage": holding_percentage,
                    "price": price,
                    "price_gain": price_gain,
                    "price_gain_percentage": price_gain_percentage,
                    "value": value,
                    "gain": gain,
                    "gain_percentage": gain_percentage,
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

    def get_leaderboard(self, game_id: str, download: bool = False):
        """
        Get the leaderboard of a game
                        :param download: Download the leaderboard
        :param game_id: Game id

        :return: Leaderboard of the game
        """
        self.check_login()
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
            print(players)
        return players

    def get_search(self, search: str):
        """
        Get the search of a mw

        :param search: Search query

        :return: Search results
        """
        # https://api.wsj.net/api/autocomplete/search?q=AAPL&need=symbol&excludeExs=xmstar&maxRows=12&entitlementToken=cecc4267a0194af89ca343805a3e57af&it=stock,exchangetradedfund,fund&cc=us&xe=coindesk
        response = self.session.get(
            f"https://api.wsj.net/api/autocomplete/search?q={search}",
            params={
                "q": search,
                "need": "symbol",
                "excludeExs": "xmstar",
                "maxRows": 12,
                "it": "stock,exchangetradedfund,fund",
                "cc": "us",
                "xe": "coindesk",
            },
        )
        if response.status_code != 200:
            raise MarketWatchException("Error while getting search")

        results = response.json()[0]
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
            game_id=self.game_id,
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
            game_id=self.game_id,
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
            game_id=self.game_id,
            ticker=ticker,
            shares=shares,
            term=term,
            priceType=priceType,
            price=price,
            orderType=OrderType.COVER,
        )

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
        self.check_login()
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

        return self._submit(game_id, payload)

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
    def _submit(self, game_id, payload):
        url = (
            f"https://vse-api.marketwatch.com/v1/games/{game_id}/ledgers/"
            + payload["ledgerId"]
            + "/trades"
        )
        headers = {"Content-Type": "application/json"}
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
        """
        return None if ("$" not in order) else float(order[(order.index("$") + 1) :])

    def get_positions(self, game_id: str):
        soup = BeautifulSoup(
            self.session.get(
                f"https://www.marketwatch.com/games/{game_id}/portfolio"
            ).text,
            features="lxml",
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
        for parts in reader:
            if len(parts) > 0:
                avg_entry = float(parts[4].replace("$", "").replace(",", "")) - float(
                    parts[5]
                )
                # create a Position object for each ticker
                positions.append(Position(parts[0], parts[3], int(parts[1]), avg_entry))

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

    def _clean_text(self, text):
        """
        Clean text

        :param text: Text to clean
        :return: Cleaned text
        """
        return (
            text.replace("\r\n", "").replace("\t", "").replace(" ", "").replace(",", "")
        )

    def check_error(self):
        """
        Check if the game is down

        :param game_id: Game ID
        :return: None
        """
        if self.session.get("https://www.marketwatch.com/games").status_code != 200:
            raise MarketWatchException("Marketwatch Stock Market Game Down")


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
