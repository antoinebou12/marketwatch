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
	marketwatch = MarketWatch(
		"username", "password"
	)

	print(marketwatch.get_games())
	games1 = marketwatch.get_games()[0]["name"].lower().replace(" ", "-")
	print(marketwatch.get_game(games1))
	print(marketwatch.get_price("AAPL"))
	print(marketwatch.get_portfolio(games1))
```
