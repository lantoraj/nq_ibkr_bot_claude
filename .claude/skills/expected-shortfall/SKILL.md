---
name: expected-shortfall
description: "Expected Shortfall calculation, advantages over VaR, regulatory adoption under FRTB, extreme value theory, and tail dependence modeling. Use when: User needs a coherent risk measure that captures tail losses beyond VaR; Regulatory capital computation under FRTB (Fundamental Review of the Trading Book); Portfolio optimization with tail risk constraints."
---

# Expected Shortfall (CVaR) and Tail Risk Measurement

> Expected Shortfall calculation, advantages over VaR, regulatory adoption under FRTB, extreme value theory, and tail dependence modeling.

## When to Activate

- User needs a coherent risk measure that captures tail losses beyond VaR
- Regulatory capital computation under FRTB (Fundamental Review of the Trading Book)
- Portfolio optimization with tail risk constraints
- Analyzing extreme loss scenarios and tail dependence between assets
- Comparing ES across portfolios for risk budgeting
- Stress testing that requires understanding the full tail distribution

## Core Concepts

### Expected Shortfall Definition

Expected Shortfall at confidence level alpha is the expected loss conditional on the loss exceeding VaR:

- ES_alpha = E[L | L > VaR_alpha]
- Also called Conditional VaR (CVaR), Tail VaR, or Average VaR
- For continuous distributions: ES_alpha = (1/(1-alpha)) * integral from alpha to 1 of VaR_u du
- ES always >= VaR at the same confidence level
- ES is a coherent risk measure (satisfies subadditivity); VaR is not

### Coherent Risk Measures (Artzner et al.)

A risk measure rho is coherent if it satisfies:

1. **Monotonicity**: If X <= Y in all states, then rho(X) >= rho(Y)
2. **Subadditivity**: rho(X + Y) <= rho(X) + rho(Y) — diversification cannot increase risk
3. **Positive homogeneity**: rho(lambda * X) = lambda * rho(X) for lambda > 0
4. **Translation invariance**: rho(X + c) = rho(X) - c

VaR violates subadditivity for non-elliptical distributions. A merged portfolio can have higher VaR than the sum of individual VaRs. ES satisfies all four properties.

### ES for Standard Distributions

**Normal distribution**: ES_alpha = sigma * phi(z_alpha) / (1 - alpha) - mu
- At 97.5%: ES = sigma * phi(1.96) / 0.025 = sigma * 2.338
- At 99%: ES = sigma * phi(2.326) / 0.01 = sigma * 2.665

**Student-t distribution**: ES is larger due to heavier tails
- ES_alpha = (nu + z_alpha^2) / (nu - 1) * f_t(z_alpha) / (1 - alpha) * sigma
- Lower degrees of freedom (nu) produce dramatically larger ES relative to VaR

**Empirical (historical)**: ES = average of all losses beyond the VaR quantile
- If 99% VaR is the 5th worst of 500 observations, ES_99 = average of the 5 worst losses

### Regulatory Shift: VaR to ES (FRTB)

Basel III.1 / FRTB replaces VaR with ES for internal models approach (IMA):

- ES computed at 97.5% confidence (calibrated to approximate 99% VaR under normality)
- Liquidity-adjusted ES: different holding periods for different risk factor categories
  - 10 days: large-cap equities, major FX, interest rates
  - 20 days: small-cap equities, corporate bonds, minor FX
  - 40 days: credit spreads, exotic FX
  - 60 days: certain credit and equity volatility factors
  - 120 days: structured credit, illiquid positions
- Aggregation: ES_liquidity-adjusted = sqrt(sum over j of (ES_j * sqrt(LH_j/10))^2) approximately
- Stressed ES calibrated to worst 12-month period (same concept as stressed VaR)
- P&L attribution test: compare risk-theoretical P&L to hypothetical P&L

## Methodology

### ES Estimation Methods

**Parametric ES**
1. Fit a distribution to return data (normal, Student-t, skewed-t)
2. Compute ES analytically using the closed-form expression for that distribution
3. Best for portfolios with approximately elliptical return distributions
4. Fast but misses complex tail behavior

**Historical ES**
1. Compute portfolio P&L for each historical scenario
2. Sort losses from worst to best
3. Identify the VaR threshold (e.g., 5th worst of 500 for 99%)
4. ES = average of all losses at or beyond the VaR threshold
5. Sample size matters: with 500 days at 99%, ES is the average of only 5 observations — high estimation uncertainty
6. Bootstrap confidence intervals around ES estimate

**Monte Carlo ES**
1. Simulate N scenarios from fitted model (e.g., 100,000 paths)
2. Revalue portfolio under each scenario
3. Sort simulated P&L, compute ES as average of worst (1-alpha)*N losses
4. More stable than historical due to larger sample in the tail
5. Model risk: results depend on assumed stochastic process

### Extreme Value Theory (EVT)

EVT provides a principled framework for modeling the tail beyond available data:

**Generalized Pareto Distribution (GPD)**
- For exceedances over a high threshold u: F_u(x) = 1 - (1 + xi*x/beta)^(-1/xi)
- Shape parameter xi > 0: heavy tails (Pareto-like); xi = 0: exponential tails; xi < 0: bounded tail
- Financial returns typically have xi in range [0.1, 0.4] — heavy tails confirmed
- ES from GPD: ES = VaR/(1-xi) + (beta - xi*u)/(1-xi)

**POT (Peaks Over Threshold) Method**
1. Choose threshold u (typically 90th-95th percentile of losses)
2. Fit GPD to exceedances above u
3. Extrapolate to desired quantile and compute ES
4. Mean excess plot helps select threshold: should be approximately linear above u for GPD fit
5. Advantage: can estimate ES at confidence levels beyond available data (e.g., 99.9%)

### Tail Dependence

Tail dependence measures the probability that two assets experience extreme losses simultaneously:

- Upper tail dependence: lambda_U = lim P(X > F_X^{-1}(u) | Y > F_Y^{-1}(u)) as u->1
- Normal copula: lambda_U = 0 for all rho < 1 — underestimates joint tail risk
- Student-t copula: lambda_U > 0 for rho > -1 and finite df — captures tail dependence
- Clayton copula: lower tail dependence (crashes), no upper tail dependence
- Gumbel copula: upper tail dependence, no lower tail dependence
- For portfolio ES, tail dependence structure matters more than linear correlation

### ES Decomposition and Risk Budgeting

- Component ES: ES_i = w_i * partial(ES)/partial(w_i) — Euler allocation
- Sum of component ES equals total portfolio ES
- Risk contribution: RC_i = Component_ES_i / Total_ES
- Risk budgeting: set target risk contributions and solve for weights
- ES-based optimization: min ES subject to return constraint (linear program for empirical ES)

## Examples

### Historical ES Calculation
```
500 daily P&L observations for a $10M portfolio.
Sorted worst losses: -$620K, -$580K, -$540K, -$490K, -$470K, ...
99% VaR = $470K (5th worst).
99% ES = average(-$620K, -$580K, -$540K, -$490K, -$470K) = $540K.
ES exceeds VaR by $70K (15% higher), capturing the tail severity.
```

### EVT-Based ES at 99.9%
```
Fit GPD to 50 exceedances above the 90th percentile threshold.
Estimated xi = 0.25, beta = $150K, threshold u = $300K.
99.9% VaR (GPD) = $300K + ($150K/0.25)*[(500*0.001/50)^(-0.25) - 1] = $892K.
99.9% ES = $892K/(1-0.25) + ($150K - 0.25*$300K)/(1-0.25) = $1,289K.
```

### FRTB Liquidity-Adjusted ES
```
Equity desk ES(10-day): $2.1M
Credit desk ES(40-day): $1.8M
FX desk ES(10-day): $900K
Liquidity-adjusted ES = sqrt((2.1)^2 + (1.8*sqrt(40/10))^2 + (0.9)^2)
                       = sqrt(4.41 + 12.96 + 0.81) = sqrt(18.18) = $4.26M
```

## Quality Gate

- ES estimates must include confidence intervals (bootstrap or analytical)
- Historical ES requires minimum 5 tail observations; prefer at least 10 for stability
- GPD fit must be validated: Q-Q plot, Anderson-Darling test on exceedances
- Threshold selection for POT must be justified (mean excess plot, stability of xi and beta)
- Tail dependence model must be tested against empirical tail dependence estimates
- ES backtesting: use multinomial test or bootstrap test (ES backtesting is harder than VaR backtesting)
- Regulatory ES must use correct liquidity horizons per FRTB risk factor categories
- Component ES must sum to total ES (verify Euler decomposition numerically)
- Compare parametric, historical, and MC estimates; investigate divergences
- Re-estimate EVT parameters at least quarterly
