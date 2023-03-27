from marketwatch import MarketWatch


class MarketWatchGame(MarketWatch):
    def __init__(self, email, password, game_id):
        super().__init__(email, password)
        self.game_id = game_id
