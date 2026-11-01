---
name: execution-algos
description: "Execution algorithms — TWAP, VWAP, IS, POV, Iceberg for optimal trade execution. Use when: User needs to execute large orders with minimal market impact; Choosing between execution algorithm types (benchmark, scheduled, opportunistic); Implementing TWAP, VWAP, or implementation shortfall algorithms."
---

# Execution Algorithms

> Execution algorithms — TWAP, VWAP, IS, POV, Iceberg for optimal trade execution.

## When to Activate

- User needs to execute large orders with minimal market impact
- Choosing between execution algorithm types (benchmark, scheduled, opportunistic)
- Implementing TWAP, VWAP, or implementation shortfall algorithms
- Designing iceberg or hidden order strategies
- Building an algo selection framework based on order characteristics

## Core Concepts

### Why Execution Algorithms?

Large orders face a fundamental tradeoff:
- **Trade fast**: high market impact (move the price against you)
- **Trade slow**: high timing risk (market moves away while you wait)

Execution algorithms automate the process of slicing a parent order into child orders, balancing impact against timing risk.

### Algorithm Taxonomy

| Category | Algorithm | Benchmark | Best For |
|----------|-----------|-----------|----------|
| **Scheduled** | TWAP | Even time distribution | Low urgency, steady execution |
| **Scheduled** | VWAP | Volume-weighted average price | Matching market volume profile |
| **Arrival** | IS (Implementation Shortfall) | Arrival price | Minimizing total execution cost |
| **Opportunistic** | POV (% of Volume) | Market participation rate | Adapting to real-time liquidity |
| **Liquidity** | Iceberg | Hidden quantity | Large orders in thin markets |
| **Dark** | Dark Sweep | Best dark pool prices | Minimizing information leakage |
| **Adaptive** | Adaptive IS | Arrival + real-time signals | Sophisticated cost minimization |

### The Almgren-Chriss Framework

The theoretical foundation for optimal execution. Trade a position X over time T:

```
Total Cost = Market Impact Cost + Timing Risk Cost

Market Impact = permanent impact (price moves permanently) + temporary impact (bid-ask, resilience)
Timing Risk = variance of execution cost from price movement during trading
```

Optimal trajectory minimizes: E[Cost] + λ * Var[Cost]

Where λ is the urgency parameter (risk aversion toward timing risk).

## Methodology

### Step 1: TWAP Implementation

```python
import numpy as np
from datetime import datetime, timedelta

def twap_schedule(total_shares, start_time, end_time, slice_interval_sec=60):
    """
    Time-Weighted Average Price: equal-sized slices over time.

    Simple but effective for:
    - Low-urgency orders
    - Illiquid stocks where volume profile is unreliable
    - Benchmarking other algos
    """
    duration = (end_time - start_time).total_seconds()
    n_slices = int(duration / slice_interval_sec)
    shares_per_slice = total_shares / n_slices

    schedule = []
    for i in range(n_slices):
        slice_time = start_time + timedelta(seconds=i * slice_interval_sec)
        schedule.append({
            'time': slice_time,
            'shares': shares_per_slice,
            'cumulative_pct': (i + 1) / n_slices
        })

    return schedule

def twap_with_randomization(total_shares, n_slices, randomize_pct=0.20):
    """
    Add randomization to avoid detection by predatory algorithms.
    Vary slice sizes by +/- randomize_pct.
    """
    base = total_shares / n_slices
    noise = np.random.uniform(1 - randomize_pct, 1 + randomize_pct, n_slices)
    slices = base * noise
    slices = slices * (total_shares / slices.sum())  # renormalize
    return slices
```

### Step 2: VWAP Implementation

```python
def vwap_schedule(total_shares, volume_profile, start_time, end_time):
    """
    Volume-Weighted Average Price: distribute shares proportional to
    historical intraday volume pattern.

    volume_profile: array of expected volume fractions per time bucket
    (e.g., 30-min buckets, should sum to 1.0 for trading day)
    """
    # Typical US equity volume profile (U-shaped):
    # Open: 8-10% first 30 min
    # Midday: 3-5% per 30-min bucket
    # Close: 10-15% last 30 min

    # Select buckets within our trading window
    active_buckets = select_buckets(volume_profile, start_time, end_time)

    # Normalize volume fractions for active window
    total_vol_pct = sum(active_buckets.values())
    schedule = {}
    for bucket_time, vol_pct in active_buckets.items():
        schedule[bucket_time] = total_shares * (vol_pct / total_vol_pct)

    return schedule

def adaptive_vwap(total_shares, volume_profile, real_time_volume):
    """
    Adjust VWAP schedule based on real-time volume observations.
    If actual volume is running ahead of historical, speed up.
    If volume is light, slow down.
    """
    expected_cum_vol = volume_profile.cumsum()
    actual_cum_vol = real_time_volume.cumsum()

    # Volume surprise ratio
    vol_ratio = actual_cum_vol / expected_cum_vol

    # Adjust remaining shares: if volume is 1.2x expected, increase pace
    remaining_shares = total_shares - shares_executed
    adjusted_rate = base_rate * vol_ratio.iloc[-1]

    return adjusted_rate
```

### Step 3: Implementation Shortfall (IS) Algorithm

```python
def implementation_shortfall_schedule(total_shares, arrival_price, sigma,
                                       eta, gamma, lambda_risk, T=1.0):
    """
    Almgren-Chriss optimal execution schedule.

    Parameters:
    - sigma: daily volatility
    - eta: temporary impact coefficient (cost = eta * trading_rate)
    - gamma: permanent impact coefficient (cost = gamma * total_traded)
    - lambda_risk: risk aversion (urgency)
    - T: trading horizon in days

    Higher lambda_risk = more aggressive (front-loaded) execution.
    """
    kappa = np.sqrt(lambda_risk * sigma**2 / eta)

    def optimal_trajectory(t, n_steps=100):
        """Shares remaining at time t."""
        return total_shares * np.sinh(kappa * (T - t)) / np.sinh(kappa * T)

    # Generate schedule
    times = np.linspace(0, T, 100)
    remaining = [optimal_trajectory(t) for t in times]
    trade_rate = -np.diff(remaining) / np.diff(times)

    # High urgency (large lambda): trades concentrated at start
    # Low urgency (small lambda): evenly spread (approaches TWAP)

    return times, remaining, trade_rate

def estimate_impact_params(adv, spread, sigma):
    """
    Estimate Almgren-Chriss parameters from market data.
    ADV = average daily volume, spread = bid-ask spread, sigma = daily vol.
    """
    # Temporary impact: proportional to spread and inverse of ADV
    eta = spread / (2 * adv)  # simplified

    # Permanent impact: fraction of daily vol
    gamma = sigma / (10 * adv)  # rough approximation

    return eta, gamma
```

### Step 4: Participation Rate (POV) Algorithm

```python
def pov_algorithm(total_shares, target_participation=0.10,
                  max_participation=0.25, min_participation=0.02):
    """
    Percentage of Volume: trade as a fixed fraction of market volume.

    Advantages:
    - Naturally adapts to liquidity
    - Simple to understand and monitor
    - Completion time unknown but bounded

    Typical participation rates:
    - 5-10%: low impact, suitable for most orders
    - 10-20%: moderate urgency
    - 20-30%: high urgency (significant impact risk)
    """
    def on_volume_update(market_volume_since_last):
        """Called each time new volume is observed."""
        target_shares = market_volume_since_last * target_participation
        target_shares = min(target_shares, remaining_shares)

        # Clip to participation bounds
        actual_participation = target_shares / market_volume_since_last
        if actual_participation > max_participation:
            target_shares = market_volume_since_last * max_participation
        elif actual_participation < min_participation:
            target_shares = market_volume_since_last * min_participation

        return target_shares

    return on_volume_update
```

### Step 5: Iceberg Orders

```python
def iceberg_order(total_shares, display_size, price_limit,
                  refill_delay_ms=500, randomize=True):
    """
    Iceberg: show only display_size on the book, refill when executed.

    Key parameters:
    - display_size: visible quantity (typically 5-20% of total)
    - refill_delay: pause before refreshing (avoid detection)
    - randomize: vary display size +/- 20% each refill
    """
    remaining = total_shares
    fills = []

    while remaining > 0:
        if randomize:
            this_display = display_size * np.random.uniform(0.8, 1.2)
        else:
            this_display = display_size

        this_display = min(this_display, remaining)

        # Place limit order with visible quantity
        order = {
            'type': 'LIMIT',
            'price': price_limit,
            'total_qty': this_display,
            'display_qty': this_display,
        }

        # Wait for fill, then refill after delay
        remaining -= this_display

    return fills
```

### Step 6: Algo Selection Framework

```python
def select_algo(order_size, adv, urgency, alpha_signal=None,
                spread_bps=None, volatility=None):
    """
    Choose execution algorithm based on order characteristics.
    """
    participation_rate = order_size / adv

    if participation_rate < 0.01:
        # Small order: just cross the spread
        return 'MARKET' if urgency == 'high' else 'LIMIT'

    elif participation_rate < 0.05:
        if urgency == 'high':
            return 'IS_AGGRESSIVE'
        elif alpha_signal and alpha_signal > 0:
            return 'IS_STANDARD'  # front-load to capture alpha
        else:
            return 'VWAP'

    elif participation_rate < 0.25:
        if urgency == 'high':
            return 'IS_AGGRESSIVE'
        else:
            return 'POV_10PCT'

    else:
        # Very large order: multi-day execution
        return 'POV_5PCT_MULTIDAY'
```

## Examples

### Comparing Algo Performance

```python
# Order: Buy 500,000 shares, ADV = 2M, stock price = $50
order_pct_adv = 0.25  # 25% of ADV — significant order

# Expected costs (bps of notional):
algo_costs = {
    'TWAP_full_day': {'impact': 15, 'timing_risk': 25, 'total': 40},
    'VWAP_full_day': {'impact': 12, 'timing_risk': 25, 'total': 37},
    'IS_moderate': {'impact': 20, 'timing_risk': 15, 'total': 35},
    'IS_aggressive': {'impact': 30, 'timing_risk': 8, 'total': 38},
    'POV_10pct': {'impact': 10, 'timing_risk': 30, 'total': 40},
}
# IS typically wins for moderate-size orders with some urgency
```

### Real-Time Algo Monitoring

Key metrics to track during execution:
- **Participation rate**: are we trading at the intended pace?
- **Slippage vs arrival**: how much have we paid vs the decision price?
- **Volume surprise**: is actual volume matching the forecast?
- **Spread dynamics**: is the spread widening (information leakage)?

## Quality Gate

- [ ] Algorithm choice matches order characteristics (size relative to ADV, urgency, alpha decay)
- [ ] Volume profile for VWAP uses recent data (not stale historical patterns)
- [ ] IS algorithm urgency parameter calibrated to alpha half-life or portfolio manager preference
- [ ] Randomization applied to avoid detection by predatory algos
- [ ] Participation rate capped to avoid excessive market impact (typically < 25% ADV)
- [ ] Multi-day execution considered for orders > 20% ADV
- [ ] Real-time monitoring in place: slippage tracking, volume comparison, spread alerts
- [ ] Post-trade TCA performed to evaluate algo performance vs benchmark
- [ ] Dark pool routing considered for reducing information leakage
- [ ] Algo parameters documented and reviewed periodically (not set-and-forget)
