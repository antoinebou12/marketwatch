# Algo Trading with MarketWatch API

## Overview

This project is an example of how to automate stock trading based on Exponential Moving Averages (EMAs) using the MarketWatch API.

## Prerequisites

- Python 3.8+
- pandas
- marketwatch Python package

## Configuration

Before running the script, you need to replace the following placeholder values:

- `your_username_here` with your MarketWatch username
- `your_password_here` with your MarketWatch password
- `your_game_name_here` with your MarketWatch game name

These values are located at the top of the main script.

## How It Works

### Exponential Moving Averages (EMAs)

This project uses two EMAs:

- Short-term EMA (20 periods)
- Long-term EMA (80 periods)

### Trading Signals

1. **Golden Cross**: When the short-term EMA crosses above the long-term EMA, it's a signal to buy.
2. **Death Cross**: When the short-term EMA crosses below the long-term EMA, it's a signal to sell.



### Algorithm Flow

1. The script fetches the latest price of a stock (in this example, AAPL).
2. It calculates the short-term and long-term EMAs.
3. If a Golden Cross is detected, it places a buy order.
4. If a Death Cross is detected, it places a sell order.

![Strat](http://www.plantuml.com/plantuml/dpng/jPF1QlCm48JlVeeX9mSIo7_DuITfKdffe912ZsOhBOcfB0Lf5SZRLxOfLeERjeTUR7OrysaOq2e8UOcDAKY9yzXHRVVAroSfs4ej5zplri-UDFkFnOxy6yiBYJeMhQi-at1c77Q3DPDbPkFS2Hjd32l1beH0LgEp500o9kR_1zeIqluhPolbNGZkpBwSTewHgzlzC2PGdc690qjryhNYSh9UFprEhZXvNW3vZFddK9ubUeiErcarZs560cKGHKP5Gy8LDrHEhxL9F9IoxAk2PbM7sbaqQUhnP0GFpcYssBGLTSlRHRp6ItcWXYkRFZFqRSpmRx7eKzoivPjgxk85GKZY44Jpbp0sWR5bakEFmmSsvi_IxnFyD_6jBeehJVw8qgdciNUpIcUnCUy0)

## Usage

Run the script:

[python main.py](https://github.com/antoinebou12/marketwatch/blob/main/notebook/ema.ipynb)

```
import time
import pandas as pd
from marketwatch import MarketWatch

def calculate_ema(price_series, periods):
    return price_series.ewm(span=periods, adjust=False).mean()

def trade_on_crossover(df, marketwatch, game_name, symbol, quantity):
    short_term = df['EMA_Short'].iloc[-1]
    long_term = df['EMA_Long'].iloc[-1]
    prev_short_term = df['EMA_Short'].iloc[-2]
    prev_long_term = df['EMA_Long'].iloc[-2]
    
    if short_term > long_term and prev_short_term <= prev_long_term:
        print('Golden Cross detected. Attempting to buy stock.')
        marketwatch.buy(game_name, symbol, quantity)
        
        positions = marketwatch.get_positions(game_name)
        if any(pos['ticker'] == symbol for pos in positions):
            print('Buy order successful.')
        else:
            print('Buy order failed.')
        
    elif short_term < long_term and prev_short_term >= prev_long_term:
        print('Death Cross detected. Attempting to sell stock.')
        marketwatch.sell(game_name, symbol, quantity)
        
        positions = marketwatch.get_positions(game_name)
        if not any(pos['ticker'] == symbol for pos in positions):
            print('Sell order successful.')
        else:
            print('Sell order failed.')

def main(username, password, game_name, symbol, short_term_period, long_term_period, quantity):
    marketwatch = MarketWatch(username, password)
    price_data = []
    
    for _ in range(max(short_term_period, long_term_period) * 2):  # Collect more data points
        price = marketwatch.get_price(symbol)
        price_data.append(price)
        if len(price_data) > 150:
            price_data.pop(0)
        
        df = pd.DataFrame(price_data, columns=['Close'])
        df['EMA_Short'] = calculate_ema(df['Close'], short_term_period)
        df['EMA_Long'] = calculate_ema(df['Close'], long_term_period)
        
        if len(df) >= long_term_period:
            trade_on_crossover(df, marketwatch, game_name, symbol, quantity)
        
        time.sleep(60)

if __name__ == "__main__":
    username = 'your_username_here'
    password = 'your_password_here'
    game_name = 'your_game_name_here'
    symbol = 'AAPL'
    short_term_period = 20
    long_term_period = 80
    quantity = 100
    
    main(username, password, game_name, symbol, short_term_period, long_term_period, quantity)
```

The script will execute trades in your MarketWatch game based on the detected EMAs.

## Tutorials

- [MarketWatch Help](https://www.marketwatch.com/help)
- [MarketWatch API Wiki](https://github.com/antoinebou12/marketwatch/wiki)
