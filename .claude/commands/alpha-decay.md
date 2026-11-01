---
description: Analyze signal half-life, alpha decay curves, and strategy capacity
---

# /alpha-decay

## What This Command Does

Measures how quickly a trading signal loses predictive power over time (alpha decay), estimates signal half-life, analyzes capacity constraints, and recommends optimal trading frequency. The quant-researcher agent leads with rigorous statistical methodology.

## When to Use

- You have a validated signal and need to determine optimal holding period
- You want to understand how crowding or information diffusion erodes alpha
- You need to estimate maximum strategy capacity before market impact erodes returns
- You want to compare decay profiles across multiple signals

## How It Works

1. **Signal construction** — Builds the signal and measures predictive power at multiple forward horizons.
2. **Decay curve** — Plots information coefficient (IC) or return predictability as a function of horizon.
3. **Half-life estimation** — Fits exponential decay model to determine the signal half-life.
4. **Capacity analysis** — Estimates market impact at various AUM levels and determines the capacity ceiling.
5. **Crowding assessment** — Evaluates whether signal decay has accelerated due to factor crowding.
6. **Frequency optimization** — Recommends optimal rebalance frequency balancing alpha capture vs transaction costs.

## Example Usage

**Input:**
```
/alpha-decay analyze decay profile for earnings surprise signal
in US large-caps, determine optimal holding period and capacity
```

**Output:**
```
## Alpha Decay Analysis — Earnings Surprise Signal

### Signal Definition
- Signal: Standardized unexpected earnings (SUE) = (actual - estimate) / std(surprise)
- Universe: S&P 500
- History: 2005-2025 (80 quarterly observations)

### Decay Curve (IC by Holding Period)
| Horizon      | IC     | t-stat | Cumulative Return (L/S) |
|-------------|--------|--------|-------------------------|
| 1 day       | 0.082  | 5.1    | 0.42%                   |
| 1 week      | 0.071  | 4.8    | 1.18%                   |
| 2 weeks     | 0.058  | 4.2    | 1.65%                   |
| 1 month     | 0.043  | 3.4    | 2.14%                   |
| 2 months    | 0.028  | 2.1    | 2.52%                   |
| 3 months    | 0.015  | 1.2    | 2.68%                   |
| 6 months    | 0.004  | 0.3    | 2.71%                   |

### Half-Life
- Estimated half-life: 18 trading days (3.6 weeks)
- 90% of alpha captured within 45 trading days
- Decay model: IC(t) = 0.082 * exp(-0.039t), R-squared = 0.96

### Decay Trend Over Time
| Period       | Half-Life | Peak IC | Interpretation        |
|-------------|-----------|---------|----------------------|
| 2005-2010   | 28 days   | 0.095   | Strong, slow decay    |
| 2010-2015   | 22 days   | 0.088   | Moderate compression  |
| 2015-2020   | 16 days   | 0.078   | Accelerating decay    |
| 2020-2025   | 14 days   | 0.072   | Further compression   |

Signal half-life has compressed by 50% over 20 years, consistent
with increased quant adoption and faster information processing.

### Capacity Analysis
| AUM Level   | Est. Impact (bps) | Net Alpha (ann) | Viable? |
|-------------|-------------------|-----------------|---------|
| $50M        | 2                 | 5.8%            | Yes     |
| $200M       | 5                 | 4.8%            | Yes     |
| $500M       | 11                | 3.2%            | Yes     |
| $1B         | 22                | 1.4%            | Marginal|
| $2B         | 38                | -0.6%           | No      |

Estimated capacity ceiling: ~$800M-$1B

### Optimal Trading Frequency
| Rebalance   | Alpha Captured | Costs (ann) | Net Alpha |
|-------------|---------------|-------------|-----------|
| Daily       | 95%           | 3.2%        | 4.2%      |
| Weekly      | 82%           | 1.4%        | 5.1%      |
| Bi-weekly   | 68%           | 0.8%        | 4.8%      |
| Monthly     | 52%           | 0.4%        | 3.6%      |
| Quarterly   | 22%           | 0.2%        | 1.4%      |

Optimal: Weekly rebalance maximizes net alpha after costs.

### Recommendations
1. Trade weekly, not daily — marginal alpha from daily doesn't justify costs
2. Size strategy at $200-500M for best risk-adjusted returns
3. Monitor half-life quarterly — if it drops below 10 days, reassess viability
4. Combine with other signals to extend effective capacity
```

## Related Agents

- **quant-researcher** — Primary agent, conducts decay and capacity analysis
- **algo-strategist** — Designs execution rules to capture decaying alpha
- **execution-specialist** — Optimizes trading to minimize impact at given capacity
- **backtesting-engineer** — Validates decay estimates with out-of-sample testing
