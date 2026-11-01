---
name: alpha-research
description: "Alpha Research. Use when: User is exploring new predictive signals for asset returns; Evaluating whether a trading idea has genuine predictive power; Combining multiple alpha signals into a composite."
---

# Alpha Research

name: alpha-research
description: Alpha signal discovery, testing, and evaluation. Use when researching new trading signals.

## When to Activate

- User is exploring new predictive signals for asset returns
- Evaluating whether a trading idea has genuine predictive power
- Combining multiple alpha signals into a composite
- Diagnosing why an alpha signal is decaying
- Designing a research pipeline for systematic signal discovery
- Applying multiple testing corrections to a signal library

## First Questions

1. What is the universe and asset class (equities, futures, FX, crypto)?
2. Is this a cross-sectional signal (ranking stocks) or a time-series signal (timing a single asset)?
3. What is the intended holding period (intraday, days, weeks, months)?
4. How many signals have you already tested (needed for multiple testing adjustment)?
5. Do you have access to point-in-time data, or is there look-ahead risk?

## Core Concepts

### Hypothesis-Driven Research

The strongest alpha signals start with an economic hypothesis, not a data mining exercise. A valid hypothesis answers:

- **Why** does this signal predict returns? (behavioral bias, structural constraint, information asymmetry)
- **Who** is on the other side of the trade? (identify the loser)
- **Why** hasn't this been arbitraged away? (barriers to implementation, limits to arbitrage)
- **Will** this persist? (structural vs temporary inefficiency)

### Information Coefficient (IC)

The IC is the rank correlation (Spearman) between a signal's predicted values and subsequent realized returns. It is the primary metric for evaluating alpha signals.

- **IC** = corr(rank(signal_t), rank(return_{t+1}))
- **IC Mean**: Average IC across time periods. Even IC = 0.02-0.05 is valuable at scale.
- **IC Standard Deviation**: Volatility of IC over time. Lower is better.
- **IC Information Ratio (ICIR)**: IC_mean / IC_std. An ICIR > 0.10 is noteworthy. ICIR > 0.25 is strong.

### The Fundamental Law of Active Management

IR = IC * sqrt(BR) * TC

- IR: Information Ratio (excess return / tracking error)
- IC: Information Coefficient (signal quality)
- BR: Breadth (number of independent bets per year)
- TC: Transfer Coefficient (portfolio implementation efficiency, 0 to 1)

Implication: A weak signal (low IC) applied across many assets (high BR) can produce a strong strategy.

## Detailed Methodology

### IC Decay Analysis

IC decay measures how quickly a signal's predictive power diminishes over time:

```
Compute IC at horizons: 1-day, 5-day, 10-day, 21-day, 63-day
Plot IC vs horizon — the decay curve reveals:
- Fast decay (< 5 days): Signal is short-lived, requires high-frequency trading
- Medium decay (5-21 days): Sweet spot for systematic strategies
- Slow decay (21-63+ days): Lower turnover, capacity-friendly
- Non-monotonic decay: May indicate reversal at certain horizons
```

The optimal holding period is where IC * sqrt(horizon) is maximized — balancing signal strength against breadth.

### Turnover Analysis

High alpha signals are useless if they require excessive trading:

```
Single-period turnover = sum(|w_t - w_{t-1}|) / 2
Annualized turnover = single-period turnover * periods_per_year

Cost-adjusted alpha = gross_alpha - (turnover * round_trip_cost)
Break-even cost = gross_alpha / turnover
```

If break-even cost is below your actual trading cost, the signal is unprofitable.

### Multiple Testing Correction

When testing N signals, some will appear significant by chance. Apply corrections:

- **Bonferroni:** Divide significance threshold by N. Conservative.
- **Holm-Bonferroni:** Stepwise improvement on Bonferroni.
- **Benjamini-Hochberg (FDR):** Controls false discovery rate. Less conservative, often preferred.
- **Harvey-Liu-Zhu haircut:** Adjust t-statistics for the number of factors tested in the literature. A t-stat of 2.0 is no longer sufficient; use t > 3.0 as a threshold.
- **Sharpe Ratio haircut (Bailey-Lopez de Prado):** SR_adjusted = SR * sqrt(1 - N_tests/N_observations)

### Out-of-Sample Validation Protocol

```
Step 1: Split data — 60% in-sample, 20% validation, 20% holdout
Step 2: Develop signal on in-sample only
Step 3: Tune parameters on validation set
Step 4: Final evaluation on holdout — ONE chance, no iteration
Step 5: Compare holdout performance to in-sample:
        - Holdout SR / In-sample SR > 0.5: Robust
        - Ratio 0.3-0.5: Marginal, proceed with caution
        - Ratio < 0.3: Likely overfit, discard or redesign
```

### Signal Combination

Combining signals improves stability if they are not perfectly correlated:

- **Equal weight:** Simple, robust, no estimation error
- **IC-weighted:** Weight by trailing IC or ICIR
- **Optimized weights:** Use mean-variance optimization on signal returns — but estimation error is a real risk
- **Rank averaging:** Rank each signal, average ranks, re-rank. Non-parametric, robust.
- **Machine learning:** Use signals as features in a tree or linear model with purged CV

### Alpha Decay Management

Alpha signals decay over time as markets adapt. Monitor and respond:

**Decay indicators:**
- Rolling 12-month IC declining
- Gross Sharpe ratio declining while turnover stays constant
- Crowding indicators rising (more capital in the signal)
- Academic publication of the signal (typical 30-50% decay post-publication)

**Responses:**
- Diversify across many signals so no single decay is catastrophic
- Continuously research new signals (research pipeline)
- Modify signal construction (proprietary variations on known themes)
- Reduce position sizes in decaying signals dynamically

## Templates / Examples

### Alpha Signal Evaluation Report

```
Signal Name: [e.g., Earnings Revision Breadth]
Universe: S&P 500
Signal Frequency: Monthly
Test Period: 2005-01-01 to 2024-12-31 (IS: 2005-2017, OOS: 2018-2024)

--- In-Sample ---
IC Mean:            0.042
IC Std:             0.085
ICIR:               0.49
Monthly Turnover:   18%
Quintile Spread:    65 bps/month (Q1 - Q5)
Hit Rate:           58%
Max DD (L/S):       -12.3%
Sharpe (L/S):       1.25

--- Out-of-Sample ---
IC Mean:            0.031
IC Std:             0.092
ICIR:               0.34
Sharpe (L/S):       0.88
OOS/IS SR Ratio:    0.70

--- Correlation with Existing Alphas ---
Alpha_momentum:     0.15
Alpha_value:        -0.08
Alpha_quality:      0.22

Verdict: PASS — robust OOS performance, low correlation to existing book
```

### Research Pipeline Checklist

```
[ ] Hypothesis documented with economic rationale
[ ] Data sourced with point-in-time timestamps
[ ] Survivorship bias handled (include delisted securities)
[ ] Signal computed at each rebalance date
[ ] IC and ICIR computed across full sample
[ ] IC decay curve plotted across multiple horizons
[ ] Turnover and break-even cost computed
[ ] Quintile analysis: monotonic spread required
[ ] Sector and market-cap neutralization tested
[ ] Multiple testing adjustment applied (record total tests run)
[ ] Out-of-sample validation on held-out period
[ ] Correlation with existing signals < 0.40
[ ] Capacity analysis: can signal absorb target AUM?
[ ] Implementation simulation with realistic costs
```

## Quality Gate

Before adding an alpha signal to production:

- [ ] IC is positive and statistically significant after multiple testing correction
- [ ] ICIR exceeds 0.10 in out-of-sample period
- [ ] OOS/IS Sharpe ratio > 0.50 (signal is not overfit)
- [ ] Turnover is compatible with actual trading costs (break-even cost > actual cost)
- [ ] Signal is not highly correlated (> 0.40) with existing production signals
- [ ] IC decay profile matches intended holding period
- [ ] Signal has capacity for the intended allocation
- [ ] No look-ahead bias in signal construction
- [ ] Economic rationale is documented and defensible
- [ ] Monitoring dashboard established for ongoing IC tracking
