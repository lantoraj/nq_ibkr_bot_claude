---
name: liquidity-risk
description: "Bid-ask spreads, market impact, Amihud illiquidity, liquidity-adjusted VaR, and the illiquidity premium. Use when: User evaluating the liquidity profile of a portfolio or individual positions; Estimating market impact costs for large trades; Computing liquidity-adjusted risk measures (LVaR)."
---

# Liquidity Risk Assessment

> Bid-ask spreads, market impact, Amihud illiquidity, liquidity-adjusted VaR, and the illiquidity premium.

## When to Activate

- User evaluating the liquidity profile of a portfolio or individual positions
- Estimating market impact costs for large trades
- Computing liquidity-adjusted risk measures (LVaR)
- Assessing liquidity risk during stress periods
- Analyzing the illiquidity premium in asset pricing
- Designing execution strategies that minimize market impact

## Core Concepts

### Dimensions of Liquidity

**Tightness (Bid-Ask Spread)**
- Quoted spread: ask - bid
- Effective spread: 2 * |trade_price - midpoint| (captures actual execution vs. midpoint)
- Relative spread: spread / midpoint (percentage terms for cross-asset comparison)
- Typical ranges: large-cap equities 1-5bp, IG bonds 5-50bp, HY bonds 50-200bp, emerging market 100-500bp
- Spreads widen dramatically in stress: 2008 IG bond spreads went from 10bp to 200bp+

**Depth (Volume)**
- Average daily volume (ADV): baseline liquidity measure
- Days to liquidate = position_size / (participation_rate * ADV)
- Participation rate: typically 10-25% of ADV to avoid excessive impact
- Depth at best quote: number of shares/contracts available at the inside bid/ask
- Book depth: cumulative volume available within N ticks of best quote

**Resilience**
- How quickly prices and spreads recover after a large trade
- High resilience: price returns to pre-trade level quickly (deep, liquid markets)
- Low resilience: price impact persists (thin markets, information-driven flow)
- Measured by the half-life of price impact decay

**Immediacy**
- Cost of executing immediately vs. patiently
- Urgent execution (market orders) pays wider spreads and higher impact
- Patient execution (limit orders, TWAP/VWAP algorithms) reduces cost but adds timing risk

### Liquidity Metrics

**Amihud Illiquidity Ratio**
- ILLIQ = (1/D) * sum(|r_d| / V_d) over D days
- Higher ILLIQ = more price impact per dollar of volume = less liquid
- Cross-sectionally comparable and widely used in academic research
- Captures the intuition that illiquid stocks move more per unit of trading volume
- Typically computed monthly using daily data

**Kyle's Lambda**
- From market microstructure theory: delta_p = lambda * order_flow
- Lambda measures permanent price impact per unit of signed order flow
- Estimated from regression of price changes on order imbalance
- Higher lambda = less liquid, more information in trades

**Roll's Spread Estimator**
- Estimated from serial covariance of returns: spread = 2 * sqrt(-cov(r_t, r_{t-1}))
- Only valid when cov is negative (bid-ask bounce dominates)
- Useful when actual bid-ask data is unavailable (e.g., daily bond data)

**Pastor-Stambaugh Liquidity Measure**
- Captures return reversals following high-volume days
- Signed volume predicts next-day return reversal in illiquid stocks
- Aggregate liquidity factor: systematic liquidity risk

## Methodology

### Market Impact Models

**Linear (Permanent) Impact**
- delta_p = lambda * Q, where Q = quantity traded
- Permanent: price does not revert — information content of trade
- Too simplistic for large trades — impact is concave (square root law)

**Square Root Law (Empirical)**
- Impact = sigma * k * sqrt(Q / V), where sigma = volatility, V = ADV, k = constant (typically 0.5-1.5)
- Well-documented empirically across equities, futures, FX
- Total impact for executing fraction f of ADV: approximately sigma * sqrt(f)
- Example: stock vol = 2%/day, trading 10% of ADV -> impact approximately 2% * sqrt(0.10) = 0.63%

**Almgren-Chriss Optimal Execution**
- Tradeoff between market impact (trading fast) and timing risk (trading slow)
- Temporary impact: g(v) = eta * v (proportional to trading rate)
- Permanent impact: h(v) = gamma * v (proportional to cumulative volume)
- Optimal execution trajectory minimizes: E[cost] + lambda * Var[cost]
- Risk-neutral: trade at constant rate (TWAP)
- Risk-averse: front-load trading (trade faster initially)
- Result is an optimal trading schedule: number of shares per time interval

### Liquidity-Adjusted VaR (LVaR)

**Exogenous Spread Approach**
- LVaR = VaR + 0.5 * spread * position_value
- Adds half the bid-ask spread (cost of liquidating) to standard VaR
- Simple but ignores that spreads widen in stress

**Endogenous Spread Approach**
- Model spread as a function of market conditions (spread widens with vol, position size)
- LVaR = VaR + liquidity_cost(position_size, stressed_spread)
- Stressed spread: use crisis-period spreads or scale current spread by stress factor

**Holding Period Adjustment**
- Standard VaR assumes 1-day liquidation; illiquid positions need longer
- Adjust holding period based on days to liquidate: VaR_T = VaR_1 * sqrt(T_liquidation)
- T_liquidation = position / (participation_rate * ADV)
- For a position taking 10 days to liquidate: VaR_10 = VaR_1 * sqrt(10) = 3.16 * VaR_1

**FRTB Liquidity Horizons**
- Regulatory framework assigns liquidity horizons by risk factor category
- 10 days: large-cap equities, G10 FX, sovereign rates
- 20 days: small/mid-cap equities, investment grade credit
- 40 days: high yield credit, EM FX
- 60 days: volatility risk factors, exotic FX
- 120 days: correlation, structured credit

### Liquidity Stress Testing

1. Identify positions that become illiquid in stress (credit, EM, small-cap)
2. Apply historical stress bid-ask spreads (2008, 2020) or multiples of current spreads (3-5x)
3. Model volume decline: in crisis, trading volumes can drop 50-80% in credit markets
4. Compute liquidation timeline under stressed volumes
5. Assess margin calls: forced liquidation at worst prices compounds losses
6. Identify liquidity mismatches: illiquid assets funded by short-term borrowing

## Examples

### Amihud Illiquidity Comparison
```
Stock A (large-cap): avg |daily return| = 1.2%, avg daily volume = $500M
  ILLIQ_A = 0.012 / 500,000,000 = 2.4e-11

Stock B (small-cap): avg |daily return| = 2.5%, avg daily volume = $5M
  ILLIQ_B = 0.025 / 5,000,000 = 5.0e-9

Stock B is 208x more illiquid than Stock A by Amihud measure.
Expected price impact of $1M trade:
  Stock A: negligible (0.2bp)
  Stock B: approximately 50bp (material)
```

### Liquidation Cost Estimation
```
Portfolio: $200M in corporate bonds
Average bid-ask spread (normal): 15bp
Stressed bid-ask spread (2020 COVID): 120bp
Average daily volume per bond: $2M
Participation rate: 20%

Days to liquidate (normal): $200M / (20% * $2M * 100 bonds) = 5 days
Days to liquidate (stressed, vol drops 60%): $200M / (20% * $0.8M * 100 bonds) = 12.5 days

Liquidation cost (normal): $200M * 15bp / 2 = $150K
Liquidation cost (stressed): $200M * 120bp / 2 = $1.2M + market impact
Total stressed cost including impact: approximately $2-3M (1-1.5% of portfolio)
```

### LVaR Calculation
```
Portfolio: $50M, 1-day 99% VaR = $800K
Position in illiquid small-cap: $10M, days to liquidate = 8 days
Bid-ask spread (stressed): 150bp

Standard VaR: $800K
Liquidity adjustment:
  Holding period: VaR * (sqrt(8) - 1) = $800K * 1.83 = $1,464K additional
  Spread cost: $10M * 150bp / 2 = $75K
LVaR = $800K + $1,464K + $75K = $2,339K

LVaR is 2.9x standard VaR — the illiquid position triples the effective risk.
```

## Quality Gate

- Liquidity metrics must be computed for every position, not just portfolio-level
- Amihud or equivalent illiquidity ratio must be tracked over time to detect liquidity deterioration
- Market impact estimates must use the square root law or a calibrated model, not linear assumptions
- LVaR must include both spread cost and holding period adjustment
- Liquidation timeline must be computed at both normal and stressed volume levels
- Positions exceeding 1 day of ADV at 20% participation must be flagged as liquidity risks
- Liquidity stress tests must use crisis-period spreads and volumes, not current conditions
- Portfolio liquidity profile must be reported: percentage of portfolio liquidatable in 1, 5, 10, 20 days
- Illiquid positions funded by short-term leverage must be identified and flagged
- Liquidity metrics must be refreshed at least weekly; daily during periods of market stress
