"""
This module contains the MarketWatchWatchlist class.

The MarketWatchWatchlist class is a subclass of the MarketWatch class.
It is used to interact with a specific watchlist on MarketWatch.

Example:
    from marketwatch import MarketWatchWatchlist

    watchlist = MarketWatchWatchlist(email, password, watchlist_id)
    watchlist.add_item('AAPL')
    watchlist.delete_item('AAPL')
    watchlist.create('My Watchlist')
    watchlist.delete()
    watchlist.watchlists
    watchlist.watchlist
"""

from marketwatch import MarketWatch


class MarketWatchWatchlist(MarketWatch):
    """
    MarketWatchWatchlist class is a subclass of MarketWatch class.
    It is used to interact with a specific watchlist on MarketWatch.
    """
    def __init__(self, email, password, watchlist):
        super().__init__(email, password)
        self._id = watchlist

    def delete_item(self, ticker: str) -> dict:
        """
        Deletes an item from the watchlist.

        :param ticker: str
        :return: dict
        """
        return super().delete_watchlist_item(self._id, ticker)

    def add_item(self, ticker: str) -> dict:
        """
        Adds an item to the watchlist.

        :param ticker: str
        :return: dict
        """
        return super().add_to_watchlist(self._id, ticker)

    def create(self, name: str) -> dict:
        """
        Creates a watchlist.

        :param name: str
        :return: dict
        """

        return super().create_watchlist(name)

    def delete(self) -> dict:
        """
        Deletes a watchlist.

        :return: dict
        """
        return super().delete_watchlist(self._id)

    @property
    def watchlists(self):
        """
        Returns the watchlists for the game.

        :return: dict
        """
        return super().get_watchlists()

    @property
    def watchlist(self):
        """
        Returns the watchlist for the game.

        :return: dict
        """
        return super().get_watchlist(self._id)

    @property
    def watchlist_id(self):
        """
        Returns the watchlist id.

        :return: str
        """
        return self._id
