---
description: Research and validate alpha signals with statistical rigor
---

# /signal-research

## What This Command Does

Conducts systematic alpha signal research including hypothesis formulation, data requirements, statistical testing, decay analysis, and capacity estimation. The quant-researcher agent leads with rigorous methodology to separate genuine signals from noise.

## When to Use

- You have a hypothesis about a predictive signal and want to test it
- You want to mine alternative data sources for alpha potential
- You need to validate a signal's statistical significance and economic intuition
- You want to understand a signal's decay profile and portfolio capacity

## How It Works

1. **Hypothesis formulation** — Defines the economic rationale, expected relationship, and testable prediction.
2. **Data specification** — Identifies required data sources, frequency, history, and quality requirements.
3. **Signal construction** — Specifies exact calculation methodology, normalization, and cross-sectional vs time-series framing.
4. **Statistical testing** — Runs t-tests, information coefficient analysis, quintile spreads, and Fama-MacBeth regressions.
5. **Robustness checks** — Tests across subperiods, geographies, market regimes, and after controlling for known factors.
6. **Decay and capacity** — Estimates signal half-life and maximum portfolio capacity before alpha erosion.

## Example Usage

**Input:**
```
/signal-research earnings revision momentum as predictor of
future returns in US mid-cap equities
```

**Output:**
```
## Signal Research — Earnings Revision Momentum

### Hypothesis
Stocks with positive analyst earnings revision momentum (3-month
change in consensus EPS estimates) outperform over the subsequent
1-3 months. Economic rationale: analyst herding and anchoring cause
underreaction to fundamental information.

### Signal Construction
- Universe: Russell Midcap Index (point-in-time constituents)
- Signal: 3-month change in FY1 consensus EPS / stock price
- Normalization: Cross-sectional z-score within GICS sector
- Frequency: Weekly signal update, monthly portfolio rebalance

### Statistical Results (2005-2025)
| Metric                      | Value    | Significance |
|-----------------------------|----------|-------------|
| Mean IC (rank correlation)  | 0.048    | t=4.2 ***   |
| IC hit rate                 | 56.3%    | Significant  |
| Long-short quintile spread  | 8.2% ann | t=3.1 ***   |
| After Fama-French 5-factor  | 4.8% ann | t=2.4 **    |
| Sharpe of L/S portfolio     | 1.12     | —           |

### Quintile Analysis (Ann. Returns)
| Q1 (Low) | Q2   | Q3   | Q4   | Q5 (High) | L/S  |
|----------|------|------|------|-----------|------|
| 5.8%     | 8.2% | 9.4% | 11.1%| 14.0%     | 8.2% |

Monotonic quintile spread confirms signal has predictive power
across the full distribution, not just in extremes.

### Robustness
- Subperiod stability: IC positive in 18 of 20 years
- Regime analysis: stronger in trending markets (IC: 0.061)
  vs volatile (IC: 0.032), but positive in both
- Post-2015 performance: signal weakened (IC: 0.038) — possible
  crowding as factor has become well-known

### Decay Profile
- Half-life: ~45 trading days
- Peak IC at 1-month horizon, decays to insignificance by month 4
- Recommend monthly rebalance frequency

### Capacity Estimate
- Estimated capacity: $500M-$1B before significant market impact
- Constraint: mid-cap liquidity limits position sizes
```

## Related Agents

- **quant-researcher** — Primary agent, conducts signal research and validation
- **financial-data-scientist** — Assists with feature engineering and ML-based signal extraction
- **algo-strategist** — Translates validated signals into trading strategies
- **backtesting-engineer** — Validates signal in portfolio context
