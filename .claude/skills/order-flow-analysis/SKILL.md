---
name: order-flow-analysis
description: "Order flow analysis — volume profile, footprint charts, delta for short-term price prediction. Use when: User is analyzing intraday order flow for trading signals; Building volume profile analysis (POC, value area, single prints); Using cumulative delta and footprint charts for directional bias."
---

# Order Flow Analysis

> Order flow analysis — volume profile, footprint charts, delta for short-term price prediction.

## When to Activate

- User is analyzing intraday order flow for trading signals
- Building volume profile analysis (POC, value area, single prints)
- Using cumulative delta and footprint charts for directional bias
- Identifying aggressor imbalances and absorption patterns
- Predicting short-term price moves from order flow data

## Core Concepts

### What Is Order Flow?

Order flow is the stream of actual buy and sell transactions hitting the market. Unlike price charts, which show outcomes, order flow reveals the process — who is aggressive, where liquidity rests, and where price is accepted or rejected.

Key distinction:
- **Passive orders**: limit orders resting on the book (provide liquidity)
- **Aggressive orders**: market orders or marketable limit orders that cross the spread (take liquidity)

Price moves when aggressive demand exceeds passive supply (or vice versa). Order flow analysis identifies these imbalances in real time.

### Volume Profile

Volume profile shows the distribution of traded volume at each price level over a defined period:

- **Point of Control (POC)**: the price level with the highest traded volume — acts as a magnet
- **Value Area (VA)**: the price range containing 70% of total volume (one standard deviation)
- **Value Area High (VAH)**: upper boundary of the value area — resistance
- **Value Area Low (VAL)**: lower boundary — support
- **High Volume Nodes (HVN)**: prices with concentrated volume — acceptance zones, tend to attract price
- **Low Volume Nodes (LVN)**: prices with thin volume — rejection zones, price moves quickly through these

### Cumulative Delta

Delta = volume traded at the ask (buyer-initiated) minus volume traded at the bid (seller-initiated):

```
Delta = Ask Volume - Bid Volume
```

- **Positive delta**: net buying pressure
- **Negative delta**: net selling pressure
- **Cumulative delta**: running sum of delta over time

Divergences between cumulative delta and price are powerful signals:
- Price rising + delta falling = buying exhaustion (bearish divergence)
- Price falling + delta rising = selling exhaustion (bullish divergence)

### Footprint Charts

Footprint charts (also called order flow charts) show bid/ask volume at each price level within each candle:

```
Price   Bid Vol x Ask Vol
150.05   1200  x  3500    ← aggressive buying
150.00   2800  x  2900    ← balanced
149.95   4100  x  1500    ← aggressive selling
149.90   3200  x  800     ← aggressive selling
```

Imbalance ratios (ask/bid at each price) reveal where aggressive participants dominate.

## Methodology

### Step 1: Classify Trade Direction

```python
import pandas as pd
import numpy as np

def classify_trades_tick_rule(trades):
    """
    Tick rule: classify trades as buyer/seller initiated.
    - Trade at higher price than previous = buyer-initiated
    - Trade at lower price than previous = seller-initiated
    - Same price = use previous classification
    """
    trades = trades.copy()
    trades['price_change'] = trades['price'].diff()

    trades['direction'] = 0  # 0 = unknown
    trades.loc[trades['price_change'] > 0, 'direction'] = 1   # uptick = buy
    trades.loc[trades['price_change'] < 0, 'direction'] = -1  # downtick = sell

    # Forward-fill zeros (same price uses last direction)
    trades['direction'] = trades['direction'].replace(0, np.nan).ffill().fillna(1)

    trades['buy_volume'] = trades['size'] * (trades['direction'] == 1)
    trades['sell_volume'] = trades['size'] * (trades['direction'] == -1)

    return trades

def classify_trades_quote_rule(trades, quotes):
    """
    Quote rule (more accurate than tick rule):
    - Trade above midpoint = buyer-initiated
    - Trade below midpoint = seller-initiated
    - At midpoint = use tick rule as tiebreaker
    """
    merged = pd.merge_asof(trades, quotes, on='timestamp', direction='backward')
    merged['midpoint'] = (merged['bid'] + merged['ask']) / 2

    merged['direction'] = 0
    merged.loc[merged['price'] > merged['midpoint'], 'direction'] = 1
    merged.loc[merged['price'] < merged['midpoint'], 'direction'] = -1

    # Lee-Ready: at midpoint, use tick rule
    at_mid = merged['direction'] == 0
    merged.loc[at_mid, 'direction'] = classify_trades_tick_rule(
        merged.loc[at_mid]
    )['direction']

    return merged
```

### Step 2: Volume Profile Construction

```python
def build_volume_profile(trades, tick_size=0.01, value_area_pct=0.70):
    """
    Build volume profile from trade data.
    """
    # Round prices to tick size
    trades['price_level'] = (trades['price'] / tick_size).round() * tick_size

    # Aggregate volume at each price level
    profile = trades.groupby('price_level').agg(
        total_volume=('size', 'sum'),
        buy_volume=('buy_volume', 'sum'),
        sell_volume=('sell_volume', 'sum'),
        trade_count=('size', 'count'),
    )

    # Point of Control
    poc = profile['total_volume'].idxmax()

    # Value Area: expand from POC until 70% of volume is captured
    total_vol = profile['total_volume'].sum()
    target_vol = total_vol * value_area_pct

    va_volume = profile.loc[poc, 'total_volume']
    va_high = poc
    va_low = poc
    prices_sorted = profile.index.sort_values()

    while va_volume < target_vol:
        # Expand in the direction with more volume
        high_idx = prices_sorted.get_loc(va_high)
        low_idx = prices_sorted.get_loc(va_low)

        vol_above = profile.loc[prices_sorted[high_idx + 1], 'total_volume'] if high_idx + 1 < len(prices_sorted) else 0
        vol_below = profile.loc[prices_sorted[low_idx - 1], 'total_volume'] if low_idx > 0 else 0

        if vol_above >= vol_below:
            va_high = prices_sorted[high_idx + 1]
            va_volume += vol_above
        else:
            va_low = prices_sorted[low_idx - 1]
            va_volume += vol_below

    return {
        'profile': profile,
        'poc': poc,
        'vah': va_high,
        'val': va_low,
        'total_volume': total_vol,
    }
```

### Step 3: Footprint Chart Analysis

```python
def build_footprint(trades, bar_interval='5min', tick_size=0.01):
    """
    Build footprint (bid x ask at each price) for each time bar.
    """
    trades['bar'] = trades['timestamp'].dt.floor(bar_interval)
    trades['price_level'] = (trades['price'] / tick_size).round() * tick_size

    footprint = trades.groupby(['bar', 'price_level']).agg(
        bid_vol=('sell_volume', 'sum'),
        ask_vol=('buy_volume', 'sum'),
        total_vol=('size', 'sum'),
    )

    footprint['delta'] = footprint['ask_vol'] - footprint['bid_vol']
    footprint['imbalance_ratio'] = footprint['ask_vol'] / footprint['bid_vol'].clip(lower=1)

    return footprint

def detect_imbalances(footprint, imbalance_threshold=3.0):
    """
    Flag price levels with significant buyer/seller imbalance.
    Imbalance ratio > 3 = strong aggressor dominance at that price.
    """
    footprint['buy_imbalance'] = footprint['imbalance_ratio'] > imbalance_threshold
    footprint['sell_imbalance'] = (1 / footprint['imbalance_ratio']) > imbalance_threshold

    # Stacked imbalances: 3+ consecutive prices with buy imbalance = strong demand
    # These often indicate institutional buying
    return footprint
```

### Step 4: Cumulative Delta Analysis

```python
def cumulative_delta(trades, interval='1min'):
    """
    Compute cumulative delta over time intervals.
    """
    trades['interval'] = trades['timestamp'].dt.floor(interval)

    delta_series = trades.groupby('interval').apply(
        lambda g: g['buy_volume'].sum() - g['sell_volume'].sum()
    )

    cum_delta = delta_series.cumsum()

    return cum_delta

def delta_divergence(price_series, cum_delta, lookback=20):
    """
    Detect divergences between price and cumulative delta.

    Bearish divergence: price makes new high but cum_delta doesn't
    Bullish divergence: price makes new low but cum_delta doesn't
    """
    price_high = price_series.rolling(lookback).max()
    delta_at_price_high = cum_delta[price_series == price_high]

    # If price is at new high but delta is below its previous value at the last high
    # → bearish divergence (buyers are weakening)

    divergences = []
    highs = price_series[price_series == price_high].index
    for i in range(1, len(highs)):
        if cum_delta[highs[i]] < cum_delta[highs[i-1]]:
            divergences.append({
                'time': highs[i],
                'type': 'bearish',
                'price': price_series[highs[i]],
                'delta_deficit': cum_delta[highs[i]] - cum_delta[highs[i-1]]
            })

    return divergences
```

### Step 5: Absorption Detection

```python
def detect_absorption(footprint, price_series, volume_threshold=2.0):
    """
    Absorption: large volume at a price level but price doesn't move through it.
    Indicates strong passive orders absorbing aggressive flow.

    Buy absorption: large sell aggression at a level, but price holds = hidden buyer
    Sell absorption: large buy aggression at a level, but price holds = hidden seller
    """
    for bar, group in footprint.groupby('bar'):
        for price_level, row in group.iterrows():
            avg_vol = group['total_vol'].mean()

            if row['bid_vol'] > avg_vol * volume_threshold:
                # Heavy selling at this level
                next_bar_low = get_next_bar_low(bar)
                if next_bar_low >= price_level:
                    # Price held despite selling = buy absorption
                    yield {
                        'time': bar, 'price': price_level,
                        'type': 'buy_absorption',
                        'volume': row['bid_vol'],
                        'signal': 'bullish'
                    }
```

## Examples

### Intraday Trading with Volume Profile

```python
# Yesterday's profile
yesterday = build_volume_profile(yesterday_trades)
# POC at 4150, VAH at 4165, VAL at 4135

# Today's opening:
# If price opens above VAH (4165) = bullish breakout (look for long entries)
# If price opens below VAL (4135) = bearish breakout (look for short entries)
# If price opens inside VA = expect rotation between VAH and VAL

# POC as magnet: if price moves away from POC on low volume,
# expect a return to POC
```

### Real-Time Delta for Execution

```python
# Use delta to time entries within an algo execution window:
# If you need to buy and delta is negative (sellers aggressive),
# place patient limit orders — supply is available
# If delta turns strongly positive, consider crossing spread
# before buyers push price higher
```

## Quality Gate

- [ ] Trade classification method documented (tick rule, quote rule, or Lee-Ready)
- [ ] Volume profile uses appropriate time period (session, multi-day, or developing profile)
- [ ] Value area calculated correctly (70% of volume, expanding from POC)
- [ ] Delta calculation handles trades at midpoint correctly
- [ ] Footprint imbalance thresholds calibrated to the specific instrument
- [ ] Divergence signals confirmed with price action (divergence alone is not a trade signal)
- [ ] Absorption detection accounts for hidden orders and iceberg refills
- [ ] Latency of data feed adequate for the trading timeframe
- [ ] Data excludes off-exchange prints, block trades, and other non-informative volume
- [ ] Backtested edge of order flow signals accounts for realistic execution delays
