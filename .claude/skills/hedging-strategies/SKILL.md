---
name: hedging-strategies
description: "Derivatives Hedging Strategies. Use when: User wants to hedge a derivatives position or portfolio; Designing delta-neutral strategies with gamma scalping; Managing vega exposure across a vol surface."
---

# Derivatives Hedging Strategies

name: hedging-strategies
description: Derivatives hedging — delta-neutral, gamma scalping, vega hedging.
origin: ECT

## When to Activate

- User wants to hedge a derivatives position or portfolio
- Designing delta-neutral strategies with gamma scalping
- Managing vega exposure across a vol surface
- Building portfolio hedges using options or futures
- Analyzing cross-hedging and basis risk
- Understanding hedge accounting requirements

## First Questions

1. What is the position to be hedged (single option, book, portfolio)?
2. Which Greeks are the primary concern (delta, gamma, vega, rho, theta)?
3. What is the hedging objective (minimize variance, protect downside, reduce tail risk)?
4. What is the rebalancing frequency and transaction cost budget?
5. Are there accounting or regulatory constraints on hedge design?

## Core Concepts

### Delta Hedging

Delta hedging neutralizes the first-order sensitivity of an option position to changes in the underlying.

```
Basic delta hedge:
  Option position: long N calls with delta = 0.55
  Hedge: short N * 0.55 shares of underlying
  Net delta = N * 0.55 - N * 0.55 = 0 (delta neutral)

  Delta changes as underlying moves (gamma), so hedge must be rebalanced

Discrete delta hedging:
  - Continuous hedging is impossible in practice
  - Rebalance at fixed intervals (daily, hourly) or on delta threshold
  - Hedging error = function of gamma, realized vol, and rebalance frequency

  Hedging error per rebalance:
    epsilon ~ 0.5 * Gamma * (delta_S)^2 - Theta * delta_t
    This is the gamma-theta tradeoff: gamma profits offset theta decay

Delta hedging P&L:
  For a long option position, delta-hedged:
    Daily P&L = 0.5 * Gamma * S^2 * (realized_return^2 - implied_vol^2 * dt)
    If realized vol > implied vol: profit (bought cheap vol)
    If realized vol < implied vol: loss (bought expensive vol)
```

### Gamma Scalping

Gamma scalping is the active management of a delta-hedged option position to capture the difference between realized and implied volatility.

```
Mechanics:
  1. Buy options (long gamma position)
  2. Delta hedge with underlying
  3. As underlying moves up: delta increases, sell shares to rehedge (sell high)
  4. As underlying moves down: delta decreases, buy shares to rehedge (buy low)
  5. Net effect: systematically buy low, sell high

P&L decomposition:
  Gamma scalping P&L = Gamma P&L - Theta cost

  Gamma P&L (per day):
    = 0.5 * Gamma * S^2 * (daily_return^2)
    = 0.5 * Gamma * S^2 * realized_vol^2 * dt

  Theta cost (per day):
    = -Theta (option time decay)
    = 0.5 * Gamma * S^2 * implied_vol^2 * dt (approximately, for ATM options)

  Net P&L per day:
    = 0.5 * Gamma * S^2 * (realized_vol^2 - implied_vol^2) * dt

  Breakeven: realized vol = implied vol
  Profit if: realized vol > implied vol (bought cheap options)
  Loss if: realized vol < implied vol (bought expensive options)

Optimal rebalancing frequency:
  Too frequent: transaction costs eat gamma profits
  Too infrequent: large delta drift, poor gamma capture
  Rule of thumb: rebalance when delta moves by 0.05-0.10
  Or at fixed intervals calibrated to gamma * expected move
  Zakamouline (2006): optimal bandwidth = f(gamma, transaction_cost, vol)
```

### Vega Hedging

Vega hedging neutralizes sensitivity to changes in implied volatility.

```
Why hedge vega:
  - Options books accumulate large vega exposure
  - Vol surface moves can cause significant P&L swings
  - Vega risk is not hedgeable with the underlying (only with other options)

Vega hedging approaches:

  1. Single-strike vega hedge:
     Offset vega with opposite position in another option
     Example: long 3-month ATM calls (vega = 0.15)
     Hedge: short 3-month ATM puts (same vega, different delta — adjust delta)
     Limitation: only hedges parallel vol shifts at that strike/tenor

  2. Vega-weighted hedge across term structure:
     Short-dated options have lower vega per unit vol
     Long-dated options have higher vega
     Match weighted vega across tenor buckets: 1M, 3M, 6M, 1Y, 2Y
     Residual: vol curve twist and butterfly exposures

  3. Vanna and volga hedging:
     Vanna = d(delta)/d(vol) = d(vega)/d(spot)
     Volga = d(vega)/d(vol) (second-order vol sensitivity)
     For exotic options: hedge vanna and volga using 25-delta risk reversals and strangles
     Standard approach for FX exotic desks

Vega bucketing:
  Decompose total vega into tenor buckets:
    1M vega: sensitivity to 1-month implied vol change
    3M vega: sensitivity to 3-month implied vol change
    6M vega: sensitivity to 6-month implied vol change
    1Y vega: sensitivity to 1-year implied vol change
  Hedge each bucket independently
  Monitor residual curve risk (flattening, steepening of vol term structure)
```

### Portfolio Hedging with Options

```
Hedging a stock portfolio with index options:

  Portfolio beta approach:
    Portfolio value: $10M, beta = 1.2 to S&P 500
    SPX at 5000, contract multiplier = 100
    Notional to hedge: $10M * 1.2 = $12M
    Contracts needed: $12M / (5000 * 100) = 24 puts

  Protective put:
    Buy 24 SPX puts at 95% strike (5% OTM)
    Cost: ~2% of portfolio value (annualized, depends on vol)
    Protection: limits loss to ~7% (5% deductible + put cost)

  Collar:
    Buy 95% puts + Sell 105% calls (zero-cost or near zero-cost)
    Caps upside at +5% but eliminates downside below -5%
    Popular for concentrated stock positions and tax-deferred hedging

  Put spread:
    Buy 95% put + Sell 85% put (reduces cost by 40-60%)
    Protection between -5% and -15%
    No protection beyond -15% (gap risk in crashes)

Cost reduction techniques:
  - Put spreads: sell lower-strike put to reduce premium
  - Collars: sell upside calls to fund puts
  - Put ratio spread: buy 1 ATM put, sell 2 OTM puts (risk: below lower strike)
  - Calendar spread: sell short-dated put, buy long-dated put
  - Seagull: put spread + sell OTM call
```

### Cross-Hedging and Basis Risk

```
Cross-hedging:
  Hedging an exposure with a related but different instrument
  Example: hedge single stock with sector ETF, hedge commodity with a correlated one

Basis risk:
  Basis = Spot price of hedged asset - Price of hedging instrument
  Basis risk = variability of the basis over the hedge horizon

  Sources of basis risk:
    - Grade/quality differences (Brent vs WTI)
    - Location differences (Henry Hub vs TTF natural gas)
    - Timing differences (hedge maturity vs exposure maturity)
    - Cross-asset correlation instability

Optimal hedge ratio (minimum variance):
  h* = rho * (sigma_hedged / sigma_hedge_instrument)
  Where rho = correlation between hedged asset and hedge instrument
  If rho = 0.8, sigma_hedged = 20%, sigma_hedge = 25%:
    h* = 0.8 * (20/25) = 0.64
    Hedge 64% of notional, not 100%

  Hedge effectiveness:
    R^2 = rho^2 = proportion of variance eliminated
    At rho = 0.8: hedge effectiveness = 64% (significant residual risk)
    At rho = 0.95: hedge effectiveness = 90% (good hedge)

Cross-hedge examples:
  Stock vs ETF: high correlation (0.85-0.95 for large caps vs sector ETF)
  Commodity grades: moderate (0.80-0.95 for Brent vs WTI)
  FX proxy hedges: variable (0.5-0.9 depending on currency pair relationship)
```

### Hedge Accounting

```
IAS 39 / IFRS 9 / ASC 815 requirements:

  Fair value hedge:
    - Hedges changes in fair value of a recognized asset/liability
    - Both hedge instrument and hedged item marked to market through P&L
    - Reduces P&L volatility if hedge is effective

  Cash flow hedge:
    - Hedges variability of future cash flows
    - Effective portion of hedge gain/loss goes to OCI (Other Comprehensive Income)
    - Transferred to P&L when hedged cash flow affects earnings
    - Ineffective portion goes directly to P&L

  Hedge effectiveness requirements:
    - Prospective: demonstrate hedge will be highly effective (80-125% under IAS 39)
    - IFRS 9: no bright-line 80-125% test, but economic relationship required
    - Retrospective: test actual effectiveness each period
    - Documentation: formal designation at inception

  Critical terms match:
    - Notional, maturity, underlying, reset dates should match
    - Perfect match: hedge accounting straightforward
    - Imperfect match: must demonstrate and measure effectiveness

  Impact on trading decisions:
    - Hedge accounting constraints may prevent optimal hedge design
    - Rolling short-dated hedges vs single long-dated hedge: accounting implications differ
    - Basis risk may cause hedge ineffectiveness, disqualifying from hedge accounting
```

## Detailed Methodology

### Greeks Management for a Book

```
Multi-dimensional risk management:

  Step 1: Compute aggregate Greeks by underlying, tenor, strike bucket
    - Delta by underlying (netted)
    - Gamma by underlying and tenor
    - Vega by underlying, tenor, and strike (vol surface grid)
    - Theta (total portfolio time decay)

  Step 2: Set risk limits per Greek
    Delta: max |delta| = $X per underlying (or equivalent shares)
    Gamma: max |gamma| = $Y per 1% move in underlying
    Vega: max |vega| = $Z per 1 vol point per tenor bucket
    Theta: monitor daily P&L bleed, ensure gamma scalping offsets

  Step 3: Hedge priority
    1. Delta: hedge first (largest and most immediate risk)
    2. Gamma: manage through option trades (buy/sell options)
    3. Vega: hedge with matching-tenor options or variance swaps
    4. Cross-Greeks (vanna, volga): monitor, hedge if material

  Step 4: Residual risk reporting
    Report unhedged exposures: pin risk, correlation, gap risk
    Stress test: what happens with 3-sigma move + vol spike
```

### Dynamic Hedging Cost Analysis

```
Cost of delta hedging (Leland 1985):
  Modified vol for hedging cost:
    sigma_adjusted = sigma * sqrt(1 + sqrt(2/pi) * k / (sigma * sqrt(dt)))
  Where k = round-trip transaction cost, dt = rebalance interval

  For sigma = 20%, k = 0.1%, daily rebalancing:
    sigma_adjusted = 20% * sqrt(1 + 0.30) = 22.8%
    Hedging cost adds ~2.8 vol points to effective implied vol

  Implication: options sold at 20 implied vol but hedged at cost of 22.8 vol
  Must sell options at implied vol > realized vol + hedging cost to profit

Cost optimization:
  1. Wider rebalancing bandwidth: reduces cost but increases tracking error
  2. Hedge with options instead of underlying: reduces rebalancing frequency
  3. Portfolio netting: offset delta across correlated positions before hedging
  4. Batch hedging: aggregate delta changes and execute once per day
```

## Quality Gate

Before implementing a hedging strategy:

- [ ] Hedged risk clearly identified (delta, gamma, vega, tail, or all)
- [ ] Hedge instrument selected with minimal basis risk
- [ ] Hedge ratio calculated using appropriate method (minimum variance, beta-adjusted)
- [ ] Transaction costs of hedging quantified (rebalancing costs erode performance)
- [ ] Rebalancing frequency determined (tradeoff: tracking error vs cost)
- [ ] Cross-hedge basis risk measured and accepted
- [ ] Stress test: hedge performance in 2008, 2020 scenarios
- [ ] Hedge accounting requirements checked (if applicable)
- [ ] Liquidity of hedge instrument verified (can you roll and adjust under stress?)
- [ ] Residual risk after hedging documented and reported to risk management
