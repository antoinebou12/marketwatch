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

### Get Portfolio Performance

```
marketwatch.get_portfolio_performance("game-name")
```

### Get Transactions

```
marketwatch.get_transactions("game-name")
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