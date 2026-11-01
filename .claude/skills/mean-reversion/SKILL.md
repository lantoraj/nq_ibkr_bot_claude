---
name: mean-reversion
description: "Mean Reversion. Use when: User wants to trade assets that revert to a mean or equilibrium level; Building pairs trading or spread trading strategies; Using Bollinger Bands, Z-scores, or OU models for entry/exit."
---

# Mean Reversion

name: mean-reversion
description: Mean reversion strategies — Bollinger, Z-score, Ornstein-Uhlenbeck, and statistical approaches. Use when designing mean-reversion systems.

## When to Activate

- User wants to trade assets that revert to a mean or equilibrium level
- Building pairs trading or spread trading strategies
- Using Bollinger Bands, Z-scores, or OU models for entry/exit
- Estimating half-life of mean reversion
- Distinguishing between mean-reverting and trending instruments

## First Questions

1. Are you trading a single asset, a pair, or a basket/spread?
2. What time horizon — intraday, daily, weekly?
3. Do you have evidence of mean reversion (stationarity tests, Hurst exponent)?
4. What defines the "mean" — historical average, moving average, model-implied fair value?
5. What are the costs and constraints (bid-ask spread, borrowing costs for shorts)?

## Core Concepts

### Ornstein-Uhlenbeck (OU) Process

The mathematical foundation for mean-reversion trading:

```
dx_t = theta * (mu - x_t) * dt + sigma * dW_t

x_t:   current value of the spread/price
mu:    long-run mean (equilibrium level)
theta: speed of mean reversion (larger = faster reversion)
sigma: volatility of the process
dW_t:  Wiener process (random noise)

Key derived quantity — half-life of mean reversion:
  t_half = ln(2) / theta

Interpretation:
  Half-life < 5 days: Fast reversion, suitable for intraday/daily trading
  Half-life 5-20 days: Sweet spot for daily mean-reversion strategies
  Half-life 20-60 days: Slower, requires patience and wider stops
  Half-life > 60 days: Too slow for practical mean-reversion trading
```

### Hurst Exponent

The Hurst exponent H characterizes the memory of a time series:

```
H < 0.5:  Mean-reverting (anti-persistent)
H = 0.5:  Random walk (no memory)
H > 0.5:  Trending (persistent)

Estimation methods:
- Rescaled range (R/S) analysis
- Detrended Fluctuation Analysis (DFA) — more robust
- Variance ratio test

Practical interpretation:
  H = 0.3-0.4:  Strong mean reversion, good candidate
  H = 0.4-0.5:  Weak mean reversion, marginal
  H = 0.5:      Random walk, avoid mean-reversion strategies
  H > 0.5:      Use trend-following instead
```

### Mean Reversion vs Trending Detection

Before deploying a mean-reversion strategy, verify the instrument actually mean-reverts:

```
Tests to apply:
1. ADF test on the series (reject unit root = mean-reverting)
2. Hurst exponent (H < 0.5)
3. Variance ratio test (ratio < 1 at relevant horizon)
4. Half-life estimation (finite and practical)
5. Visual inspection of autocorrelation (negative at lag 1 for returns)

WARNING: Individual stock prices rarely mean-revert.
Mean reversion is found in:
  - Spreads between cointegrated pairs
  - Deviations from fair value models
  - Implied vs realized volatility
  - Cross-sectional relative valuations
  - Interest rate spreads
```

## Detailed Methodology

### Half-Life Estimation

```
Method 1: AR(1) regression
  delta_y_t = a + b * y_{t-1} + epsilon_t
  theta = -b
  half_life = -ln(2) / ln(1 + b)   [discrete time version]
  Or approximately: half_life = -ln(2) / b  [when |b| is small]

  b should be negative and significant for mean reversion

Method 2: OU parameter estimation (MLE)
  Estimate theta, mu, sigma by maximum likelihood
  half_life = ln(2) / theta

Method 3: Variance ratio
  VR(k) = Var(y_t - y_{t-k}) / (k * Var(y_t - y_{t-1}))
  VR < 1 indicates mean reversion at horizon k
  Plot VR(k) vs k to find the horizon of maximum mean reversion
```

### Z-Score Trading

The Z-score normalizes the deviation from the mean:

```
z_t = (x_t - mu_t) / sigma_t

Where:
  x_t: current value of spread or price
  mu_t: rolling mean (window = 2 * half_life or longer)
  sigma_t: rolling standard deviation (same window)

Trading rules:
  Entry long:   z_t < -entry_threshold (e.g., -2.0)
  Entry short:  z_t > +entry_threshold (e.g., +2.0)
  Exit:         |z_t| < exit_threshold (e.g., 0.5)
  Stop-loss:    |z_t| > stop_threshold (e.g., 4.0) — relationship may be broken

Parameter selection:
  Entry at 2.0 sigma: captures ~95% of excursions
  Entry at 1.5 sigma: more trades, lower per-trade P&L
  Exit at 0.5 sigma: partial mean reversion capture
  Exit at 0.0 sigma: full mean reversion (longer holding period)
```

### Bollinger Band Strategy

```
Upper band: MA(N) + k * std(N)
Lower band: MA(N) - k * std(N)
Middle:     MA(N)

Classic parameters: N=20, k=2

Mean-reversion rules:
  Buy when price touches lower band
  Sell when price touches upper band
  Exit at middle band

Bandwidth = (Upper - Lower) / Middle
  Narrow bandwidth: low volatility, expect breakout (NOT mean reversion)
  Wide bandwidth: high volatility, mean reversion more likely

%B = (Price - Lower) / (Upper - Lower)
  %B < 0: Below lower band (oversold)
  %B > 1: Above upper band (overbought)
```

### Entry and Exit Rule Design

```
Entry signals (pick one or combine):
  1. Z-score exceeds threshold (2.0 standard deviations)
  2. Price touches Bollinger band
  3. RSI < 30 (oversold) or RSI > 70 (overbought)
  4. OU model probability of reversion exceeds threshold

Exit signals:
  1. Z-score returns to target (0 or 0.5)
  2. Price returns to moving average
  3. Time-based exit (close after N days regardless)
  4. Profit target hit (fixed % or ATR-based)

Stop-loss rules (critical for mean reversion):
  1. Z-score exceeds extreme level (4.0+) — regime change likely
  2. Fixed dollar loss per trade
  3. Spread half-life appears to be increasing (relationship weakening)
  4. Cointegration test fails on recent data

Time-based exit rationale:
  If the spread has not reverted within 2-3 half-lives, the
  mean-reversion assumption may be invalid. Exit and reassess.
```

### Risk Management for Mean Reversion

Mean-reversion strategies have specific risk characteristics:

```
Key risks:
1. Convergence failure: The spread diverges instead of reverting
   - Structural break in the relationship
   - Regime change (cointegration breaks down)
   - Fundamental change in one of the assets

2. Adding to losers: Mean reversion naturally pyramids into losing positions
   - Cap maximum position size
   - Use time stops (exit if no reversion in 2-3 half-lives)
   - Hard stop-loss at extreme Z-scores

3. Negative skew: Many small wins, occasional large losses
   - Kelly criterion or fractional Kelly for sizing
   - Diversify across many mean-reverting instruments
   - Limit concentration in any single spread

4. Liquidity risk: Wide spreads during stress precisely when you need to exit
   - Trade liquid instruments only
   - Size positions relative to ADV
   - Maintain portfolio-level stop-loss

Position sizing:
  Size per trade = risk_budget / (entry_z - stop_z) / sigma
  Or: fractional Kelly: f* = (p*b - q) / b * fraction
  Where p = win rate, q = loss rate, b = avg win / avg loss
```

## Templates / Examples

### Mean Reversion Strategy Report

```
Strategy: Z-Score Mean Reversion on ETF Spread
Spread: XLE - 0.85 * SPY (energy sector relative value)
Period: 2015-01-01 to 2024-12-31

--- Spread Properties ---
ADF Statistic:      -3.42 (p = 0.01) [Stationary]
Hurst Exponent:     0.38 [Mean-reverting]
Half-Life:          12 days
OU Parameters:      theta=0.058, mu=2.15, sigma=1.82

--- Trading Rules ---
Entry:              |Z| > 2.0
Exit:               |Z| < 0.5
Stop:               |Z| > 4.0 or 36 days (3x half-life)
Position Sizing:    Risk 1% of capital per trade

--- Performance ---
Number of Trades:    84 (round trips)
Win Rate:            72%
Average Win:         1.8%
Average Loss:        -2.5%
Profit Factor:       2.1
Sharpe Ratio:        1.35
Max Drawdown:        -8.2%
Average Holding:     9 days
Annual Turnover:     380%

--- Risk Metrics ---
Skewness of P&L:    -0.6 (negative skew, as expected)
Kurtosis:           4.2 (fat tails)
Worst Trade:        -5.8%
Max Consecutive Losses: 4
```

### Mean Reversion Screening Template

```
Instrument          | ADF p-val | Hurst | Half-Life | Verdict
ETF spread A-B      | 0.01      | 0.38  | 12 days   | TRADE
ETF spread C-D      | 0.08      | 0.45  | 28 days   | MARGINAL
Single stock X      | 0.45      | 0.52  | N/A       | REJECT (random walk)
FX cross EUR/GBP    | 0.03      | 0.42  | 18 days   | TRADE
Implied-realized vol| 0.001     | 0.32  | 8 days    | TRADE
Commodity spread    | 0.12      | 0.48  | 45 days   | REJECT (too slow)
```

### Parameter Sensitivity Analysis

```
Entry Z | Exit Z | Stop Z | Win Rate | Sharpe | Trades/Year
1.5     | 0.0    | 3.5    | 65%      | 0.95   | 18
1.5     | 0.5    | 3.5    | 68%      | 1.05   | 18
2.0     | 0.0    | 4.0    | 70%      | 1.20   | 10
2.0     | 0.5    | 4.0    | 72%      | 1.35   | 10
2.5     | 0.0    | 4.5    | 75%      | 1.10   | 5
2.5     | 0.5    | 4.5    | 78%      | 1.15   | 5

Sweet spot: Entry 2.0, Exit 0.5 — balances trade frequency with quality
```

## Quality Gate

Before deploying a mean-reversion strategy:

- [ ] Statistical evidence of mean reversion (ADF rejects unit root, Hurst < 0.5)
- [ ] Half-life is practical for intended trading frequency (5-30 days for daily)
- [ ] OU model parameters are stable over different estimation windows
- [ ] Entry/exit thresholds tested for robustness (small parameter changes do not destroy performance)
- [ ] Stop-loss rules in place (Z-score extreme, time-based, dollar-based)
- [ ] Risk of convergence failure acknowledged and sized accordingly
- [ ] Negative skew of returns understood — position sizing accounts for tail risk
- [ ] Transaction costs deducted (mean reversion can be high turnover)
- [ ] Relationship retested periodically (cointegration can break)
- [ ] Portfolio diversification across multiple mean-reverting instruments
