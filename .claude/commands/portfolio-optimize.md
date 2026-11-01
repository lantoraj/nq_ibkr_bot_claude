---
description: Optimize portfolio allocation using mean-variance, risk parity, or factor-based methods
---

# /portfolio-optimize

## What This Command Does

Runs portfolio optimization to determine optimal asset weights given your objectives, constraints, and risk tolerance. Supports mean-variance (Markowitz), Black-Litterman, risk parity, minimum variance, and factor-based approaches. The portfolio-manager agent leads the optimization.

## When to Use

- You need to determine target weights for a new portfolio
- You want to rebalance an existing portfolio given updated views or constraints
- You want to compare different optimization approaches (MVO vs risk parity vs equal weight)
- You need to incorporate investor views into a systematic allocation framework

## How It Works

1. **Input parsing** — Captures asset universe, constraints (min/max weights, sector limits, turnover), and optimization objective.
2. **Return estimation** — Uses historical returns, factor models, or Black-Litterman to estimate expected returns and covariance.
3. **Optimization** — Solves the constrained optimization problem for the selected method.
4. **Robustness checks** — Tests sensitivity to input assumptions, runs resampled efficient frontier if applicable.
5. **Trade list** — Generates the rebalance trades from current to target weights.
6. **Risk verification** — Validates the optimized portfolio against risk limits.

## Example Usage

**Input:**
```
/portfolio-optimize risk parity across US equities, international equities,
US bonds, TIPS, gold, REITs. $5M AUM, max 40% in any asset.
```

**Output:**
```
## Portfolio Optimization — Risk Parity

### Methodology
Risk parity: equalize risk contribution from each asset class.
Covariance estimated from 10-year daily returns with exponential
weighting (half-life: 126 days).

### Optimal Weights
| Asset Class       | Ticker | Weight | Risk Contrib | Vol   |
|-------------------|--------|--------|--------------|-------|
| US Equities       | VTI    | 14.2%  | 16.7%        | 18.3% |
| Intl Equities     | VXUS   | 12.8%  | 16.7%        | 19.8% |
| US Bonds          | BND    | 32.5%  | 16.7%        | 5.2%  |
| TIPS              | TIP    | 18.1%  | 16.7%        | 6.8%  |
| Gold              | GLD    | 11.8%  | 16.7%        | 16.4% |
| REITs             | VNQ    | 10.6%  | 16.7%        | 21.2% |

### Portfolio Characteristics
| Metric                | Value   |
|-----------------------|---------|
| Expected return (ann) | 6.8%    |
| Portfolio volatility  | 7.2%    |
| Sharpe ratio (est)    | 0.65    |
| Max historical DD     | -12.4%  |
| Diversification ratio | 2.31    |

### Comparison vs Alternatives
| Method          | Ret   | Vol   | Sharpe | Max DD  |
|-----------------|-------|-------|--------|---------|
| Risk Parity     | 6.8%  | 7.2%  | 0.65   | -12.4%  |
| Equal Weight    | 7.4%  | 9.8%  | 0.55   | -18.2%  |
| Min Variance    | 5.2%  | 5.1%  | 0.67   | -8.6%   |
| 60/40 Benchmark | 7.8%  | 10.4% | 0.56   | -21.3%  |

### Rebalance Trades (from equal weight)
| Asset | Current | Target | Trade     | Shares | Cost Est |
|-------|---------|--------|-----------|--------|----------|
| VTI   | 16.7%   | 14.2%  | Sell $12K | -52    | $6       |
| VXUS  | 16.7%   | 12.8%  | Sell $19K | -340   | $10      |
| BND   | 16.7%   | 32.5%  | Buy $79K  | +1,068 | $40      |
| TIP   | 16.7%   | 18.1%  | Buy $7K   | +63    | $4       |
| GLD   | 16.7%   | 11.8%  | Sell $24K | -128   | $12      |
| VNQ   | 16.7%   | 10.6%  | Sell $31K | -340   | $16      |
```

## Related Agents

- **portfolio-manager** — Primary agent, runs optimization and rebalancing
- **risk-manager** — Validates optimized portfolio against risk limits
- **quant-researcher** — Provides factor-based return estimates if needed
- **execution-specialist** — Plans rebalance trade execution
