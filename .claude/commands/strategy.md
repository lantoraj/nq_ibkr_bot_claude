---
description: Design a systematic trading strategy from concept to implementation
---

# /strategy

## What This Command Does

Designs a complete systematic trading strategy including signal generation, entry/exit rules, position sizing, and risk management. The algo-strategist agent leads, pulling in quant-researcher for signal validation and risk-manager for risk assessment when needed.

## When to Use

- You have a trading idea or market hypothesis and want to formalize it into a systematic strategy
- You need to define entry signals, exit rules, and position sizing for an existing concept
- You want to evaluate whether a discretionary approach can be systematized
- You are building a new strategy for a specific asset class, timeframe, or market regime

## How It Works

1. **Idea capture** — Parses your strategy description, target asset class, timeframe, and objectives.
2. **Signal design** — Defines the alpha signal(s) driving the strategy, including data inputs, calculation logic, and expected decay profile.
3. **Rule specification** — Produces concrete entry conditions, exit conditions (take-profit, stop-loss, time-based), and position sizing rules.
4. **Risk framework** — Specifies maximum drawdown tolerance, position limits, correlation constraints, and portfolio-level risk budget.
5. **Implementation plan** — Outputs pseudocode or structured logic suitable for backtesting.

The algo-strategist agent orchestrates the process. If the signal requires statistical validation, it delegates to quant-researcher. If risk constraints need formal modeling, it consults risk-manager.

## Example Usage

**Input:**
```
/strategy momentum breakout on US large-cap equities, daily timeframe,
long-only, targeting Sharpe > 1.5 after costs
```

**Output:**
```
## Momentum Breakout Strategy — US Large-Cap Equities

### Signal
- 12-month price momentum (skip last month) ranked across S&P 500
- Entry: Top decile momentum score, confirmed by 20-day volume breakout (> 1.5x average)
- Lookback: 252 trading days for momentum, 20 days for volume confirmation

### Entry Rules
- Buy on next open after signal triggers
- Require ADV > $10M for liquidity filter
- Maximum 30 positions at any time

### Exit Rules
- Stop-loss: 8% trailing from peak price
- Time exit: Rebalance monthly, drop stocks falling below top quartile
- Take-profit: None (let winners run within momentum regime)

### Position Sizing
- Equal risk contribution: size inversely proportional to 20-day realized vol
- Target 15bps portfolio risk per position
- Maximum single position: 5% of NAV

### Risk Framework
- Maximum portfolio drawdown: 15%
- Sector concentration limit: 30% in any single GICS sector
- Beta cap: gross portfolio beta < 1.3
- Correlation to benchmark: monitor, target information ratio > 0.8

### Implementation Notes
- Universe: S&P 500 constituents (point-in-time to avoid survivorship bias)
- Data: Adjusted close prices, volume, GICS sector codes
- Rebalance: Monthly, first trading day
- Estimated turnover: ~150% annually
- Transaction cost assumption: 5bps per side
```

## Related Agents

- **algo-strategist** — Primary agent, designs the strategy architecture
- **quant-researcher** — Validates signal significance and decay characteristics
- **risk-manager** — Reviews risk framework and position limits
- **backtesting-engineer** — Next step after strategy design (use `/backtest`)
