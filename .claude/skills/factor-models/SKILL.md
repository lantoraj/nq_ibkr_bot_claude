---
name: factor-models
description: "Factor Models. Use when: User wants to build a factor-based investment strategy; Decomposing portfolio returns into systematic risk exposures; Constructing custom factors from fundamental or technical data."
---

# Factor Models

name: factor-models
description: Factor model construction and analysis — Fama-French, Carhart, Barra, custom factors. Use when building or analyzing factor-based strategies.

## When to Activate

- User wants to build a factor-based investment strategy
- Decomposing portfolio returns into systematic risk exposures
- Constructing custom factors from fundamental or technical data
- Evaluating factor premia or factor crowding risk
- Building a Barra-style risk model for portfolio construction
- Comparing single-factor (CAPM) to multi-factor frameworks

## First Questions

1. Which asset universe are you targeting (US equities, global, fixed income, multi-asset)?
2. Are you building a risk model or a return-generating alpha model?
3. What is your rebalancing frequency (daily, monthly, quarterly)?
4. Do you have access to point-in-time fundamental data, or are you using price-based factors only?
5. What is the intended holding period of your strategy?

## Core Concepts

### Evolution from CAPM to Multi-Factor

CAPM posits a single market factor explains all cross-sectional return variation. The empirical failure of CAPM led to multi-factor extensions:

- **Fama-French 3-Factor (1993):** Market (MKT-RF), Size (SMB), Value (HML)
- **Carhart 4-Factor (1997):** Adds Momentum (UMD/WML)
- **Fama-French 5-Factor (2015):** Adds Profitability (RMW), Investment (CMA)
- **Barra/MSCI models:** Industry factors + style factors (60+ factors), estimated via cross-sectional regression rather than time-series sorts

### Factor Construction Methodology

**Portfolio Sort Method (Fama-French style):**
1. At each rebalancing date, sort stocks by characteristic (e.g., B/M ratio)
2. Form long-short portfolios (top quintile minus bottom quintile)
3. Compute equal- or value-weighted returns
4. The resulting return series IS the factor

**Cross-Sectional Regression (Barra style):**
1. Standardize factor exposures (z-score across universe)
2. Run cross-sectional regression: R_i = sum(beta_ik * f_k) + epsilon_i
3. The estimated f_k coefficients ARE the factor returns
4. Advantage: handles many correlated factors simultaneously

### Factor Premium Estimation

- Use long historical samples (50+ years for robust estimation)
- Test across geographies and time periods for out-of-sample validity
- Adjust for transaction costs — many factors lose significance after costs
- Account for the Arnott et al. "factor timing" critique: factors may be overvalued at any given time

## Detailed Methodology

### Building a Custom Factor

```
Step 1: Define hypothesis — WHY should this characteristic predict returns?
Step 2: Source point-in-time data (avoid survivorship and look-ahead bias)
Step 3: Compute factor exposures for each security at each rebalancing date
Step 4: Winsorize exposures at 3 standard deviations
Step 5: Neutralize sector and country effects (regression or demeaning)
Step 6: Standardize to z-scores (mean 0, std 1)
Step 7: Construct long-short portfolio (top decile - bottom decile)
Step 8: Evaluate: IC, IC_IR, turnover, capacity, drawdown
```

### Factor Quality Metrics

| Metric | Good Threshold | Excellent Threshold |
|--------|---------------|-------------------|
| Information Coefficient (IC) | > 0.02 | > 0.05 |
| IC Information Ratio (IC_IR) | > 0.10 | > 0.25 |
| Annual Sharpe (long-short) | > 0.3 | > 0.7 |
| Monthly turnover | < 30% | < 15% |
| Hit rate (% positive months) | > 52% | > 55% |

### Factor Crowding Detection

Factor crowding occurs when too much capital chases the same factor exposure, compressing future returns and amplifying drawdowns.

**Signals of crowding:**
- Valuation spread compression (cheap-minus-expensive narrows within factor quintiles)
- Short interest concentration in the short leg
- Factor momentum (recent strong performance attracts flows)
- Pairwise correlation increase among factor-aligned stocks
- Abnormal ETF inflows into factor-tilted products

**Crowding mitigation:**
- Diversify across multiple uncorrelated factors
- Use proprietary factor definitions (non-standard construction)
- Monitor crowding indicators and reduce exposure dynamically
- Blend factors rather than pure-play single-factor portfolios

### Factor Timing

Factor timing is the attempt to dynamically allocate across factors based on macro conditions, valuations, or momentum signals:

- **Macro regime:** Value outperforms in recoveries; Momentum outperforms in trends; Quality outperforms in downturns
- **Valuation timing:** When the value spread (cheap vs expensive within a factor) is wide, the factor tends to perform well going forward
- **Momentum timing:** Use 12-1 month factor return as a timing signal (factor momentum)

Caveat: Factor timing is difficult. Most academic studies find limited out-of-sample evidence. A blend of factors typically dominates timing.

## Templates / Examples

### Fama-French 3-Factor Regression Template

```
Model: R_portfolio - R_f = alpha + beta_MKT * (R_MKT - R_f) + beta_SMB * SMB + beta_HML * HML + epsilon

Interpretation:
- alpha > 0 and statistically significant: genuine skill
- beta_MKT: market exposure (should be ~1 for equity portfolio)
- beta_SMB > 0: small-cap tilt; < 0: large-cap tilt
- beta_HML > 0: value tilt; < 0: growth tilt
- R-squared: fraction of return variance explained by factors
```

### Custom Factor Construction Checklist

```
[ ] Economic rationale documented
[ ] Point-in-time data sourced (no look-ahead)
[ ] Survivorship bias addressed
[ ] Universe defined (liquidity filters, market cap cutoffs)
[ ] Exposures winsorized and standardized
[ ] Sector/country neutralization applied
[ ] Long-short portfolio constructed
[ ] Transaction cost analysis performed
[ ] Out-of-sample test window reserved
[ ] Correlation with known factors measured
[ ] Capacity estimate provided
```

### Factor Decomposition Report Template

```
Portfolio Factor Exposure Report — [Date]

Factor        | Exposure (z) | Factor Return (bps) | Contribution (bps)
Market        | 1.05         | +120                | +126
Size (SMB)    | -0.30        | +45                 | -13.5
Value (HML)   | +0.80        | -30                 | -24.0
Momentum      | +0.15        | +60                 | +9.0
Quality       | +0.50        | +25                 | +12.5
Residual      | —            | —                   | +18.0

Total Portfolio Return: +128.0 bps
Factor-Explained: +110.0 bps | Residual (Alpha): +18.0 bps
```

## Quality Gate

Before deploying a factor model or factor-based strategy, confirm:

- [ ] Factor has economic rationale, not just data-mined statistical significance
- [ ] Premium is robust across geographies, time periods, and market cap segments
- [ ] Factor survives transaction cost deduction (especially for high-turnover factors)
- [ ] Correlation with existing portfolio factors is acceptable (< 0.5 pairwise)
- [ ] Crowding indicators are not at extreme levels
- [ ] Out-of-sample performance is directionally consistent with in-sample
- [ ] Factor exposure can be achieved with sufficient capacity for your AUM
- [ ] Risk model properly attributes return to factor vs residual components
- [ ] Multiple testing adjustment applied if screening many candidate factors
- [ ] Rebalancing frequency matches the factor's alpha decay profile
