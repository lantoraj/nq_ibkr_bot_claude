---
name: market-making
description: "Market Making. Use when: User wants to design a market-making strategy; Understanding bid-ask spread management and inventory risk; Implementing the Avellaneda-Stoikov optimal quoting framework."
---

# Market Making

name: market-making
description: Market making strategies — bid-ask management, inventory risk, Avellaneda-Stoikov framework. Use for market-making strategy design.

## When to Activate

- User wants to design a market-making strategy
- Understanding bid-ask spread management and inventory risk
- Implementing the Avellaneda-Stoikov optimal quoting framework
- Analyzing order book dynamics and adverse selection
- Setting risk limits and position bounds for market makers

## First Questions

1. What market/instrument (equities, futures, options, crypto)?
2. What is the typical bid-ask spread and daily volume?
3. Are you a designated market maker (obligations) or proprietary?
4. What latency/technology stack is available?
5. What is the maximum inventory you can carry (position limits)?

## Core Concepts

### Market Making Economics

Market makers profit by continuously quoting bid and ask prices, earning the spread:

```
Revenue model:
  Gross revenue = spread_captured * volume_traded
  Net revenue = gross - adverse_selection_cost - inventory_cost - technology_cost

The spread has three components (Roll/Glosten-Harris decomposition):
  1. Order processing cost: Fixed cost of providing liquidity
  2. Inventory holding cost: Risk of carrying positions
  3. Adverse selection cost: Loss to informed traders

Typical P&L distribution:
  Many small wins (spread capture)
  Occasional large losses (adverse selection, gap risk)
  Positive expected value IF adverse selection is managed
```

### Order Book Dynamics

```
Level 1: Best bid and best ask (BBO)
  Spread = Ask - Bid
  Mid-price = (Bid + Ask) / 2
  Microprice = (Bid * AskSize + Ask * BidSize) / (AskSize + BidSize)
    Microprice is a better fair value estimate — weighted by opposite-side size

Level 2: Full depth of book
  Bid/ask at multiple price levels with quantities
  Order book imbalance: (BidSize - AskSize) / (BidSize + AskSize)
    Imbalance > 0: More buying pressure, price likely to rise
    Imbalance < 0: More selling pressure, price likely to fall

Trade flow:
  Aggressive orders: Market orders that cross the spread (price takers)
  Passive orders: Limit orders that add to the book (price makers)
  Trade imbalance: Net aggressive buying vs selling — key signal for fair value
```

### Adverse Selection

The primary risk for market makers. Adverse selection occurs when the market maker trades against informed participants:

```
Adverse selection cost:
  When an informed trader buys from you, the stock goes up → you sold cheap
  When an informed trader sells to you, the stock goes down → you bought expensive

Adverse selection indicators:
  - Order flow toxicity (VPIN — Volume-Synchronized Probability of Informed Trading)
  - Large order size relative to normal
  - Unusual activity in correlated instruments (e.g., options before equity move)
  - News arrival (widening spreads, increased toxicity)
  - Order-to-trade ratio spikes

Mitigation:
  - Widen spreads when toxicity is detected
  - Reduce quoted size in toxic conditions
  - Fade quotes (pull orders) before expected news releases
  - Skew quotes based on inventory and flow direction
```

## Detailed Methodology

### Avellaneda-Stoikov Framework

The foundational model for optimal market-making quotes:

```
Setup:
  Mid-price follows: dS_t = sigma * dW_t (arithmetic Brownian motion)
  Inventory: q_t (number of units held, positive = long)
  Terminal time: T
  Risk aversion: gamma

Reservation price (fair value adjusted for inventory):
  r_t = S_t - q_t * gamma * sigma^2 * (T - t)

  Interpretation: When long (q > 0), your fair value is BELOW mid-price
  (you want to sell to reduce inventory). When short (q < 0), fair value
  is ABOVE mid-price (you want to buy).

Optimal spread (around reservation price):
  delta = gamma * sigma^2 * (T - t) + (2/gamma) * ln(1 + gamma/k)

  Where k is related to order arrival intensity

Optimal quotes:
  Bid = r_t - delta/2
  Ask = r_t + delta/2

Key insights:
  1. Wider spread when volatility is high (more risk per trade)
  2. Wider spread when risk aversion is high
  3. Skew quotes based on inventory (pull bid up when short, push ask down when long)
  4. Spread narrows as T approaches (less time = less inventory risk)
```

### Inventory Management

```
Inventory risk management hierarchy:

Level 1: Quote skewing (passive)
  Shift bid/ask based on inventory:
    If long: lower both bid and ask (encourage sells, discourage buys)
    If short: raise both bid and ask (encourage buys, discourage sells)
    Skew amount proportional to inventory * gamma * sigma^2

Level 2: Inventory limits (hard bounds)
  Maximum long position: Q_max
  Maximum short position: -Q_max
  When at limit: remove quote on the side that would increase inventory

Level 3: Active hedging
  When inventory exceeds soft limit, send aggressive orders to reduce
  Trade off: hedging cost (crossing spread) vs inventory risk
  Hedge with correlated instrument if available (e.g., ETF vs basket)

Level 4: End-of-day flattening
  Reduce position to zero by market close
  Ramp up hedging aggressiveness as close approaches
  Accept crossing spread to eliminate overnight risk
```

### Spread Decomposition

Understanding WHY the spread exists guides how to set your quotes:

```
Observed spread decomposition:
  Spread = Order Processing + Inventory + Adverse Selection

Estimation methods:

1. Roll model (simplest):
   Effective spread = 2 * sqrt(-cov(r_t, r_{t-1}))
   Works only if serial correlation is negative (mean-reverting midquote)

2. Huang-Stoll model:
   Trade indicator: d_t = +1 (buy), -1 (sell)
   p_t - p_{t-1} = (alpha + beta) * S/2 * d_t - alpha * S/2 * d_{t-1} + epsilon_t
   alpha: probability of informed trading
   beta: inventory adjustment coefficient

3. PIN (Probability of Informed Trading):
   Models order flow as mixture of informed and uninformed
   High PIN → high adverse selection → wider spreads needed
```

### HFT Considerations

```
Latency matters:
  - Stale quotes are free options for faster traders
  - If you are slow, you get adversely selected on EVERY news event
  - Minimum viable latency depends on the market:
    US equities: < 10 microseconds for competitive HFT
    Crypto: < 1 millisecond is competitive
    Less liquid markets: 10-100 milliseconds may be sufficient

Technology requirements:
  - Co-location at exchange (or cloud with low-latency networking)
  - FPGA or optimized C++ for order management
  - Direct market access (DMA) — no intermediary broker latency
  - Real-time risk system (position limits, P&L limits)

Queue position:
  In price-time priority markets, queue position at a price level matters
  First in queue gets filled first at that price
  Strategy: place orders early when spread is wide, manage queue position
  Cancel-replace has a cost: you lose queue priority
```

### Risk Limits for Market Makers

```
Position limits:
  Maximum inventory: +/- Q_max per instrument
  Maximum notional exposure: $X per instrument
  Maximum portfolio delta: $Y total

P&L limits:
  Daily loss limit: -$Z (stop making markets, flatten)
  Position loss limit: -$W per instrument
  Drawdown limit: -$V from peak equity

Spread limits:
  Minimum spread: never quote tighter than break-even
  Maximum spread: regulatory obligations or competitive pressure
  Spread floor = adverse_selection_cost + order_processing_cost + margin

Volume limits:
  Maximum participation rate: < 5% of daily volume
  Avoid becoming the dominant liquidity provider (concentration risk)

Circuit breakers:
  Halt quoting during exchange halts
  Widen spreads or pull quotes on extreme volatility
  Automatic position flattening on connectivity loss
```

## Templates / Examples

### Market Making Strategy Specification

```
Instrument: BTC/USDT perpetual futures
Exchange: [Exchange Name]
Strategy: Avellaneda-Stoikov with adaptive parameters

Parameters:
  Base spread: 5 bps (0.05%)
  Inventory limit: +/- 10 BTC
  Risk aversion (gamma): 0.001
  Volatility window: 60-second realized vol
  Order refresh: Every 500ms
  Quote levels: 3 (each side)
  Size per level: 0.5 BTC

Inventory Management:
  Skew: 0.5 bps per BTC of inventory
  Soft limit: +/- 5 BTC (begin active hedging)
  Hard limit: +/- 10 BTC (remove quote on increasing side)

Risk Limits:
  Daily loss limit: $5,000
  Hourly loss limit: $2,000
  Position loss limit: $3,000

Expected Performance (daily):
  Trades: 500-1,000
  Gross spread capture: $2,000-$4,000
  Adverse selection cost: $800-$1,500
  Net P&L: $500-$2,000
  Sharpe (annualized): 3.0-5.0
```

### Market Making P&L Attribution

```
Daily P&L Report — [Date]

Component           | P&L
Spread capture      | +$3,200
Inventory carry     | -$450
Adverse selection   | -$1,100
Hedging cost        | -$200
Fees/rebates        | +$180
Technology cost     | -$50
NET P&L             | +$1,580

Inventory Summary:
  Opening: +2.1 BTC
  Closing: -0.5 BTC
  Max long: +8.3 BTC (14:32 UTC)
  Max short: -4.1 BTC (09:15 UTC)
  Avg absolute inventory: 3.2 BTC

Spread Summary:
  Avg quoted spread: 5.8 bps
  Avg effective spread: 4.2 bps
  Fill rate: 35%
  Quote-to-trade ratio: 12:1
```

### Adverse Selection Monitoring

```
Adverse Selection Report — [Period]

Metric                    | Value  | Threshold | Status
Realized spread (vs mid)  | 1.2 bps| > 0       | OK
Mark-to-market after 1min | -0.8 bp| > -1.5    | OK
Mark-to-market after 5min | -1.5 bp| > -2.5    | WARNING
VPIN (toxicity)           | 0.42   | < 0.60    | OK
Informed trade fraction   | 18%    | < 25%     | OK
Large order impact        | 3.2 bps| < 5.0     | OK

Action: 5-minute adverse selection elevated. Consider widening
quotes by 0.5 bps during high-toxicity periods.
```

## Quality Gate

Before deploying a market-making strategy:

- [ ] Adverse selection cost estimated — spread exceeds this cost with margin
- [ ] Inventory limits defined (hard and soft) with automatic enforcement
- [ ] Quote skewing logic tested — inventory mean-reverts toward zero
- [ ] Daily and hourly loss limits programmed with automatic shutdown
- [ ] Latency is competitive for the target market
- [ ] Spread decomposition performed — understand what you are being compensated for
- [ ] Connectivity failure plan in place (auto-cancel all open orders)
- [ ] Regulatory obligations understood (if designated market maker)
- [ ] Backtested on order book data (not just OHLCV)
- [ ] Paper trading period completed with realistic fill simulation
- [ ] Kill switch tested and functional
