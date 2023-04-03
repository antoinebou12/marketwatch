"""
MarketWatch Schemas

This file contains the schemas for the MarketWatch API.
"""

from enum import Enum


# Order Types and Enums
class Term(Enum):
    """
    Order Term

    Day, Indefinite
    """

    DAY = "Day"
    INDEFINITE = "Cancelled"


class PriceType(Enum):
    """
    Order Price Type

    Market, Limit, Stop
    """

    MARKET = "Market"
    LIMIT = "Limit"
    STOP = "Stop"


class OrderType(Enum):
    """
    Order Type

    Buy, Sell, Short, Cover
    """

    BUY = "Buy"
    SELL = "Sell"
    SHORT = "Short"
    COVER = "Cover"


class GameSettings:
    def __init__(self):
        self.game = None
        self.private = None
        self.player_portfolios = None
        self.starting_balance = None
        self.commission = None
        self.credit_interest_rate = None
        self.leverage_debt_interest_rate = None
        self.minimum_stock_price = None
        self.maximum_stock_price = None
        self.short_selling = None
        self.margin_trading = None
        self.limit_orders = None
        self.stop_loss_trades = None
        self.partial_share_trading = None

    def __str__(self):
        return f"GameSettings(game={self.game}, private={self.private}, player_portfolios={self.player_portfolios}, starting_balance={self.starting_balance}, commission={self.commission}, credit_interest_rate={self.credit_interest_rate}, leverage_debt_interest_rate={self.leverage_debt_interest_rate}, minimum_stock_price={self.minimum_stock_price}, maximum_stock_price={self.maximum_stock_price}, short_selling={self.short_selling}, margin_trading={self.margin_trading}, limit_orders={self.limit_orders}, stop_loss_trades={self.stop_loss_trades}, partial_share_trading={self.partial_share_trading})"


class Order:
    """
    Order Structure
    """

    def __init__(self, id, ticker, quantity, orderType, priceType, price=None):
        """
                Order Structure

        :param id: Order ID
        :param ticker: Ticker
        :param quantity: Quantity
        :param orderType: Order Type
        :param priceType: Price Type
        :param price: Price
        """
        self.id = id
        self.ticker = ticker
        self.quantity = quantity
        self.orderType = orderType
        self.priceType = priceType
        self.price = price

    def __str__(self):
        return f"Order(id={self.id}, ticker={self.ticker}, quantity={self.quantity}, orderType={self.orderType}, priceType={self.priceType}, price={self.price})"

    def __repr__(self):
        return f"Order(id={self.id}, ticker={self.ticker}, quantity={self.quantity}, orderType={self.orderType}, priceType={self.priceType}, price={self.price})"


# Position Structure
class Position:
    """
    Position Structure
    """

    def __init__(self, ticker, orderType, quantity, ep):
        """
                Position Structure

        :param ticker: Ticker
        :param orderType: Order Type
        :param quantity: Quantity
        :param ep: Entry Price
        """
        self.ticker = ticker
        self.orderType = orderType
        self.quantity = quantity
        self.entry_price = ep

    def __str__(self):
        return f"Position(ticker={self.ticker}, orderType={self.orderType}, quantity={self.quantity}, entry_price={self.entry_price})"

    def __repr__(self):
        return f"Position(ticker={self.ticker}, orderType={self.orderType}, quantity={self.quantity}, entry_price={self.entry_price})"


class Player:
    def __init__(self, id, name, cash, positions, orders, game_id):
        self.id = id
        self.name = name
        self.cash = cash
        self.positions = positions
        self.orders = orders
        self.game_id = game_id
        self.url = f"https://www.marketwatch.com/games/{game_id}/portfolio?pub{id}"

    def __str__(self):
        return f"Player(id={self.id}, name={self.name}, cash={self.cash}, positions={self.positions}, orders={self.orders}, game_id={self.game_id}, url={self.url})"

    def __repr__(self):
        return f"Player(id={self.id}, name={self.name}, cash={self.cash}, positions={self.positions}, orders={self.orders}, game_id={self.game_id}, url={self.url})"


# Game Structure
class Game:
    """
    Game Structure
    """

    def __init__(self, id, name, status, start, end, cash, positions, orders):
        """
        Game Structure

        :param id: Game ID
        :param name: Game Name
        :param status: Game Status
        :param start: Game Start Time
        :param end: Game End Time
        :param cash: Cash
        :param positions: Positions
        :param orders: Orders
        """
        self.id = id
        self.name = name
        self.status = status
        self.start = start
        self.end = end
        self.cash = cash
        self.positions = positions
        self.orders = orders
        self.settings = GameSettings()

    def __str__(self):
        return f"Game(id={self.id}, name={self.name}, status={self.status}, start={self.start}, end={self.end}, cash={self.cash}, positions={self.positions}, orders={self.orders}, settings={self.settings})"

    def __repr__(self):
        return f"Game(id={self.id}, name={self.name}, status={self.status}, start={self.start}, end={self.end}, cash={self.cash}, positions={self.positions}, orders={self.orders}, settings={self.settings})"
