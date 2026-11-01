---
name: monte-carlo-simulation
description: "Monte Carlo Simulation for Strategy Evaluation. Use when: Estimating confidence intervals for strategy performance metrics (Sharpe, drawdown, CAGR); Assessing ruin probability and worst-case drawdown distributions; Stress testing strategy robustness through path simulation."
---

# Monte Carlo Simulation for Strategy Evaluation

## When to Activate
- Estimating confidence intervals for strategy performance metrics (Sharpe, drawdown, CAGR)
- Assessing ruin probability and worst-case drawdown distributions
- Stress testing strategy robustness through path simulation
- Evaluating parameter sensitivity via randomized perturbation
- Building realistic performance expectations beyond single-path backtests

## Core Concepts

### Why Monte Carlo?

**Problem with Single-Path Backtests:**
- A backtest is ONE realization of a stochastic process
- Different market conditions would have produced different results
- Single-path metrics (Sharpe, max drawdown) are point estimates with wide confidence intervals
- Monte Carlo generates MANY plausible paths, revealing the distribution of outcomes

**Key Insight:** A strategy with a 1.5 Sharpe ratio and 15% max drawdown in backtest could have a 40% max drawdown with 10% probability. Without Monte Carlo, you would not know this.

### Bootstrap Methods

**Standard Bootstrap (IID):**
```
Method:
1. Take the strategy's realized daily returns: [r1, r2, ..., rN]
2. Resample WITH replacement to create synthetic return series of same length
3. Calculate metrics (Sharpe, drawdown, CAGR) on synthetic series
4. Repeat 5,000-10,000 times
5. Result: distribution of each metric

Assumptions:
- Returns are independent and identically distributed
- Preserves the marginal distribution (mean, variance, skewness, kurtosis)
- BREAKS: autocorrelation structure, volatility clustering

Appropriate when: strategy has no significant autocorrelation in returns
```

**Block Bootstrap (Preserves Autocorrelation):**
```
Method:
1. Divide return series into blocks of length L
2. Resample blocks with replacement
3. Concatenate blocks to create synthetic series

Block length selection:
- Too short: destroys autocorrelation (same as IID bootstrap)
- Too long: too few blocks, poor resampling
- Optimal L ≈ T^(1/3) for stationary data (Politis & Romano)
- For daily data with 1000 observations: L ≈ 10 days
- Or use automatic block length selection (Politis & White, 2004)

Stationary bootstrap: random block lengths (geometric distribution)
- More robust than fixed block length
- Mean block length is the parameter to set
```

**Circular Block Bootstrap:**
```
Wraps data around so the last observation connects to the first
Ensures every observation can appear at any position in the synthetic series
Preferred for mean-reverting strategies where position in the cycle matters
```

### Path Simulation for P&L

**Parametric Simulation:**
```
Assume return distribution (normal, t, or skewed-t):
1. Estimate distribution parameters from historical returns
   - mean (mu), std (sigma), skewness, kurtosis
   - For heavy tails: use Student-t with estimated degrees of freedom
2. Generate N simulated return paths
3. Convert to P&L paths: cumulative product of (1 + r_t)
4. Calculate metrics on each path

Normal distribution:
r_t ~ N(mu, sigma^2)
Underestimates tail risk (crypto and equities have fat tails)

Student-t distribution:
r_t ~ t(df, mu, sigma)
Better captures fat tails; df=4-6 is typical for daily equity returns
df=3-4 for crypto (fatter tails)

Skewed-t distribution:
Adds skewness parameter; best for strategies with asymmetric returns
```

**Regime-Switching Simulation:**
```
More realistic: model returns as coming from 2+ regimes

Example (2-state model):
State 1 (calm): mu=0.05%, sigma=0.8%, prob(staying)=0.97
State 2 (volatile): mu=-0.10%, sigma=2.5%, prob(staying)=0.90

Transition matrix:
P = [[0.97, 0.03],
     [0.10, 0.90]]

Simulation:
1. At each time step, draw regime from Markov chain
2. Draw return from regime-specific distribution
3. This captures volatility clustering and regime changes
4. Much more realistic than IID or single-distribution approaches
```

### Confidence Intervals for Metrics

**Sharpe Ratio Confidence Interval:**
```
SE(SR) = sqrt((1 + SR^2/2) / T)  (for normal returns)

For T=252 (1 year), SR=1.0:
SE = sqrt((1 + 0.5) / 252) = 0.077
95% CI: [1.0 - 1.96*0.077, 1.0 + 1.96*0.077] = [0.85, 1.15]

For T=252, SR=0.5:
SE = sqrt((1 + 0.125) / 252) = 0.067
95% CI: [0.37, 0.63]

Key insight: Sharpe ratio is imprecisely estimated from short samples.
1 year of data gives ±0.15 precision at best.
5 years needed for ±0.07 precision.

Monte Carlo improvement: bootstrap directly estimates CI without
normality assumption, incorporating skewness and kurtosis effects.
```

**Maximum Drawdown Distribution:**
```
Max drawdown is NOT well-estimated from a single backtest path.

Bootstrap approach:
1. Generate 10,000 synthetic return paths (bootstrap or parametric)
2. Calculate max drawdown for each path
3. Sort drawdowns: empirical distribution

Typical results for a Sharpe 1.0 strategy (5 years daily):
- Backtest max drawdown: 12%
- Bootstrap median max drawdown: 14%
- Bootstrap 90th percentile: 22%
- Bootstrap 99th percentile: 35%

The 12% backtest drawdown was LUCKY.
With 10% probability, drawdown could exceed 22%.
Size positions for the 90th percentile, not the backtest maximum.
```

### Drawdown Distribution Estimation

**Analytical Approximation (Grossman-Zhou):**
```
For a strategy with Sharpe ratio S and volatility sigma:
Expected max drawdown ≈ sigma * sqrt(2 * ln(T)) / S  (rough approximation)

Better: use the exact distribution from Monte Carlo simulation
Plot histogram of max drawdowns across all simulated paths
Report percentiles: 50th, 75th, 90th, 95th, 99th
```

**Drawdown Duration:**
```
Also simulate:
- Maximum drawdown duration (time from peak to recovery)
- Average drawdown duration
- Frequency of drawdowns exceeding X%

Drawdown duration is often more painful than depth:
- 20% drawdown recovered in 2 months: manageable
- 10% drawdown lasting 18 months: psychologically devastating
- Monte Carlo reveals the distribution of both depth and duration
```

### Ruin Probability

**Definition:** Probability that the strategy's cumulative P&L drops below a specified threshold (e.g., losing 50% of capital).

```
Simulation approach:
1. Define ruin threshold (e.g., -50% from initial capital)
2. Simulate 10,000 P&L paths over the investment horizon
3. Count paths that breach the ruin threshold
4. Ruin probability = breaching paths / total paths

Example:
Strategy: Sharpe 1.0, vol 15%, 5-year horizon
Simulated paths: 10,000
Paths hitting -50%: 85
Ruin probability: 0.85%

With leverage:
2x leverage: Sharpe 2.0 (same), vol 30%, paths hitting -50%: 1,250 (12.5%)
3x leverage: Sharpe 3.0 (same), vol 45%, paths hitting -50%: 3,400 (34%)

Insight: leverage increases Sharpe but DRAMATICALLY increases ruin probability
The optimal leverage (Kelly) maximizes geometric growth, not Sharpe
```

### Parameter Sensitivity Analysis

**Randomized Parameter Perturbation:**
```
Method:
1. Take optimal parameters from backtest
2. Add random noise to each parameter: p_new = p_optimal * (1 + epsilon)
   where epsilon ~ N(0, sigma_perturbation)
3. Run backtest with perturbed parameters
4. Repeat 1,000+ times
5. Distribution of performance under parameter uncertainty

sigma_perturbation choices:
- 5%: tests local sensitivity
- 10%: tests moderate robustness
- 20%: tests broad robustness

Results interpretation:
- If 90% of perturbations are profitable: robust
- If 50% of perturbations are profitable: fragile
- If performance variance is high: sensitive to parameter choice (overfit)
```

## Methodology

### Monte Carlo Workflow
1. **Choose simulation method** — bootstrap (nonparametric) or parametric (distribution-based)
2. **Validate assumptions** — check for autocorrelation, fat tails, regime changes
3. **Generate simulated paths** — minimum 5,000 paths for stable estimates; 10,000+ for tail quantiles
4. **Calculate metrics per path** — Sharpe, max drawdown, CAGR, max drawdown duration, ruin probability
5. **Build distributions** — histograms, CDFs, percentile tables for each metric
6. **Extract confidence intervals** — report median and 5th/95th percentile bounds
7. **Stress test** — repeat with adverse assumptions (higher vol, fatter tails, lower returns)

### Simulation Design Decisions
```
Number of simulations:
- 1,000: sufficient for mean estimates, not for tail quantiles
- 5,000: adequate for 95th percentile estimates
- 10,000+: needed for 99th percentile and ruin probability estimates
- Check convergence: run twice, compare results

Path length:
- Match the intended investment horizon
- If deploying for 3 years: simulate 3-year paths
- Also simulate longer paths (10 years) for ruin analysis

Return frequency:
- Match the strategy's rebalance frequency
- Daily returns for daily strategies
- Monthly returns for monthly rebalance strategies
```

### Combining Bootstrap with Walk-Forward
```
Enhanced validation:
1. Run walk-forward optimization to get OOS return series
2. Bootstrap the OOS returns (not IS returns!)
3. Calculate confidence intervals on OOS-based simulations
4. This gives the most realistic estimate of future performance

Key: never bootstrap IS returns — they are biased by optimization
Only OOS returns provide unbiased estimates for bootstrapping
```

## Examples

### Example 1: Drawdown Risk Assessment
```
Strategy backtest results:
- CAGR: 18%
- Volatility: 12%
- Sharpe: 1.50
- Max drawdown: 8%
- Backtest period: 5 years

Monte Carlo (10,000 paths, block bootstrap, L=10):
Metric              | Backtest | MC Median | MC 90th %ile | MC 99th %ile
CAGR                | 18%      | 16%       | 12%          | 8%
Max Drawdown        | 8%       | 11%       | 18%          | 28%
Max DD Duration     | 45 days  | 72 days   | 145 days     | 280 days
Sharpe Ratio        | 1.50     | 1.35      | 0.95         | 0.55

Key finding: the 8% max drawdown was fortunate. 10% of the time,
drawdown would exceed 18%. Position sizing should assume 18% max DD
(90th percentile), not 8% (backtest point estimate).
```

### Example 2: Ruin Analysis with Leverage
```
Base strategy: Sharpe 1.2, vol 10%, no leverage
Investment horizon: 10 years
Ruin threshold: -30% from peak

Monte Carlo results (10,000 paths each):

Leverage | Expected CAGR | P(Ruin) | Median Max DD | 95th Max DD
1.0x     | 12%           | 0.3%    | 9%            | 18%
1.5x     | 16%           | 2.1%    | 14%           | 27%
2.0x     | 18%           | 8.5%    | 19%           | 38%
2.5x     | 17%           | 18.2%   | 25%           | 50%
3.0x     | 14%           | 31.5%   | 32%           | 62%

Kelly optimal leverage: 1.2x (maximizes expected log wealth)
Practical Kelly: 0.5-0.75 * Kelly = 0.6x to 0.9x leverage

Note: at 2.5x leverage, expected CAGR DECLINES vs 2.0x
(volatility drag exceeds additional return). This is the point
where leverage destroys value — invisible in Sharpe ratio but
clear in Monte Carlo geometric return analysis.
```

### Example 3: Parameter Robustness
```
Strategy: RSI mean reversion
Optimal parameters: RSI period=14, oversold=30, overbought=70
Backtest Sharpe: 1.35

Perturbation analysis (1,000 random perturbations, sigma=10%):
RSI period range tested: 12-16
Oversold range: 27-33
Overbought range: 63-77

Results:
- Mean Sharpe across perturbations: 1.18
- Std of Sharpe: 0.22
- % perturbations with Sharpe > 0.5: 95%
- % perturbations with Sharpe > 1.0: 72%
- % perturbations with positive return: 98%

Assessment: Strategy is robust to parameter perturbation.
72% of nearby parameter combinations maintain Sharpe > 1.0.
Performance plateau is broad — not a narrow overfit spike.

Compare with fragile strategy:
- Mean Sharpe across perturbations: 0.45
- Std of Sharpe: 0.85
- % perturbations with Sharpe > 0.5: 38%
- % perturbations with positive return: 55%
This strategy is clearly overfit — performance collapses with small parameter changes.
```

## Quality Gate

Before relying on Monte Carlo results, verify:

- [ ] Simulation method matches data characteristics — block bootstrap for autocorrelated returns, stationary bootstrap for mean-reverting strategies
- [ ] Number of simulations is sufficient — at least 5,000 for percentile estimates, 10,000+ for tail risk
- [ ] Convergence verified — running twice produces similar distributions
- [ ] Return distribution assumptions validated — if parametric, tested against empirical distribution (KS test, QQ plot)
- [ ] Fat tails are captured — normal distribution underestimates tail risk; use t-distribution or empirical bootstrap
- [ ] Regime changes considered — single-regime simulations may underestimate tail risk
- [ ] Block length justified — if using block bootstrap, tested sensitivity to block length choice
- [ ] Results are from OOS returns (not IS returns) when combined with walk-forward analysis
- [ ] Ruin probability is calculated for realistic leverage levels and investment horizons
- [ ] Decision-making uses conservative percentiles (90th or 95th), not median or mean estimates
