# Autor: bwees, based on code from https://github.com/kevindong/MarketWatch_API/

import json
import requests
from urllib.parse import urlparse
from enum import Enum
import re
import csv
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

# Main Class for Interacting with MarketWatch API
class MarketWatch:
	def __init__(self, email, password, game, debug = False, new_backend=True):
		self.debug = debug
		self.game = game
		self.session = requests.Session()
		self.route = "games/" if new_backend else "game/"

		self.login(email, password)
		self.check_error()

	# Main login flow, subject to change at any point
	def login(self, email, password):
		r = self.session.get("https://sso.accounts.dowjones.com/login-page")

		# parse url and extract query string into dictionary
		url = urlparse(r.url)
		given_params = dict(q.split("=") for q in url.query.split("&"))

		login_data = {
			"client_id": given_params['client'],
			"connection": "DJldap",
			"headers": {"X-REMOTE-USER": email},
			"nonce": given_params["nonce"],
			"ns": "prod/accounts-mw",
			"password": password,
			"protocol": "oauth2",
			"redirect_uri": "https://accounts.marketwatch.com/auth/sso/login",
			"response_type": "code",
			"scope": "openid idp_id roles email given_name family_name djid djUsername djStatus trackid tags prts suuid createTimestamp",
			"state": given_params["state"],
			"tenant": "sso",
			"ui_locales": ",en-us-x-mw-3-8",
			"username": email,
			"_csrf": self.session.cookies.get_dict()['_csrf'],
			"_intstate": "deprecated"
		}

		login = self.session.post("https://sso.accounts.dowjones.com/usernamepassword/login", data=login_data).content
		soup = BeautifulSoup(login, "html.parser")

		try:
			soup.findAll("input", {"name": "wa"})[0]
		except Exception:
			m = json.loads(login)["message"]
			raise Exception(f"Login Failed: {m}")

		callback_payload = {
			"wa": [soup.findAll("input", {"name": "wa"})[0]["value"].strip()],
			"wresult": [soup.findAll("input", {"name": "wresult"})[0]["value"].strip()],
			"wctx": [soup.findAll("input", {"name": "wctx"})[0]["value"].strip()]
		}

		self.session.post("https://sso.accounts.dowjones.com/login/callback", data=callback_payload)

	def check_error(self):  # sourcery skip: raise-specific-error
		if (
			self.session.get(
				f"https://www.marketwatch.com/{self.route}{self.game}"
			).status_code
			!= 200
		):
			raise Exception("Marketwatch Stock Market Game Down")

	# Get current market price for ticker
	def get_price(self, ticker):
		try:
			page = self.session.get(f"http://www.marketwatch.com/investing/stock/{ticker}")
			tree = html.fromstring(page.content)
			price = tree.xpath("//*[@id='maincontent']/div[2]/div[3]/div/div[2]/h2/bg-quote")
			return round(float(price[0].text), 2)
		except Exception:
			return None

	# Main Order execution functions

	def buy(self, ticker, shares, term = Term.INDEFINITE, priceType = PriceType.MARKET, price = None):
		return self._create_payload(ticker, shares, term, priceType, price, OrderType.BUY)

	def short(self, ticker, shares, term = Term.INDEFINITE, priceType = PriceType.MARKET, price = None):
		return self._create_payload(ticker, shares, term, priceType, price, OrderType.SHORT)

	def sell(self, ticker, shares, term = Term.INDEFINITE, priceType = PriceType.MARKET, price = None):
		return self._create_payload(ticker, shares, term, priceType, price, OrderType.SELL)

	def cover(self, ticker, shares, term = Term.INDEFINITE, priceType = PriceType.MARKET, price = None):
		return self._create_payload(ticker, shares, term, priceType, price, OrderType.COVER)

	# Payload creation for order execution
	def _create_payload(self, ticker, shares, term, priceType, price, orderType):
		ticker = self._get_ticker_uid(ticker)

		# Get form payload
		r = self.session.get(
			f"https://www.marketwatch.com/{self.route}{self.game}/tradeorder?chartingSymbol={ticker}"
		)

		# Parse form payload
		soup = BeautifulSoup(r.content, "html.parser")
		form = soup.findAll("form")[0]

		# with form payload
		payload = {
			"djid":form["data-djkey"],
			"ledgerId":form["data-pub"],
			"tradeType":orderType.value,
			"shares":shares,
			"expiresEndOfDay": term == Term.DAY,
			"orderType":priceType.value
		}

		if priceType in [PriceType.LIMIT, PriceType.STOP]:
			payload['limitStopPrice'] = str(price)

		return self._submit(payload)

	# Get UID from ticker name
	def _get_ticker_uid(self, ticker):
		page = self.session.get(f"http://www.marketwatch.com/investing/stock/{ticker}")
		soup = BeautifulSoup(page.text, features="lxml")

		try:
			return self._clean_text(soup.find_all("mw-chart")[0]["data-ticker"])
		except Exception:
			return None

	# Execture order
	def _submit(self, payload):
		url = (
			f'https://vse-api.marketwatch.com/v1/games/{self.game}/ledgers/'
			+ payload["ledgerId"]
			+ '/trades'
		)
		headers = {'Content-Type': 'application/json'}
		response = json.loads(self.session.post(url=url, headers=headers, json=payload).text)
		return response["data"]["status"]

	def cancel_order(self, id):
		url = f'http://www.marketwatch.com/{self.route}{self.game}/trade/cancelorder?id={str(id)}'
		self.session.get(url)

	def cancel_all_orders(self):
		for order in self.getPendingOrders():
			url = f'http://www.marketwatch.com/{self.route}{self.game}/trade/cancelorder?id={str(order.id)}'
			self.session.get(url)

	def get_pending_orders(self):
		tree = html.fromstring(
			self.session.get(
				f"http://www.marketwatch.com/{self.route}{self.game}/portfolio"
			).content
		)
		rawOrders = tree.xpath("//*[@id='maincontent']/div[3]/div[1]/div[6]/mw-tabs/div[2]/div[2]/div/table/tbody")

		orders = []
		try:
			numberOfOrders = len(rawOrders[0])
		except Exception:
			return orders
		for i in range(numberOfOrders):
			try:
				cleanID = self._clean_text(rawOrders[0][i][4][0][0].get("data-order"))
			except Exception:
				cleanID = None

			ticker = self._clean_text(rawOrders[0][i][0][0][0].text)
			quantity = int(self._clean_text(rawOrders[0][i][3].text))
			orderType = self._get_order_type(self._clean_text(rawOrders[0][i][2].text))
			priceType = self._get_price_type(self._clean_text(rawOrders[0][i][2].text))
			price = self._get_order_price(self._clean_text(rawOrders[0][i][2].text))

			orders.append(Order(cleanID, ticker, quantity, orderType, priceType, price))

		return orders

	def _clean_text(self, text):
		return text.replace("\r\n", "").replace("\t", "").replace(" ", "").replace(",", "")

	def _get_order_type(self, order):
		order = order.lower()
		if ("buy" in order):
			return OrderType.BUY
		elif ("short" in order):
			return OrderType.SHORT
		elif ("cover" in order):
			return OrderType.COVER
		elif ("sell" in order):
			return OrderType.SELL
		else:
			return None

	def _get_price_type(self, order):
		order = order.lower()
		if ("market" in order):
			return PriceType.MARKET
		elif ("limit" in order):
			return PriceType.LIMIT
		elif ("stop" in order):
			return PriceType.STOP
		else:
			return None

	def _get_order_price(self, order):
		return None if ("$" not in order) else float(order[(order.index('$') + 1):])

	def get_positions(self):
		soup = BeautifulSoup(
			self.session.get(
				f"https://www.marketwatch.com/{self.route}{self.game}/portfolio"
			).text,
			features="lxml",
		)

		try:
			position_csv = self.session.get("https://www.marketwatch.com" + soup.select("a[href*='download?view=holdings']")[0]["href"]).text
		except IndexError:
			return []

		positions = []
		# extract all lines, skipping the header, in the given csv text
		reader = csv.reader(position_csv.split("\n")[1:])
		for parts in reader:
			if len(parts) > 0:
				avg_entry = float(parts[4].replace("$", "").replace(",", "")) - float(parts[5])
				# create a Position object for each ticker
				positions.append(Position(parts[0], parts[3], int(parts[1]), avg_entry))

		return positions

	def get_portfolio_stats(self):
		soup = BeautifulSoup(
			self.session.get(
				f"http://www.marketwatch.com/{self.route}{self.game}/portfolio"
			).content,
			features="lxml",
		)
		table = soup.find_all("div", {"class": "element--profile"})[0]
		table = table.find_all("ul", {"class": "list"})[0]

		stats_elements = table.find_all("span", {"class": "primary"})
		stats_elements = [x.text.strip() for x in stats_elements]
		return {
			"cash": float(
				self._clean_text(stats_elements[0].replace("$", "").replace(",", ""))
			),
			"value": float(
				self._clean_text(stats_elements[4].replace("$", "").replace(",", ""))
			),
			"power": float(
				self._clean_text(stats_elements[5].replace("$", "").replace(",", ""))
			),
			"rank": int(
				self._clean_text(
					soup.find_all("div", {"class": "rank__number"})[0].text.strip()
				)
			),
			"overall_gains": float(
				self._clean_text(stats_elements[2].replace("$", "").replace(",", ""))
			),
			"overall_returns": float(
				self._clean_text(stats_elements[3].replace("%", ""))
			)
			/ 100,
			"short_reserve": float(
				self._clean_text(stats_elements[6].replace("$", "").replace(",", ""))
			),
			"borrowed": float(
				self._clean_text(stats_elements[7].replace("$", "").replace(",", ""))
			),
		}

	def get_game_settings(self):
		soup = BeautifulSoup(
			self.session.get(
				f"http://www.marketwatch.com/{self.route}{self.game}/settings"
			).content,
			features="lxml",
		)
		sTable1 = [x.text.strip() for x in soup.find_all("table", {"class": "portfolio-options"})[0].find_all("td", {"class": "table__cell"})]
		sTable2 = [x.text.strip() for x in soup.find_all("table", {"class": "portfolio-options"})[1].find_all("td", {"class": "table__cell"})]
		sTable3 = [x.text.strip() for x in soup.find_all("table", {"class": "portfolio-options"})[2].find_all("td", {"class": "table__cell"})]
		sTable4 = [x.text.strip() for x in soup.find_all("table", {"class": "portfolio-options"})[3].find_all("td", {"class": "table__cell"})]


		return {
			"game_public": self._clean_text(sTable1[1]) == "Public",
			"portfolios_public": self._clean_text(sTable2[1]) == "Public",
			"start_balance": float(
				self._clean_text(sTable3[1]).replace("$", "").replace(",", "")
			),
			"commission": float(
				self._clean_text(sTable3[3]).replace("$", "").replace(",", "")
			),
			"credit_interest_rate": float(
				self._clean_text(sTable3[5]).replace("%", "")
			)
			/ 100,
			"leverage_debt_interest_rate": float(
				self._clean_text(sTable3[7]).replace("%", "")
			)
			/ 100,
			"minimum_stock_price": float(
				self._clean_text(sTable3[9]).replace("$", "").replace(",", "")
			),
			"maximum_stock_price": float(
				self._clean_text(sTable3[11]).replace("$", "").replace(",", "")
			),
			"volume_limit": float(self._clean_text(sTable4[1]).replace("%", ""))
			/ 100,
			"short_selling_enabled": self._clean_text(sTable4[3]) == "Enabled",
			"margin_trading_enabled": self._clean_text(sTable4[5]) == "Enabled",
			"limit_orders_enabled": self._clean_text(sTable4[7]) == "Enabled",
			"stop_loss_orders_enabled": self._clean_text(sTable4[9]) == "Enabled",
			"partial_share_trading_enabled": self._clean_text(sTable4[11])
			== "Enabled",
		}
