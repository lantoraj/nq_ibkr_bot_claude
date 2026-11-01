---
name: var-models
description: "Parametric, historical simulation, and Monte Carlo VaR. Confidence levels, holding periods, backtesting, regulatory requirements, and known limitations. Use when: User asks about VaR calculation for a portfolio or single position; Risk reporting requires VaR numbers at specific confidence levels; Backtesting existing VaR models for accuracy."
---

# Value at Risk Models

> Parametric, historical simulation, and Monte Carlo VaR. Confidence levels, holding periods, backtesting, regulatory requirements, and known limitations.

## When to Activate

- User asks about VaR calculation for a portfolio or single position
- Risk reporting requires VaR numbers at specific confidence levels
- Backtesting existing VaR models for accuracy
- Regulatory capital calculations under Basel III/IV
- Comparing VaR methodologies for a given portfolio composition
- Evaluating holding period assumptions for different asset classes

## Core Concepts

### Three VaR Approaches

**Parametric (Variance-Covariance) VaR**
Assumes returns follow a known distribution (typically normal). For a portfolio with value W, mean return mu, and standard deviation sigma:

- VaR(alpha) = W * (mu - z_alpha * sigma)
- For 99% confidence: z = 2.326
- For 95% confidence: z = 1.645
- Requires covariance matrix estimation for multi-asset portfolios
- Fast computation but fails with non-linear positions (options) and fat tails
- Delta-normal approach: linearize option positions using delta
- Delta-gamma approach: include second-order terms for better accuracy with options

**Historical Simulation VaR**
Uses actual historical returns without distributional assumptions:

- Collect T historical return observations
- Revalue portfolio under each historical scenario
- Sort P&L outcomes and take the (1-alpha)*T-th worst loss
- No parametric assumptions — captures fat tails, skewness naturally
- Ghosting problem: extreme events enter and leave the window abruptly
- Age-weighted historical simulation (BRW): exponentially decay older observations
- Filtered historical simulation: scale returns by current GARCH volatility estimate before resampling

**Monte Carlo VaR**
Simulate risk factor paths from a fitted stochastic model:

- Fit marginal distributions to each risk factor (e.g., GBM, jump-diffusion, GARCH)
- Model dependence structure (correlation matrix, copulas)
- Generate N simulated scenarios (typically 10,000-100,000)
- Revalue portfolio under each scenario using full repricing
- Take the (1-alpha)*N-th worst loss from the simulated P&L distribution
- Most flexible: handles non-linear payoffs, complex dependence, path-dependent instruments
- Computationally expensive; convergence depends on N

### Confidence Levels and Holding Periods

- Regulatory VaR: 99% confidence, 10-day holding period (Basel)
- Internal risk: often 95% or 99%, 1-day holding period
- Square-root-of-time scaling: VaR_T = VaR_1 * sqrt(T) — valid only under i.i.d. assumption
- For mean-reverting or trending processes, sqrt(T) scaling is inaccurate
- Actual 10-day VaR should use 10-day overlapping or non-overlapping returns when data permits

### Covariance Estimation

- Sample covariance: unbiased but noisy for large portfolios (N >> T problem)
- Exponentially weighted (EWMA/RiskMetrics): lambda = 0.94 (daily), more responsive to recent data
- GARCH(1,1): conditional variance h_t = omega + alpha * r_{t-1}^2 + beta * h_{t-1}
- Shrinkage estimators (Ledoit-Wolf): shrink sample covariance toward structured target
- Factor models: reduce dimensionality, e.g., PCA-based covariance

## Methodology

### VaR Backtesting

Backtesting validates whether the VaR model produces the correct number of exceptions (actual losses exceeding VaR).

**Kupiec Test (Unconditional Coverage)**
- Null hypothesis: exception rate equals (1 - confidence level)
- Under H0, number of exceptions X ~ Binomial(T, 1-alpha)
- Likelihood ratio test: LR_uc = -2 * ln[(1-p)^(T-x) * p^x / (1-x/T)^(T-x) * (x/T)^x]
- LR_uc ~ chi-squared(1) under H0
- Basel traffic light: green (0-4 exceptions at 99%/250 days), yellow (5-9), red (10+)

**Christoffersen Test (Conditional Coverage)**
- Tests both correct coverage AND independence of exceptions
- Exceptions should not cluster — consecutive VaR breaches indicate model failure
- LR_cc = LR_uc + LR_ind, where LR_ind tests serial independence
- LR_cc ~ chi-squared(2)
- Clustering of exceptions suggests volatility dynamics are not captured

**Additional Backtesting Approaches**
- Berkowitz test: tests entire forecast distribution, not just the quantile
- Duration-based tests: analyze time between exceptions
- Traffic light approach per Basel: multiplier increases from 3x to 4x based on exception count

### Regulatory VaR (Basel Framework)

- Market risk capital = max(VaR_{t-1}, m_c * avg(VaR_60)) + specific risk charge
- Multiplier m_c starts at 3, increases based on backtesting performance
- Stressed VaR (sVaR): VaR calculated over a 12-month stress period
- Capital charge includes both current VaR and sVaR components
- FRTB (Basel III.1): shifting from VaR to Expected Shortfall for internal models

### Implementation Steps

1. Define risk factors (equity prices, rates, FX, spreads, vols)
2. Map portfolio positions to risk factors
3. Estimate risk factor distribution (choose VaR method)
4. Revalue portfolio under scenarios (full repricing or approximation)
5. Aggregate P&L distribution, extract VaR quantile
6. Decompose VaR by desk, asset class, risk factor (component VaR, incremental VaR)
7. Backtest and validate regularly

## Examples

### Parametric VaR for Equity Portfolio
```
Portfolio value: $10M
Daily portfolio sigma: 1.5%
99% 1-day VaR = $10M * 2.326 * 0.015 = $348,900
95% 1-day VaR = $10M * 1.645 * 0.015 = $246,750
10-day 99% VaR (sqrt scaling) = $348,900 * sqrt(10) = $1,103,338
```

### Historical Simulation with 500 Days
```
Collect 500 daily P&L observations for the portfolio.
Sort from worst to best.
99% VaR = 5th worst loss (500 * 0.01 = 5).
If 5th worst is -$420,000, then 1-day 99% VaR = $420,000.
```

### Component VaR Decomposition
```
Total portfolio VaR: $500K
Component VaR (equities): $320K (64%)
Component VaR (fixed income): $130K (26%)
Component VaR (FX): $50K (10%)
Sum of component VaR = total VaR (property of Euler decomposition).
Marginal VaR identifies which positions contribute most to total risk.
```

## Quality Gate

- VaR model must pass Kupiec unconditional coverage test at 95% significance
- Christoffersen independence test must not reject at 95% significance
- Backtesting window: minimum 250 trading days (1 year)
- Exception count within Basel green zone for regulatory VaR
- Compare across all three methods; if results diverge significantly (>30%), investigate portfolio non-linearity
- Stressed VaR must be computed over an appropriate stress window capturing the worst 12-month period
- Document all assumptions: distribution, holding period scaling, covariance estimation method
- Component VaR must sum to total VaR (verify Euler decomposition)
- Review and recalibrate quarterly or after significant market regime changes
