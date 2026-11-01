---
description: Decompose portfolio returns by factor exposures and identify unintended bets
---

# /factor-analysis

## What This Command Does

Performs factor exposure analysis on a portfolio, decomposing returns and risk into systematic factor contributions (market, size, value, momentum, quality, volatility, and custom factors). The quant-researcher and portfolio-manager agents collaborate to identify intended and unintended factor bets.

## When to Use

- You want to understand what factors are driving your portfolio returns
- You need to check for unintended factor tilts or crowded exposures
- You are building a factor-neutral portfolio and need to verify neutrality
- You want to attribute past performance to factor vs alpha contributions

## How It Works

1. **Portfolio mapping** — Maps holdings to factor loadings using cross-sectional regression or characteristic-based assignment.
2. **Factor decomposition** — Decomposes portfolio returns into factor and residual (alpha) components.
3. **Exposure analysis** — Quantifies active factor tilts relative to the benchmark.
4. **Crowding assessment** — Checks factor exposures against aggregate market positioning for crowding risk.
5. **Attribution** — Attributes historical returns to each factor and the residual.
6. **Recommendations** — Identifies factor tilts to adjust and hedging trades to neutralize unintended exposures.

## Example Usage

**Input:**
```
/factor-analysis for a US equity long-short portfolio,
benchmark Russell 1000, check for factor crowding
```

**Output:**
```
## Factor Analysis — US Equity Long-Short

### Factor Exposures (Active vs Russell 1000)
| Factor         | Long Book | Short Book | Net   | Benchmark | Active |
|----------------|-----------|-----------|-------|-----------|--------|
| Market (beta)  | 1.05      | 0.92      | 0.13  | 1.00      | +0.13  |
| Size (SMB)     | 0.28      | -0.15     | 0.43  | 0.00      | +0.43  |
| Value (HML)    | 0.35      | 0.02      | 0.33  | 0.00      | +0.33  |
| Momentum (UMD) | 0.18      | -0.42     | 0.60  | 0.00      | +0.60  |
| Quality (QMJ)  | 0.22      | -0.31     | 0.53  | 0.00      | +0.53  |
| Low Vol (BAB)  | -0.08     | 0.12      | -0.20 | 0.00      | -0.20  |

### Return Attribution (Last 12 Months)
| Component      | Contribution | % of Total Return |
|----------------|-------------|-------------------|
| Market         | +1.4%       | 12%               |
| Size           | +2.1%       | 18%               |
| Value          | +1.8%       | 15%               |
| Momentum       | +3.6%       | 31%               |
| Quality        | +2.4%       | 20%               |
| Low Vol        | -0.3%       | -3%               |
| **Alpha**      | **+0.8%**   | **7%**            |
| **Total**      | **+11.8%**  | **100%**          |

### Crowding Assessment
| Factor    | Portfolio Tilt | Hedge Fund Avg | Crowding Risk |
|-----------|---------------|----------------|---------------|
| Momentum  | +0.60         | +0.52          | HIGH          |
| Quality   | +0.53         | +0.41          | MODERATE      |
| Size      | +0.43         | +0.18          | LOW           |
| Value     | +0.33         | +0.25          | LOW           |

WARNING: Momentum exposure (+0.60) is at the 89th percentile of
hedge fund positioning. Risk of crowded unwind during momentum
reversal events.

### Findings
1. Only 7% of returns attributable to alpha — 93% is factor exposure
2. Momentum is the dominant driver and is potentially crowded
3. Net long beta (+0.13) introduces unintended directional risk
4. Quality tilt is appropriate for late-cycle positioning

### Recommendations
- Reduce momentum exposure by 0.20 to bring below crowding threshold
- Hedge residual beta with S&P 500 futures (short ~$2M notional)
- Consider adding low-vol names to long book for diversification
- Monitor momentum factor for reversal signals (momentum crash indicator)
```

## Related Agents

- **quant-researcher** — Co-leads, performs factor regression and crowding analysis
- **portfolio-manager** — Co-leads, translates factor insights into portfolio adjustments
- **risk-manager** — Validates factor exposure limits and concentration
- **algo-strategist** — Designs factor-hedging overlay strategies
