---
description: Analyze options strategies including pricing, Greeks, vol surfaces, and trade structuring
---

# /options-analysis

## What This Command Does

Performs comprehensive options analysis including pricing, Greeks computation, volatility surface construction, strategy structuring, and P&L scenario analysis. The options-strategist and derivatives-analyst agents collaborate to deliver actionable trade recommendations.

## When to Use

- You need to price an option or evaluate a complex spread
- You want to analyze the volatility surface for trading opportunities
- You need Greeks-based risk analysis for an existing options position
- You want to construct an optimal hedge or income strategy using options

## How It Works

1. **Market context** — Captures the underlying, expiration, strikes of interest, and current market conditions.
2. **Vol surface analysis** — Builds or analyzes the implied volatility surface, identifies skew and term structure opportunities.
3. **Strategy construction** — Designs the optimal options structure given your view and risk tolerance.
4. **Greeks profile** — Computes delta, gamma, theta, vega, and higher-order Greeks across the position.
5. **P&L scenarios** — Models P&L at expiration and before expiration under various price and vol scenarios.
6. **Risk assessment** — Identifies worst-case scenarios, margin requirements, and tail risks.

## Example Usage

**Input:**
```
/options-analysis AAPL earnings play, expecting 5% move,
want limited risk, budget $10K premium
```

**Output:**
```
## Options Analysis — AAPL Earnings Play

### Market Context
- AAPL spot: $242.50
- Earnings date: April 24, 2026
- IV30: 38% (vs 22% realized — elevated for earnings)
- Expected move (options-implied): +/- $14.50 (6.0%)

### Recommended Strategy: Long Strangle
- Buy 1x Apr 25 $250 Call @ $4.20
- Buy 1x Apr 25 $235 Put @ $3.80
- Total premium: $800 per strangle
- Position: 12 strangles ($9,600 total, within $10K budget)

### Greeks Profile (Total Position)
| Greek  | Value     | Interpretation                    |
|--------|-----------|-----------------------------------|
| Delta  | +0.04     | Near delta-neutral                |
| Gamma  | +1.44     | Benefits from large moves         |
| Theta  | -$312/day | Time decay cost until expiration  |
| Vega   | +$480     | Long vol — benefits from IV rise  |

### P&L Scenarios at Expiration
| AAPL Price | P&L       | Return    |
|------------|-----------|-----------|
| $260 (+7%) | +$2,400   | +25%      |
| $255 (+5%) | -$3,600   | -37%      |
| $250 (+3%) | -$9,600   | -100%     |
| $242 (flat)| -$9,600   | -100%     |
| $230 (-5%) | -$3,600   | -37%      |
| $225 (-7%) | +$2,400   | +25%      |

### Alternative: Iron Condor (Short Vol View)
If you believe the move will be smaller than implied:
- Sell Apr 25 $255C / Buy $260C
- Sell Apr 25 $230P / Buy $225P
- Net credit: $2.10 per condor
- Max profit: $2,520 (if AAPL stays $230-$255)
- Max loss: $3,480

### Risk Notes
- Strangle loses 100% if move is < 6% — high probability outcome
- IV crush post-earnings will reduce value even with a move
- Consider closing pre-earnings if IV spikes further
```

## Related Agents

- **options-strategist** — Primary agent, constructs option strategies
- **derivatives-analyst** — Prices options, builds vol surfaces, computes Greeks
- **risk-manager** — Validates position risk and margin requirements
- **volatility-trader** — Provides vol surface context and term structure views
