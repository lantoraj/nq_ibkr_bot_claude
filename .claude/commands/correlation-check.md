---
description: Analyze portfolio correlations, detect regime breaks, and identify hidden exposures
---

# /correlation-check

## What This Command Does

Analyzes cross-asset and within-portfolio correlations to detect hidden risk concentrations, correlation regime changes, and diversification breakdowns. The risk-manager and portfolio-manager agents collaborate to identify when correlation assumptions are breaking down.

## When to Use

- You want to check if your portfolio is truly diversified or has hidden correlation risk
- You need to detect correlation regime shifts (e.g., bonds and equities moving together)
- You want to monitor correlation stability for pairs trading or risk parity strategies
- You are evaluating new positions for correlation impact on the portfolio

## How It Works

1. **Correlation matrix** — Computes rolling and expanding correlation matrices for portfolio constituents.
2. **Regime detection** — Identifies correlation regime changes using change-point detection and rolling window analysis.
3. **Clustering analysis** — Groups assets by correlation similarity to reveal hidden factor structure.
4. **Stress correlation** — Estimates correlation under stress (tail dependence, DCC-GARCH).
5. **Diversification metrics** — Computes diversification ratio, effective number of bets, and marginal risk contribution.
6. **Monitoring dashboard** — Sets up correlation monitoring thresholds and alerts.

## Example Usage

**Input:**
```
/correlation-check for a portfolio of SPY, TLT, GLD, VNQ, EEM, BTC
over the past 3 years, flag any regime breaks
```

**Output:**
```
## Correlation Analysis — Multi-Asset Portfolio

### Current Correlation Matrix (6-Month Rolling)
|     | SPY   | TLT   | GLD   | VNQ   | EEM   | BTC   |
|-----|-------|-------|-------|-------|-------|-------|
| SPY | 1.00  | 0.32  | -0.08 | 0.72  | 0.68  | 0.42  |
| TLT | 0.32  | 1.00  | 0.18  | 0.25  | 0.10  | -0.05 |
| GLD | -0.08 | 0.18  | 1.00  | -0.12 | 0.15  | 0.20  |
| VNQ | 0.72  | 0.25  | -0.12 | 1.00  | 0.55  | 0.35  |
| EEM | 0.68  | 0.10  | 0.15  | 0.55  | 1.00  | 0.48  |
| BTC | 0.42  | -0.05 | 0.20  | 0.35  | 0.48  | 1.00  |

### Regime Break Detection
| Pair      | Current | 3Y Avg | Change | Regime Break? |
|-----------|---------|--------|--------|---------------|
| SPY-TLT   | +0.32   | -0.15  | +0.47  | YES (critical)|
| SPY-BTC   | +0.42   | +0.28  | +0.14  | MONITORING    |
| SPY-VNQ   | +0.72   | +0.68  | +0.04  | No            |
| SPY-EEM   | +0.68   | +0.62  | +0.06  | No            |
| GLD-TLT   | +0.18   | +0.25  | -0.07  | No            |
| EEM-BTC   | +0.48   | +0.32  | +0.16  | MONITORING    |

ALERT: SPY-TLT correlation has flipped from -0.15 (3Y average)
to +0.32. This is the most significant regime break. Traditional
60/40 diversification benefit is severely impaired.

### Correlation Clustering
Cluster analysis reveals 2 dominant groups:
- **Risk-on block**: SPY, VNQ, EEM, BTC (avg intra-cluster corr: 0.54)
- **Diversifiers**: GLD, TLT (avg intra-cluster corr: 0.18)

Effective number of independent bets: 2.8 (out of 6 assets)
Diversification ratio: 1.42 (1.0 = no diversification)

### Stress Correlations (Tail Dependence, 5th Percentile)
| Pair      | Normal Corr | Stress Corr | Convergence |
|-----------|-------------|-------------|-------------|
| SPY-TLT   | +0.32       | +0.55       | Worsens     |
| SPY-VNQ   | +0.72       | +0.88       | Worsens     |
| SPY-EEM   | +0.68       | +0.82       | Worsens     |
| SPY-BTC   | +0.42       | +0.68       | Worsens     |
| GLD-SPY   | -0.08       | -0.22       | Improves    |

In stress, all risk assets converge. Only gold provides genuine
tail diversification.

### Portfolio Impact
- Current portfolio diversification assumes SPY-TLT negative correlation
- With current positive correlation, portfolio vol is 14.2% vs
  expected 11.8% under historical correlation assumptions
- Risk parity weights would shift: increase GLD from current weight,
  reduce SPY and VNQ allocation

### Recommendations
1. Increase gold allocation — only true diversifier in current regime
2. Reduce REITs — adding correlated equity risk without compensation
3. Review bond allocation — positive stock-bond correlation means
   bonds no longer hedge equity risk; consider short-duration or TIPS
4. BTC correlation rising with equities — not the uncorrelated
   asset it was in 2019-2020; size accordingly
5. Set alert: if SPY-TLT correlation exceeds +0.40, trigger
   portfolio rebalance review
```

## Related Agents

- **risk-manager** — Co-leads, detects correlation regime breaks and stress dependence
- **portfolio-manager** — Co-leads, adjusts allocations based on correlation changes
- **quant-researcher** — Provides DCC-GARCH and copula-based correlation models
- **stat-arb-specialist** — Monitors pair correlation stability for stat-arb positions
