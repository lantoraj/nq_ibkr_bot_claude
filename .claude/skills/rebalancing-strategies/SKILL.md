---
name: rebalancing-strategies
description: "Portfolio rebalancing methodologies — when, how, and how much to trade. Use when: User needs to decide how often and by what rules to rebalance a portfolio; Comparing calendar vs threshold vs tactical rebalancing; Minimizing rebalancing costs (transaction costs, taxes, market impact)."
---

# Rebalancing Strategies

> Portfolio rebalancing methodologies — when, how, and how much to trade.

## When to Activate

- User needs to decide how often and by what rules to rebalance a portfolio
- Comparing calendar vs threshold vs tactical rebalancing
- Minimizing rebalancing costs (transaction costs, taxes, market impact)
- Implementing tax-aware rebalancing with tax-loss harvesting
- Analyzing the rebalancing premium and drift tolerance

## Core Concepts

### Why Rebalance?

Portfolios drift from target weights as assets generate different returns. Without rebalancing:
- Risk profile changes — a 60/40 portfolio can drift to 75/25 after a bull market
- Factor exposures shift unintentionally
- Risk parity portfolios lose their equal-risk-contribution property

The **rebalancing premium** is a small but real return benefit from systematically selling winners and buying losers in a mean-reverting environment. Estimated at 0.15-0.50% annually for diversified multi-asset portfolios (Willenbrock, 2011).

### Rebalancing Approaches

| Method | Rule | Typical Frequency | Pros | Cons |
|--------|------|-------------------|------|------|
| **Calendar** | Rebalance on fixed dates | Monthly/Quarterly | Simple, predictable | May trade unnecessarily or miss large drifts |
| **Threshold** | Rebalance when drift exceeds band | Event-driven | Only trades when needed | Requires daily monitoring |
| **Calendar + Threshold** | Check on dates, trade only if drifted | Monthly check | Good balance | Slightly more complex |
| **Tactical** | Rebalance toward dynamic targets | Varies | Captures alpha | Requires timing skill |
| **Optimal** | Minimize cost function (drift penalty + trading cost) | Continuous | Theoretically best | Complex to implement |

### The Cost-Drift Tradeoff

Every rebalance incurs costs:
- **Explicit costs**: commissions, bid-ask spreads
- **Market impact**: price movement caused by trading
- **Tax costs**: realized capital gains (for taxable accounts)
- **Opportunity cost**: time and attention

But drift also has costs:
- **Risk budget violation**: portfolio risk exceeds target
- **Tracking error**: deviation from policy benchmark
- **Regulatory/mandate breaches**: violating IPS constraints

The optimal strategy minimizes total cost = trading costs + drift penalty.

## Methodology

### Step 1: Measure Drift

```python
import numpy as np
import pandas as pd

def compute_drift(current_weights, target_weights):
    """
    Multiple drift metrics:
    - Max absolute drift: max single-asset deviation
    - Sum absolute drift: total deviation (related to turnover needed)
    - Weighted drift: risk-adjusted deviation using volatility
    """
    diff = current_weights - target_weights
    metrics = {
        'max_drift': np.abs(diff).max(),
        'sum_drift': np.abs(diff).sum(),
        'rms_drift': np.sqrt((diff ** 2).mean()),
        'largest_overweight': diff.idxmax(),
        'largest_underweight': diff.idxmin()
    }
    return metrics

def drift_over_time(prices, target_weights, start_date):
    """Track portfolio drift without rebalancing."""
    returns = prices.pct_change()
    weights = target_weights.copy()

    drift_history = []
    for date, ret in returns.iterrows():
        # Update weights based on returns
        portfolio_value = (weights * (1 + ret)).sum()
        weights = weights * (1 + ret) / portfolio_value
        drift_history.append({
            'date': date,
            **compute_drift(weights, target_weights)
        })

    return pd.DataFrame(drift_history)
```

### Step 2: Calendar Rebalancing

```python
def calendar_rebalance(prices, target_weights, frequency='quarterly'):
    """
    Rebalance to target weights on fixed dates.
    frequency: 'monthly', 'quarterly', 'semi-annual', 'annual'
    """
    returns = prices.pct_change().dropna()
    rebal_dates = get_rebalance_dates(returns.index, frequency)

    weights = target_weights.copy()
    portfolio_returns = []
    turnover_history = []

    for date, ret in returns.iterrows():
        # Daily portfolio return
        port_ret = (weights * ret).sum()
        portfolio_returns.append(port_ret)

        # Update weights
        weights = weights * (1 + ret) / (1 + port_ret)

        # Rebalance on scheduled dates
        if date in rebal_dates:
            turnover = np.abs(weights - target_weights).sum() / 2  # one-way
            turnover_history.append({'date': date, 'turnover': turnover})
            weights = target_weights.copy()

    return pd.Series(portfolio_returns, index=returns.index), turnover_history
```

### Step 3: Threshold Rebalancing

```python
def threshold_rebalance(prices, target_weights, threshold=0.05,
                        partial=False, rebal_to='target'):
    """
    Rebalance when any asset drifts beyond threshold.

    partial: if True, only rebalance back to threshold edge (not target)
    rebal_to: 'target' (full) or 'edge' (partial, reduces trading)
    """
    returns = prices.pct_change().dropna()
    weights = target_weights.copy()
    portfolio_returns = []
    rebal_events = []

    for date, ret in returns.iterrows():
        port_ret = (weights * ret).sum()
        portfolio_returns.append(port_ret)
        weights = weights * (1 + ret) / (1 + port_ret)

        # Check if any asset breaches threshold
        drift = np.abs(weights - target_weights)
        if drift.max() > threshold:
            if rebal_to == 'target':
                new_weights = target_weights.copy()
            elif rebal_to == 'edge':
                # Partial rebalance: bring back to threshold edge
                new_weights = weights.copy()
                for asset in weights.index:
                    if weights[asset] > target_weights[asset] + threshold:
                        new_weights[asset] = target_weights[asset] + threshold * 0.5
                    elif weights[asset] < target_weights[asset] - threshold:
                        new_weights[asset] = target_weights[asset] - threshold * 0.5
                new_weights = new_weights / new_weights.sum()

            turnover = np.abs(weights - new_weights).sum() / 2
            rebal_events.append({'date': date, 'turnover': turnover})
            weights = new_weights

    return pd.Series(portfolio_returns, index=returns.index), rebal_events
```

### Step 4: Optimal Rebalancing (Cost Minimization)

```python
import cvxpy as cp

def optimal_rebalance(current_weights, target_weights, sigma,
                      tcost_bps=10, risk_aversion=1.0, tax_rates=None):
    """
    Optimal rebalance minimizing: drift_penalty + trading_cost + tax_cost.
    """
    n = len(current_weights)
    w = cp.Variable(n)
    trades = w - current_weights

    # Drift penalty: tracking error from target
    drift_penalty = risk_aversion * cp.quad_form(w - target_weights, sigma)

    # Transaction cost: proportional to trade size
    tcost = tcost_bps / 10000 * cp.norm(trades, 1)

    # Tax cost (if applicable)
    if tax_rates is not None:
        # Simplified: tax cost proportional to sales of appreciated positions
        tax_cost = sum(
            tax_rates[i] * cp.pos(-trades[i]) * max(0, unrealized_gain[i])
            for i in range(n)
        )
    else:
        tax_cost = 0

    objective = cp.Minimize(drift_penalty + tcost + tax_cost)
    constraints = [cp.sum(w) == 1, w >= 0]

    prob = cp.Problem(objective, constraints)
    prob.solve()
    return w.value
```

### Step 5: Tax-Aware Rebalancing

```python
def tax_loss_harvest(current_weights, cost_basis, current_prices,
                     target_weights, wash_sale_window=30):
    """
    Rebalance with tax-loss harvesting:
    1. Identify positions with unrealized losses
    2. Sell losers to realize losses (tax benefit)
    3. Replace with correlated substitute (avoid wash sale)
    4. Rebalance remaining positions toward target
    """
    unrealized_gains = (current_prices - cost_basis) / cost_basis

    harvest_candidates = []
    for i, gain in enumerate(unrealized_gains):
        if gain < -0.05:  # at least 5% loss to justify trading
            harvest_candidates.append({
                'asset': i,
                'loss': gain * current_weights[i],
                'substitute': find_substitute(i)  # correlated but not "substantially identical"
            })

    # Prioritize by tax benefit (loss size * tax rate)
    harvest_candidates.sort(key=lambda x: x['loss'])

    return harvest_candidates

def find_substitute(asset_idx):
    """
    Find a substitute asset that:
    1. Has high correlation (>0.95) with original
    2. Is not "substantially identical" (IRS wash sale rule)
    3. Maintains portfolio factor exposure
    Example: swap one S&P 500 ETF for another (SPY -> IVV)
    """
    pass
```

## Examples

### Comparing Rebalancing Frequencies

```python
# Backtest calendar rebalancing at different frequencies
for freq in ['monthly', 'quarterly', 'annual']:
    returns, turnover = calendar_rebalance(prices, target_weights, freq)
    ann_return = (1 + returns).prod() ** (252/len(returns)) - 1
    ann_turnover = sum(t['turnover'] for t in turnover) / (len(returns)/252)
    net_return = ann_return - ann_turnover * 0.001  # 10bps round-trip cost
    print(f"{freq}: return={ann_return:.2%}, turnover={ann_turnover:.1%}, "
          f"net={net_return:.2%}")
```

Typical finding: quarterly rebalancing captures most of the rebalancing premium with reasonable turnover. Monthly adds cost, annual allows excessive drift.

### Setting Threshold Bands

Rules of thumb for threshold width:
- **Tight (2-3%)**: for institutional mandates with strict tracking error limits
- **Medium (5%)**: good default for multi-asset portfolios
- **Wide (10%+)**: for taxable accounts where trading cost is high
- **Asymmetric**: wider bands for illiquid assets, tighter for liquid ones

```python
# Asset-specific thresholds based on volatility and liquidity
thresholds = {
    'US_Equity': 0.03,      # liquid, moderate vol
    'Intl_Equity': 0.04,    # slightly less liquid
    'EM_Equity': 0.05,      # less liquid, higher vol
    'US_Bonds': 0.02,       # low vol, drift slowly
    'Real_Estate': 0.07,    # illiquid, wider band
}
```

## Quality Gate

- [ ] Rebalancing strategy matches account type (taxable vs tax-exempt has very different optimal rules)
- [ ] Transaction costs included in all rebalancing comparisons
- [ ] Threshold bands set with reference to asset volatility and liquidity
- [ ] Tax-loss harvesting avoids wash sale violations (30-day rule)
- [ ] Partial rebalancing considered for high-cost environments
- [ ] Drift monitoring includes risk-adjusted metrics, not just weight deviation
- [ ] Cash flows used as rebalancing opportunities (deposit into underweight assets)
- [ ] Backtest covers multiple market regimes (trending markets penalize rebalancing)
- [ ] Rebalancing premium estimate is realistic (0.15-0.50%, not inflated)
- [ ] Operational feasibility verified — daily threshold monitoring requires infrastructure
