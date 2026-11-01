---
description: Assess macroeconomic outlook and cross-asset market impact
---

# /macro-outlook

## What This Command Does

Generates a macroeconomic outlook covering growth, inflation, monetary policy, and cross-asset implications. The fx-strategist and commodities-analyst agents collaborate to cover currency, commodity, and global macro dimensions, producing actionable portfolio positioning guidance.

## When to Use

- You need to understand the current macro regime and its market implications
- You want to assess how rate expectations, inflation, or growth data affect your portfolio
- You need a cross-asset view covering equities, bonds, FX, and commodities
- You are positioning for a macro event (central bank meeting, employment report, CPI)

## How It Works

1. **Regime assessment** — Classifies the current macro environment (growth/inflation quadrant, monetary policy stance).
2. **Data analysis** — Reviews key economic indicators (PMI, employment, CPI, yields, credit spreads).
3. **Central bank outlook** — Assesses rate expectations, forward guidance, and balance sheet policy.
4. **Cross-asset implications** — Maps macro view to expected performance across asset classes.
5. **FX outlook** — Analyzes currency dynamics, carry, and macro-driven FX flows.
6. **Commodity outlook** — Covers energy, metals, and agricultural commodities supply-demand dynamics.
7. **Portfolio positioning** — Recommends asset allocation tilts based on the macro outlook.

## Example Usage

**Input:**
```
/macro-outlook current US and global macro environment,
implications for multi-asset portfolio positioning
```

**Output:**
```
## Macro Outlook — March 2026

### Regime Classification
- US: Late-cycle expansion, above-trend growth, sticky inflation
- Europe: Early recovery, improving PMIs, ECB easing cycle
- China: Policy-driven stabilization, property sector still dragging

### Key Indicators
| Indicator         | Current | Trend    | Signal        |
|-------------------|---------|----------|---------------|
| US ISM Mfg PMI    | 52.4    | Rising   | Expansion     |
| US Core CPI (YoY) | 3.1%    | Flat     | Sticky        |
| US 10Y yield      | 4.35%   | Rising   | Hawkish       |
| US HY spread      | 340bps  | Stable   | No stress     |
| EU Composite PMI  | 51.8    | Rising   | Recovery      |
| China Caixin PMI  | 50.2    | Flat     | Stagnation    |
| DXY               | 104.2   | Rising   | USD strength  |
| Gold              | $2,180  | Rising   | Haven bid     |
| Brent crude       | $82     | Stable   | Range-bound   |

### Monetary Policy
- **Fed**: On hold at 4.75%. Market pricing 1 cut by Dec 2026.
  Inflation stickiness argues for higher-for-longer.
- **ECB**: Mid-easing cycle, rate at 2.75%. Expect 2 more cuts.
- **BOJ**: Gradual normalization, next hike expected Q2 2026.

### Cross-Asset Implications
| Asset Class       | View      | Rationale                         |
|-------------------|-----------|-----------------------------------|
| US Equities       | Neutral   | Earnings OK but valuations rich   |
| Intl Dev Equities | Overweight| Cheaper valuations, ECB easing    |
| EM Equities       | Underweight| USD strength headwind            |
| US Treasuries     | Underweight| Inflation sticky, supply heavy   |
| IG Credit         | Neutral   | Carry OK, spreads fair            |
| HY Credit         | Underweight| Spreads tight for late cycle     |
| Gold              | Overweight| Hedge for policy uncertainty      |
| Oil               | Neutral   | OPEC+ supply discipline vs demand |
| USD               | Overweight| Rate differential supports       |
| EUR               | Neutral   | ECB cuts offset by recovery       |
| JPY               | Underweight| BOJ still behind the curve       |

### Portfolio Positioning Recommendations
1. Tilt toward international developed markets (Europe, Japan)
2. Reduce duration — favor short-to-intermediate bonds
3. Add gold and commodities as inflation hedge
4. Maintain quality bias in equities (high ROE, low leverage)
5. Hedge EM exposure for USD strength scenario
```

## Related Agents

- **fx-strategist** — Co-leads, covers currency and macro-driven FX analysis
- **commodities-analyst** — Co-leads, covers commodity supply-demand dynamics
- **portfolio-manager** — Translates macro views into allocation changes
- **fixed-income-analyst** — Provides yield curve and credit analysis
- **risk-manager** — Stress-tests portfolio against macro scenarios
