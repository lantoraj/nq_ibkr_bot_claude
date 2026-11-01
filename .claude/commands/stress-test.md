---
description: Run historical and hypothetical stress test scenarios on a portfolio
---

# /stress-test

## What This Command Does

Runs comprehensive stress tests on a portfolio using historical crisis scenarios, hypothetical shock scenarios, and reverse stress tests. The risk-manager agent quantifies potential losses, identifies vulnerabilities, and recommends mitigating actions.

## When to Use

- You need to understand portfolio behavior under extreme market conditions
- You want to test specific hypothetical scenarios (rate spike, credit crisis, geopolitical event)
- You need to identify the scenarios that would cause maximum portfolio damage (reverse stress test)
- You are preparing risk reports for management or compliance

## How It Works

1. **Portfolio snapshot** — Captures current positions, exposures, and Greeks (for derivatives).
2. **Historical replay** — Applies historical crisis return vectors to the current portfolio.
3. **Hypothetical scenarios** — Models custom shocks to rates, spreads, equities, FX, and vol.
4. **Reverse stress test** — Finds the minimum shock magnitude that breaches risk limits.
5. **Concentration analysis** — Identifies which positions contribute most to stress losses.
6. **Mitigation recommendations** — Suggests hedges or position adjustments to reduce stress vulnerability.

## Example Usage

**Input:**
```
/stress-test multi-asset portfolio: 50% US equities, 20% US bonds,
15% intl equities, 10% commodities, 5% crypto
```

**Output:**
```
## Stress Test Report — Multi-Asset Portfolio

### Historical Scenarios (Portfolio Impact on $10M)
| Scenario                      | Equity   | Bonds    | Intl Eq  | Commod   | Crypto   | Total     |
|-------------------------------|----------|----------|----------|----------|----------|-----------|
| 2008 GFC (Sep-Nov)            | -$1,950K | +$180K   | -$2,100K | -$350K   | N/A      | -$4,220K  |
| 2020 COVID (Feb-Mar)          | -$1,650K | +$240K   | -$1,800K | -$280K   | -$250K   | -$3,740K  |
| 2022 Rate Shock (Jan-Oct)     | -$1,200K | -$320K   | -$1,050K | +$120K   | -$350K   | -$2,800K  |
| 2011 EU Sovereign Crisis      | -$900K   | +$160K   | -$1,350K | -$80K    | N/A      | -$2,170K  |
| 2018 Vol Shock (Feb)          | -$500K   | +$40K    | -$480K   | -$30K    | -$120K   | -$1,090K  |
| 2015 China Devaluation        | -$600K   | +$80K    | -$900K   | -$180K   | -$50K    | -$1,650K  |

### Hypothetical Scenarios
| Scenario                      | Total Impact | Worst Sleeve     |
|-------------------------------|-------------|------------------|
| Rates +200bps                 | -$1,180K    | Bonds (-$640K)   |
| Equities -20%                 | -$1,850K    | US Eq (-$1,000K) |
| Credit spreads +300bps        | -$920K      | Intl Eq (-$450K) |
| USD +10%                      | -$680K      | Intl Eq (-$420K) |
| Oil -40%                      | -$580K      | Commod (-$310K)  |
| Crypto -50%                   | -$250K      | Crypto (-$250K)  |
| Combined: rates+equity shock  | -$2,640K    | Multi-factor     |

### Reverse Stress Test
| Risk Limit              | Limit    | Minimum Shock to Breach         |
|-------------------------|----------|---------------------------------|
| Max drawdown (-15%)     | -$1.5M   | Equities -18% with no bond rally|
| Max monthly loss (-8%)  | -$800K   | Equities -12%, rates +100bps    |
| Liquidity crisis        | N/A      | Crypto positions illiquid first  |

### Vulnerability Analysis
1. **International equities** are the largest stress contributor in 4 of 6
   historical scenarios — FX amplifies losses
2. **Bond-equity correlation** risk: in 2022-type scenario, both legs lose
3. **Crypto** has outsized loss contribution relative to 5% weight
4. **Commodity hedge** partially effective but small allocation limits benefit

### Mitigation Recommendations
1. Add tail risk hedges: buy 3-month 10% OTM SPY puts (cost: ~40bps/quarter)
2. Hedge FX on international equity sleeve (50% hedge ratio)
3. Consider reducing crypto to 2-3% given tail risk contribution
4. Add TIPS to bond sleeve as inflation hedge for rate shock scenario
```

## Related Agents

- **risk-manager** — Primary agent, designs and runs stress scenarios
- **derivatives-analyst** — Computes stress Greeks for options positions
- **portfolio-manager** — Implements portfolio adjustments based on findings
- **fixed-income-analyst** — Models rate and credit stress scenarios
