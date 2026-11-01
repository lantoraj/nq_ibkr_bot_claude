---
description: Design hedging strategies for portfolio risk or single-name exposure
---

# /hedging-plan

## What This Command Does

Designs a comprehensive hedging strategy to reduce specific portfolio risks, covering instrument selection (options, futures, swaps), hedge ratio calculation, cost analysis, and ongoing management rules. The derivatives-analyst and risk-manager agents collaborate on optimal hedge construction.

## When to Use

- You want to hedge market, sector, or factor exposure in your portfolio
- You need to protect against a specific tail risk event
- You want to compare hedging approaches (options vs futures vs swaps)
- You need to hedge currency, interest rate, or commodity exposure

## How It Works

1. **Risk identification** — Quantifies the specific risk to be hedged (directional, volatility, correlation, tail).
2. **Instrument selection** — Evaluates hedging instruments and selects the most cost-effective approach.
3. **Hedge ratio** — Calculates the optimal hedge ratio (delta, beta, or regression-based).
4. **Cost analysis** — Estimates upfront cost, carry cost, and expected drag on returns.
5. **Scenario analysis** — Models hedge effectiveness across bull, bear, and stress scenarios.
6. **Management rules** — Defines rebalance triggers, roll schedules, and hedge removal criteria.

## Example Usage

**Input:**
```
/hedging-plan hedge $20M US equity portfolio against
a 15%+ drawdown over the next 6 months
```

**Output:**
```
## Hedging Plan — Tail Risk Protection

### Risk Profile
- Portfolio: $20M US large-cap equities (beta: 1.05 to SPY)
- Risk: Drawdown exceeding 15% over 6 months
- Historical probability: ~8% in any 6-month period
- Current VIX: 14.8 (cheap protection environment)

### Hedging Alternatives Compared
| Strategy               | Cost (ann) | Max Loss | Upside Cap | Complexity |
|------------------------|-----------|----------|------------|------------|
| 1. Put spread          | 1.2%      | -15%     | None       | Low        |
| 2. Put spread collar   | 0.3%     | -15%     | +12%       | Medium     |
| 3. VIX call spread     | 0.8%      | ~-18%    | None       | Medium     |
| 4. Managed futures     | 0.5%      | Variable | None       | High       |
| 5. Dynamic delta hedge | 0.6%      | -12%     | Reduced    | High       |

### Recommended: Put Spread (Strategy 1)
Best balance of protection, cost, and simplicity.

#### Structure
- Buy 10x SPY Sep 2026 $375 Puts (90% strike) @ $8.40
- Sell 10x SPY Sep 2026 $340 Puts (82% strike) @ $3.20
- Net debit: $5.20 per spread ($52,000 total)
- Cost as % of portfolio: 0.26% (0.52% annualized)

#### Hedge Ratio
- Portfolio beta to SPY: 1.05
- Notional per SPY put: $41,500
- Contracts needed: 10 spreads (covering ~$415K each)
- Effective coverage: $4.15M of downside (scaled to beta)

#### Payoff Scenarios
| SPY Move  | Portfolio (Unhedged) | Hedge P&L  | Net Result  |
|-----------|---------------------|------------|-------------|
| +15%      | +$3.15M             | -$52K      | +$3.10M     |
| +5%       | +$1.05M             | -$52K      | +$998K      |
| Flat      | $0                  | -$52K      | -$52K       |
| -10%      | -$2.10M             | +$48K      | -$2.05M     |
| -15%      | -$3.15M             | +$298K     | -$2.85M     |
| -20%      | -$4.20M             | +$298K     | -$3.90M     |
| -30%      | -$6.30M             | +$298K     | -$6.00M     |

#### Management Rules
- Roll 30 days before expiration if protection still needed
- Remove hedge if VIX spikes above 35 (sell puts into fear)
- Rebalance hedge ratio quarterly as portfolio beta drifts
- Consider upgrading to full puts if VIX drops below 12

### Alternative: Put Spread Collar (Strategy 2)
If you want near-zero-cost protection and can accept capped upside:
- Same put spread as above
- Sell 10x SPY Sep 2026 $465 Calls (112% strike) @ $4.80
- Net cost: $0.40 per contract ($4,000 total, near zero-cost)
- Trade-off: upside capped at +12%
```

## Related Agents

- **derivatives-analyst** — Co-leads, prices hedging instruments and computes Greeks
- **risk-manager** — Co-leads, identifies risks to hedge and validates effectiveness
- **options-strategist** — Assists with complex option hedge structures
- **portfolio-manager** — Integrates hedges into overall portfolio framework
