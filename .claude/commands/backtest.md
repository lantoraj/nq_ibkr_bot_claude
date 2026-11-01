---
description: Backtest a trading strategy with rigorous validation and overfitting checks
---

# /backtest

## What This Command Does

Runs a comprehensive backtest of a trading strategy including walk-forward analysis, out-of-sample validation, Monte Carlo simulation, and overfitting diagnostics. The backtesting-engineer agent ensures methodological rigor and flags common pitfalls.

## When to Use

- You have a defined strategy and need to validate it against historical data
- You want to check if backtest results are robust or likely overfit
- You need performance metrics (Sharpe, Sortino, max drawdown, Calmar) with confidence intervals
- You want to compare multiple strategy variants or parameter sets

## How It Works

1. **Setup validation** — Checks the strategy definition for completeness, flags missing stop-losses, undefined position sizing, or ambiguous rules.
2. **Data requirements** — Specifies the historical data needed, checks for survivorship bias, point-in-time compliance, and corporate action adjustments.
3. **Walk-forward design** — Splits data into in-sample and out-of-sample windows. Minimum 3 out-of-sample periods required.
4. **Execution simulation** — Models realistic fills with slippage, commission, and market impact estimates.
5. **Overfitting diagnostics** — Runs deflated Sharpe ratio, combinatorial cross-validation, and parameter stability analysis.
6. **Report generation** — Produces performance summary, drawdown analysis, risk metrics, and robustness assessment.

## Example Usage

**Input:**
```
/backtest momentum breakout strategy on S&P 500, 2010-2024,
monthly rebalance, 5bps transaction costs
```

**Output:**
```
## Backtest Report — Momentum Breakout Strategy

### Data & Setup
- Universe: S&P 500 (point-in-time constituents, survivorship-bias free)
- Period: Jan 2010 — Dec 2024 (15 years, 180 monthly observations)
- Walk-forward: 5 windows, 24-month in-sample / 12-month out-of-sample
- Transaction costs: 5bps per side, market-on-open fills

### Performance Summary (Out-of-Sample Aggregate)
| Metric              | Strategy | Benchmark (SPY) |
|---------------------|----------|-----------------|
| CAGR                | 14.2%    | 11.8%           |
| Sharpe Ratio        | 1.32     | 0.89            |
| Sortino Ratio       | 1.87     | 1.15            |
| Max Drawdown        | -18.4%   | -33.7%          |
| Calmar Ratio        | 0.77     | 0.35            |
| Annual Turnover     | 142%     | —               |
| Net of Costs Return | 12.8%    | —               |

### Overfitting Diagnostics
- Deflated Sharpe Ratio: 1.08 (significant at 5% level)
- In-sample vs out-of-sample Sharpe decay: 22% (acceptable, < 40% threshold)
- Parameter stability: momentum lookback robust across 9-15 month range
- Monte Carlo (1000 paths): 5th percentile Sharpe = 0.74

### Risk Events
- COVID drawdown (Feb-Mar 2020): -14.2% (strategy), -33.7% (benchmark)
- 2022 rate shock: -11.8% (strategy), -18.1% (benchmark)

### Verdict
Strategy shows statistically significant alpha with acceptable parameter
stability. Recommend paper trading for 3 months before live deployment.
```

## Related Agents

- **backtesting-engineer** — Primary agent, runs validation and diagnostics
- **risk-manager** — Reviews drawdown profiles and tail risk
- **quant-researcher** — Assists with statistical significance testing
- **algo-strategist** — Provides strategy definition to backtest
