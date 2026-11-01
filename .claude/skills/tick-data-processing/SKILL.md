---
name: tick-data-processing
description: "Tick data processing — cleaning, aggregation, bar construction from raw market data. Use when: User is working with raw tick-level trade and quote data; Cleaning tick data (outliers, splits, corporate actions, bad prints); Constructing bars from ticks (time, volume, dollar, tick, entropy bars)."
---

# Tick Data Processing

> Tick data processing — cleaning, aggregation, bar construction from raw market data.

## When to Activate

- User is working with raw tick-level trade and quote data
- Cleaning tick data (outliers, splits, corporate actions, bad prints)
- Constructing bars from ticks (time, volume, dollar, tick, entropy bars)
- Handling bid-ask bounce and trade classification
- Designing data storage and retrieval for large tick datasets

## Core Concepts

### What Is Tick Data?

Tick data is the finest granularity of market data — every individual trade and quote update:

**Trade ticks**: timestamp, price, size, exchange, conditions (regular, odd lot, block, etc.)
**Quote ticks**: timestamp, bid price, bid size, ask price, ask size, exchange

A liquid US equity generates 10,000-100,000 trade ticks and 500,000-5,000,000 quote updates per day. Storage and processing at scale is a significant engineering challenge.

### Data Quality Issues

Raw tick data is messy. Common problems:

1. **Erroneous prints**: trades reported at clearly wrong prices (fat fingers, test trades)
2. **Stale quotes**: quotes that persist after the market has moved (delayed cancellations)
3. **Stock splits**: price drops by the split factor but shares outstanding change
4. **Dividends**: ex-date price drop equal to dividend amount
5. **Corporate actions**: mergers, spinoffs, ticker changes
6. **Odd lots**: trades below 100 shares (different handling by data vendors)
7. **Consolidated vs direct**: SIP consolidation introduces variable delays
8. **Time zone issues**: exchange timestamps vs UTC vs local time
9. **Late prints**: trades reported after the fact (sometimes hours later)
10. **Crossed/locked markets**: bid >= ask (usually transient, data artifact)

### Bar Types

Beyond traditional time bars, alternative bar types proposed by Lopez de Prado (2018):

| Bar Type | Trigger | Property | Use Case |
|----------|---------|----------|----------|
| **Time** | Fixed time interval | Equal time spacing | Standard analysis |
| **Tick** | Fixed # of trades | Equal information events | Removes time seasonality |
| **Volume** | Fixed volume traded | Equal activity | Normalizes for liquidity |
| **Dollar** | Fixed dollar value | Equal capital flow | Handles price changes |
| **Imbalance (tick)** | Signed tick imbalance | Detects order flow shifts | ML features |
| **Imbalance (volume)** | Signed volume imbalance | Detects large traders | ML features |

## Methodology

### Step 1: Data Cleaning

```python
import pandas as pd
import numpy as np

def clean_trade_ticks(trades):
    """
    Clean raw trade tick data. Apply filters in order.
    """
    original_count = len(trades)

    # 1. Remove trades outside regular trading hours (if desired)
    trades = trades.between_time('09:30', '16:00')

    # 2. Remove trades with condition codes indicating non-regular
    # Condition codes vary by exchange; common exclusions:
    irregular_conditions = {'W', 'Z', 'T', 'U', 'L', 'G', 'P'}
    # W = average price, Z = sold out of sequence, T = form-T (after hours)
    if 'condition' in trades.columns:
        trades = trades[~trades['condition'].isin(irregular_conditions)]

    # 3. Remove zero-price and zero-volume trades
    trades = trades[(trades['price'] > 0) & (trades['size'] > 0)]

    # 4. Remove outlier prices (median filter)
    trades = remove_price_outliers(trades, window=50, threshold=5.0)

    # 5. Remove duplicate timestamps (keep first)
    trades = trades[~trades.index.duplicated(keep='first')]

    cleaned_count = len(trades)
    print(f"Removed {original_count - cleaned_count} ticks "
          f"({(original_count - cleaned_count)/original_count:.1%})")

    return trades

def remove_price_outliers(trades, window=50, threshold=5.0):
    """
    Remove ticks where price deviates more than `threshold` rolling MADs
    from the rolling median.
    """
    rolling_median = trades['price'].rolling(window, center=True).median()
    rolling_mad = trades['price'].rolling(window, center=True).apply(
        lambda x: np.median(np.abs(x - np.median(x)))
    )

    # MAD-based z-score
    deviation = np.abs(trades['price'] - rolling_median) / rolling_mad.clip(lower=1e-8)
    mask = deviation < threshold

    return trades[mask]
```

### Step 2: Corporate Action Adjustments

```python
def adjust_for_splits(trades, splits_df):
    """
    Adjust historical prices for stock splits.
    splits_df: DataFrame with columns ['date', 'ratio']
    Example: 2-for-1 split has ratio = 2.0
    """
    trades = trades.copy()
    adjustment_factor = 1.0

    # Apply splits in reverse chronological order
    for _, split in splits_df.sort_values('date', ascending=False).iterrows():
        mask = trades.index.date < split['date'].date()
        trades.loc[mask, 'price'] /= split['ratio']
        trades.loc[mask, 'size'] *= split['ratio']

    return trades

def adjust_for_dividends(trades, dividends_df, method='proportional'):
    """
    Adjust for cash dividends.
    method: 'proportional' (most common) or 'subtractive'
    """
    trades = trades.copy()

    for _, div in dividends_df.sort_values('ex_date', ascending=False).iterrows():
        mask = trades.index.date < div['ex_date'].date()
        if method == 'proportional':
            # Adjust by (1 - div/close_before_ex)
            factor = 1 - div['amount'] / div['close_before_ex']
            trades.loc[mask, 'price'] *= factor
        elif method == 'subtractive':
            trades.loc[mask, 'price'] -= div['amount']

    return trades
```

### Step 3: Bar Construction

```python
def time_bars(trades, interval='5min'):
    """Standard OHLCV time bars."""
    ohlcv = trades.resample(interval).agg({
        'price': ['first', 'max', 'min', 'last'],
        'size': 'sum',
    })
    ohlcv.columns = ['open', 'high', 'low', 'close', 'volume']
    ohlcv = ohlcv.dropna()
    return ohlcv

def volume_bars(trades, bar_volume=10000):
    """
    Each bar contains exactly `bar_volume` shares traded.
    More bars during active periods, fewer during quiet periods.
    """
    trades = trades.copy()
    trades['cum_volume'] = trades['size'].cumsum()
    trades['bar_id'] = (trades['cum_volume'] / bar_volume).astype(int)

    bars = trades.groupby('bar_id').agg({
        'price': ['first', 'max', 'min', 'last'],
        'size': 'sum',
    })
    bars.columns = ['open', 'high', 'low', 'close', 'volume']
    bars.index = trades.groupby('bar_id')['price'].apply(lambda x: x.index[0])

    return bars

def dollar_bars(trades, bar_dollars=1_000_000):
    """
    Each bar contains `bar_dollars` worth of trading activity.
    Robust to price level changes (a $500 stock needs fewer shares than a $50 stock).
    """
    trades = trades.copy()
    trades['dollar_volume'] = trades['price'] * trades['size']
    trades['cum_dollars'] = trades['dollar_volume'].cumsum()
    trades['bar_id'] = (trades['cum_dollars'] / bar_dollars).astype(int)

    bars = trades.groupby('bar_id').agg({
        'price': ['first', 'max', 'min', 'last'],
        'size': 'sum',
        'dollar_volume': 'sum',
    })
    bars.columns = ['open', 'high', 'low', 'close', 'volume', 'dollar_volume']
    bars.index = trades.groupby('bar_id')['price'].apply(lambda x: x.index[0])

    return bars

def tick_imbalance_bars(trades, expected_imbalance=None):
    """
    Lopez de Prado (2018) tick imbalance bars.
    New bar forms when cumulative signed tick imbalance exceeds a threshold.
    Detects shifts in buying/selling pressure.
    """
    trades = trades.copy()
    trades['tick_direction'] = np.sign(trades['price'].diff()).replace(0, np.nan).ffill().fillna(1)

    if expected_imbalance is None:
        # Use exponentially weighted estimate of expected imbalance
        expected_imbalance = abs(trades['tick_direction'].ewm(span=1000).mean()) * 1000

    cum_imbalance = 0
    bar_indices = [0]

    for i in range(1, len(trades)):
        cum_imbalance += trades['tick_direction'].iloc[i]

        # Dynamic threshold based on expected bar size
        threshold = expected_imbalance if isinstance(expected_imbalance, float) \
                    else expected_imbalance.iloc[i]

        if abs(cum_imbalance) >= threshold:
            bar_indices.append(i)
            cum_imbalance = 0

    # Build bars from bar_indices
    bars = []
    for j in range(len(bar_indices) - 1):
        start, end = bar_indices[j], bar_indices[j + 1]
        segment = trades.iloc[start:end + 1]
        bars.append({
            'timestamp': segment.index[0],
            'open': segment['price'].iloc[0],
            'high': segment['price'].max(),
            'low': segment['price'].min(),
            'close': segment['price'].iloc[-1],
            'volume': segment['size'].sum(),
            'n_ticks': len(segment),
        })

    return pd.DataFrame(bars).set_index('timestamp')
```

### Step 4: Trade Classification (Lee-Ready)

```python
def lee_ready_classification(trades, quotes, delay_sec=5):
    """
    Lee-Ready (1991) algorithm for classifying trades as buyer/seller initiated.

    1. Compare trade price to quote midpoint (with 5-second delay for quote staleness)
    2. If above midpoint → buyer-initiated
    3. If below midpoint → seller-initiated
    4. If at midpoint → use tick test (compare to previous different price)
    """
    # Merge trades with quotes (lagged by delay_sec)
    quotes_delayed = quotes.copy()
    quotes_delayed.index = quotes_delayed.index + pd.Timedelta(seconds=delay_sec)

    merged = pd.merge_asof(
        trades.reset_index(), quotes_delayed.reset_index(),
        on='timestamp', direction='backward'
    ).set_index('timestamp')

    merged['midpoint'] = (merged['bid'] + merged['ask']) / 2

    # Quote rule
    merged['direction'] = np.where(
        merged['price'] > merged['midpoint'], 1,
        np.where(merged['price'] < merged['midpoint'], -1, 0)
    )

    # Tick rule for trades at midpoint
    at_mid = merged['direction'] == 0
    tick_dir = np.sign(merged['price'].diff()).replace(0, np.nan).ffill().fillna(1)
    merged.loc[at_mid, 'direction'] = tick_dir[at_mid]

    merged['buy_volume'] = merged['size'] * (merged['direction'] == 1)
    merged['sell_volume'] = merged['size'] * (merged['direction'] == -1)

    return merged
```

### Step 5: Data Storage

```python
def storage_architecture():
    """
    Tick data storage considerations for a trading operation.
    """
    storage_options = {
        'parquet': {
            'description': 'Columnar, compressed, fast reads',
            'compression': '5-10x over CSV',
            'query': 'Excellent with pandas, Spark, DuckDB',
            'best_for': 'Historical analysis, backtesting',
            'partition_by': 'date/symbol for efficient queries',
        },
        'arctic': {
            'description': 'Built for financial time series (on MongoDB)',
            'features': 'Versioning, chunked storage, tick store',
            'query': 'Python-native, good for tick data',
            'best_for': 'Research teams, rapid iteration',
        },
        'kdb+/q': {
            'description': 'Column-oriented database for time series',
            'performance': 'Fastest for time series queries',
            'query': 'q language (steep learning curve)',
            'best_for': 'Production tick databases, banks',
            'cost': '$50-100K+ per core license',
        },
        'timescaledb': {
            'description': 'PostgreSQL extension for time series',
            'features': 'SQL interface, automatic partitioning',
            'best_for': 'Teams with SQL skills, moderate scale',
        },
        'duckdb': {
            'description': 'Embedded analytical database',
            'performance': 'Excellent for Parquet files',
            'best_for': 'Single-machine analysis, replacing pandas',
        },
    }

    # Data volume estimates (single US equity):
    # Trade ticks: ~50K/day × 252 days × 10 bytes = ~125 MB/year
    # Quote ticks: ~2M/day × 252 days × 20 bytes = ~10 GB/year
    # Full US equity universe (~8000 stocks): ~80 TB/year for quotes

    return storage_options
```

## Examples

### Processing a Day of AAPL Tick Data

```python
# Load and clean
trades = pd.read_parquet('aapl_trades_20240115.parquet')
trades = clean_trade_ticks(trades)

# Build different bar types
time_5m = time_bars(trades, '5min')       # ~78 bars (6.5 hours)
vol_bars = volume_bars(trades, 50000)      # variable count
dollar_b = dollar_bars(trades, 5_000_000)  # variable count

# Compare bar properties:
# Time bars: uneven information content (busy open vs quiet midday)
# Volume bars: more uniform information, better statistical properties
# Dollar bars: normalize for price level changes, best for multi-year analysis
```

### Bid-Ask Bounce Effect

```python
# Bid-ask bounce: trades alternate between bid and ask, creating
# artificial negative autocorrelation in trade prices at high frequency
# This inflates realized volatility from tick data

# Solution: use midpoint returns, not trade price returns
quotes['midpoint'] = (quotes['bid'] + quotes['ask']) / 2
mid_returns = quotes['midpoint'].resample('1min').last().pct_change()
# Cleaner than trade price returns for volatility estimation
```

## Quality Gate

- [ ] Trade condition codes filtered appropriately (exclude irregular prints)
- [ ] Price outliers detected and removed using robust methods (MAD, not standard deviation)
- [ ] Corporate actions (splits, dividends, mergers) adjusted correctly with point-in-time data
- [ ] Time zones handled consistently (UTC preferred for storage, local for display)
- [ ] Bar type chosen with rationale (volume/dollar bars for ML features, time bars for reporting)
- [ ] Lee-Ready or equivalent trade classification applied for buy/sell volume
- [ ] Bid-ask bounce effect accounted for in volatility and return calculations
- [ ] Data storage format supports efficient queries by date and symbol
- [ ] Late prints and out-of-sequence trades handled (exclude or mark)
- [ ] Survivorship-free universe maintained — include delisted tickers through their active period
