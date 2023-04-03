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