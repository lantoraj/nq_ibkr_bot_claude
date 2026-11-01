---
description: Generate a comprehensive portfolio risk report with VaR, stress tests, and exposure analysis
---

# /risk-report

## What This Command Does

Produces a detailed risk report for a portfolio or strategy, covering Value-at-Risk, Expected Shortfall, drawdown analysis, factor exposures, concentration risk, and stress test results. The risk-manager agent leads the analysis.

## When to Use

- You need a snapshot of portfolio risk before making allocation changes
- You want to quantify tail risk and worst-case scenarios
- You need to check risk limit compliance (leverage, concentration, drawdown)
- You are preparing a risk report for stakeholders or compliance

## How It Works

1. **Portfolio ingestion** — Parses current positions, weights, and asset details.
2. **VaR and CVaR** — Calculates parametric, historical, and Monte Carlo VaR at 95% and 99% confidence levels, plus Expected Shortfall.
3. **Factor decomposition** — Breaks down risk by factor exposures (market, size, value, momentum, quality, volatility).
4. **Concentration analysis** — Identifies single-name, sector, geography, and factor concentration risks.
5. **Stress testing** — Runs historical scenarios (2008 GFC, 2020 COVID, 2022 rate shock) and hypothetical scenarios (rate spike, credit spread blowout, liquidity crisis).
6. **Limit check** — Validates all positions and exposures against defined risk limits.

## Example Usage

**Input:**
```
/risk-report for a 60/40 equity-bond portfolio with $10M AUM,
include factor decomposition and stress tests
```

**Output:**
```
## Portfolio Risk Report — 60/40 Equity-Bond
### Portfolio: $10M AUM | Date: 2026-03-14

### Value-at-Risk (1-day)
| Method        | 95% VaR   | 99% VaR   | 99% CVaR  |
|---------------|-----------|-----------|-----------|
| Parametric    | -$68,400  | -$112,300 | -$141,200 |
| Historical    | -$72,100  | -$128,600 | -$159,800 |
| Monte Carlo   | -$70,200  | -$121,400 | -$148,500 |

### Factor Exposure (Equity Sleeve)
| Factor     | Loading | Contribution to Vol |
|------------|---------|---------------------|
| Market     | 0.98    | 82%                 |
| Size       | -0.12   | 3%                  |
| Value      | 0.08    | 2%                  |
| Momentum   | 0.15    | 5%                  |
| Quality    | 0.22    | 6%                  |
| Residual   | —       | 2%                  |

### Stress Scenarios
| Scenario                    | Portfolio Impact |
|-----------------------------|-----------------|
| 2008 GFC (Sep-Nov)          | -$1,420,000     |
| 2020 COVID (Feb-Mar)        | -$980,000       |
| 2022 Rate Shock (Jan-Oct)   | -$1,180,000     |
| Hypothetical: +200bps rates | -$640,000       |
| Hypothetical: credit +300bps| -$520,000       |

### Risk Limit Status
| Limit                | Current | Limit  | Status |
|----------------------|---------|--------|--------|
| Max drawdown (YTD)   | -3.2%   | -15%   | OK     |
| Gross leverage       | 1.0x    | 2.0x   | OK     |
| Single name max      | 4.1%    | 5.0%   | OK     |
| Sector concentration | 24%     | 30%    | OK     |

### Recommendations
1. Equity-bond correlation has risen to 0.35 — consider adding
   commodities or managed futures for diversification
2. Duration risk elevated at 6.2 years — consider shortening
   bond sleeve duration given rate environment
```

## Related Agents

- **risk-manager** — Primary agent, conducts all risk calculations
- **portfolio-manager** — Provides portfolio context and allocation targets
- **derivatives-analyst** — Assists with Greeks-based risk for options positions
