# Marketwatch API Python Library

![PyPI](https://img.shields.io/pypi/v/marketwatch)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/marketwatch)
![PyPI - License](https://img.shields.io/pypi/l/marketwatch)
![PyPI - Downloads](https://img.shields.io/pypi/dm/marketwatch)
![GitHub last commit](https://img.shields.io/github/last-commit/antoinebou12/marketwatch)
[![Python Test and Build](https://github.com/antoinebou12/marketwatch/actions/workflows/python-test.yml/badge.svg)](https://github.com/antoinebou12/marketwatch/actions/workflows/python-test.yml)
![Coverage](https://raw.githubusercontent.com/antoinebou12/marketwatch/main/.github/badge/coverage.svg)

[MarketWatch](https://www.marketwatch.com)

[Documentation](https://antoinebou12.github.io/marketwatch/)

A Python libary to interact with the MarketWatch Stock Market Game
Based on code from

- https://github.com/kevindong/MarketWatch_API/
- https://github.com/bwees/pymarketwatch

## Feature
- [X]  Logging in and out of the site
- [X]  Getting the current price of a stock
- [X]  Getting information about games on the site
- [X]  Buying, selling, shorting, and covering stocks in a game
- [X]  Creating, adding to, getting, and deleting watchlists
- [X]  Getting, adding to, and deleting items from a portfolio
- [X]  Getting and cancelling pending orders
- [X]  Checking if the game is down

## Installation

```shell
pip install marketwatch
```

```shell
pip install git+https://github.com/antoinebou12/marketwatch.git
```

```shell
git clone https://github.com/antoinebou12/marketwatch.git
```

## Usage
Here are some examples of how you can use the MarketWatch class:

### Import
First, import the MarketWatch class from the script:
```python
from marketwatch import MarketWatch
```

### Login
Then, create an instance of the MarketWatch class using your MarketWatch username and password:
```python
marketwatch = MarketWatch(username, password)
```

### Get Stock Price
To get the current price of a stock:
```python
marketwatch.get_price("AAPL")
```

### Interact with Games
https://www.marketwatch.com/games

To get information about games on the site:
```python
marketwatch.get_games()
```

### Get Game
```python
marketwatch.get_game("game-name")
```

### Get Game Settings
```python
marketwatch.get_game_settings("game-name")
```

### Get Leaderboard
```python
marketwatch.get_leaderboard("game-name")
```

### Get Portfolio
```python
marketwatch.get_portfolio("game-name")
```

### Get Positions
```python
marketwatch.get_positions("game-name")
```

### Get Pending Orders 
```python
marketwatch.get_pending_orders("game-name")
```

### Buy Stock
```python
marketwatch.buy(game_id, "AAPL", 100)
```

### Sell Stock
```python
marketwatch.sell("game-name", "AAPL", 100)
```

### Create Watchlist
https://www.marketwatch.com/watchlist

To create a watchlist:
```python
marketwatch.create_watchlist('My Watchlist')
```

### Add Stock to Watchlist
To add stocks to a watchlist:
```python
marketwatch.add_to_watchlist(watchlist_id, ['AAPL', 'GOOG'])
```

### Get All Watchlists
To get all watchlists:
```python
watchlists = marketwatch.get_watchlists()
```

### Delete Watchlist
To delete a watchlist:
```python
marketwatch.delete_watchlist(watchlist_id)
```

### Example

```python
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

## Contributing
Contributions are welcome. Please open an issue or submit a pull request.

## License
This project is licensed under the MIT License.
