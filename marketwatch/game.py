"""
This module contains the MarketWatchGame class.

The MarketWatchGame class is a subclass of the MarketWatch class.
It is used to interact with a specific game on MarketWatch.

Example:
    from marketwatch import MarketWatchGame

    game = MarketWatchGame(email, password, game_id)
    game.settings
    game.leaderboard
    game.orders
    game.portfolio
    game.game
    game.portfolio_performance

"""

from marketwatch import MarketWatch


class MarketWatchGame(MarketWatch):
    """
    MarketWatchGame class is a subclass of MarketWatch class.
    It is used to interact with a specific game on MarketWatch.
    """
    def __init__(self, email: str, password: str, game_id: str) -> None:
        super().__init__(email, password)
        self._id = game_id
        self.ledger_id = super().get_ledger_id(self._id)

    def create_game(self, name: str, start_date: int, end_date: int, **kwargs) -> dict:
        """
        Creates a game on MarketWatch.

        :param name: str
        :param start_date: int
        :param end_date: int
        :param kwargs: dict

        """
        return super().create_game(name, start_date, end_date, **kwargs)

    def buy(self, symbol: str, quantity: int, order_type: str = 'market', **kwargs) -> dict:
        """
        Buy a stock on MarketWatch.

        :param symbol: str
        :param quantity: int
        :param order_type: str
        :param kwargs: dict
        :return: dict

        """
        return super().buy(self._id, symbol, quantity, order_type, **kwargs)

    def sell(self, symbol: str, quantity: int, order_type: str = 'market', **kwargs) -> dict:
        """
        Sell a stock on MarketWatch.

        :param symbol: str
        :param quantity: int
        :param order_type: str
        :param kwargs: dict
        :return: dict

        """
        return super().sell(self._id, symbol, quantity, order_type, **kwargs)

    def short(self, symbol: str, quantity: int, order_type: str = 'market', **kwargs) -> dict:
        """
        Short a stock on MarketWatch.

        :param symbol: str
        :param quantity: int
        :param order_type: str
        :param kwargs: dict
        :return: dict

        """
        return super().short(self._id, symbol, quantity, order_type, **kwargs)

    def cover(self, symbol: str, quantity: int, order_type: str = 'market', **kwargs) -> dict:
        """
        Cover a stock on MarketWatch.

        :param symbol: str
        :param quantity: int
        :param order_type: str
        :param kwargs: dict
        :return: dict

        """
        return super().cover(self._id, symbol, quantity, order_type, **kwargs)

    def reset_game(self):
        """
        Reset this specific game using the stored game_id.

        :return: dict or str indicating the status of the operation
        """
        return super().reset_game(self._id)

    def cancel(self, order_id: str) -> dict:
        """
        Cancel an order on MarketWatch.

        :param order_id: str
        :return: dict

        """
        return super().cancel_order(self._id, order_id)

    def cancel_all(self) -> dict:
        """
        Cancel all orders on MarketWatch.

        :return: dict

        """
        return super().cancel_all_orders(self._id)

    @property
    def settings(self) -> dict:
        """
        Returns the game settings for the game.
        :return: dict
        """
        return super().get_game_settings(self._id)

    @property
    def leaderboard(self)-> dict:
        """
        Returns the leaderboard for the game.
        :return: dict
        """
        return super().get_leaderboard(self._id)

    @property
    def orders(self):
        """
        Returns the orders for the game.

        :return: dict
        """
        return super().get_pending_orders(self._id)

    @property
    def portfolio(self):
        """
        Returns the portfolio for the game.

        :return: dict
        """
        return super().get_portfolio(self.game_id)

    @property
    def game(self) -> dict:
        """
        Returns the game for the game.

        :return: dict
        """
        return super().get_game(self._id)

    @property
    def portfolio_performance(self, download: bool = False, next_page_url: str = None):
        """
        Returns the portfolio performance for the game.

        :param download: bool
        :param next_page_url: str
        :return: dict
        """
        return super().get_portfolio_performance(self._id, download, next_page_url)

    @property
    def transactions(self, download: bool = False, next_page_url: str = None):
        """
        Returns the transactions for the game.

        :param download: bool
        :param next_page_url: str
        :return: dict
        """
        return super().get_transactions(self._id, download, next_page_url)

    @property
    def positions(self, download: bool = False):
        """
        Returns the positions for the game.

        :param download: bool
        :return: dict
        """
        return super().get_positions(self._id, download)

    @property
    def game_id(self):
        """
        Returns the game id.

        :return: str
        """
        return self._id
