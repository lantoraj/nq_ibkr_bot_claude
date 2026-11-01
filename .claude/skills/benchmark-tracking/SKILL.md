---
name: benchmark-tracking
description: "Index tracking and replication strategies — full replication, sampling, and optimization. Use when: User is building an index-tracking portfolio or ETF; Minimizing tracking error against a benchmark with fewer securities; Understanding ETF creation/redemption mechanics."
---

# Benchmark Tracking

> Index tracking and replication strategies — full replication, sampling, and optimization.

## When to Activate

- User is building an index-tracking portfolio or ETF
- Minimizing tracking error against a benchmark with fewer securities
- Understanding ETF creation/redemption mechanics
- Handling index reconstitution and rebalancing events
- Evaluating tracking error sources and budgeting

## Core Concepts

### Replication Methods

| Method | Holdings | Tracking Error | Cost | When to Use |
|--------|----------|---------------|------|-------------|
| **Full Replication** | All index constituents | Lowest (~1-10 bps) | Highest trading cost | Liquid indices (S&P 500) |
| **Stratified Sampling** | Subset matching factor exposures | Low-moderate (5-30 bps) | Lower trading cost | Large/illiquid indices |
| **Optimization-Based** | Optimized subset | Lowest for given # holdings | Model risk | Broad indices (Russell 3000, MSCI ACWI) |
| **Synthetic (Swaps)** | Swap contract | Near zero (counterparty risk) | Swap fees | European ETFs, tax optimization |

### Tracking Error

The standard deviation of the difference between portfolio and benchmark returns:

```
TE = std(R_p - R_b) * sqrt(252)    (annualized, from daily returns)
```

Sources of tracking error:
- **Sampling error**: not holding all index constituents
- **Cash drag**: uninvested cash from dividends, inflows
- **Transaction costs**: rebalancing, reconstitution trading
- **Corporate actions**: dividends, splits, mergers handled differently
- **Fair value pricing**: NAV vs market price differences
- **Securities lending**: income offsets costs but introduces risk
- **Withholding taxes**: cross-border dividend taxation

### ETF Creation/Redemption

The authorized participant (AP) mechanism keeps ETF prices close to NAV:

**Creation**: AP delivers a basket of underlying securities to the ETF issuer, receives ETF shares in return. Occurs when ETF trades at a premium (ETF price > NAV).

**Redemption**: AP delivers ETF shares to the issuer, receives underlying securities. Occurs when ETF trades at a discount (ETF price < NAV).

This in-kind mechanism is tax-efficient — no cash changes hands for the fund, so no capital gains are triggered.

## Methodology

### Step 1: Full Replication

```python
import pandas as pd
import numpy as np

def full_replication(index_weights, portfolio_value, lot_sizes=None):
    """
    Compute share counts for full replication.
    Handle lot-size constraints and residual cash.
    """
    target_dollars = index_weights * portfolio_value
    shares = target_dollars / prices

    if lot_sizes is not None:
        # Round to lot sizes (e.g., 100-share lots for some markets)
        shares = (shares / lot_sizes).round() * lot_sizes

    actual_dollars = shares * prices
    actual_weights = actual_dollars / actual_dollars.sum()
    residual_cash = portfolio_value - actual_dollars.sum()

    # Tracking error from rounding
    weight_diff = actual_weights - index_weights
    te_contribution = weight_diff  # proportional to tracking error

    return shares, actual_weights, residual_cash
```

### Step 2: Stratified Sampling

```python
def stratified_sample(index_data, target_holdings=200):
    """
    Select a subset of securities that matches the index on key dimensions:
    1. Sector weights
    2. Country/region weights
    3. Market cap distribution
    4. Factor exposures (beta, value, momentum)
    5. Duration/credit (for fixed income)
    """
    # Define strata: sector x size buckets
    index_data['size_bucket'] = pd.qcut(index_data['market_cap'], 3, labels=['S','M','L'])
    strata = index_data.groupby(['sector', 'size_bucket'])

    selected = []
    for (sector, size), group in strata:
        # Number of stocks to select from this stratum
        stratum_weight = group['weight'].sum()
        n_select = max(1, round(target_holdings * stratum_weight))

        # Select largest stocks in each stratum (most representative)
        top = group.nlargest(n_select, 'market_cap')
        selected.append(top)

    sample = pd.concat(selected)

    # Re-weight to match sector weights
    for sector in sample['sector'].unique():
        mask = sample['sector'] == sector
        target_sector_weight = index_data[index_data['sector'] == sector]['weight'].sum()
        current_sector_weight = sample.loc[mask, 'weight'].sum()
        sample.loc[mask, 'weight'] *= target_sector_weight / current_sector_weight

    # Normalize
    sample['weight'] /= sample['weight'].sum()

    return sample
```

### Step 3: Optimization-Based Tracking

```python
import cvxpy as cp

def tracking_portfolio(index_returns, candidate_returns, max_holdings=150,
                       te_budget=0.003):
    """
    Find portfolio weights that minimize tracking error using a subset of securities.

    index_returns: T x 1 benchmark return series
    candidate_returns: T x N matrix of candidate security returns
    """
    T, N = candidate_returns.shape
    w = cp.Variable(N)

    # Tracking error: variance of active returns
    active_returns = candidate_returns @ w - index_returns
    tracking_var = cp.sum_squares(active_returns) / T

    # Cardinality constraint via L1 regularization (relaxation)
    # For exact cardinality, use mixed-integer programming
    objective = cp.Minimize(tracking_var + 0.001 * cp.norm(w, 1))

    constraints = [
        cp.sum(w) == 1,
        w >= 0,
        w <= 0.05,  # max 5% per security
    ]

    prob = cp.Problem(objective, constraints)
    prob.solve()

    # Post-process: remove tiny weights
    weights = w.value
    weights[weights < 0.001] = 0
    weights /= weights.sum()

    return weights

def tracking_with_factor_matching(index_exposures, candidate_exposures,
                                   candidate_sigma, max_te=0.005):
    """
    Match factor exposures of the index while minimizing residual tracking error.
    """
    N = candidate_exposures.shape[0]
    F = candidate_exposures.shape[1]
    w = cp.Variable(N)

    # Factor exposure matching
    port_exposures = candidate_exposures.T @ w
    index_exp = index_exposures  # F x 1 vector

    # Minimize tracking error subject to factor matching
    te_sq = cp.quad_form(w, candidate_sigma)

    constraints = [
        cp.sum(w) == 1,
        w >= 0,
        # Match factor exposures within tolerance
        cp.norm(port_exposures - index_exp, 'inf') <= 0.1,
    ]

    prob = cp.Problem(cp.Minimize(te_sq), constraints)
    prob.solve()
    return w.value
```

### Step 4: Index Reconstitution Handling

```python
def reconstitution_trading(old_constituents, new_constituents, current_weights,
                           expected_volume, max_participation=0.10):
    """
    Handle index reconstitution (additions/deletions).
    Key challenge: everyone trades the same names on the same day.
    """
    additions = set(new_constituents) - set(old_constituents)
    deletions = set(old_constituents) - set(new_constituents)

    trades = {}

    for stock in additions:
        target_weight = new_constituents[stock]
        # Estimate market impact: added stocks face buying pressure
        est_volume = expected_volume[stock]
        shares_needed = target_weight * portfolio_value / prices[stock]
        days_to_trade = shares_needed / (est_volume * max_participation)
        trades[stock] = {
            'action': 'BUY', 'target_weight': target_weight,
            'est_days': max(1, int(np.ceil(days_to_trade))),
            'impact_warning': days_to_trade > 3
        }

    for stock in deletions:
        current_weight = current_weights.get(stock, 0)
        trades[stock] = {
            'action': 'SELL', 'current_weight': current_weight,
            'est_days': 1,  # deletions typically liquid enough
        }

    # Pre-trade: can start buying additions before effective date
    # Post-trade: sell deletions after effective date to reduce impact
    return trades
```

### Step 5: Tracking Error Budget

```python
def te_budget_analysis(portfolio_weights, benchmark_weights, sigma,
                       factor_exposures, factor_cov, specific_risk):
    """
    Decompose tracking error into components for budgeting.
    """
    active_weights = portfolio_weights - benchmark_weights

    # Total ex-ante tracking error
    te_total = np.sqrt(active_weights @ sigma @ active_weights) * np.sqrt(252)

    # Factor tracking error
    active_factor_exp = factor_exposures.T @ active_weights
    te_factor = np.sqrt(active_factor_exp @ factor_cov @ active_factor_exp) * np.sqrt(252)

    # Specific (idiosyncratic) tracking error
    te_specific = np.sqrt((active_weights ** 2) @ (specific_risk ** 2)) * np.sqrt(252)

    budget = {
        'total_te': te_total,
        'factor_te': te_factor,
        'specific_te': te_specific,
        'sector_te': compute_sector_te(active_weights, sigma),  # sector contribution
        'cash_drag_te': estimate_cash_drag_te(avg_cash_pct=0.005),
    }

    return budget

def estimate_cash_drag_te(avg_cash_pct, benchmark_vol=0.15):
    """Cash drag TE approximately equals cash_pct * benchmark_vol."""
    return avg_cash_pct * benchmark_vol
```

## Examples

### Tracking S&P 500 with 200 Stocks

```python
# Top 200 by market cap covers ~85% of index weight
# Optimization reduces TE from ~50 bps (naive) to ~15 bps
sp500 = load_sp500_constituents()
sample = stratified_sample(sp500, target_holdings=200)

# Expected TE sources:
# Sampling: ~10-15 bps
# Cash drag: ~5-8 bps (0.5% average cash * 15% vol)
# Rebalancing: ~3-5 bps
# Total: ~15-25 bps annualized
```

### Securities Lending Revenue

```python
# ETFs offset costs through securities lending
lending_revenue = {
    'US Large Cap': 0.01,       # 1 bp (low demand)
    'US Small Cap': 0.05,       # 5 bps
    'Emerging Markets': 0.10,   # 10 bps
    'High Yield Bonds': 0.08,   # 8 bps
}
# Lending revenue partially offsets expense ratio and trading costs
```

## Quality Gate

- [ ] Tracking error measured correctly (annualized std of daily return differences)
- [ ] Replication method appropriate for index size and liquidity
- [ ] Stratified sampling matches key dimensions (sector, size, factor exposures)
- [ ] Cash drag estimated and managed (dividend reinvestment, flow management)
- [ ] Reconstitution costs estimated — pre-positioning considered for predictable changes
- [ ] Tracking error budget decomposed into factor, specific, and cash components
- [ ] Securities lending terms reviewed (counterparty risk, collateral, revenue split)
- [ ] Synthetic replication counterparty risk assessed (swap provider creditworthiness)
- [ ] Corporate action handling procedures documented and tested
- [ ] Realized TE compared to ex-ante TE estimate — persistent gaps indicate model issues
