# Marketwatch API Python Library

[![Python package]()]
[![PyPI version]()]
[![PyPI pyversions]()]
[![PyPI status]()]
[![PyPI license]()]

A Python libary to interact with the MarketWatch Stock Market Game
Based on code from

- https://github.com/kevindong/MarketWatch_API/
- https://github.com/bwees/pymarketwatch

### Example

```
if __name__ == "__main__":
    import os
    username = os.environ.get("MARKETWATCH_USERNAME")
    password = os.environ.get("MARKETWATCH_PASSWORD")

    marketwatch = MarketWatch(username, password)

    print(f"Price: {marketwatch.get_price('AAPL')} \n")
    print(f"Games: {marketwatch.get_games()} \n")

    games1 = marketwatch.get_games()[0]["name"].lower().replace(" ", "-")

    print(f"Game: {marketwatch.get_game(games1)} \n")
    print(f"Game Settings: {marketwatch.get_game_settings(games1)} \n")

    print(f"Leaderboard: {marketwatch.get_leaderboard(games1)} \n")
    print(f"Porfolio: {marketwatch.get_portfolio(games1)} \n")

    print(f"Position: {marketwatch.get_positions(games1)}")
    print(f"Orders Pending: {marketwatch.get_pending_orders(games1)}")
    marketwatch.buy(games1, "AAPL", 100)

    print(f"Position diff: {marketwatch.get_positions(games1)}")
```
