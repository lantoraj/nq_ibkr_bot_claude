---
description: Scan for pairs trading opportunities using cointegration and mean-reversion analysis
---

# /pairs-scan

## What This Command Does

Scans a universe of securities for cointegrated pairs suitable for statistical arbitrage trading. Tests for cointegration, measures mean-reversion speed, calculates hedge ratios, and identifies current entry opportunities. The stat-arb-specialist agent leads the analysis.

## When to Use

- You want to find market-neutral trading opportunities
- You need to identify cointegrated pairs within a sector or index
- You want to evaluate whether two specific securities are suitable for pairs trading
- You are building a stat-arb portfolio and need candidate pairs

## How It Works

1. **Universe selection** — Defines the scan universe (sector, index, or custom list).
2. **Cointegration testing** — Runs Engle-Granger and Johansen cointegration tests on all candidate pairs.
3. **Mean-reversion metrics** — Calculates half-life, Hurst exponent, and variance ratio for cointegrated pairs.
4. **Hedge ratio estimation** — Computes optimal hedge ratios using OLS, TLS, and Kalman filter methods.
5. **Current signals** — Identifies pairs currently at extreme z-scores (entry candidates).
6. **Risk metrics** — Estimates stop-loss levels, expected holding period, and pair breakdown risk.

## Example Usage

**Input:**
```
/pairs-scan US energy sector large-caps, find top 5
cointegrated pairs with current entry signals
```

**Output:**
```
## Pairs Scan — US Energy Sector

### Universe
Large-cap energy stocks (S&P 500 Energy constituents), 16 names.
120 candidate pairs tested over 3-year lookback.

### Top 5 Cointegrated Pairs
| # | Pair         | EG p-val | Johansen | Half-Life | Hurst |
|---|--------------|----------|----------|-----------|-------|
| 1 | XOM / CVX    | 0.008    | Rank 1   | 14 days   | 0.32  |
| 2 | COP / EOG    | 0.012    | Rank 1   | 18 days   | 0.35  |
| 3 | PXD / FANG   | 0.021    | Rank 1   | 11 days   | 0.28  |
| 4 | SLB / HAL    | 0.034    | Rank 1   | 22 days   | 0.38  |
| 5 | MPC / VLO    | 0.018    | Rank 1   | 9 days    | 0.26  |

### Current Entry Signals
| Pair       | Z-Score | Signal    | Hedge Ratio | Entry Side          |
|------------|---------|-----------|-------------|---------------------|
| XOM / CVX  | +2.14   | SELL pair | 0.82        | Short XOM, Long CVX |
| MPC / VLO  | -1.92   | BUY pair  | 1.15        | Long MPC, Short VLO |
| PXD / FANG | +0.34   | No signal | 0.71        | —                   |
| COP / EOG  | -0.62   | No signal | 0.93        | —                   |
| SLB / HAL  | +1.21   | Monitor   | 1.08        | Approaching entry   |

### Trade Detail — XOM / CVX (Strongest Signal)
- Current spread z-score: +2.14 (entry threshold: 2.0)
- Hedge ratio (Kalman filter): Short 100 XOM / Long 122 CVX
- Expected holding period: 14 days (half-life)
- Stop-loss: z-score > 3.5 or 21 calendar days
- Target: z-score returns to 0.5
- Historical win rate: 68% (n=42 trades since 2022)
- Average profit per trade: 1.8% on capital deployed

### Risk Warnings
- Energy sector pairs can decouple during oil price shocks
- M&A risk for PXD/FANG pair (monitor news flow)
- Correlation regime shifts during macro events (OPEC decisions)
```

## Related Agents

- **stat-arb-specialist** — Primary agent, runs cointegration and mean-reversion analysis
- **quant-researcher** — Assists with statistical testing methodology
- **risk-manager** — Validates pair trade risk and stop-loss adequacy
- **execution-specialist** — Plans simultaneous leg execution to minimize slippage
