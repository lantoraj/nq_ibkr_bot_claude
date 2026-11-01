---
name: market-microstructure-theory
description: "Market microstructure theory — limit order books, price discovery, bid-ask spread economics. Use when: User needs to understand how prices form in electronic markets; Analyzing bid-ask spread components (adverse selection, inventory, order processing); Modeling limit order book dynamics and depth."
---

# Market Microstructure Theory

> Market microstructure theory — limit order books, price discovery, bid-ask spread economics.

## When to Activate

- User needs to understand how prices form in electronic markets
- Analyzing bid-ask spread components (adverse selection, inventory, order processing)
- Modeling limit order book dynamics and depth
- Understanding informed vs uninformed trading (Kyle, Glosten-Milgrom models)
- Evaluating market quality metrics (spread, depth, resilience, price efficiency)

## Core Concepts

### What Is Microstructure?

Market microstructure studies how the mechanics of trading — order types, market rules, information asymmetry, and participant behavior — affect price formation, liquidity, and transaction costs. It bridges the gap between financial theory (efficient prices) and trading reality (discrete orders, imperfect information, strategic behavior).

### The Limit Order Book (LOB)

The central data structure of modern electronic markets:

```
Ask Side (sell orders)           Price    Bid Side (buy orders)
                                150.10   [500, 200, 1000]     ← best bid
                                150.09   [300, 800]
                                150.08   [2000]
[1500, 300]     ← best ask      150.11
[800, 600, 200]                  150.12
[2500]                           150.13
```

Key LOB metrics:
- **Spread**: best ask - best bid (150.11 - 150.10 = $0.01)
- **Depth at best**: total quantity at best bid/ask
- **Book depth**: total quantity within N ticks of midpoint
- **Book imbalance**: (bid_depth - ask_depth) / (bid_depth + ask_depth)
- **Order arrival rate**: frequency of new limit orders
- **Cancellation rate**: frequency of order cancellations (60-90% of all orders in modern markets)

### Bid-Ask Spread Components

The spread compensates market makers for three costs (Stoll, 1978; Huang and Stoll, 1997):

1. **Adverse Selection** (30-60% of spread): risk of trading with informed counterparties who know the true value. The market maker loses on these trades.

2. **Inventory Risk** (10-30%): cost of holding an unbalanced position. Market makers must adjust quotes to manage inventory.

3. **Order Processing** (10-30%): fixed costs of operating (technology, compliance, exchange fees). This component has shrunk dramatically with electronic trading.

### Price Discovery Models

**Kyle (1985)**: a single informed trader, noise traders, and a competitive market maker.
- Informed trader splits orders to hide information
- Market maker sets price as a linear function of net order flow: P = μ + λ * order_flow
- λ (Kyle's lambda) measures price impact per unit of order flow = market's estimate of information content
- Higher λ = less liquid, more information asymmetry

**Glosten-Milgrom (1985)**: sequential trade model with Bayesian updating.
- Each trade is either informed or uninformed (with known probability)
- Market maker updates beliefs about true value after each trade
- Bid and ask are conditional expectations of true value given a sell/buy
- Spread exists even with competition because of adverse selection

**Glosten (1994)**: limit order book as a discriminatory pricing mechanism.
- Depth at each price level reflects break-even condition for that marginal unit
- Deeper into the book = higher adverse selection per unit (larger trades are more likely informed)

## Methodology

### Step 1: LOB State Representation

```python
import numpy as np
import pandas as pd
from collections import defaultdict

class LimitOrderBook:
    def __init__(self, tick_size=0.01):
        self.tick_size = tick_size
        self.bids = defaultdict(list)  # price -> [order_ids]
        self.asks = defaultdict(list)
        self.orders = {}  # order_id -> {price, size, side, timestamp}

    def add_order(self, order_id, side, price, size, timestamp):
        price = round(price / self.tick_size) * self.tick_size
        self.orders[order_id] = {
            'price': price, 'size': size, 'side': side, 'ts': timestamp
        }
        if side == 'bid':
            self.bids[price].append(order_id)
        else:
            self.asks[price].append(order_id)

    def best_bid(self):
        return max(self.bids.keys()) if self.bids else None

    def best_ask(self):
        return min(self.asks.keys()) if self.asks else None

    def spread(self):
        bb, ba = self.best_bid(), self.best_ask()
        return (ba - bb) if (bb and ba) else None

    def midpoint(self):
        bb, ba = self.best_bid(), self.best_ask()
        return (bb + ba) / 2 if (bb and ba) else None

    def book_imbalance(self, levels=5):
        """
        Bid-ask imbalance at top N levels.
        Positive = more bid depth = buying pressure.
        Strong predictor of short-term price direction.
        """
        bid_prices = sorted(self.bids.keys(), reverse=True)[:levels]
        ask_prices = sorted(self.asks.keys())[:levels]

        bid_depth = sum(
            sum(self.orders[oid]['size'] for oid in self.bids[p])
            for p in bid_prices
        )
        ask_depth = sum(
            sum(self.orders[oid]['size'] for oid in self.asks[p])
            for p in ask_prices
        )

        return (bid_depth - ask_depth) / (bid_depth + ask_depth) if (bid_depth + ask_depth) > 0 else 0

    def depth_at_price(self, price):
        side = self.bids if price <= self.midpoint() else self.asks
        return sum(self.orders[oid]['size'] for oid in side.get(price, []))
```

### Step 2: Spread Decomposition

```python
def huang_stoll_decomposition(trades, quotes):
    """
    Huang-Stoll (1997) spread decomposition into adverse selection,
    inventory, and order processing components.

    Uses the covariance of trade direction and quote changes.
    """
    # Trade direction: +1 for buyer-initiated, -1 for seller-initiated
    merged = pd.merge_asof(trades, quotes, on='timestamp')
    merged['direction'] = np.sign(merged['trade_price'] - merged['midpoint'])

    # Quote revision after trade
    merged['midpoint_change'] = merged['midpoint'].shift(-1) - merged['midpoint']

    # Adverse selection component: correlation between trade direction and price change
    half_spread = merged['spread'] / 2
    alpha = merged['direction'].cov(merged['midpoint_change']) / half_spread.mean()

    # alpha = adverse selection fraction of the spread
    # Typical values: 30-60% for equities
    return {
        'adverse_selection_pct': alpha,
        'inventory_order_processing_pct': 1 - alpha,
        'avg_spread_bps': (merged['spread'] / merged['midpoint']).mean() * 10000,
    }

def kyle_lambda(trades, prices, interval='5min'):
    """
    Estimate Kyle's lambda (price impact coefficient).
    Regress price changes on signed order flow.

    ΔP = λ * OFI + ε
    """
    # Aggregate signed volume per interval
    trades['interval'] = trades['timestamp'].dt.floor(interval)
    ofi = trades.groupby('interval').apply(
        lambda g: (g['direction'] * g['size']).sum()
    )

    price_changes = prices.resample(interval).last().diff()

    # Regression: price change on order flow imbalance
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    X = ofi.values.reshape(-1, 1)
    y = price_changes.reindex(ofi.index).values

    model.fit(X, y)
    lambda_est = model.coef_[0]

    # Higher lambda = less liquid = more adverse selection
    return lambda_est, model.score(X, y)
```

### Step 3: Price Impact Analysis

```python
def permanent_vs_temporary_impact(trades, midpoints, windows=[1, 5, 10, 30]):
    """
    Decompose price impact into permanent and temporary components.

    Permanent: price change that persists after the trade
    Temporary: price displacement that reverts
    """
    results = []

    for _, trade in trades.iterrows():
        t = trade['timestamp']
        direction = trade['direction']
        pre_mid = midpoints.asof(t - pd.Timedelta(seconds=1))
        at_trade_mid = midpoints.asof(t)

        impacts = {'immediate': direction * (at_trade_mid - pre_mid) / pre_mid * 10000}

        for w in windows:
            future_t = t + pd.Timedelta(minutes=w)
            future_mid = midpoints.asof(future_t)
            impacts[f'{w}min'] = direction * (future_mid - pre_mid) / pre_mid * 10000

        results.append(impacts)

    impact_df = pd.DataFrame(results)

    # Permanent impact: the long-horizon impact (e.g., 30-min)
    # Temporary impact: immediate - permanent
    return {
        'permanent_bps': impact_df['30min'].mean(),
        'temporary_bps': impact_df['immediate'].mean() - impact_df['30min'].mean(),
        'reversion_profile': impact_df.mean(),
    }
```

### Step 4: Market Quality Metrics

```python
def market_quality_dashboard(trades, quotes, interval='5min'):
    """
    Comprehensive market quality metrics.
    """
    metrics = {}

    # Spread metrics
    metrics['avg_spread_bps'] = (quotes['spread'] / quotes['midpoint']).mean() * 10000
    metrics['effective_spread_bps'] = (
        2 * abs(trades['price'] - quotes['midpoint'].reindex(trades.index, method='ffill'))
        / quotes['midpoint'].reindex(trades.index, method='ffill')
    ).mean() * 10000

    # Depth metrics
    metrics['avg_bid_depth'] = quotes['bid_size'].mean()
    metrics['avg_ask_depth'] = quotes['ask_size'].mean()
    metrics['depth_imbalance'] = (
        (quotes['bid_size'] - quotes['ask_size']) /
        (quotes['bid_size'] + quotes['ask_size'])
    ).mean()

    # Resilience: how quickly does the book recover after a trade?
    # Measure time for spread to return to pre-trade level

    # Price efficiency: variance ratio
    returns_1 = quotes['midpoint'].pct_change(1)
    returns_5 = quotes['midpoint'].pct_change(5)
    metrics['variance_ratio_5'] = returns_5.var() / (5 * returns_1.var())
    # VR = 1 means efficient; VR < 1 means negative autocorrelation (overreaction/bounce)
    # VR > 1 means positive autocorrelation (trending)

    return metrics
```

## Examples

### Interpreting Book Imbalance

```python
# Strong positive imbalance (0.6+): much more bid depth than ask depth
# → Price likely to move up in the short term
# → But beware: sophisticated traders "spoof" one side

# Book imbalance as a feature in ML models:
# Cartea, Jaimungal, Penalva (2015) show book imbalance predicts
# next-trade direction with 55-60% accuracy in liquid markets
```

### Kyle's Lambda Across Stocks

```python
# Typical Kyle's lambda values (price impact per $1M of order flow):
# Large-cap (AAPL, MSFT): 0.01-0.05 bps per $1M
# Mid-cap: 0.1-0.5 bps per $1M
# Small-cap: 1-5 bps per $1M
# Micro-cap: 10-50 bps per $1M

# Lambda increases around events (earnings, M&A) as information asymmetry rises
```

## Quality Gate

- [ ] LOB data source quality verified (exchange direct feed vs consolidated, latency)
- [ ] Trade classification method appropriate (Lee-Ready for intraday, tick rule fallback)
- [ ] Spread decomposition uses sufficient data for stable estimates (>1000 trades)
- [ ] Kyle's lambda estimated with appropriate frequency aggregation (too fine = noisy)
- [ ] Permanent vs temporary impact windows calibrated to market speed
- [ ] Book imbalance features tested for spoofing robustness
- [ ] Variance ratio calculated at multiple horizons to characterize price efficiency
- [ ] Market quality metrics compared across venues for the same instrument
- [ ] Off-hours and auction data handled separately from continuous trading
- [ ] Results validated against academic benchmarks for the same asset class
