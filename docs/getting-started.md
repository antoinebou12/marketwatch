# MarketWatch Python Library

This is a Python library for interacting with the [MarketWatch](https://www.marketwatch.com/) virtual trading platform. The library provides an easy-to-use interface for performing various actions such as getting game details, portfolio information, buying and selling stocks, getting leaderboard information, and more.

## Installation

```python
pip install marketwatch
```

## Usage

First, you need to create an account on [MarketWatch](https://www.marketwatch.com/) and then create a virtual game.

Once you have created a game, you will be able to get the game's `id` from its URL, which will be used throughout the library.

```python
if __name__ == "__main__":
    import os
    username = os.environ.get("MARKETWATCH_USERNAME")
    password = os.environ.get("MARKETWATCH_PASSWORD")

    marketwatch = MarketWatch(username, password)
```

### Examples

```python
import os
from marketwatch import MarketWatch
```

```python
# Login
mw = MarketWatch(os.environ["MARKETWATCH_USERNAME"], os.environ["MARKETWATCH_PASSWORD"])
```

#### Get Games

```python
mw.get_games()
```

This method returns a list of games the user has created or joined. For each game, you get its `name`, `url`, `id`, `return`, `total_return`, `rank`, `end`, and `players`.

#### Get portfolio

```python
mw.get_portfolio(game_id)
```

This method returns a dictionary containing information about the user's portfolio, including the `ticker`, `quantity`, `price`, `value`, and `value_percentage` for each holding. `game_id` is the `id` of the game you want to retrieve the portfolio for.

#### Buy and Sell stocks

```python
mw.buy(game_id, ticker, quantity)
mw.sell(game_id, ticker, quantity)
```

These methods allow the user to buy or sell stocks in the specified game. `game_id` is the `id` of the game you want to trade in, `ticker` is the stock's symbol, and `quantity` is the number of shares you want to buy or sell.

#### Get leaderboard

```python
mw.get_leaderboard(game_id)
```

This method returns a list of the top players in the specified game. For each player, you get their `rank`, `name`, `return`, and `return_percentage`. `game_id` is the `id` of the game you want to retrieve the leaderboard for.

#### Get game settings

```python
mw.get_game_settings(game_id)
```

This method returns a dictionary containing information about the specified game, including the `id`, `name`, `description`, `end_date`, `currency`, `starting_balance`, `transaction_fee`, `margin_interest_rate`, `order_types`, and `leverage`.

#### Get stock price

```
mw.get_price(ticker)
```

This method returns the current price of the specified stock.

#### Get positions

```mw.get_positions(game_id)```

This method returns a list of the user's current positions in the specified game. For each position, you get the `ticker`, `quantity`, `price`, `gain`, `gain_percentage`, `value`, and `value_percentage`.

#### Get pending orders

```mw.get_pending_orders(game_id)```

This method returns a list of the user's pending orders in the specified game. For each order, you get the `ticker`, `quantity`, `price`, `order_type`, and `expiration`.


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