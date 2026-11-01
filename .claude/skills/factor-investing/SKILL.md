---
name: factor-investing
description: "Factor investing and smart beta strategies — systematic exposure to return drivers. Use when: User is building factor-based portfolios (value, momentum, quality, low-vol, size); Designing smart beta strategies or evaluating factor ETFs; Analyzing factor crowding, timing, or cycle dynamics."
---

# Factor Investing

> Factor investing and smart beta strategies — systematic exposure to return drivers.

## When to Activate

- User is building factor-based portfolios (value, momentum, quality, low-vol, size)
- Designing smart beta strategies or evaluating factor ETFs
- Analyzing factor crowding, timing, or cycle dynamics
- Constructing multi-factor portfolios and managing factor interactions
- Evaluating implementation costs and capacity constraints of factor strategies

## Core Concepts

### What Are Factors?

Factors are persistent, systematic drivers of returns across asset classes. The academic canon:

| Factor | Seminal Paper | Long/Short Return | Rationale |
|--------|--------------|-------------------|-----------|
| **Market** | Sharpe (1964) | ~6% equity premium | Compensation for systematic risk |
| **Value** | Fama-French (1993) | ~3-5% historically | Distress risk, behavioral overreaction |
| **Size** | Fama-French (1993) | ~2-3% (weakened) | Illiquidity, neglect premium |
| **Momentum** | Jegadeesh-Titman (1993) | ~6-8% (gross) | Behavioral underreaction, herding |
| **Quality** | Novy-Marx (2013), Asness (2019) | ~3-4% | Mispricing of earnings quality |
| **Low Volatility** | Frazzini-Pedersen (2014) | ~3-4% (BAB) | Leverage constraints, lottery preference |

### Factor Construction

Long-short factors:
1. Rank stocks on the characteristic (e.g., B/P for value)
2. Form quintile or decile portfolios (cross-sectionally within a universe)
3. Go long top quintile, short bottom quintile
4. Weight by equal-weight or value-weight within each leg

Long-only smart beta:
1. Start from a broad benchmark (e.g., Russell 1000)
2. Tilt weights toward desired factor exposure
3. Apply constraints (sector neutrality, turnover, tracking error)

### Factor Definitions in Practice

**Value**: Book-to-Price, Earnings Yield (E/P), EBITDA/EV, CF/P, Sales/Price. Composite signals (multi-metric) are more robust than any single measure.

**Momentum**: 12-month return minus the most recent month (12-1 momentum). The last month is excluded to avoid short-term reversal contamination. Typical holding period: 3-12 months.

**Quality**: Gross profitability (GP/Assets), ROE, earnings stability, low leverage, low accruals. AQR's QMJ factor combines profitability, growth, safety, and payout.

**Low Volatility**: Realized volatility (trailing 1-3 years), beta, or idiosyncratic volatility. BAB (Betting Against Beta) is the levered/de-levered formulation from Frazzini-Pedersen.

**Size**: Market capitalization. Small-cap premium has been weak post-publication. Survives mainly in micro-caps and in interaction with other factors (small-cap value).

## Methodology

### Step 1: Factor Signal Construction

```python
import pandas as pd
import numpy as np

def compute_value_signal(fundamentals):
    """Composite value signal from multiple metrics."""
    signals = pd.DataFrame()
    signals['bp'] = fundamentals['book_value'] / fundamentals['market_cap']
    signals['ep'] = fundamentals['earnings'] / fundamentals['market_cap']
    signals['cfp'] = fundamentals['cash_flow'] / fundamentals['market_cap']

    # Cross-sectional z-score each metric
    for col in signals.columns:
        signals[col] = (signals[col] - signals[col].mean()) / signals[col].std()

    # Composite: equal-weight average of z-scores
    return signals.mean(axis=1)

def compute_momentum_signal(prices, lookback=252, skip=21):
    """12-1 month momentum."""
    total_return = prices.pct_change(lookback)
    recent_return = prices.pct_change(skip)
    return total_return - recent_return

def compute_quality_signal(fundamentals):
    """Profitability-based quality."""
    gp_a = fundamentals['gross_profit'] / fundamentals['total_assets']
    roe = fundamentals['net_income'] / fundamentals['book_value']
    accruals = (fundamentals['net_income'] - fundamentals['cash_flow']) / fundamentals['total_assets']
    # Z-score and combine
    signals = pd.DataFrame({'gpa': zscore(gp_a), 'roe': zscore(roe), 'accruals': -zscore(accruals)})
    return signals.mean(axis=1)
```

### Step 2: Portfolio Formation

```python
def form_factor_portfolio(signal, returns, n_quantiles=5, weighting='equal'):
    """
    Sort stocks into quantiles based on signal, compute long-short returns.
    """
    quantiles = signal.groupby(signal.index.get_level_values('date')).transform(
        lambda x: pd.qcut(x, n_quantiles, labels=False, duplicates='drop')
    )

    long_mask = quantiles == (n_quantiles - 1)
    short_mask = quantiles == 0

    if weighting == 'equal':
        long_ret = returns[long_mask].groupby('date').mean()
        short_ret = returns[short_mask].groupby('date').mean()
    elif weighting == 'value':
        # Value-weight within each leg
        pass

    factor_return = long_ret - short_ret
    return factor_return
```

### Step 3: Multi-Factor Portfolio Construction

```python
def multi_factor_portfolio(signals_dict, sigma, risk_aversion=1.0,
                           sector_neutral=True, max_active_weight=0.02):
    """
    Combine multiple factor signals into a single portfolio.

    Approaches:
    1. Signal blending: average z-scores, then optimize
    2. Portfolio blending: optimize each factor separately, average weights
    3. Integrated optimization: optimize with all factor tilts simultaneously
    """
    import cvxpy as cp

    # Approach 1: Signal blending (preferred — avoids cancellation)
    composite_signal = sum(signals_dict.values()) / len(signals_dict)

    n = len(composite_signal)
    w = cp.Variable(n)
    w_bench = np.ones(n) / n  # equal-weight benchmark

    # Maximize factor exposure subject to risk constraints
    objective = cp.Maximize(composite_signal.values @ w)
    constraints = [
        cp.sum(w) == 1,
        w >= 0,
        cp.norm(w - w_bench, 'inf') <= max_active_weight,  # position limit
        cp.quad_form(w - w_bench, sigma) <= te_budget**2,   # TE constraint
    ]

    if sector_neutral:
        for sector_mask in sector_masks:
            constraints.append(
                cp.sum(w[sector_mask]) == cp.sum(w_bench[sector_mask])
            )

    prob = cp.Problem(objective, constraints)
    prob.solve()
    return w.value
```

### Step 4: Factor Timing (Use with Caution)

Factor timing attempts to vary factor exposures based on macro or valuation signals. Evidence is mixed:

```python
def factor_valuation_signal(factor_returns, lookback=60):
    """
    Factor valuation spread: compare current value spread
    to historical average. Wide spreads -> overweight value.
    """
    # Value spread: median P/E of cheap quintile vs expensive quintile
    # When spread is wide (cheap stocks are very cheap), value factor is attractive
    pass

def macro_factor_timing(macro_data):
    """
    Macro-based factor rotation:
    - Early cycle (recovery): small cap, value, high beta
    - Mid cycle (expansion): momentum, quality
    - Late cycle (slowdown): quality, low vol, defensive
    - Recession: low vol, quality, bonds
    """
    pass
```

Arnott et al. (2019) show factor timing based on valuation spreads has modest efficacy. Most practitioners use fixed strategic factor weights with limited tactical adjustment.

### Step 5: Factor Crowding Analysis

```python
def detect_crowding(factor_signal, short_interest, fund_flows):
    """
    Crowding indicators:
    1. Factor valuation spread compression (cheaper than usual = less crowded)
    2. Pairwise correlation of factor stocks (high = crowded)
    3. Short interest concentration in short-leg stocks
    4. AUM growth in factor ETFs/funds
    5. Factor return autocorrelation turning negative (reversal = crowding)
    """
    pass
```

Crowding matters because:
- Crowded factors are vulnerable to rapid unwinds (quant crisis of August 2007)
- Transaction costs increase as many managers trade the same signals
- Alpha decays as the factor becomes well-known (publication effect)

## Examples

### Evaluating Factor ETF Exposure

```python
# Regress ETF returns on Fama-French 5 factors + momentum
import statsmodels.api as sm

ff_factors = pd.read_csv('F-F_Research_Data_5_Factors_2x3_daily.csv')
etf_returns = pd.read_csv('MTUM_returns.csv')  # iShares Momentum ETF

merged = etf_returns.merge(ff_factors, on='date')
X = merged[['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'Mom']]
y = merged['ETF_excess']

model = sm.OLS(y, sm.add_constant(X)).fit()
# Check: MTUM should have high Mom loading, modest market beta
```

### Implementation Cost Analysis

```python
def factor_turnover_analysis(signal, rebalance_freq='monthly'):
    """
    Key cost metrics for factor strategies:
    - One-way turnover per rebalance
    - Estimated market impact (higher for small-cap, momentum)
    - Net-of-cost factor premium
    """
    # Momentum: 80-100% annual one-way turnover (expensive)
    # Value: 20-40% annual turnover (cheap)
    # Quality: 15-30% annual turnover (cheapest)
    # Low-vol: 25-40% annual turnover (moderate)
    pass
```

Novy-Marx and Velikov (2016) show that many published anomalies disappear after realistic transaction costs. Momentum is especially vulnerable.

## Quality Gate

- [ ] Factor signals use point-in-time data — no look-ahead bias in fundamentals
- [ ] Cross-sectional signals are sector/industry neutralized where appropriate
- [ ] Momentum signal excludes the most recent month (reversal contamination)
- [ ] Multi-metric composites used rather than single-metric signals
- [ ] Transaction costs and turnover estimated realistically (especially for momentum)
- [ ] Factor crowding risk assessed — check valuation spreads and strategy AUM
- [ ] Out-of-sample and out-of-region tests performed (US factor ≠ global factor)
- [ ] Factor interactions checked — value and momentum are negatively correlated (beneficial)
- [ ] Capacity constraints estimated for small-cap factor strategies
- [ ] Reporting includes both gross and net-of-cost factor returns
- [ ] Compared against simple market-cap benchmark over the full cycle (including drawdowns)
