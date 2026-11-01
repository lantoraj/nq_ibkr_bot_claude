---
name: correlation-risk
description: "Regime-dependent correlation, diversification failure, dynamic correlation models, and correlation trading strategies. Use when: User analyzes portfolio diversification and correlation assumptions; Correlation breakdown during market stress events; Dynamic correlation modeling with DCC-GARCH or similar."
---

# Correlation Risk Analysis

> Regime-dependent correlation, diversification failure, dynamic correlation models, and correlation trading strategies.

## When to Activate

- User analyzes portfolio diversification and correlation assumptions
- Correlation breakdown during market stress events
- Dynamic correlation modeling with DCC-GARCH or similar
- Correlation trading strategies (dispersion, correlation swaps)
- Risk model validation where correlation assumptions drive results
- Multi-asset portfolio construction sensitive to correlation estimates

## Core Concepts

### Correlation Measurement

**Pearson Correlation**
- Linear association between two return series: rho = cov(X,Y) / (sigma_X * sigma_Y)
- Assumes bivariate normality for inference — violated by financial returns
- Sensitive to outliers: a single extreme co-movement can dominate the estimate
- Does not capture non-linear dependence or tail dependence

**Rank Correlation (Spearman, Kendall)**
- Spearman: Pearson correlation on ranked data — robust to outliers
- Kendall tau: proportion of concordant vs. discordant pairs — better for small samples
- Both capture monotonic (not just linear) relationships
- Preferred for non-normal distributions and copula calibration

**Rolling Correlation**
- Compute correlation over a trailing window (e.g., 60, 120, 252 days)
- Reveals time-varying nature of correlation
- Window length tradeoff: short = responsive but noisy; long = stable but lagging
- Exponentially weighted correlation: more weight on recent observations, decay factor lambda

### Correlation Dynamics in Crises

The most dangerous property of correlation: it increases precisely when diversification is needed most.

- During calm markets: cross-asset correlations are moderate, diversification works
- During stress: correlations spike toward 1.0 (or -1.0 for safe havens), diversification fails
- Equity correlations: pairwise stock correlations routinely jump from 0.3 to 0.7+ in sell-offs
- Cross-asset: equity-credit correlation spikes (both sell off); equity-Treasury correlation flips negative (flight to quality)
- 2022 anomaly: stocks and bonds fell together — 60/40 portfolio assumption of negative correlation failed
- Correlation asymmetry: higher correlation in down markets than up markets (documented in academic literature)

### Why Correlation Increases in Stress

1. **Common factor dominance**: in crisis, a single "risk-on/risk-off" factor drives all assets
2. **Leverage and forced selling**: margin calls force liquidation across asset classes simultaneously
3. **Information cascading**: panic spreads, investors herd into similar trades
4. **Liquidity withdrawal**: market makers widen spreads on everything, co-movement increases mechanically
5. **Volatility effect**: correlation and volatility are positively linked (conditional correlation rises with vol)

## Methodology

### Dynamic Conditional Correlation (DCC-GARCH)

The DCC model of Engle (2002) captures time-varying correlation:

1. **Step 1 — Univariate GARCH**: fit GARCH(1,1) to each return series to obtain standardized residuals
   - h_it = omega_i + alpha_i * r_{i,t-1}^2 + beta_i * h_{i,t-1}
   - Standardized: epsilon_it = r_it / sqrt(h_it)

2. **Step 2 — Dynamic correlation**: model the correlation of standardized residuals
   - Q_t = (1 - a - b) * Q_bar + a * epsilon_{t-1} * epsilon_{t-1}' + b * Q_{t-1}
   - R_t = diag(Q_t)^{-1/2} * Q_t * diag(Q_t)^{-1/2} (normalize to get correlation matrix)
   - Parameters a and b control correlation dynamics (a = news impact, b = persistence)
   - Q_bar is the unconditional correlation matrix of standardized residuals

3. **Estimation**: two-step quasi-maximum likelihood — first step estimates univariate GARCH, second step estimates DCC parameters

4. **Advantages**: captures time variation, mean-reversion in correlation, parsimonious (2 parameters for any dimension)
5. **Limitations**: symmetric (does not distinguish up/down moves), computationally intensive for large N

### Asymmetric DCC (aDCC)

Extends DCC to capture the asymmetry that correlations increase more in downturns:
- Q_t = (1-a-b)*Q_bar - g*N_bar + a*epsilon_{t-1}*epsilon_{t-1}' + b*Q_{t-1} + g*n_{t-1}*n_{t-1}'
- Where n_t = epsilon_t if epsilon_t < 0, else 0 (captures negative shocks)
- Parameter g captures the asymmetric correlation response to negative returns

### Copula-Based Dependence Modeling

Copulas separate marginal distributions from the dependence structure:

- **Gaussian copula**: no tail dependence — underestimates joint extreme risk
- **Student-t copula**: symmetric tail dependence — better for financial data
- **Clayton copula**: lower (left) tail dependence — captures crash co-movement
- **Time-varying copulas**: fit copula parameters dynamically, similar to DCC approach
- Calibration: use Kendall's tau or maximum likelihood on pseudo-observations

### Correlation Risk in Portfolio Context

**Diversification Ratio**
- DR = (sum of w_i * sigma_i) / sigma_portfolio
- DR = 1 means no diversification (perfect correlation); higher DR = more diversification
- Monitor DR over time; declining DR signals rising correlations

**Effective Number of Bets (ENB)**
- Based on PCA of the portfolio return covariance
- ENB = exp(-sum of p_i * ln(p_i)) where p_i are normalized eigenvalue shares
- Low ENB despite many positions means hidden concentration through correlation

**Correlation Stress Testing**
- Stressed correlation matrix: increase all pairwise correlations by a fixed amount (e.g., +0.3)
- Must ensure the resulting matrix is positive semi-definite (nearest PSD matrix if not)
- Alternatively, use shrinkage: C_stressed = (1-w)*C_current + w*C_crisis
- Compute portfolio risk under stressed correlations

## Examples

### Rolling Correlation Regime Detection
```
SPY-TLT rolling 60-day correlation:
  2019 (calm):     -0.35 (negative — diversification working)
  Mar 2020 (COVID): -0.55 (strongly negative — flight to quality)
  2021 (recovery): -0.20 (weakly negative)
  2022 (inflation): +0.40 (positive — stocks and bonds falling together)
  2023 (normalization): -0.25 (returning to negative)

A 60/40 portfolio assuming -0.30 correlation was severely mispriced in 2022.
Actual 2022 portfolio vol was 40% higher than model predicted due to correlation shift.
```

### DCC-GARCH Fitted Correlation
```
Pair: Bank of America (BAC) vs. JPMorgan (JPM)
DCC parameters: a = 0.03, b = 0.95 (high persistence)
Unconditional correlation: 0.78
Conditional correlation range: 0.55 (calm periods) to 0.95 (crisis periods)
2008 peak conditional correlation: 0.96
2020 COVID peak: 0.93
Current: 0.75

Implication: during stress, these two positions offer almost zero diversification.
Portfolio VaR assuming constant 0.78 correlation underestimates stress losses by 15-20%.
```

### Dispersion Trading Example
```
S&P 500 implied correlation (from index vol vs. component vols): 0.65
Historical realized correlation (trailing 3 months): 0.50
Trade: Sell index straddle, buy single-stock straddles (short correlation).
Profit if realized correlation stays below implied correlation.
Risk: correlation spike event (market crash) causes large loss on short index vol.
Size: limit notional so max loss at correlation = 1.0 is within risk budget.
```

## Quality Gate

- Correlation estimates must use at least 120 observations (approximately 6 months daily data)
- DCC model must be validated: Ljung-Box test on standardized residuals, likelihood ratio test vs. constant correlation
- Stressed correlation matrix must be verified as positive semi-definite
- Portfolio risk under both current and stressed correlation must be reported
- Diversification ratio and ENB must be monitored and reported alongside standard risk metrics
- Correlation asymmetry must be tested: compare up-market vs. down-market correlations
- Copula model selection must be justified: compare Gaussian, t, and Clayton via AIC/BIC
- Tail dependence estimates must accompany linear correlation for any risk assessment
- Correlation assumptions in risk models (VaR, ES) must be stress-tested separately
- Re-estimate dynamic correlation models at least monthly; review for regime changes quarterly
