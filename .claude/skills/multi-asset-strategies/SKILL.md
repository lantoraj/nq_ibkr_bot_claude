---
name: multi-asset-strategies
description: "Multi-Asset Systematic Strategies. Use when: User wants to build a multi-asset systematic portfolio; Designing risk premia harvesting strategies across asset classes; Building CTA / managed futures trend-following systems."
---

# Multi-Asset Systematic Strategies

name: multi-asset-strategies
description: Multi-asset systematic strategies — risk premia, CTA, global macro systematic.
origin: ECT

## When to Activate

- User wants to build a multi-asset systematic portfolio
- Designing risk premia harvesting strategies across asset classes
- Building CTA / managed futures trend-following systems
- Implementing systematic global macro strategies
- Constructing a portfolio of uncorrelated strategies

## First Questions

1. Which strategy style (risk premia, trend-following, macro systematic, or combined)?
2. What is the investment universe (futures, ETFs, FX, or mixed)?
3. What is the target volatility and drawdown tolerance?
4. What is the AUM and capacity requirement?
5. What is the rebalancing frequency (daily, weekly, monthly)?

## Core Concepts

### Risk Premia Harvesting

Risk premia are systematic return sources that compensate investors for bearing specific risks. They persist because they are economically justified and painful to hold through drawdowns.

```
Major documented risk premia:

  Equity risk premium:     ~5-7% long-term (equity over bonds)
  Value premium:           ~2-4% (cheap over expensive assets)
  Momentum premium:        ~4-8% (winners over losers)
  Carry premium:           ~3-5% (high yield over low yield)
  Low volatility premium:  ~2-3% (low vol over high vol)
  Quality premium:         ~2-3% (profitable over unprofitable)
  Term premium:            ~1-3% (long bonds over short bonds)
  Credit premium:          ~2-4% (corporate over government)
  Liquidity premium:       ~1-3% (illiquid over liquid)
  Volatility risk premium: ~3-5% (selling vol over buying vol)

Implementation across asset classes:
  Equities:    Value, momentum, quality, low vol, size
  Fixed income: Term, carry, value (real yield), momentum
  FX:          Carry, momentum, value (PPP)
  Commodities: Carry (roll yield), momentum, value (mean reversion)
```

### Global Macro Systematic

Systematic macro strategies use quantitative signals to take directional positions across global markets based on macroeconomic analysis.

```
Signal categories:

  1. Growth signals:
     - PMI momentum (3-month change in manufacturing PMI)
     - Industrial production growth
     - Employment data surprises
     - Consumer confidence changes
     - Trade: long equities/credit when growth accelerates, short when decelerates

  2. Inflation signals:
     - CPI surprises vs expectations
     - Breakeven inflation rate changes
     - Commodity price momentum as inflation proxy
     - Trade: long TIPS/commodities when inflation rising, long nominals when falling

  3. Policy signals:
     - Central bank rate expectations (OIS forwards)
     - Yield curve slope as policy indicator
     - QE/QT flow data
     - Trade: receive rates when easing expected, pay when tightening

  4. Risk appetite signals:
     - Credit spread momentum
     - VIX term structure (contango vs backwardation)
     - Cross-asset correlation regime
     - Trade: risk-on assets in positive appetite, defensive in negative
```

### Trend-Following Across Assets (CTA)

Managed futures / CTA strategies apply time-series momentum across a diversified basket of futures contracts.

```
Classic CTA implementation:

  Universe: 40-80 liquid futures contracts
    Equities: S&P 500, Euro Stoxx, Nikkei, FTSE, Hang Seng
    Bonds: US 10Y, Bund, JGB, Gilt, Australian 10Y
    FX: EUR, JPY, GBP, AUD, CHF, CAD, MXN, BRL
    Commodities: Crude, Gold, Copper, Corn, Soybeans, Natural Gas

  Signal: Weighted combination of lookbacks
    Fast: 10-20 day exponential moving average crossover
    Medium: 50-100 day trend signal
    Slow: 150-250 day trend signal
    Blend: 25% fast + 50% medium + 25% slow (typical)

  Position sizing:
    For each contract i:
      signal_i = blended trend signal (scaled to [-1, +1])
      vol_i = 20-day exponential realized volatility
      position_i = signal_i * (target_risk_per_contract / vol_i)

    Target risk: equal risk across all contracts
    Typical: 10-15 bps risk per contract, targeting 10-15% portfolio vol

  Rebalancing: daily for signal updates, weekly for full rebalance

  Performance characteristics:
    Sharpe: 0.5-0.8 (diversified multi-asset trend)
    Max drawdown: 15-25%
    Correlation to equities: near zero in normal times, positive in sustained trends
    Crisis alpha: positive returns in prolonged drawdowns (2008: +20-40%)
    Negative returns in choppy, mean-reverting markets
```

### Risk Parity Multi-Asset

Risk parity allocates risk equally across asset classes rather than capital equally.

```
Standard risk parity allocation:

  Asset classes: Equities, Bonds, Commodities, TIPS

  Step 1: Estimate covariance matrix (exponentially weighted, 60-day halflife)
  Step 2: Solve for weights where each asset contributes equal risk
    Risk contribution_i = w_i * (Sigma * w)_i / (w' * Sigma * w)
    Set RC_i = 1/N for all i (equal risk contribution)
  Step 3: Scale to target volatility (typically 10-12%)

  Typical resulting weights (at 10% target vol):
    Equities: 15-25% capital (but ~33% risk contribution)
    Bonds: 50-70% capital (leveraged to match equity risk)
    Commodities: 10-20% capital
    TIPS: 10-20% capital

  Leverage: 1.5-2.5x gross exposure (needed to lever up low-vol assets)

  Bridgewater All Weather: foundational risk parity framework
  Sharpe: 0.5-0.7 historically, with lower drawdowns than 60/40
```

### Portfolio of Strategies

Building a meta-portfolio of systematic strategies to maximize diversification.

```
Strategy allocation framework:

  Available strategies:
    Equity momentum (Sharpe 0.5, vol 15%)
    FX carry (Sharpe 0.7, vol 8%)
    CTA trend (Sharpe 0.6, vol 12%)
    Statistical arb (Sharpe 1.2, vol 6%)
    Volatility selling (Sharpe 0.8, vol 10%)
    Macro systematic (Sharpe 0.5, vol 10%)

  Correlation matrix: key to diversification
    Momentum vs Carry: -0.2 (natural diversifier)
    CTA vs Equity beta: 0.0 (uncorrelated in normal times)
    Vol selling vs CTA: -0.3 (CTA profits in vol spikes)
    Stat arb vs everything: ~0.0 (market neutral)

  Allocation methods:
    1. Equal risk: allocate equal vol budget to each strategy
    2. Max diversification: maximize diversification ratio
    3. Mean-variance: optimize on estimated Sharpe and correlations
    4. Minimum correlation: maximize number of uncorrelated return streams
    5. Kelly criterion: maximize log utility across strategies

  Meta-portfolio Sharpe: 1.0-1.5 (vs 0.5-0.8 for individual strategies)
  Key insight: mediocre strategies combined intelligently beat a single great strategy
```

### Correlation Benefits

```
Diversification math:

  Portfolio of N uncorrelated strategies, each with Sharpe S:
    Portfolio Sharpe = S * sqrt(N)

  With average correlation rho:
    Portfolio Sharpe = S * sqrt(N / (1 + (N-1) * rho))

  Example: 6 strategies, Sharpe 0.5 each, avg correlation 0.1
    Portfolio Sharpe = 0.5 * sqrt(6 / (1 + 5*0.1)) = 0.5 * 2.0 = 1.0

  Implication: adding a mediocre uncorrelated strategy is more valuable
  than improving a correlated strategy's Sharpe

Correlation instability:
  - Correlations increase in crises (diversification fails when needed most)
  - Use stressed correlation matrices for risk budgeting (not average)
  - Conditional correlation: estimate correlation in high-vol regimes separately
  - DCC-GARCH: dynamic conditional correlation model for time-varying estimates
```

## Detailed Methodology

### Signal Combination Framework

```
Combining signals across asset classes:

  1. Normalize each signal within asset class:
     z_i = (signal_i - cross_sectional_mean) / cross_sectional_std
     This ensures comparability across different signal scales

  2. Combine signal types:
     composite_i = w_carry * z_carry_i + w_mom * z_mom_i + w_value * z_value_i
     Typical weights: equal weight or optimize on historical IC

  3. Position sizing:
     raw_position_i = composite_i / vol_i * target_risk
     Constrain: |position_i| <= max_position_limit

  4. Portfolio-level risk scaling:
     portfolio_vol = sqrt(w' * Sigma * w)
     scale_factor = target_vol / portfolio_vol
     final_positions = raw_positions * scale_factor
```

### Regime-Aware Multi-Asset Allocation

```
Regime identification:
  1. Growth-inflation grid: 4 quadrants
     - Rising growth, rising inflation: equities, commodities
     - Rising growth, falling inflation: equities, credit
     - Falling growth, rising inflation: commodities, TIPS (stagflation)
     - Falling growth, falling inflation: bonds, cash (recession)

  2. Signal-based regime classification:
     - Use PMI, yield curve, credit spreads, VIX as regime indicators
     - HMM or threshold-based classification
     - Tilt allocations based on current regime
     - But: regime detection has lag, transitions are noisy

  3. Risk-off detection:
     - Monitor: VIX level + slope, credit spreads, FX carry returns
     - When 2+ indicators flag risk-off: reduce gross exposure by 50%
     - Revert when indicators normalize for 5+ consecutive days
```

### Capacity and Implementation

```
Capacity by strategy type:
  Risk premia (futures):  $5-20B per strategy
  CTA trend following:    $50-100B across industry
  Stat arb equities:      $1-5B per strategy
  FX carry:               $20-50B
  Macro systematic:       $10-30B

Implementation vehicles:
  Futures: most capital-efficient, minimal tracking error, margin-based
  ETFs: simpler, no margin, but tracking error and fees
  Swaps: for OTC risk premia (credit, rates)
  Direct: individual securities (equities, bonds) for stat arb

Transaction cost budget:
  CTA: 0.5-1.5% annually (daily rebalancing, liquid futures)
  Risk premia: 0.3-1.0% annually (monthly rebalancing)
  Stat arb: 2-5% annually (high turnover)
  Budget must be subtracted from gross returns for realistic Sharpe
```

## Quality Gate

Before deploying a multi-asset systematic strategy:

- [ ] Each individual risk premium has academic documentation and economic rationale
- [ ] Backtest covers multiple market regimes (including 2008, 2020, 2022 rate shock)
- [ ] Correlation assumptions stress-tested with crisis-period correlations
- [ ] Leverage is within broker and regulatory limits (Reg T, UCITS, etc.)
- [ ] Margin requirements modeled under stress (exchanges raise margins in vol)
- [ ] Rebalancing frequency justified by turnover-adjusted performance
- [ ] Transaction costs deducted at realistic levels for each instrument
- [ ] Capacity assessed for target AUM (will market impact erode alpha?)
- [ ] Portfolio-level risk controls in place (max drawdown trigger, gross exposure limit)
- [ ] Live monitoring framework ready (drift detection, signal validation, kill switch)
