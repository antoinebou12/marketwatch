# pymarketwatch

A Python libary to interact with the MarketWatch Stock Market Game
Based on code from https://github.com/kevindong/MarketWatch_API/, https://github.com/bwees/pymarketwatch

### Example

```
from marketwatch import MarketWatch

api = MarketWatch("email", "password")
api.set_game("algoets")
api.buy("AAPL", 100)

print(api.get_pending_orders())
print(api.get_positions())
```
