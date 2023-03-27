# Marketwatch API Python Library

![PyPI](https://img.shields.io/pypi/v/marketwatch)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/marketwatch)
![PyPI - License](https://img.shields.io/pypi/l/marketwatch)
![PyPI - Downloads](https://img.shields.io/pypi/dm/marketwatch)
![GitHub last commit](https://img.shields.io/github/last-commit/antoinebou12/marketwatch)
[![Publish 📦 to PyPI](https://github.com/antoinebou12/marketwatch/actions/workflows/python-publish.yml/badge.svg?branch=main)](https://github.com/antoinebou12/marketwatch/actions/workflows/python-publish.yml)
[![Python Test and Build](https://github.com/antoinebou12/marketwatch/actions/workflows/python-test.yml/badge.svg)](https://github.com/antoinebou12/marketwatch/actions/workflows/python-test.yml)
![Coverage](https://raw.githubusercontent.com/antoinebou12/marketwatch/main/.github/badge/coverage.svg)

https://www.marketwatch.com

A Python libary to interact with the MarketWatch Stock Market Game
Based on code from

- https://github.com/kevindong/MarketWatch_API/
- https://github.com/bwees/pymarketwatch

## Installation

```
pip install marketwatch
```

```
pip install git+https://github.com/antoinebou12/marketwatch.git
```

```
git clone https://github.com/antoinebou12/marketwatch.git
```

## Usage

### Import

```
from marketwatch import MarketWatch
```

### Login

```
marketwatch = MarketWatch(username, password)
```

### Get Price

```
marketwatch.get_price("AAPL")
```

### Get Games

```
marketwatch.get_games()
```

### Get Game

```
marketwatch.get_game("game-name")
```

### Get Game Settings

```
marketwatch.get_game_settings("game-name")
```

### Get Leaderboard

```
marketwatch.get_leaderboard("game-name")
```

### Get Portfolio

```
marketwatch.get_portfolio("game-name")
```

### Get Positions

```
marketwatch.get_positions("game-name")
```

### Get Pending Orders

```
marketwatch.get_pending_orders("game-name")
```

### Buy

```
marketwatch.buy("game-name", "AAPL", 100)
```

### Sell

```
marketwatch.sell("game-name", "AAPL", 100)
```

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
