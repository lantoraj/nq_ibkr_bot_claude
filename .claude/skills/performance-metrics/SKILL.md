---
name: performance-metrics
description: "Sharpe, Sortino, Calmar, Information Ratio, and comprehensive performance measurement. Use when: User needs to evaluate or compare trading strategy performance; Computing risk-adjusted return metrics (Sharpe, Sortino, Calmar, IR); Analyzing drawdown characteristics and recovery periods."
---

# Trading Performance Metrics

> Sharpe, Sortino, Calmar, Information Ratio, and comprehensive performance measurement.

## When to Activate

- User needs to evaluate or compare trading strategy performance
- Computing risk-adjusted return metrics (Sharpe, Sortino, Calmar, IR)
- Analyzing drawdown characteristics and recovery periods
- Understanding return calculation methodologies (arithmetic, geometric, annualization)
- Applying Sharpe ratio haircuts for backtest overfitting

## Core Concepts

### Return Calculation Foundations

**Arithmetic vs Geometric Returns**:
```
Arithmetic: R_a = (P_t - P_{t-1}) / P_{t-1}
Geometric (log): R_g = ln(P_t / P_{t-1})

Arithmetic mean overstates compounded growth.
For annualization: geometric is more accurate for multi-period performance.
```

**Annualization**:
```
Annualized return = (1 + R_total)^(252/N_days) - 1     (from daily)
Annualized return = (1 + R_total)^(12/N_months) - 1     (from monthly)
Annualized volatility = σ_daily * sqrt(252)
```

Note: sqrt(252) annualization assumes i.i.d. returns. Autocorrelated returns (momentum strategies) may have higher true annualized vol; mean-reverting returns may have lower.

### Core Metrics Reference

| Metric | Formula | Good Value | Interpretation |
|--------|---------|-----------|----------------|
| **Sharpe Ratio** | (R_p - R_f) / σ_p | > 1.0 | Excess return per unit of total risk |
| **Sortino Ratio** | (R_p - R_f) / σ_downside | > 1.5 | Excess return per unit of downside risk |
| **Calmar Ratio** | Ann. Return / Max Drawdown | > 1.0 | Return per unit of worst loss |
| **Information Ratio** | (R_p - R_b) / TE | > 0.5 | Active return per unit of tracking error |
| **Omega Ratio** | ∫(1-F(r))dr / ∫F(r)dr | > 1.5 | Probability-weighted gain/loss ratio |
| **Max Drawdown** | max peak-to-trough decline | < 20% | Worst cumulative loss experienced |
| **Hit Ratio** | % profitable trades | > 50% | Win frequency (context-dependent) |
| **Profit Factor** | Gross profit / Gross loss | > 1.5 | Dollar gain per dollar lost |

## Methodology

### Step 1: Basic Return and Risk Metrics

```python
import numpy as np
import pandas as pd

def compute_returns(prices, method='arithmetic'):
    """Compute return series from price series."""
    if method == 'arithmetic':
        return prices.pct_change().dropna()
    elif method == 'log':
        return np.log(prices / prices.shift(1)).dropna()

def annualized_return(returns, periods_per_year=252):
    """Annualized geometric return."""
    total_return = (1 + returns).prod()
    n_periods = len(returns)
    return total_return ** (periods_per_year / n_periods) - 1

def annualized_volatility(returns, periods_per_year=252):
    """Annualized standard deviation of returns."""
    return returns.std() * np.sqrt(periods_per_year)

def downside_deviation(returns, mar=0.0, periods_per_year=252):
    """
    Downside deviation: std of returns below the minimum acceptable return (MAR).
    Only negative deviations count.
    """
    downside = returns[returns < mar] - mar
    if len(downside) == 0:
        return 0.0
    return np.sqrt((downside ** 2).mean()) * np.sqrt(periods_per_year)
```

### Step 2: Risk-Adjusted Return Ratios

```python
def sharpe_ratio(returns, risk_free_rate=0.0, periods_per_year=252):
    """
    Sharpe Ratio = (annualized return - risk-free rate) / annualized volatility.

    Interpretation guidelines:
    - < 0.5: poor
    - 0.5 - 1.0: acceptable
    - 1.0 - 2.0: good
    - > 2.0: excellent (verify — may indicate data issues or overfitting)
    - > 3.0: almost certainly too good to be true in live trading

    Common pitfalls:
    - Computed from backtests without transaction costs = inflated
    - Short sample period = high standard error
    - Non-normal returns (fat tails, skew) make Sharpe misleading
    """
    ann_ret = annualized_return(returns, periods_per_year)
    ann_vol = annualized_volatility(returns, periods_per_year)
    if ann_vol == 0:
        return 0.0
    return (ann_ret - risk_free_rate) / ann_vol

def sharpe_ratio_standard_error(sharpe, n_observations, skew=0, kurtosis=3):
    """
    Standard error of the Sharpe ratio (Lo, 2002).
    With non-normal returns, SE increases with skew and kurtosis.
    """
    se = np.sqrt(
        (1 + 0.5 * sharpe**2 - skew * sharpe + (kurtosis - 3) / 4 * sharpe**2)
        / n_observations
    )
    return se

def deflated_sharpe_ratio(observed_sharpe, n_trials, n_observations,
                           skew=0, kurtosis=3):
    """
    Bailey and Lopez de Prado (2014): Deflated Sharpe Ratio.
    Adjusts for multiple testing — the more strategies you test,
    the higher the expected maximum Sharpe by chance.

    Returns probability that the observed Sharpe is genuine (not from luck).
    """
    from scipy.stats import norm

    # Expected maximum Sharpe from n_trials of random strategies
    e_max_sharpe = norm.ppf(1 - 1/n_trials) * np.sqrt(1/n_observations)
    # Correct for non-normality
    e_max_sharpe *= np.sqrt(1 + 0.5 * (kurtosis - 3))

    se = sharpe_ratio_standard_error(observed_sharpe, n_observations, skew, kurtosis)

    # Probability that observed Sharpe exceeds expected maximum
    dsr = norm.cdf((observed_sharpe - e_max_sharpe) / se)

    return dsr

def sortino_ratio(returns, risk_free_rate=0.0, mar=0.0, periods_per_year=252):
    """
    Sortino Ratio: like Sharpe but penalizes only downside volatility.
    Better for strategies with asymmetric return distributions (e.g., options selling).
    """
    ann_ret = annualized_return(returns, periods_per_year)
    dd = downside_deviation(returns, mar, periods_per_year)
    if dd == 0:
        return 0.0
    return (ann_ret - risk_free_rate) / dd

def information_ratio(returns, benchmark_returns, periods_per_year=252):
    """
    Information Ratio = active return / tracking error.
    Measures skill of active management relative to benchmark.

    Guidelines:
    - 0.0 - 0.3: below average
    - 0.3 - 0.5: average
    - 0.5 - 0.7: good
    - > 0.7: exceptional (top decile of managers)
    """
    active_returns = returns - benchmark_returns
    ann_active = annualized_return(active_returns, periods_per_year)
    te = annualized_volatility(active_returns, periods_per_year)
    if te == 0:
        return 0.0
    return ann_active / te

def calmar_ratio(returns, periods_per_year=252):
    """
    Calmar Ratio = annualized return / maximum drawdown.
    Focuses on the worst-case loss experience.
    """
    ann_ret = annualized_return(returns, periods_per_year)
    mdd = max_drawdown(returns)
    if mdd == 0:
        return 0.0
    return ann_ret / abs(mdd)
```

### Step 3: Drawdown Analysis

```python
def max_drawdown(returns):
    """Maximum peak-to-trough drawdown."""
    cum_returns = (1 + returns).cumprod()
    running_max = cum_returns.cummax()
    drawdown = cum_returns / running_max - 1
    return drawdown.min()

def drawdown_series(returns):
    """Full drawdown time series."""
    cum_returns = (1 + returns).cumprod()
    running_max = cum_returns.cummax()
    drawdown = cum_returns / running_max - 1
    return drawdown

def drawdown_analysis(returns):
    """
    Comprehensive drawdown statistics.
    """
    dd = drawdown_series(returns)
    cum_ret = (1 + returns).cumprod()

    # Find drawdown periods
    in_drawdown = dd < 0
    drawdown_starts = in_drawdown & ~in_drawdown.shift(1, fill_value=False)
    drawdown_ends = ~in_drawdown & in_drawdown.shift(1, fill_value=False)

    drawdowns = []
    starts = dd.index[drawdown_starts]
    ends = dd.index[drawdown_ends]

    for i, start in enumerate(starts):
        end = ends[ends > start][0] if any(ends > start) else dd.index[-1]
        period_dd = dd[start:end]
        trough_date = period_dd.idxmin()

        drawdowns.append({
            'start': start,
            'trough': trough_date,
            'recovery': end,
            'depth': period_dd.min(),
            'duration_days': (end - start).days,
            'drawdown_days': (trough_date - start).days,
            'recovery_days': (end - trough_date).days,
        })

    dd_df = pd.DataFrame(drawdowns).sort_values('depth')

    stats = {
        'max_drawdown': dd.min(),
        'avg_drawdown': dd[dd < 0].mean(),
        'max_duration_days': dd_df['duration_days'].max() if len(dd_df) > 0 else 0,
        'avg_recovery_days': dd_df['recovery_days'].mean() if len(dd_df) > 0 else 0,
        'n_drawdowns': len(dd_df),
        'top_5_drawdowns': dd_df.head(5),
        'underwater_pct': (dd < 0).mean(),  # % of time in drawdown
    }

    return stats
```

### Step 4: Trade-Level Metrics

```python
def trade_statistics(trades_df):
    """
    Compute trade-level performance metrics.
    trades_df: DataFrame with columns ['pnl', 'return', 'duration', 'side']
    """
    winners = trades_df[trades_df['pnl'] > 0]
    losers = trades_df[trades_df['pnl'] < 0]

    stats = {
        'n_trades': len(trades_df),
        'hit_ratio': len(winners) / len(trades_df) if len(trades_df) > 0 else 0,
        'profit_factor': winners['pnl'].sum() / abs(losers['pnl'].sum()) if len(losers) > 0 else float('inf'),
        'avg_win': winners['pnl'].mean() if len(winners) > 0 else 0,
        'avg_loss': losers['pnl'].mean() if len(losers) > 0 else 0,
        'win_loss_ratio': abs(winners['pnl'].mean() / losers['pnl'].mean()) if len(losers) > 0 else float('inf'),
        'largest_win': winners['pnl'].max() if len(winners) > 0 else 0,
        'largest_loss': losers['pnl'].min() if len(losers) > 0 else 0,
        'avg_duration': trades_df['duration'].mean(),
        'expectancy': trades_df['pnl'].mean(),  # avg PnL per trade
        'total_pnl': trades_df['pnl'].sum(),
    }

    # Recovery factor: total PnL / max drawdown of equity curve
    equity = trades_df['pnl'].cumsum()
    stats['recovery_factor'] = equity.iloc[-1] / abs((equity - equity.cummax()).min()) \
        if (equity - equity.cummax()).min() < 0 else float('inf')

    return stats
```

### Step 5: Omega Ratio

```python
def omega_ratio(returns, threshold=0.0):
    """
    Omega ratio: probability-weighted ratio of gains to losses
    relative to a threshold.

    Unlike Sharpe, captures the full return distribution
    (not just mean and variance).

    Omega > 1: gains outweigh losses at the threshold
    Omega = 1 + (E[R] - threshold) / E[max(threshold - R, 0)]
    """
    excess = returns - threshold
    gains = excess[excess > 0].sum()
    losses = abs(excess[excess <= 0].sum())

    if losses == 0:
        return float('inf')

    return gains / losses
```

### Step 6: Comprehensive Report

```python
def performance_report(returns, benchmark_returns=None, risk_free_rate=0.0,
                       periods_per_year=252):
    """
    Full performance report.
    """
    report = {
        # Return metrics
        'total_return': (1 + returns).prod() - 1,
        'ann_return': annualized_return(returns, periods_per_year),
        'ann_volatility': annualized_volatility(returns, periods_per_year),
        'skewness': returns.skew(),
        'kurtosis': returns.kurtosis() + 3,  # excess -> raw

        # Risk-adjusted
        'sharpe_ratio': sharpe_ratio(returns, risk_free_rate, periods_per_year),
        'sortino_ratio': sortino_ratio(returns, risk_free_rate, 0.0, periods_per_year),
        'calmar_ratio': calmar_ratio(returns, periods_per_year),
        'omega_ratio': omega_ratio(returns, 0.0),

        # Drawdown
        'max_drawdown': max_drawdown(returns),
        **drawdown_analysis(returns),

        # Distribution
        'best_day': returns.max(),
        'worst_day': returns.min(),
        'pct_positive_days': (returns > 0).mean(),
    }

    if benchmark_returns is not None:
        report['information_ratio'] = information_ratio(
            returns, benchmark_returns, periods_per_year
        )
        report['beta'] = returns.cov(benchmark_returns) / benchmark_returns.var()
        report['alpha'] = report['ann_return'] - report['beta'] * annualized_return(
            benchmark_returns, periods_per_year
        )
        report['tracking_error'] = annualized_volatility(
            returns - benchmark_returns, periods_per_year
        )

    # Sharpe ratio confidence
    report['sharpe_se'] = sharpe_ratio_standard_error(
        report['sharpe_ratio'], len(returns),
        report['skewness'], report['kurtosis']
    )
    report['sharpe_95_ci'] = (
        report['sharpe_ratio'] - 1.96 * report['sharpe_se'],
        report['sharpe_ratio'] + 1.96 * report['sharpe_se']
    )

    return report
```

## Examples

### Interpreting a Strategy Report

```python
# Strategy: Equity momentum, 2010-2024
report = performance_report(strategy_returns, sp500_returns)
# Ann. Return: 12.5%, Vol: 14%, Sharpe: 0.89, Sortino: 1.32
# Max DD: -22%, Calmar: 0.57, IR: 0.45
# Sharpe SE: 0.15, 95% CI: [0.60, 1.18]

# Interpretation:
# - Sharpe 0.89 is decent but confidence interval includes 0.60 (mediocre)
# - Sortino >> Sharpe suggests positive skew (wins > losses)
# - Max DD of 22% is manageable for equity strategy
# - IR of 0.45 is average for active management
# - Need 5+ years of live trading to confirm in-sample results
```

### Applying the Deflated Sharpe Ratio

```python
# You tested 200 strategy variants and the best has Sharpe = 2.1
dsr = deflated_sharpe_ratio(
    observed_sharpe=2.1, n_trials=200,
    n_observations=2520,  # 10 years daily
    skew=-0.5, kurtosis=5
)
# DSR might be only 0.65 — 35% chance this Sharpe is just luck from 200 trials
```

## Quality Gate

- [ ] Returns computed correctly (geometric for compounding, arithmetic for attribution)
- [ ] Annualization uses correct factor (252 for daily, 12 for monthly, 52 for weekly)
- [ ] Sharpe ratio includes standard error and confidence interval
- [ ] Deflated Sharpe ratio applied when multiple strategies/parameters were tested
- [ ] Transaction costs and slippage included in return calculation
- [ ] Drawdown analysis includes duration and recovery time, not just depth
- [ ] Benchmark comparison uses an appropriate benchmark (not cherry-picked)
- [ ] Survivorship and look-ahead bias ruled out before celebrating good metrics
- [ ] Out-of-sample period explicitly separated from in-sample
- [ ] Reported Sharpe below 3.0 for realistic strategies — higher values require extraordinary justification
- [ ] Tail risk metrics (kurtosis, worst days, conditional VaR) reported alongside Sharpe
