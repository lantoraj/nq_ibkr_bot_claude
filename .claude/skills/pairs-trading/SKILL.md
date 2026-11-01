---
name: pairs-trading
description: "Pairs Trading. Use when: User wants to trade the spread between two related securities; Selecting pairs using cointegration, correlation, or fundamental linkage; Constructing and monitoring spread positions."
---

# Pairs Trading

name: pairs-trading
description: Pairs trading methodology — cointegration, distance, copula methods. Use when designing market-neutral pairs strategies.

## When to Activate

- User wants to trade the spread between two related securities
- Selecting pairs using cointegration, correlation, or fundamental linkage
- Constructing and monitoring spread positions
- Managing risk in market-neutral pair portfolios
- Evaluating pair stability and when to exit broken pairs

## First Questions

1. What universe are you selecting pairs from (sector, index, asset class)?
2. What pair selection method — cointegration, distance, fundamental, or ML-based?
3. What is the trading frequency (intraday, daily, weekly)?
4. Long-short (market neutral) or long-only (switch between pair members)?
5. How many pairs do you intend to trade simultaneously?

## Core Concepts

### Why Pairs Trading Works

Pairs trading exploits temporary mispricings between related securities. Two stocks with a fundamental economic link (same sector, similar business, shared risk factors) should move together over time. When they diverge, the spread is expected to revert.

**Sources of edge:**
- Mean reversion of residual mispricings
- Market microstructure effects (temporary supply/demand imbalance)
- Slow information diffusion between related securities
- Investor behavioral biases (overreaction to firm-specific news)

**Key property:** Market neutral. The long and short legs offset market risk, leaving only the spread as the bet.

### Pair Selection Methods

**1. Cointegration-based (preferred):**
- Two prices are cointegrated if a linear combination is stationary
- Does not require high correlation — only that they share a common stochastic trend
- Test using Engle-Granger or Johansen procedure
- Provides the hedge ratio directly

**2. Distance method (Gatev et al. 2006):**
- Normalize prices, compute sum of squared differences over formation period
- Select pairs with minimum distance (most similar price paths)
- Simple but does not guarantee mean reversion

**3. Correlation-based:**
- Select highly correlated pairs (> 0.80)
- Monitor for correlation breakdown
- Weaker theoretical basis than cointegration

**4. Fundamental/sector-based:**
- Pair companies with similar business models, market caps, factor exposures
- Use cointegration as a filter, not the sole criterion
- More robust because the economic link provides a structural reason for co-movement

## Detailed Methodology

### Pair Selection Pipeline

```
Step 1: Define universe (e.g., S&P 500 stocks within same GICS sector)
Step 2: Pre-filter by correlation (keep pairs with corr > 0.70)
Step 3: Test cointegration on formation period (12 months)
         - Engle-Granger: ADF on OLS residuals, p < 0.05
         - Use Engle-Granger critical values, NOT standard ADF
Step 4: Estimate half-life of mean reversion
         - Keep pairs with half-life between 5 and 60 days
Step 5: Check Hurst exponent of spread (H < 0.5)
Step 6: Verify economic rationale (same sector, similar business)
Step 7: Rank qualifying pairs by:
         - Cointegration test statistic (most negative = strongest)
         - Half-life (shorter = better)
         - Historical spread Sharpe ratio
Step 8: Select top N pairs (10-30 for diversification)
Step 9: Re-run selection monthly or quarterly
```

### Spread Construction

```
Given pair (A, B) with cointegrating relationship:
  Price_A = alpha + beta * Price_B + spread

Hedge ratio estimation:
  Method 1: OLS regression (simple, biased)
    beta = cov(A, B) / var(B)

  Method 2: Total Least Squares (TLS/Deming regression)
    Accounts for noise in both variables
    More symmetric (A on B gives same ratio as B on A)

  Method 3: Kalman filter (dynamic, adaptive)
    Tracks time-varying hedge ratio
    Best for production use

  Method 4: Johansen cointegrating vector
    Estimated jointly, handles multiple pairs

Spread computation:
  spread_t = Price_A_t - beta * Price_B_t - alpha

Z-score:
  z_t = (spread_t - mean(spread)) / std(spread)
  Use rolling statistics (window = 2 * half_life minimum)
```

### Trading Rules

```
Entry:
  Long spread:  z_t < -2.0 (spread is abnormally negative)
    → Buy A, Sell B (in ratio beta)
  Short spread: z_t > +2.0 (spread is abnormally positive)
    → Sell A, Buy B (in ratio beta)

Exit:
  Close when z_t crosses 0 (full mean reversion)
  Or close when z_t crosses +/-0.5 (partial, more conservative)
  Or time-based exit after 3 * half_life days

Stop-loss:
  Close if |z_t| > 4.0 (spread blew out — relationship may be broken)
  Close if cointegration re-test fails on recent data
  Close on corporate event (M&A announcement, earnings shock, sector re-classification)

Position sizing:
  Dollar-neutral: Long $100K of A, Short $100K * beta of B
  Beta-neutral: Adjust for beta difference to eliminate market exposure
  Volatility-sized: Each pair contributes equal risk to portfolio
```

### Risk Management

```
Pair-level risks:
1. Divergence risk: Spread keeps widening instead of reverting
   - Hard stop-loss (Z > 4)
   - Time stop (3x half-life)
   - Maximum loss per pair (e.g., 2% of capital)

2. Structural break: Cointegration relationship permanently breaks
   - Re-test cointegration monthly
   - Monitor for fundamental changes (M&A, spin-offs, bankruptcies)
   - Automatic exit on corporate event flags

3. Leg risk: One leg moves sharply while the other is illiquid
   - Execute both legs simultaneously (or as close as possible)
   - Avoid pairs where one leg has low liquidity

4. Short squeeze: Borrowed stock gets recalled or borrow cost spikes
   - Monitor borrow availability and cost
   - Avoid hard-to-borrow stocks in the short leg

Portfolio-level risks:
1. Sector concentration: Many pairs from the same sector = sector bet
   - Diversify across sectors
   - Monitor net sector exposure

2. Factor exposure: Pairs may have hidden factor tilts
   - Compute portfolio-level factor exposure
   - Ensure approximate factor neutrality

3. Correlation among pairs: Pairs can become correlated in stress
   - Monitor pairwise correlation of spread returns
   - Reduce overall exposure during correlation spikes
```

### Portfolio of Pairs

```
Construction:
  Select 10-30 pairs across sectors
  Equal risk weight per pair (vol-adjusted)
  Maximum 3-5 pairs per sector
  Total gross exposure: 100-300% of capital

Rebalancing:
  Re-screen pairs monthly or quarterly
  Replace broken pairs (failed cointegration re-test)
  Adjust hedge ratios (rolling OLS or Kalman filter update)

Performance expectations:
  Sharpe: 1.0-2.0 for well-constructed portfolio of pairs
  Max drawdown: 5-15%
  Market correlation: near zero (by design)
  Capacity: Limited by liquidity of pair members

Diversification benefit:
  Single pair Sharpe: ~0.5-0.8
  Portfolio of 20 pairs: Sharpe improves by sqrt(N/effective_N)
  If pair returns have 0.1 average correlation:
    Effective N ≈ N / (1 + (N-1)*rho) ≈ 7 for 20 pairs with rho=0.1
    Portfolio Sharpe ≈ single_pair_Sharpe * sqrt(7) ≈ 1.5
```

## Templates / Examples

### Pair Evaluation Report

```
Pair: KO (Coca-Cola) vs PEP (PepsiCo)
Sector: Consumer Staples | Formation: 2020-01 to 2022-12

--- Cointegration Tests ---
Engle-Granger ADF:   -4.12 (p = 0.001) [Cointegrated]
Johansen Trace:       r=1 confirmed
Hedge Ratio (OLS):    0.92
Hedge Ratio (TLS):    0.95
Hedge Ratio (Kalman): 0.93 (mean), range [0.85, 1.02]

--- Spread Properties ---
Half-Life:            14 days
Hurst Exponent:       0.35
Spread Std Dev:       $2.45
Mean Z-score Range:   [-3.1, +2.8]

--- Backtest (OOS: 2023-01 to 2024-12) ---
Entry: Z > 2.0 or Z < -2.0 | Exit: |Z| < 0.5 | Stop: |Z| > 4.0
Trades (round-trip):  18
Win Rate:             78%
Average P&L per trade: $1,850
Sharpe Ratio:         1.65
Max Drawdown:         -3.8%
Average Holding:      11 days

--- Risk Assessment ---
Short borrow cost:    Low (both mega-cap, widely available)
Leg liquidity:        Excellent (both > $500M ADV)
Event risk:           Low (stable businesses)
Sector concentration: Consumer Staples (monitor if adding more from sector)

Verdict: PASS — strong cointegration, reasonable half-life, good OOS performance
```

### Pair Monitoring Dashboard Template

```
Active Pairs Report — [Date]

Pair    | Hedge | Current Z | Entry Z | Days Held | P&L   | Status
KO/PEP  | 0.93  | -0.8      | -2.1    | 8         | +$1.2K| Converging
XOM/CVX | 1.15  | -1.5      | -2.3    | 12        | +$0.6K| Slow convergence
JPM/BAC | 0.78  | +3.2      | +2.0    | 5         | -$1.8K| Diverging (watch)
MSFT/AAPL| 0.65 | +0.3      | +2.2    | 15        | +$2.1K| Near exit

Portfolio Summary:
  Pairs active: 14 of 20
  Net market exposure: -2.1% (approximately neutral)
  Gross exposure: 180%
  Portfolio Z-score (avg): 0.4
  MTD P&L: +$8.5K
  Pairs at stop-loss risk (|Z| > 3.5): 1 (JPM/BAC)
```

### Pair Selection Screening Results

```
Universe: S&P 500, same GICS sector
Formation Period: 2022-01 to 2023-12
Pairs tested: 4,850 | Cointegrated at 5%: 312 (6.4%)

Top 10 by Cointegration Strength:
Rank | Pair        | Sector  | ADF stat | Half-Life | Spread SR
1    | KO/PEP      | Staples | -4.85    | 14 days   | 1.82
2    | XOM/CVX     | Energy  | -4.52    | 18 days   | 1.45
3    | V/MA        | Fintech | -4.31    | 12 days   | 1.68
4    | HD/LOW      | Retail  | -4.15    | 22 days   | 1.25
5    | UNH/CI      | Health  | -3.98    | 16 days   | 1.52
...

Selected: Top 20 pairs across 8 sectors (max 4 per sector)
```

## Quality Gate

Before deploying a pairs trading strategy:

- [ ] Cointegration confirmed at 5% significance level with correct critical values
- [ ] Economic rationale for pair relationship documented
- [ ] Half-life is practical for trading frequency (5-60 days)
- [ ] Hedge ratio estimated robustly (TLS or Kalman, not just OLS)
- [ ] Out-of-sample backtest shows positive Sharpe
- [ ] Stop-loss rules defined for divergence, time, and corporate events
- [ ] Short leg is borrowable at reasonable cost
- [ ] Both legs have sufficient liquidity for target position sizes
- [ ] Portfolio diversified across sectors (no single-sector concentration)
- [ ] Re-screening schedule established (monthly or quarterly cointegration re-test)
- [ ] Execution plan handles simultaneous leg entry/exit
