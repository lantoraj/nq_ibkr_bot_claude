---
description: Calculate optimal position sizes using Kelly criterion, volatility targeting, or risk budgeting
---

# /position-size

## What This Command Does

Calculates optimal position sizes for trades or portfolio allocations using Kelly criterion, volatility targeting, risk parity, or fixed-risk methods. The risk-manager agent ensures sizes respect risk limits and account for correlation with existing positions.

## When to Use

- You have a trade idea and need to determine the right position size
- You want to size positions based on signal conviction and volatility
- You need to calculate Kelly-optimal sizing with practical fractional Kelly adjustment
- You want to add a position and need to assess its marginal risk impact

## How It Works

1. **Trade parameters** — Captures entry price, stop-loss, expected return, win probability, and volatility.
2. **Sizing methods** — Computes position size under multiple frameworks for comparison.
3. **Portfolio context** — Adjusts sizing for correlation with existing positions and marginal risk contribution.
4. **Risk limit check** — Validates that the proposed size respects all portfolio risk limits.
5. **Scenario analysis** — Models P&L impact at various position sizes under different outcomes.
6. **Final recommendation** — Provides a recommended size with rationale.

## Example Usage

**Input:**
```
/position-size long NVDA trade, entry $920, stop $850,
target $1050, win rate 60%, portfolio $5M, current 70% invested
```

**Output:**
```
## Position Sizing — Long NVDA

### Trade Parameters
| Parameter         | Value                           |
|-------------------|---------------------------------|
| Entry price       | $920.00                         |
| Stop-loss         | $850.00 (-7.6%)                 |
| Target            | $1,050.00 (+14.1%)              |
| Win probability   | 60%                             |
| Risk/reward ratio | 1.86:1                          |
| 20-day realized vol| 42% annualized                 |
| Portfolio NAV     | $5,000,000                      |
| Current invested  | 70% ($3,500,000)                |
| Available capital | 30% ($1,500,000)                |

### Sizing Methods Compared
| Method              | Size ($)   | % of NAV | Shares | Risk ($) |
|---------------------|-----------|----------|--------|----------|
| Full Kelly          | $680,000  | 13.6%    | 739    | $51,680  |
| Half Kelly          | $340,000  | 6.8%     | 370    | $25,840  |
| Quarter Kelly       | $170,000  | 3.4%     | 185    | $12,920  |
| Fixed risk (1% NAV) | $657,000  | 13.1%    | 714    | $50,000  |
| Fixed risk (0.5%)   | $329,000  | 6.6%     | 358    | $25,000  |
| Vol target (15%)    | $328,000  | 6.6%     | 357    | —        |
| Max position limit  | $250,000  | 5.0%     | 272    | $19,000  |

### Kelly Criterion Calculation
- Edge = (0.60 * 14.1%) - (0.40 * 7.6%) = 5.42%
- Kelly fraction = Edge / Odds = 5.42% / 14.1% = 38.4% of bankroll
- Full Kelly: $1,920,000 (too aggressive, not recommended)
- Practical Kelly (1/3 Kelly on available capital): $340,000

### Portfolio Context
| Metric                      | Before Trade | After (Half Kelly) |
|-----------------------------|-------------|-------------------|
| Gross exposure              | 70%          | 76.8%              |
| Tech sector weight          | 22%          | 28.8%              |
| Largest position             | 4.1%         | 6.8%               |
| Portfolio beta               | 1.02         | 1.06               |
| Correlation to existing book| —            | 0.62               |
| Marginal VaR contribution   | —            | $18,200/day        |

### Risk Limit Compliance
| Limit               | After Trade | Limit  | Status  |
|---------------------|-------------|--------|---------|
| Single position max  | 6.8%        | 5.0%   | BREACH  |
| Sector concentration | 28.8%       | 30%    | Warning |
| Gross leverage       | 0.77x       | 2.0x   | OK      |
| Portfolio beta       | 1.06        | 1.3    | OK      |

### Recommendation
**Quarter Kelly: $170,000 (185 shares, 3.4% of NAV)**

Rationale:
1. Half Kelly ($340K, 6.8%) breaches the 5% single-position limit
2. Quarter Kelly stays within all risk limits
3. Tech sector at 25.4% (below 30% limit) with quarter Kelly
4. Risk per trade: $12,920 (0.26% of NAV) — conservative and appropriate
5. If conviction increases after initial price action, can scale in
   another $80K at confirmed breakout level

### Scenario Analysis (at Quarter Kelly)
| Outcome            | Probability | P&L      | Portfolio Impact |
|--------------------|-------------|----------|-----------------|
| Full target hit    | 35%         | +$26,085 | +0.52%           |
| Partial (half move)| 25%         | +$13,043 | +0.26%           |
| Scratch (breakeven)| 15%         | $0       | 0%               |
| Stop-loss hit      | 25%         | -$12,920 | -0.26%           |
| Expected value     | —           | +$8,456  | +0.17%           |
```

## Related Agents

- **risk-manager** — Primary agent, validates sizing against risk limits
- **algo-strategist** — Provides signal conviction for Kelly inputs
- **portfolio-manager** — Evaluates marginal portfolio impact
- **execution-specialist** — Plans execution for the sized order
