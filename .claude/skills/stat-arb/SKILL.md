---
name: stat-arb
description: "Statistical Arbitrage. Use when: User wants to build a statistical arbitrage portfolio; Decomposing returns using PCA to extract residual alpha; Constructing sector-neutral or factor-neutral portfolios."
---

# Statistical Arbitrage

name: stat-arb
description: Statistical arbitrage — PCA-based, factor-neutral, sector-neutral portfolio construction. Use for stat-arb strategy development.

## When to Activate

- User wants to build a statistical arbitrage portfolio
- Decomposing returns using PCA to extract residual alpha
- Constructing sector-neutral or factor-neutral portfolios
- Trading mean reversion of residual returns
- Estimating capacity and managing risk of stat-arb strategies

## First Questions

1. What is the investment universe (US equities, global, sector-specific)?
2. Are you targeting residual mean reversion, or do you have a specific alpha signal?
3. What neutrality constraints are required (market, sector, factor)?
4. What is the target holding period and rebalancing frequency?
5. What AUM and capacity requirements exist?

## Core Concepts

### What is Statistical Arbitrage?

Statistical arbitrage (stat arb) is a market-neutral strategy that profits from temporary mispricings in cross-sectional return relationships. Unlike pairs trading (2 assets), stat arb operates across an entire universe simultaneously.

```
Core principle:
  1. Decompose stock returns into systematic (factor) and idiosyncratic (residual) components
  2. The residual should be mean-reverting (if it is not, there is no stat arb)
  3. Trade the residual: buy stocks with abnormally negative residuals, sell stocks with abnormally positive residuals
  4. Neutralize factor exposures so the portfolio profits ONLY from residual mean reversion
```

### PCA for Return Decomposition

Principal Component Analysis extracts the dominant systematic risk factors from the return covariance matrix:

```
R (T x N return matrix) = U * S * V'   (SVD decomposition)

First K principal components explain most variance:
  PC1: ~30-40% (market factor)
  PC2: ~5-8% (sector/size)
  PC3: ~3-5% (value/growth)
  PCs 4-10: ~1-3% each
  Residual: ~40-50% of variance (idiosyncratic)

Eigenportfolios:
  Each column of V corresponds to a portfolio (eigenportfolio)
  First eigenportfolio ≈ market portfolio
  Subsequent eigenportfolios capture sector tilts, style factors

Factor return estimation:
  f_t = R_t * V_K   (project returns onto top K eigenvectors)
  Factor loadings: B = V_K
  Residual returns: e_t = R_t - f_t * B'
```

### Residual Returns and Mean Reversion

The residual return e_{i,t} is the stock's return after removing systematic factor exposure. In stat arb, the key assumption is that cumulative residuals are mean-reverting.

```
Cumulative residual: E_{i,t} = sum(e_{i,s}) for s = t-L to t

If E_{i,t} is abnormally negative: Stock has underperformed relative to its factor exposure → BUY
If E_{i,t} is abnormally positive: Stock has outperformed relative to its factor exposure → SELL

This is the "residual reversal" effect — one of the most established statistical regularities in equity markets.
```

## Detailed Methodology

### Building a PCA-Based Stat Arb Portfolio

```
Step 1: Universe definition
  - Liquid stocks (top 500-1000 by market cap)
  - Minimum ADV filter ($5M+)
  - Remove recent IPOs (< 1 year of data)
  - Exclude stocks pending corporate actions

Step 2: Return matrix construction
  - Use daily log returns, 60-120 trading days
  - Demean returns (subtract cross-sectional mean each day)

Step 3: PCA decomposition
  - Compute covariance matrix of demeaned returns
  - Extract top K eigenvectors (K = 5-15, determined by scree plot or cross-validation)
  - Alternative: use pre-specified factors (Fama-French, Barra) instead of PCA

Step 4: Compute residual returns
  - For each stock: e_{i,t} = r_{i,t} - sum_k(beta_{i,k} * f_{k,t})
  - Cumulative residual over lookback window L (typically 5-20 days)

Step 5: Signal construction
  - s_{i,t} = -E_{i,t} / sigma(E_i)   (negative because we mean-revert)
  - Z-score normalize cross-sectionally

Step 6: Portfolio construction
  - Raw weights: w_i proportional to s_i
  - Apply neutrality constraints (see below)
  - Scale to target volatility or gross exposure
```

### Neutrality Constraints

Neutrality ensures the portfolio profits from alpha, not from unintended factor bets:

```
Market neutrality:
  sum(w_i) = 0  (dollar neutral)
  sum(w_i * beta_i) = 0  (beta neutral)

Sector neutrality:
  For each sector k: sum(w_i * I(sector_i = k)) = 0
  Ensures no net sector bet

Factor neutrality:
  For each factor k: sum(w_i * beta_{i,k}) = 0
  Neutralize market, size, value, momentum, quality exposure

Implementation:
  Solve constrained optimization:
    max sum(w_i * s_i)
    subject to:
      sum(w_i) = 0
      sum(|w_i|) <= Gross_max
      For each factor k: |sum(w_i * beta_{i,k})| < tolerance
      For each sector: |sum(w_i * I_sector)| < sector_tolerance
      |w_i| <= max_position_weight
```

### Position Construction and Sizing

```
Position weight determination:
  1. Start with signal strength: w_i^raw = s_i
  2. Cap outliers: winsorize at +/- 3 standard deviations
  3. Make dollar-neutral: w_i = w_i^raw - mean(w_i^raw)
  4. Apply sector/factor neutralization via optimization
  5. Scale to target: w_i = w_i * target_gross / sum(|w_i|)

Gross exposure targets:
  Conservative: 100% long + 100% short = 200% gross
  Moderate: 150% + 150% = 300% gross
  Aggressive: 200% + 200% = 400% gross
  Typical institutional stat arb: 200-400% gross, 3-6x leverage

Number of positions:
  Typical: 200-500 long + 200-500 short
  More positions = more diversification, lower idiosyncratic risk
  Fewer positions = higher conviction, higher volatility
```

### Portfolio-Level Risk Management

```
Risk decomposition:
  Total risk = factor risk + specific risk
  For a well-constructed stat arb: specific risk >> factor risk
  If factor risk is dominant, neutralization constraints are too loose

Daily risk monitoring:
  - Factor exposures (should be near zero)
  - Sector exposures (should be near zero)
  - Gross and net exposure
  - Portfolio volatility (ex-ante vs realized)
  - Concentration (top 10 positions as % of gross)
  - Beta to market (should be near zero)

Drawdown management:
  - Reduce gross exposure after X% drawdown (e.g., halve at -5%)
  - De-risk faster than re-risk (asymmetric response)
  - Circuit breaker: flatten at -10% drawdown, review model

Turnover management:
  - Daily turnover: 5-15% of gross (typical for 5-10 day holding period)
  - Annual turnover: 15-30x gross exposure
  - Transaction costs: 3-10 bps per trade (depends on universe)
  - Net alpha must exceed turnover * cost
```

### Capacity Estimation

```
Capacity is the maximum AUM before market impact erodes alpha:

Method 1: ADV-based
  For each stock: max_position = participation_rate * ADV * days_to_trade
  Portfolio capacity = sum(max_positions)
  Typical participation rate: 1-5% of ADV
  Days to trade: 1-3 days

Method 2: Impact cost estimation
  Market impact = kappa * sigma * sqrt(shares / ADV)
  kappa: impact coefficient (0.1-0.5 for liquid stocks)
  Breakeven capacity: where impact cost = expected alpha

Method 3: Empirical
  Plot backtest Sharpe vs AUM assumption (increasing impact)
  Capacity = AUM where Sharpe drops below hurdle (e.g., 0.5)

Typical capacity:
  US large-cap stat arb: $500M - $5B
  US mid/small-cap: $100M - $1B
  Global: $1B - $10B
  Capacity erodes as more capital enters stat arb (crowding)
```

## Templates / Examples

### Stat Arb Strategy Report

```
Strategy: PCA Residual Reversal
Universe: S&P 500 | Rebalance: Daily | Period: 2010-2024

Model:
  PCA factors: 10 (explaining 55% of return variance)
  Lookback for residual: 10 days
  Signal: Negative cumulative residual, z-scored
  Constraints: Dollar-neutral, beta-neutral, sector-neutral
  Gross exposure: 300% ($150M long + $150M short on $100M capital)

--- Performance ---
Annualized Return:     8.5% (on capital, not gross)
Annualized Volatility: 5.2%
Sharpe Ratio:          1.63
Max Drawdown:          -7.8%
Calmar Ratio:          1.09
Market Correlation:    0.03 (effectively zero)

--- Risk ---
Ex-ante vol:           5.0%
Factor risk fraction:  12% (well-controlled)
Specific risk fraction:88% (dominant, as desired)
Average positions:     280 long, 260 short
Top 10 concentration:  18% of gross

--- Costs ---
Daily turnover:        8% of gross
Annual turnover:       20x gross
Avg trade cost:        5 bps
Cost drag:             -5.0% annualized
Gross alpha:           13.5% → Net alpha: 8.5%

--- Capacity ---
Estimated capacity:    $800M (at 2% ADV participation)
Current AUM:           $100M
Capacity headroom:     8x
```

### Factor Exposure Report

```
Factor Exposure Report — [Date]

Factor      | Exposure | t-stat | Limit  | Status
Market      | +0.02    | 0.8    | 0.05   | OK
Size        | -0.03    | -1.1   | 0.10   | OK
Value       | +0.01    | 0.4    | 0.10   | OK
Momentum    | -0.04    | -1.5   | 0.10   | OK
Quality     | +0.02    | 0.7    | 0.10   | OK
Volatility  | -0.01    | -0.3   | 0.10   | OK

Sector      | Net ($M) | % of Gross | Limit  | Status
Technology  | +$1.2M   | 0.8%       | 3%     | OK
Healthcare  | -$0.8M   | 0.5%       | 3%     | OK
Financials  | +$0.3M   | 0.2%       | 3%     | OK
Energy      | -$0.5M   | 0.3%       | 3%     | OK
...

All exposures within limits.
```

## Quality Gate

Before deploying a stat arb strategy:

- [ ] PCA or factor model explains significant variance (>50%) with reasonable number of factors
- [ ] Residual returns are demonstrably mean-reverting (ADF test, Hurst exponent)
- [ ] Neutrality constraints enforced: market, sector, and key factor exposures near zero
- [ ] Out-of-sample Sharpe exceeds 1.0 (stat arb should be high Sharpe, market neutral)
- [ ] Transaction costs properly estimated and net performance is attractive
- [ ] Turnover is manageable (< 20x annual gross)
- [ ] Capacity analysis confirms strategy can absorb target AUM
- [ ] Risk system monitors factor exposures, drawdown, and concentration in real-time
- [ ] Drawdown management rules defined (de-risk triggers)
- [ ] Crowding risk assessed (are other stat arb funds trading similar signals?)
- [ ] Execution infrastructure supports daily rebalancing of 500+ positions
