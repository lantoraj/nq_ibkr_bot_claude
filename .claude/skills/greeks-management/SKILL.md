---
name: greeks-management
description: "Delta, gamma, vega, theta hedging and higher-order Greeks. Portfolio-level risk management, dynamic hedging, and rebalancing strategies. Use when: User manages an options portfolio and needs to hedge or analyze risk; Delta-neutral portfolio construction or adjustment; Gamma scalping strategies or gamma exposure analysis."
---

# Options Greeks Management

> Delta, gamma, vega, theta hedging and higher-order Greeks. Portfolio-level risk management, dynamic hedging, and rebalancing strategies.

## When to Activate

- User manages an options portfolio and needs to hedge or analyze risk
- Delta-neutral portfolio construction or adjustment
- Gamma scalping strategies or gamma exposure analysis
- Vega hedging for volatility-sensitive positions
- Theta decay analysis and time decay management
- Higher-order Greeks (vanna, volga, charm) for exotic or large positions
- Understanding P&L attribution through Greeks decomposition

## Core Concepts

### First-Order Greeks

**Delta (d price / d spot)**
- Call delta: 0 to +1; Put delta: -1 to 0
- ATM options have delta approximately +/-0.50 (slightly above for calls due to lognormal drift)
- Delta is the hedge ratio: sell delta shares per call option to be delta-neutral
- Dollar delta = delta * notional = exposure in dollar terms to underlying move
- Delta changes with spot (gamma), time (charm), and vol (vanna)

**Theta (d price / d time)**
- Measures time decay per day — negative for long options, positive for short
- ATM options have highest theta (most time value to lose)
- Theta is the "cost" of holding gamma; theta and gamma are linked: theta approximately = -0.5 * gamma * S^2 * sigma^2 (for BSM)
- Short-dated ATM options have the fastest theta decay
- Theta accelerates as expiration approaches (theta = -S*sigma*phi(d1) / (2*sqrt(T)) for calls)

**Vega (d price / d implied vol)**
- Sensitivity to implied volatility changes — positive for long options
- ATM options have highest vega
- Vega is proportional to sqrt(T): longer-dated options have more vega
- Vega is not a true Greek from BSM (not a model parameter), but essential for trading
- Weighted vega: normalize vega by sqrt(T) to compare across maturities

**Rho (d price / d interest rate)**
- Sensitivity to risk-free rate — typically small for short-dated options
- More significant for long-dated options and interest rate derivatives
- Calls have positive rho; puts have negative rho

### Second-Order Greeks

**Gamma (d delta / d spot = d^2 price / d spot^2)**
- Measures convexity of option price — positive for long options
- Highest for ATM, short-dated options
- Long gamma profits from large moves (in either direction); short gamma loses
- Dollar gamma = 0.5 * gamma * S^2 * (move%)^2 = P&L from spot move
- Gamma and theta are offsetting: you pay theta to own gamma (the "gamma-theta tradeoff")

**Vanna (d delta / d vol = d vega / d spot)**
- Cross-Greek: how delta changes when vol changes, or equivalently how vega changes when spot moves
- Critical for risk-reversal and skew positions
- Positive vanna for OTM calls and ITM puts; negative for OTM puts and ITM calls
- In a skew environment, vanna exposure can generate significant P&L

**Volga / Vomma (d vega / d vol = d^2 price / d vol^2)**
- Convexity of option price with respect to vol
- Positive for OTM and ITM options; approximately zero for ATM
- Explains why OTM options trade at higher implied vol than ATM (vol smile compensation for volga)
- Important for pricing and hedging exotic options (vanna-volga method)

**Charm (d delta / d time)**
- How delta changes as time passes
- Critical for managing delta hedges through time without rebalancing
- ATM charm is small; OTM/ITM charm can be significant near expiry

### Portfolio-Level Greeks

- Portfolio delta = sum of position deltas (linear aggregation)
- Portfolio gamma = sum of position gammas (same underlying)
- Portfolio vega = sum of position vegas
- Cross-underlying risk: need correlation-weighted exposure for portfolio risk
- Greeks are additive within the same underlying; cross-underlying requires factor models

## Methodology

### Delta Hedging

**Discrete Delta Hedging**
1. Compute portfolio delta
2. Trade underlying shares/futures to offset delta (buy if short delta, sell if long delta)
3. Rebalance at chosen frequency: time-based (daily, hourly) or threshold-based (when delta drifts by x)
4. Hedging error: proportional to gamma * (actual_move^2 - implied_vol^2 * dt)
5. P&L of delta-hedged option = path integral of 0.5 * gamma * S^2 * (realized_vol^2 - implied_vol^2) * dt
6. Transaction costs limit rebalancing frequency — optimal frequency balances hedging error vs. cost

**Futures vs. Cash Hedging**
- Futures: capital efficient, no stock borrow, but roll risk and basis
- Cash (shares): exact delta match, no roll, but requires capital
- FX delta hedging: use spot, forwards, or NDF depending on currency

### Gamma Scalping

1. Establish a long gamma position (buy straddle or strangle)
2. Delta-hedge continuously or at intervals
3. Each hedge locks in a profit from the realized move: P&L = 0.5 * gamma * (dS)^2
4. Must overcome theta decay: profitable only if realized vol > implied vol
5. Breakeven daily move = sqrt(2 * daily_theta / gamma) for a delta-hedged position
6. Scalping frequency matters: too frequent = high transaction costs; too infrequent = miss moves

### Vega Hedging

1. Compute portfolio vega exposure across the vol surface (by strike and expiry)
2. Use options (usually ATM) at matching maturities to hedge vega
3. Vega-neutral does not mean volga-neutral: second-order vol risk remains
4. Term structure hedging: bucket vega by maturity, hedge each bucket
5. Skew hedging: use risk reversals (buy OTM put, sell OTM call) or put/call spread overlays
6. Weighted vega approach: normalize all vegas to a reference maturity (e.g., 1-month equivalent)

### Cross-Greek Hedging

Simultaneous delta-gamma-vega neutral construction:
1. Need at least as many hedging instruments as Greeks to neutralize
2. Delta-neutral: use underlying (1 instrument)
3. Delta-gamma neutral: use underlying + 1 option at same expiry (2 instruments)
4. Delta-gamma-vega neutral: use underlying + 2 options at different strikes/expiries (3 instruments)
5. Solve system of linear equations for hedge ratios
6. Over-hedging introduces other risks — prioritize Greeks by materiality

### Rebalancing Decisions

- **Time-based**: hedge every hour/day regardless of move — simple but may trade unnecessarily
- **Move-based**: hedge when delta exceeds threshold — efficient but may miss fast moves
- **Tolerance bands**: set acceptable range for each Greek; rebalance when any breaches
- **Utility-based**: optimize rebalancing considering risk aversion, transaction costs, and expected holding period

## Examples

### Delta-Gamma Hedge Construction
```
Position: Short 1000 calls on stock XYZ at K=100, T=3M
Call delta = 0.55, gamma = 0.03, vega = 0.25

Current exposure:
  Portfolio delta = -1000 * 0.55 = -550
  Portfolio gamma = -1000 * 0.03 = -30
  Portfolio vega = -1000 * 0.25 = -250

Hedge with underlying + different strike call (K=110, delta=0.35, gamma=0.02):
  Gamma hedge: buy 30/0.02 = 1500 calls at K=110
  Net delta after gamma hedge: -550 + 1500*0.35 = -550 + 525 = -25
  Buy 25 shares to flatten delta.
  Net vega: -250 + 1500*0.20 = +50 (residual vega — need third instrument to zero)
```

### Gamma Scalping P&L
```
Long straddle: ATM call + ATM put on stock at $100.
Straddle gamma = 0.04, daily theta = -$200.
Day 1: Stock moves $100 -> $103. Delta-hedge: sell 0.04*3*100 = 12 shares at $103.
Day 2: Stock moves $103 -> $99. Buy back shares, sell additional.
Daily gamma P&L = 0.5 * 0.04 * 100^2 * (actual_move/100)^2 * 100 contracts.
If stock moves $3/day (3% daily realized vol), gamma P&L = 0.5*0.04*9*100 = $180/day.
Net P&L = $180 - $200 theta = -$20/day. Need >$3.16 daily move to break even.
```

## Quality Gate

- Portfolio Greeks must be computed via full repricing bump-and-revalue, not just analytical BSM
- Bump sizes: delta (1% spot), gamma (from two delta calculations), vega (1 vol point), theta (1 day)
- Cross-Greeks (vanna, volga) must be computed for portfolios with significant skew exposure
- Hedging error tracking: compare actual P&L to Greek-predicted P&L daily
- Rebalancing costs must be included in any gamma scalping or delta hedging analysis
- Greeks must be aggregated correctly: same underlying for direct addition, factor model for cross-asset
- Pin risk near expiry must be monitored for positions near ATM strikes
- Greeks must be stress-tested: compute Greeks under +-20% spot and +-5 vol point shifts
- Report dollar-denominated Greeks (dollar delta, dollar gamma, dollar vega) for cross-portfolio comparison
