---
description: Analyze volatility surfaces, term structure, and skew for trading opportunities
---

# /vol-analysis

## What This Command Does

Performs comprehensive volatility analysis including implied vs realized volatility comparison, surface construction, term structure analysis, skew dynamics, and volatility trading opportunity identification. The volatility-trader agent leads the analysis.

## When to Use

- You want to identify mispriced volatility across strikes or expirations
- You need to analyze the vol term structure for calendar spread opportunities
- You want to understand skew dynamics and their implications
- You need to compare implied vs realized vol for variance trading decisions

## How It Works

1. **Surface construction** — Builds the implied volatility surface from market option prices across strikes and expirations.
2. **Realized vol analysis** — Computes realized volatility using close-to-close, Parkinson, and Yang-Zhang estimators.
3. **Term structure** — Analyzes the volatility term structure shape (contango, backwardation, humps) and historical patterns.
4. **Skew analysis** — Measures put-call skew, risk reversal levels, and butterfly spreads across the surface.
5. **Trading signals** — Identifies opportunities where implied vol diverges significantly from expected realized vol or historical norms.
6. **Risk scenarios** — Models P&L impact of vol surface moves on existing positions.

## Example Usage

**Input:**
```
/vol-analysis SPY volatility surface, identify any term structure
or skew trading opportunities
```

**Output:**
```
## Volatility Analysis — SPY

### Implied vs Realized Snapshot
| Metric           | Value  | Percentile (2Y) |
|------------------|--------|-----------------|
| IV30 (ATM)       | 18.2%  | 42nd            |
| RV20 (C-to-C)    | 14.8%  | 35th            |
| RV20 (Yang-Zhang)| 15.3%  | 38th            |
| IV-RV spread     | +3.4%  | 55th            |
| VIX              | 17.8   | 40th            |
| VVIX             | 92.4   | 48th            |

### Term Structure
| Expiry   | ATM IV | Slope vs Front |
|----------|--------|----------------|
| 1-week   | 14.2%  | —              |
| 1-month  | 18.2%  | +4.0%          |
| 2-month  | 19.1%  | +4.9%          |
| 3-month  | 19.8%  | +5.6%          |
| 6-month  | 20.4%  | +6.2%          |
| 1-year   | 21.1%  | +6.9%          |

Shape: Normal contango. Front month elevated relative to 1-week
due to upcoming FOMC meeting (17 days). Steeper than average in
the 1W-1M segment.

### Skew Analysis (25-delta)
| Expiry   | 25d Put IV | ATM IV | 25d Call IV | RR    | BF    |
|----------|-----------|--------|-------------|-------|-------|
| 1-month  | 22.8%     | 18.2%  | 16.1%       | -6.7% | 1.3%  |
| 3-month  | 23.4%     | 19.8%  | 17.2%       | -6.2% | 0.4%  |
| 6-month  | 24.1%     | 20.4%  | 18.0%       | -6.1% | 0.7%  |

Skew is moderately steep. 1-month 25d risk reversal at -6.7% is
at the 68th percentile — slightly rich for put protection.

### Trading Opportunities

**1. Front-month calendar spread (medium conviction)**
- Sell 1M ATM straddle / Buy 2M ATM straddle
- Rationale: 1M IV elevated by FOMC, expect compression post-event
- Theta: +$12/day initially
- Risk: Large realized move before FOMC

**2. Put spread collar (low conviction)**
- 1M 25d put skew is rich — sell put spreads vs long stock
- Sell 1M 95% put, buy 1M 90% put for credit
- Funds upside via cheap 25d calls

### Historical Context
Current IV30 at 18.2% is near median levels. No extreme dislocation.
Opportunities are tactical around FOMC event, not structural.
```

## Related Agents

- **volatility-trader** — Primary agent, analyzes vol surfaces and identifies opportunities
- **derivatives-analyst** — Assists with precise pricing and Greeks computation
- **options-strategist** — Structures trades based on vol analysis findings
- **risk-manager** — Validates vol trade risk under stress scenarios
