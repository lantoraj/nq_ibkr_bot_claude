---
name: momentum-strategies
description: "Momentum Strategies. Use when: User wants to build a momentum-based trading strategy; Choosing between time-series and cross-sectional momentum; Designing lookback periods, rebalancing frequency, or volatility scaling."
---

# Momentum Strategies

name: momentum-strategies
description: Momentum strategy design — time-series, cross-sectional, and dual momentum approaches. Use when building momentum-based systems.

## When to Activate

- User wants to build a momentum-based trading strategy
- Choosing between time-series and cross-sectional momentum
- Designing lookback periods, rebalancing frequency, or volatility scaling
- Understanding momentum crashes and how to mitigate them
- Combining momentum with other factors or signals

## First Questions

1. Which asset class and universe (equities, futures, ETFs, FX)?
2. Time-series momentum (absolute returns) or cross-sectional (relative ranking)?
3. What is the target holding period (days, weeks, months)?
4. What is the AUM / capacity requirement?
5. Are you implementing at the individual security or portfolio/sector level?

## Core Concepts

### Time-Series Momentum (Trend-Following)

Time-series momentum (TSMOM) refers to the tendency of an asset's own past returns to predict its future returns. If the asset went up, buy it. If it went down, sell/short it.

- Moskowitz, Ooi, Pedersen (2012): documented TSMOM across 58 liquid futures, spanning equities, bonds, FX, and commodities
- Lookback: 12-month return is the classic signal
- Holding period: 1 month with monthly rebalancing
- Sharpe: approximately 1.0 for diversified futures TSMOM portfolio
- Works across nearly all asset classes and time periods

### Cross-Sectional Momentum (Relative Strength)

Cross-sectional momentum (XSMOM) ranks assets by past returns and goes long winners, short losers.

- Jegadeesh and Titman (1993): formation period 3-12 months, holding period 3-12 months
- Classic: 12-1 month momentum (skip most recent month to avoid short-term reversal)
- Applied within a universe (e.g., rank all S&P 500 stocks)
- Long top decile, short bottom decile
- Sharpe: approximately 0.5-0.7 for US equities (before costs)

### Dual Momentum (Antonacci)

Combines time-series and cross-sectional momentum:

```
Step 1: Compute 12-month return for each asset in universe
Step 2: Rank assets by 12-month return (cross-sectional)
Step 3: For the top-ranked asset(s), check if 12-month return > T-bill rate (time-series filter)
Step 4: If yes, invest in the top-ranked asset
Step 5: If no, move to safe haven (bonds or cash)

Advantage: Avoids holding losers AND avoids long positions in down markets
```

### The Short-Term Reversal Effect

Returns over the past 1 week to 1 month tend to REVERSE, not continue. This is the short-term reversal effect and is the reason the 12-1 momentum signal skips the most recent month.

- Caused by: liquidity provision, overreaction, bid-ask bounce
- Implication: Do NOT include the most recent month in momentum lookback
- Can be exploited as a separate strategy (mean-reversion at short horizons)

## Detailed Methodology

### Lookback Period Selection

The lookback period determines what "momentum" you are measuring:

```
1 month lookback:   Short-term reversal (negative autocorrelation)
2-6 month lookback: Intermediate momentum (positive, moderate)
7-12 month lookback: Classic momentum (strongest, most documented)
13-60 months:       Long-term reversal (value/mean-reversion territory)

Recommended approach:
- Single lookback: 12-1 month (skip last month)
- Blended lookback: Average z-scores of 3m, 6m, 12m momentum
  Blending reduces sensitivity to any single lookback
- Adaptive lookback: Use the lookback with highest recent IC (but overfitting risk)
```

### Momentum Signal Construction

```
Basic momentum signal:
  MOM_i = (Price_i,t-1 / Price_i,t-12) - 1    [skip last month with t-1]

Risk-adjusted momentum (better Sharpe):
  MOM_i = Return_i,12m / Volatility_i,12m

Residual momentum (Blitz, Huij, Martens 2011):
  Step 1: Regress returns on Fama-French factors
  Step 2: Compute cumulative residual return over lookback
  Step 3: Rank by residual momentum
  Advantage: Captures stock-specific momentum, not factor momentum
  Lower crash risk than standard momentum

Sector momentum:
  Compute momentum at sector level, then trade sector ETFs
  Lower turnover, higher capacity, still profitable
```

### Momentum Crashes

Momentum strategies experience rare but severe crashes, typically during market reversals:

**Historical momentum crashes:**
- 1932: Great Depression reversal
- 2001: Dot-com reversal
- 2009: March reversal (momentum lost 40%+ in 2 months)
- 2020: COVID reversal (momentum crashed in April-May)

**Mechanism:** After extended bear markets, past losers rally sharply (short squeeze, risk reversal) while past winners lag. The long-short momentum portfolio gets hit on both legs.

**Crash characteristics:**
- Momentum crashes follow high-volatility, high-dispersion environments
- They are concentrated in the short leg (losers rally more than winners decline)
- They are preceded by momentum strategy drawdowns (negative convexity)

### Crash Mitigation Techniques

```
1. Volatility scaling:
   w_t = target_vol / realized_vol_t
   Scale position size inversely to recent volatility
   Reduces exposure precisely when crash risk is highest
   Improves Sharpe from ~0.5 to ~0.8 for XSMOM

2. Dynamic momentum (conditional):
   Reduce momentum exposure when:
   - Market volatility > 90th percentile
   - Momentum factor has negative recent returns (12-month factor return < 0)
   - Value spread is extreme (momentum vs value divergence)

3. Capped shorts:
   Limit short leg exposure (e.g., 30% of long leg)
   Reduces crash magnitude at cost of some expected return

4. Residual momentum:
   Factor-neutral momentum has much lower crash risk
   Removes systematic market and value exposure from momentum signal

5. Diversification:
   Run momentum across multiple asset classes
   Equity, FX, commodity, bond momentum have low cross-correlation
```

### Position Sizing and Portfolio Construction

```
Cross-sectional momentum portfolio:
  Long: top quintile (or decile) by momentum signal
  Short: bottom quintile (or decile)
  Weighting within quintile: equal weight or volatility-inverse weight
  Rebalance: monthly (align with momentum signal frequency)

Time-series momentum portfolio:
  For each asset i:
    Signal: sign(12m return) or z-score(12m return)
    Position: signal_i * (target_vol / vol_i)
  Aggregate: sum across all assets
  Typical: 20-50 futures contracts for CTA implementation

Sector momentum:
  Rank 11 GICS sectors by 12-month return
  Long top 3, short bottom 3 (or long-only top 3)
  Equal weight or vol-adjusted weight
  Rebalance monthly
```

## Templates / Examples

### Momentum Strategy Backtest Report

```
Strategy: 12-1 Cross-Sectional Momentum (US Large Cap)
Universe: S&P 500 | Rebalance: Monthly | Period: 2000-2024

Portfolio Construction:
  Long: Top quintile (100 stocks, equal weight)
  Short: Bottom quintile (100 stocks, equal weight)

--- Performance ---
Annualized Return (L/S):   8.2%
Annualized Volatility:     16.5%
Sharpe Ratio:              0.50
Max Drawdown:              -52% (2009 crash)
Calmar Ratio:              0.16
Hit Rate (monthly):        55%
Monthly Turnover:          35%

--- With Volatility Scaling ---
Annualized Return (L/S):   9.8%
Annualized Volatility:     12.0%
Sharpe Ratio:              0.82
Max Drawdown:              -28%
Calmar Ratio:              0.35

--- Factor Exposures ---
Market (beta):             0.05 (approximately neutral)
Size (SMB):                0.12 (slight small-cap tilt)
Value (HML):              -0.35 (anti-value, as expected)
Quality (RMW):            -0.10

--- Transaction Cost Analysis ---
Gross Sharpe:              0.82
Round-trip cost (est):     20 bps
Net Sharpe:                0.58
Break-even cost:           55 bps
```

### Momentum Signal Comparison

```
Signal                  | IC    | ICIR  | Sharpe (L/S) | Turnover | Crash Max DD
12-1 price momentum     | 0.035 | 0.22  | 0.50         | 35%      | -52%
Risk-adjusted momentum  | 0.038 | 0.28  | 0.65         | 32%      | -42%
Residual momentum       | 0.032 | 0.30  | 0.72         | 28%      | -25%
Blended (3/6/12m)       | 0.040 | 0.32  | 0.70         | 30%      | -38%
Sector momentum         | 0.028 | 0.18  | 0.45         | 15%      | -30%
```

### Implementation Checklist

```
[ ] Universe defined with liquidity filters (ADV, market cap)
[ ] Lookback period selected (12-1m default, or blended)
[ ] Short-term reversal handled (skip most recent month)
[ ] Volatility scaling applied (target vol / realized vol)
[ ] Portfolio construction rules defined (quintile, decile, N stocks)
[ ] Rebalancing frequency set (monthly for standard momentum)
[ ] Transaction costs estimated and net performance computed
[ ] Crash mitigation in place (vol scaling, capped shorts, or residual)
[ ] Sector and factor neutralization considered
[ ] Capacity analysis performed (check ADV vs position size)
```

## Quality Gate

Before deploying a momentum strategy:

- [ ] Signal has positive IC and Sharpe in out-of-sample period
- [ ] Momentum crash risk is understood and mitigated (volatility scaling at minimum)
- [ ] Transaction costs deducted — net Sharpe remains acceptable (> 0.3)
- [ ] Turnover is manageable for the target universe and AUM
- [ ] Short leg is implementable (borrow availability, cost of borrow)
- [ ] Factor exposures are understood (momentum is anti-value by construction)
- [ ] Lookback period is robust (test 6m, 9m, 12m — results should be directionally similar)
- [ ] Capacity is sufficient for target AUM
- [ ] Rebalancing schedule is practical (monthly for most applications)
- [ ] Drawdown limits and risk controls are defined
