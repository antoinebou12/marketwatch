### Import
To start using the marketwatch library, import the MarketWatch class:
```
from marketwatch import MarketWatch
```

### Login
Create a MarketWatch instance and log in with your username and password:
```
marketwatch = MarketWatch(username, password)
```

### Get Price
Fetch the current price of a stock by passing its ticker symbol:
```
marketwatch.get_price("AAPL")
```

### Get Games
Retrieve the list of games you are participating in:
```
marketwatch.get_games()
```

### Get Game
Fetch detailed information about a specific game by providing the game's name:
```
marketwatch.get_game("game-name")
```

### Get Game Settings
Access the settings of a specific game:
```
marketwatch.get_game_settings("game-name")
```

### Get Leaderboard
Retrieve the leaderboard data for a specific game:
```
marketwatch.get_leaderboard("game-name")
```

### Get Portfolio
Fetch your portfolio information in a specific game:
```
marketwatch.get_portfolio("game-name")
```

### Get Portfolio Performance
Retrieve the performance of your portfolio in a specific game:
```
marketwatch.get_portfolio_performance("game-name")
```

### Get Transactions
Access the transaction history for your portfolio in a specific game:
```
marketwatch.get_transactions("game-name")
```

### Get Positions
Fetch the current positions of your portfolio in a specific game:
```
marketwatch.get_positions("game-name")
```

### Get Pending Orders
Retrieve the list of pending orders for your portfolio in a specific game:
```
marketwatch.get_pending_orders("game-name")
```

### Buy
Place a buy order for a specific stock by providing the game's name, the stock's ticker symbol, and the number of shares:
```
marketwatch.buy("game-name", "AAPL", 100)
```

### Sell
Place a sell order for a specific stock by providing the game's name, the stock's ticker symbol, and the number of shares:
```
marketwatch.sell("game-name", "AAPL", 100)
```
For more examples and detailed explanations of each function, visit the official GitHub repository of the marketwatch library.
