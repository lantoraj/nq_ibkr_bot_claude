---
name: smart-order-routing
description: "Smart order routing — dark pools, lit markets, internalization, and best execution. Use when: User needs to route orders across multiple venues for best execution; Evaluating dark pool strategies and hidden liquidity; Understanding Reg NMS, MiFID II best execution requirements."
---

# Smart Order Routing

> Smart order routing — dark pools, lit markets, internalization, and best execution.

## When to Activate

- User needs to route orders across multiple venues for best execution
- Evaluating dark pool strategies and hidden liquidity
- Understanding Reg NMS, MiFID II best execution requirements
- Building or evaluating a smart order routing engine
- Analyzing venue selection and latency considerations

## Core Concepts

### Fragmented Markets

Modern equity markets are fragmented across many venues:

**US Equity Venues** (~16 exchanges + 30+ dark pools + internalizers):
- NYSE, Nasdaq, BATS/CBOE (BZX, BYX, EDGX, EDGA), IEX
- Dark pools: Sigma X (Goldman), CrossFinder (Credit Suisse), Liquidnet, POSIT
- Internalizers: Citadel Securities, Virtu Financial (handle ~40% of retail flow)

**European Venues** (MiFID II framework):
- Primary exchanges (LSE, Euronext, Deutsche Borse, SIX)
- MTFs: CBOE Europe, Turquoise, Aquis
- Systematic Internalizers (SIs)
- Dark pools: Turquoise Plato, CBOE LIS

### Venue Types

| Type | Visibility | Typical Size | Price Discovery | When to Use |
|------|-----------|-------------|-----------------|-------------|
| **Lit exchange** | Full transparency | Any | Primary | Default routing, small orders |
| **Dark pool** | Hidden | Medium-large | None (derived) | Reduce information leakage |
| **Midpoint dark** | Hidden, mid-price | Medium | Derived from NBBO | Price improvement |
| **Block crossing** | Hidden | Very large | Negotiated | Institutional blocks |
| **Internalizer** | Hidden | Retail-sized | Derived from NBBO | Retail order flow |

### Best Execution Obligations

**Reg NMS (US)**: Order Protection Rule (Rule 611) requires orders be executed at the best displayed price across all venues. Cannot trade through a better price on another exchange.

**MiFID II (EU)**: Best execution requires considering price, costs, speed, likelihood of execution, settlement, order size, and nature. Must demonstrate best execution to clients.

**IEX Speed Bump**: 350-microsecond delay designed to neutralize latency advantage. Protects resting orders from stale-quote arbitrage.

## Methodology

### Step 1: Basic SOR Architecture

```python
import numpy as np
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class VenueQuote:
    venue: str
    bid: float
    bid_size: int
    ask: float
    ask_size: int
    is_dark: bool
    fee_per_share: float  # positive = taker fee, negative = rebate
    latency_us: int  # microseconds to venue

@dataclass
class ChildOrder:
    venue: str
    side: str
    price: float
    size: int
    order_type: str  # 'market', 'limit', 'midpoint_peg'

def smart_route_aggressive(parent_size: int, side: str,
                            venue_quotes: List[VenueQuote]) -> List[ChildOrder]:
    """
    Route a marketable order across venues for best execution.
    Sweep available liquidity from best price to worst.
    """
    children = []
    remaining = parent_size

    if side == 'BUY':
        # Sort venues by ask price (lowest first), then by fee
        sorted_venues = sorted(venue_quotes,
                               key=lambda v: (v.ask, v.fee_per_share))
        for venue in sorted_venues:
            if remaining <= 0:
                break
            if venue.ask_size > 0:
                fill_size = min(remaining, venue.ask_size)
                children.append(ChildOrder(
                    venue=venue.venue, side='BUY',
                    price=venue.ask, size=fill_size,
                    order_type='limit'  # IOC limit at the ask
                ))
                remaining -= fill_size

    elif side == 'SELL':
        sorted_venues = sorted(venue_quotes,
                               key=lambda v: (-v.bid, v.fee_per_share))
        for venue in sorted_venues:
            if remaining <= 0:
                break
            if venue.bid_size > 0:
                fill_size = min(remaining, venue.bid_size)
                children.append(ChildOrder(
                    venue=venue.venue, side='SELL',
                    price=venue.bid, size=fill_size,
                    order_type='limit'
                ))
                remaining -= fill_size

    return children
```

### Step 2: Dark Pool Routing

```python
def dark_pool_strategy(parent_size: int, side: str, urgency: str,
                        dark_pools: List[Dict], nbbo: Dict):
    """
    Route to dark pools before lit venues to minimize information leakage.

    Strategy depends on urgency:
    - Low urgency: post in multiple dark pools at midpoint, wait for fills
    - Medium: probe dark pools briefly, then sweep lit
    - High: sweep lit immediately, skip dark pools
    """
    midpoint = (nbbo['bid'] + nbbo['ask']) / 2
    children = []

    if urgency == 'low':
        # Post midpoint pegged orders in dark pools
        # Allocate size based on historical fill rates
        for pool in dark_pools:
            alloc = parent_size * pool['expected_fill_rate']
            children.append(ChildOrder(
                venue=pool['name'], side=side,
                price=midpoint, size=int(alloc),
                order_type='midpoint_peg'
            ))
        # Set timeout: if not filled in 5 minutes, route to lit
        children.append({'action': 'timeout', 'seconds': 300, 'then': 'route_lit'})

    elif urgency == 'medium':
        # Probe: send small IOC orders to dark pools
        probe_size = min(parent_size * 0.1, 500)
        for pool in dark_pools[:3]:  # top 3 by historical fill rate
            children.append(ChildOrder(
                venue=pool['name'], side=side,
                price=midpoint, size=int(probe_size),
                order_type='midpoint_peg'
            ))
        # Remainder goes to lit
        remaining = parent_size - probe_size * 3
        children.extend(smart_route_aggressive(remaining, side, lit_quotes))

    return children

def estimate_dark_fill_probability(dark_pool, order_size, side, time_of_day):
    """
    Estimate probability and expected time-to-fill in a dark pool.
    Based on historical data.
    """
    # Key factors:
    # - Order size relative to average dark pool trade size
    # - Time of day (more volume around open/close)
    # - Side: buy vs sell (some pools have directional bias)
    # - Stock-specific fill rates in this pool

    base_fill_rate = dark_pool['historical_fill_rate']  # e.g., 0.15 = 15%
    size_penalty = min(1.0, dark_pool['avg_trade_size'] / order_size)
    time_factor = dark_pool['intraday_pattern'][time_of_day.hour]

    return base_fill_rate * size_penalty * time_factor
```

### Step 3: Fee Optimization

```python
def optimize_venue_fees(order: ChildOrder, venues: List[VenueQuote]):
    """
    US equity fee structure: maker-taker model
    - Taker (aggressive): pay 20-30 mils ($0.0020-0.0030 per share)
    - Maker (passive): receive 15-25 mils rebate
    - Inverted venues (BYX, EDGA): taker rebate, maker pays

    For a 100-share order at $50:
    - Taker fee: $0.30
    - Maker rebate: -$0.25 (you receive)
    - Difference: $0.55 per 100 shares = 1.1 bps
    """
    if order.order_type == 'limit' and not is_marketable(order):
        # Passive order: route to venue with best rebate
        best_venue = min(venues, key=lambda v: v.fee_per_share)
    else:
        # Aggressive order: route to venue with lowest taker fee
        # But consider inverted venues where takers get rebates
        inverted = [v for v in venues if v.fee_per_share < 0]
        if inverted:
            best_venue = min(inverted, key=lambda v: v.fee_per_share)
        else:
            best_venue = min(venues, key=lambda v: v.fee_per_share)

    return best_venue
```

### Step 4: Anti-Gaming Protection

```python
def detect_information_leakage(child_orders, market_data):
    """
    Detect if our routing pattern is being detected and gamed:
    1. Quote fading: prices move away as we route (front-running)
    2. Increased spread on venues where we post
    3. Fill rate drops over time (predatory algos learn our pattern)
    """
    signals = {}

    # Quote fading: price moves against us between routing decision and fill
    fill_prices = [o.fill_price for o in child_orders if o.filled]
    route_midpoints = [o.decision_midpoint for o in child_orders if o.filled]
    slippage = np.mean([
        (f - m) * o.side_sign for f, m, o in zip(fill_prices, route_midpoints, child_orders)
    ])
    signals['avg_slippage_bps'] = slippage * 10000 / np.mean(route_midpoints)

    # Fill rate trend
    fill_rates = [
        sum(1 for o in batch if o.filled) / len(batch)
        for batch in order_batches
    ]
    signals['fill_rate_trend'] = np.polyfit(range(len(fill_rates)), fill_rates, 1)[0]

    # If slippage is excessive or fill rates declining, consider:
    # - Randomize venue selection
    # - Add delays between routes
    # - Use IEX speed bump for protection
    # - Reduce dark pool usage (adverse selection)

    return signals
```

### Step 5: Regulatory Compliance

```python
def reg_nms_check(child_orders, nbbo_at_routing):
    """
    Verify Reg NMS compliance: no trade-through of protected quotes.
    """
    for order in child_orders:
        if order.side == 'BUY' and order.price > nbbo_at_routing['best_ask']:
            # Buying above the best ask is fine
            pass
        elif order.side == 'BUY' and order.fill_price > nbbo_at_routing['best_ask']:
            raise ComplianceError(f"Trade-through: filled at {order.fill_price} "
                                  f"vs NBBO ask {nbbo_at_routing['best_ask']}")

    return True

def mifid2_best_execution_report(orders, fills, market_data):
    """
    Generate MiFID II best execution report (RTS 27/28).
    Must demonstrate consideration of:
    - Price, cost, speed, likelihood of execution, settlement
    """
    report = {
        'total_orders': len(orders),
        'fill_rate': sum(1 for f in fills if f.filled) / len(orders),
        'avg_price_improvement_bps': compute_price_improvement(fills, market_data),
        'avg_execution_speed_ms': np.mean([f.latency_ms for f in fills]),
        'venue_distribution': Counter(f.venue for f in fills),
        'dark_pool_pct': sum(1 for f in fills if f.is_dark) / len(fills),
    }
    return report
```

## Examples

### Venue Selection for a Mid-Cap Stock

```python
# Stock: mid-cap, $80, ADV 500K shares, spread 3 cents
# Order: Buy 50,000 shares (10% ADV)

# Route plan:
# 1. Probe dark pools (Liquidnet, Sigma X, POSIT) with 5K shares each at mid
# 2. If fills come back: continue dark pool rotation
# 3. After 15 minutes or 50% filled: VWAP algo across lit venues
# 4. Fee optimization: use EDGA (inverted) for aggressive slices,
#    NYSE for passive resting orders (rebate)
```

### Impact of IEX Speed Bump

```python
# IEX 350μs delay matters when:
# - Latency arbitrageurs fade our resting orders after correlated price moves
# - Our resting limit orders get stale when the NBBO moves
# - Protection value: estimated 1-3 bps for mid-cap passive orders

# IEX does NOT help when:
# - We're the aggressive side (we pay the delay)
# - Stock is extremely liquid (spread is already 1 tick)
```

## Quality Gate

- [ ] SOR considers all relevant venues (exchanges, dark pools, internalizers)
- [ ] Best execution obligation met: documented venue selection rationale
- [ ] Fee optimization accounts for maker/taker and inverted venue economics
- [ ] Dark pool fill rates monitored and routing allocations updated
- [ ] Anti-gaming protections in place (randomization, leakage detection)
- [ ] Reg NMS trade-through checks performed on every execution
- [ ] Latency to each venue measured and factored into routing decisions
- [ ] Dark pool adverse selection monitored (are we getting filled only when price moves against us?)
- [ ] Venue performance reviewed monthly with updated routing logic
- [ ] MiFID II/Reg NMS compliance reports generated and retained
