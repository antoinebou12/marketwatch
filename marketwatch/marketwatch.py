from hashlib import sha1
import httpx
from urllib.parse import urlparse
from enum import Enum
from bs4 import BeautifulSoup
from lxml import html


# Order Types and Enums
class Term(Enum):
	DAY = "Day"
	INDEFINITE = "Cancelled"

class PriceType(Enum):
	MARKET = "Market"
	LIMIT = "Limit"
	STOP = "Stop"

class OrderType(Enum):
	BUY = "Buy"
	SELL = "Sell"
	SHORT = "Short"
	COVER = "Cover"

# Order structure
class Order:
	def __init__(self, id, ticker, quantity, orderType, priceType, price = None):
		self.id = id
		self.ticker = ticker
		self.quantity = quantity
		self.orderType = orderType
		self.priceType = priceType
		self.price = price

# Position Structure
class Position:
	def __init__(self, ticker, orderType, quantity, ep):
		self.ticker = ticker
		self.orderType = orderType
		self.quantity = quantity
		self.entry_price = ep

class MarketWatchException(Exception):
	def __init__(self, message):
		self.message = f"MarketWatchException: {message}"

# Main Class for Interacting with MarketWatch API
class MarketWatch:
	def __init__(self, email, password):
		self.session = httpx.Client()

		self.email = email
		self.password = password
		self.client_id = self.get_client_id()
		self.login()


	def generate_csrf_token(self):
		# Get the csrf token from the login page
		client = self.session.get("https://sso.accounts.dowjones.com/login-page")
		return client.cookies["csrf"]


	def get_client_id(self):
		return "5hssEAdMy0mJTICnJNvC9TXEw3Va7jfO"

	def get_user_id(self):
		user = self.session.post("https://sso.accounts.dowjones.com/getuser", data={
			"username": self.email,
			"csrf": self.generate_csrf_token(),
		})

		if user.status_code == 200:
			return user.json()["id"]

	async def login(self):
		login_data = {
			"client_id": self.client_id ,
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

		login = await self.session.post("https://sso.accounts.dowjones.com/authenticate", data=login_data)

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
		'token': token,
		'params': params,
		}

		response = self.session.post('https://sso.accounts.dowjones.com/postauth/handler', data=data, follow_redirects=True)
		response = self.session.post('https://sso.accounts.dowjones.com/postauth/handler', data=data, follow_redirects=True)

		if response.status_code in [200, 302]:
			print("Login successful")

		# check if the login was successful
		if response.status_code == 200:
			soup = BeautifulSoup(response.text, 'html.parser')
			username = soup.find("li", {"class": "profile__item profile--name divider"}).text.strip()
			print(f"Logged in as {username}")

			# set all the response cookies to the session
			for cookie in response.cookies.items():
				self.session.cookies.set(cookie[0], cookie[1])


	async def check_login(self):
		# Check if the user is logged in
		response = await self.session.get("https://www.marketwatch.com")
		if response.status_code != 200:
			return False
		soup = BeautifulSoup(response.text, 'html.parser')
		return bool(
			username := soup.find(
				"li", {"class": "profile__item profile--name divider"}
			).text.strip()
		)


	def get_games(self):
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

			games_data.append({
				"name": game_name,
				"url": game_url,
				"id": game_id,
				"return": game_return,
				"total_return": game_total_return,
				"rank": game_rank,
				"end": game_end,
				"players": game_players
			})
		return games_data

	async def get_game(self, game_id):
		self.check_login()
		game_page = await self.session.get(f"https://www.marketwatch.com/games/{game_id}")

		if game_page.status_code != 200:
			raise MarketWatchException("Game not found")
		soup = BeautifulSoup(game_page.text, "html.parser")

		game_title = soup.find("h1", {"class": "game__title"}).text
		game_time = soup.find("div", {"class": "game__time"}).text
		game_url = game_page.url

		game_description = soup.find("div", {"class": "about-game"}).find_all("li", {"class": "kv__item"})
		descriptions = [
			description.find("span", {"class": "primary"}).text
			for description in game_description
		]
		game_start_date = descriptions[0]
		game_end_date = descriptions[1]
		game_players = descriptions[2]
		game_creator = descriptions[3]

		game_rank = soup.find("div", {"class": "rank__number"}).text

		profile = soup.find("div", {"class": "element--profile"}).find_all("li", {"class": "kv__item"})
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

		return {
			"name": game_id,
			"title": game_title.strip(),
			"time": game_time,
			"url": game_url.to_string(),
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
		}

	async def get_price(self, ticker):
		# Get the price of a stock
		response = await self.session.get(f"https://www.marketwatch.com/investing/stock{ticker}")
		if response.status_code != 200:
			raise MarketWatchException("Failed to get price")
		soup = BeautifulSoup(response.text, "html.parser")
		# //*[@id="maincontent"]/div[2]/div[3]/div/div[2]/h2/bg-quote
		regions = soup.find_all("div", {"class": "region--intraday"}).find("bg-quote")
		if regions is None:
			raise MarketWatchException("Failed to get price")
		return regions.find("bg-quote").text


if __name__ == "__main__":
	marketwatch = MarketWatch(
		"user", "password"
	)

	print(marketwatch.get_games())
	print(marketwatch.get_game(marketwatch.get_games()[0]["name"].lower().replace(" ", "-")))


