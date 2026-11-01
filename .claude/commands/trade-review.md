---
description: Review trading performance with execution quality analysis and lessons learned
---

# /trade-review

## What This Command Does

Conducts post-trade performance analysis covering execution quality (slippage, timing), strategy performance attribution, risk metrics review, and lessons learned. The backtesting-engineer and risk-manager agents collaborate to provide an objective assessment.

## When to Use

- You want to review performance of recent trades or a trading period
- You need post-trade TCA (transaction cost analysis) for compliance
- You want to identify patterns in execution quality or strategy drift
- You are conducting a periodic (weekly, monthly) performance review

## How It Works

1. **Trade log analysis** — Reviews all trades in the period, grouping by strategy, asset class, and direction.
2. **Execution quality** — Measures slippage vs arrival price, VWAP, and implementation shortfall.
3. **P&L attribution** — Breaks down P&L into alpha, factor, timing, and transaction cost components.
4. **Risk review** — Compares realized risk metrics to targets and limits.
5. **Behavioral analysis** — Identifies patterns like over-trading, disposition effect, or concentration drift.
6. **Lessons and actions** — Produces actionable recommendations for improvement.

## Example Usage

**Input:**
```
/trade-review February 2026 performance for systematic
equity long-short strategy
```

**Output:**
```
## Trade Review — February 2026

### Performance Summary
| Metric              | February  | YTD      | Target   |
|---------------------|-----------|----------|----------|
| Gross return        | +3.2%     | +5.8%    | —        |
| Net return          | +2.6%     | +4.9%    | +12% ann |
| Sharpe (annualized) | 2.1       | 1.8      | > 1.5    |
| Max drawdown        | -1.8%     | -2.1%    | < -10%   |
| Win rate            | 58%       | 56%      | > 52%    |
| Avg winner/loser    | 1.4x      | 1.3x     | > 1.2x   |
| Turnover            | 145% ann  | 138% ann | < 200%   |

### Execution Quality (178 trades)
| Metric                    | Value    | Benchmark | Status |
|---------------------------|----------|-----------|--------|
| Avg slippage vs arrival   | 2.1 bps  | < 3 bps   | GOOD   |
| VWAP slippage             | 0.8 bps  | < 2 bps   | GOOD   |
| Implementation shortfall  | 3.4 bps  | < 5 bps   | GOOD   |
| Fill rate                 | 94%      | > 90%     | GOOD   |
| Dark pool hit rate        | 28%      | > 20%     | GOOD   |

### P&L Attribution
| Component           | Contribution | % of Gross |
|---------------------|-------------|------------|
| Alpha (stock-level) | +1.8%       | 56%        |
| Momentum factor     | +0.9%       | 28%        |
| Quality factor      | +0.4%       | 13%        |
| Market beta residual| +0.3%       | 9%         |
| Transaction costs   | -0.6%       | -19%       |
| Financing costs     | -0.2%       | -6%        |
| **Net**             | **+2.6%**   | **100%**   |

### Risk Metrics
| Metric              | Realized | Target  | Status  |
|---------------------|----------|---------|---------|
| Gross leverage      | 1.8x     | < 2.5x  | OK      |
| Net exposure        | +12%     | +/- 20% | OK      |
| Single name max     | 3.8%     | < 5%    | OK      |
| Sector concentration| 22%      | < 30%   | OK      |
| Correlation to SPY  | 0.15     | < 0.30  | OK      |

### Notable Trades
| Trade         | P&L    | Notes                          |
|---------------|--------|--------------------------------|
| Long NVDA     | +$82K  | Earnings beat, held through    |
| Short PARA    | +$45K  | M&A premium faded as expected  |
| Long CRWD     | -$38K  | Stopped out on sector rotation |
| Short TSLA    | -$31K  | Short squeeze, exited at stop  |

### Lessons and Actions
1. **Alpha generation strong** — 56% of gross P&L from stock selection
2. **Transaction costs high** — 19% drag; review trade frequency,
   consider widening entry/exit bands by 0.25 sigma
3. **Short book** contributing negative alpha (-0.4%) — review
   short selection methodology
4. **TSLA short** violated position sizing rules temporarily —
   tighten pre-trade position limit checks
```

## Related Agents

- **backtesting-engineer** — Co-leads, provides quantitative performance analysis
- **risk-manager** — Co-leads, reviews risk metric compliance
- **execution-specialist** — Provides TCA analysis and execution quality metrics
- **portfolio-manager** — Reviews allocation drift and rebalancing effectiveness
