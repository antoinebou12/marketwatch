from marketwatch import MarketWatch


class MarketWatchGame(MarketWatch):
    def __init__(self, email, password, game_id):
        super().__init__(email, password)
        self.game_id = game_id
        self.game = self.get_game()
        self.ledger_id = super().get_ledger_id(self.game_id)

    def get_settings(self):
        return super().get_game_settings(self.game_id)

    def get_leaderboard(self):
        return super().get_leaderboard(self.game_id)

    def get_orders(self):
        return super().get_pending_orders(self.game_id)

    def get_portfolio(self):
        return super().get_portfolio(self.game_id)

    def get_game(self):
        return super().get_game(self.game_id)

    def get_portfolio_performance(
        self, download: bool = False, next_page_url: str = None
    ):
        return super().get_portfolio_performance(self.game_id, download, next_page_url)

    def get_transactions(self, download: bool = False, next_page_url: str = None):
        return super().get_transactions(self.game_id, download, next_page_url)

    def get_positions(self, download: bool = False):
        return super().get_positions(self.game_id, download)