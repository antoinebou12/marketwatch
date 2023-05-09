### Import
To start using the marketwatch library, import the MarketWatch class:
```python
from marketwatch import MarketWatch
```

### Login
Create a MarketWatch instance and log in with your username and password:
```python
marketwatch = MarketWatch(username, password)
```

### Get Price
Fetch the current price of a stock by passing its ticker symbol:
```python
marketwatch.get_price("AAPL")
```

### Get Games
Retrieve the list of games you are participating in:
```python
marketwatch.get_games()
```

### Get Game
Fetch detailed information about a specific game by providing the game's name:
```python
marketwatch.get_game("game-name")
```

### Get Game Settings
Access the settings of a specific game:
```python
marketwatch.get_game_settings("game-name")
```

### Get Leaderboard
Retrieve the leaderboard data for a specific game:
```python
marketwatch.get_leaderboard("game-name")
```

### Get Portfolio
Fetch your portfolio information in a specific game:
```python
marketwatch.get_portfolio("game-name")
```

### Get Portfolio Performance
Retrieve the performance of your portfolio in a specific game:
```python
marketwatch.get_portfolio_performance("game-name")
```

### Get Transactions
Access the transaction history for your portfolio in a specific game:
```python
marketwatch.get_transactions("game-name")
```

### Get Positions
Fetch the current positions of your portfolio in a specific game:
```python
marketwatch.get_positions("game-name")
```

### Get Pending Orders
Retrieve the list of pending orders for your portfolio in a specific game:
```python
marketwatch.get_pending_orders("game-name")
```

### Buy
Place a buy order for a specific stock by providing the game's name, the stock's ticker symbol, and the number of shares:
```python
marketwatch.buy("game-name", "AAPL", 100)
```

### Sell
Place a sell order for a specific stock by providing the game's name, the stock's ticker symbol, and the number of shares:
```python
marketwatch.sell("game-name", "AAPL", 100)
```

### Create Watchlist
Create a new watchlist by providing a name and optionally a list of tickers:
```python
marketwatch.create_watchlist("My Watchlist", ["AAPL", "GOOG", "TSLA"])
```

### Add to Watchlist
Add tickers to an existing watchlist by providing the watchlist ID and a list of tickers:
```python
marketwatch.add_to_watchlist("watchlist_id", ["MSFT", "AMZN"])
```

### Get Watchlists
Retrieve all your watchlists:
```python
marketwatch.get_watchlists()
```

### Get Watchlist
Fetch a specific watchlist by providing its ID:
```python
marketwatch.get_watchlist("watchlist_id")
```

### Delete Watchlist
Delete a specific watchlist by providing its ID:
```python
marketwatch.delete_watchlist("watchlist_id")
```

### Delete Watchlist Item
Remove a ticker from a watchlist by providing the watchlist ID and the ticker:
```python
marketwatch.delete_watchlist_item("watchlist_id", "AAPL")
```

For more examples and detailed explanations of each function, visit the official GitHub repository of the marketwatch library.
