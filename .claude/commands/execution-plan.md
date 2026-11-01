---
description: Plan trade execution with optimal scheduling, venue selection, and TCA targets
---

# /execution-plan

## What This Command Does

Designs an execution plan for trading a position, including order scheduling (TWAP, VWAP, implementation shortfall), venue selection, market impact estimation, and transaction cost analysis targets. The execution-specialist agent optimizes for minimal execution cost.

## When to Use

- You need to execute a large order and want to minimize market impact
- You want to compare execution strategies (TWAP vs VWAP vs aggressive)
- You need pre-trade TCA estimates for compliance or best-execution documentation
- You are executing a portfolio rebalance with multiple simultaneous trades

## How It Works

1. **Order analysis** — Assesses order size relative to ADV, spread, and intraday volume profile.
2. **Impact estimation** — Models expected market impact using square-root and linear impact models.
3. **Strategy selection** — Recommends TWAP, VWAP, implementation shortfall, or other strategies based on urgency and size.
4. **Venue analysis** — Evaluates lit exchanges, dark pools, and crossing networks for optimal routing.
5. **Schedule design** — Produces a time-sliced execution schedule with participation rate targets.
6. **TCA framework** — Sets benchmarks and defines post-trade TCA metrics to measure execution quality.

## Example Usage

**Input:**
```
/execution-plan buy 500,000 shares MSFT over today,
low urgency, minimize market impact
```

**Output:**
```
## Execution Plan — Buy 500,000 MSFT

### Order Context
| Parameter          | Value                          |
|--------------------|--------------------------------|
| Stock              | MSFT ($415.20)                 |
| Order size          | 500,000 shares ($207.6M)       |
| ADV (20-day)       | 22.4M shares                   |
| % of ADV           | 2.23%                          |
| Avg spread         | $0.01 (0.2bps)                 |
| Intraday vol       | 12bps                          |
| Urgency            | Low                            |

### Recommended Strategy: VWAP
Given low urgency and moderate size (2.2% ADV), VWAP execution
over the full trading day minimizes market impact while tracking
volume patterns.

### Expected Costs
| Component          | Estimate (bps) | Estimate ($)   |
|--------------------|----------------|----------------|
| Spread cost        | 0.1            | $20,760        |
| Market impact      | 1.8            | $37,368        |
| Timing risk        | 0.5            | $10,380        |
| Commission         | 0.3            | $6,228         |
| **Total expected** | **2.7**        | **$56,088**    |

### Execution Schedule
| Time Slice      | Volume % | Shares  | Participation |
|-----------------|----------|---------|---------------|
| 09:30 - 10:00   | 12%      | 60,000  | 4.5%          |
| 10:00 - 11:00   | 14%      | 70,000  | 3.8%          |
| 11:00 - 12:00   | 10%      | 50,000  | 3.2%          |
| 12:00 - 13:00   | 8%       | 40,000  | 3.0%          |
| 13:00 - 14:00   | 10%      | 50,000  | 3.2%          |
| 14:00 - 15:00   | 16%      | 80,000  | 3.5%          |
| 15:00 - 15:30   | 14%      | 70,000  | 4.0%          |
| 15:30 - 16:00   | 16%      | 80,000  | 4.2%          |

### Venue Routing
| Venue            | Target % | Rationale                      |
|------------------|----------|--------------------------------|
| Primary (NYSE)   | 40%      | Price discovery, stability     |
| Dark pools       | 30%      | Reduced information leakage    |
| Crossing networks| 15%      | Midpoint execution             |
| Other lit venues | 15%      | Best price competition         |

### TCA Benchmarks
- Primary: VWAP (target < 2bps slippage vs full-day VWAP)
- Secondary: Implementation shortfall vs arrival price
- Interval: Measure slippage per 30-min bucket
```

## Related Agents

- **execution-specialist** — Primary agent, designs execution strategies
- **market-microstructure** — Provides liquidity and order flow analysis
- **risk-manager** — Assesses execution risk and timing risk
- **portfolio-manager** — Coordinates multi-order rebalance execution
