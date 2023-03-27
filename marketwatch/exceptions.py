class MarketWatchException(Exception):
    def __init__(self, message):
        self.message = f"MarketWatchException: {message}"


class MarketWatchGameException(Exception):
    def __init__(self, message):
        self.message = f"MarketWatchException: {message}"
