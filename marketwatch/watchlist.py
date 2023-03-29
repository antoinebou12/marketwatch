from marketwatch import MarketWatch


class MarketWatchWatchlist(MarketWatch):
    def __init__(self, email, password, game_id):
        super().__init__(email, password)

    def get_watchlist(self):
        return super().get_watchlist()

    def delete_watchlist_item(self, watchlist_id: str, ticker: str):
        return super().delete_watchlist_item(watchlist_id, ticker)

    def add_watchlist_item(self, watchlist_id: str, ticker: str):
        return super().add_to_watchlist(watchlist_id, ticker)

    def delete_watchlist(self, watchlist_id: str):
        return super().delete_watchlist(watchlist_id)