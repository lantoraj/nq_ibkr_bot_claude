---
name: risk-parity
description: "Risk parity and equal risk contribution portfolios — balancing risk, not capital. Use when: User wants a portfolio where each asset contributes equally to total risk; Building an All Weather-style portfolio across asset classes; Implementing Hierarchical Risk Parity (HRP) as an alternative to MVO."
---

# Risk Parity

> Risk parity and equal risk contribution portfolios — balancing risk, not capital.

## When to Activate

- User wants a portfolio where each asset contributes equally to total risk
- Building an All Weather-style portfolio across asset classes
- Implementing Hierarchical Risk Parity (HRP) as an alternative to MVO
- Designing leveraged risk parity strategies
- Comparing risk-based allocation methods (ERC, inverse volatility, minimum variance)

## Core Concepts

### Why Risk Parity?

Traditional 60/40 portfolios have a hidden problem: equities dominate the risk budget. In a 60% equity / 40% bond portfolio, equities contribute roughly 90% of portfolio variance. Risk parity asks: what if each asset class contributed equally to risk?

### Equal Risk Contribution (ERC)

A portfolio where each asset's marginal contribution to risk (MCR) times its weight equals the same value for all assets:

```
w_i * (Σw)_i / σ_p = 1/N    for all i
```

Equivalently, the risk contribution of asset i is:

```
RC_i = w_i * ∂σ_p/∂w_i = w_i * (Σw)_i / σ_p
```

ERC requires: RC_1 = RC_2 = ... = RC_N = σ_p / N

### Inverse Volatility (Naive Risk Parity)

The simplest approximation — ignoring correlations:

```
w_i = (1/σ_i) / Σ(1/σ_j)
```

This is exact ERC only when all pairwise correlations are equal. In practice, it is a reasonable starting point but underweights the diversification benefit of low-correlation assets.

### Risk Parity Across Asset Classes

The Bridgewater All Weather framework allocates risk equally across economic regimes:
- **Rising growth**: equities, corporate credit, commodities
- **Falling growth**: nominal bonds, inflation-linked bonds
- **Rising inflation**: commodities, inflation-linked bonds, EM
- **Falling inflation**: nominal bonds, equities

Each regime-asset pair gets equal risk allocation. Since bonds have lower volatility than equities, they receive proportionally higher capital allocation — requiring leverage to achieve competitive returns.

## Methodology

### Step 1: Compute the ERC Portfolio

```python
import numpy as np
from scipy.optimize import minimize

def risk_parity_objective(w, sigma):
    """
    Minimize the sum of squared differences between each asset's
    risk contribution and the target (equal) risk contribution.
    """
    w = np.array(w)
    port_var = w @ sigma @ w
    port_vol = np.sqrt(port_var)
    marginal_contrib = sigma @ w
    risk_contrib = w * marginal_contrib / port_vol
    target_rc = port_vol / len(w)
    return np.sum((risk_contrib - target_rc) ** 2)

def solve_risk_parity(sigma, budget=None):
    """
    Solve for ERC weights. Optional risk budget for non-equal contributions.
    """
    n = sigma.shape[0]
    if budget is None:
        budget = np.ones(n) / n

    w0 = np.ones(n) / n
    bounds = [(0.01, None)] * n  # long-only, minimum weight
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]

    result = minimize(
        risk_parity_objective, w0, args=(sigma,),
        method='SLSQP', bounds=bounds, constraints=constraints
    )
    return result.x
```

### Step 2: Alternative — Spinu's Formulation

A more elegant formulation using the convex reformulation by Spinu (2013):

```python
def risk_parity_spinu(sigma, budget=None):
    """
    Solve risk budgeting problem using Spinu's convex formulation.
    Minimizes: 0.5 * y'Σy - Σ b_i * ln(y_i)
    Then normalize: w = y / sum(y)
    """
    n = sigma.shape[0]
    if budget is None:
        budget = np.ones(n) / n

    y0 = np.ones(n) / n

    def objective(y):
        return 0.5 * y @ sigma @ y - budget @ np.log(y)

    def gradient(y):
        return sigma @ y - budget / y

    bounds = [(1e-8, None)] * n
    result = minimize(objective, y0, jac=gradient, method='L-BFGS-B', bounds=bounds)
    y = result.x
    return y / np.sum(y)
```

### Step 3: Hierarchical Risk Parity (HRP)

Lopez de Prado (2016) proposed HRP as a machine-learning alternative to MVO that does not require matrix inversion and handles singular covariance matrices:

```python
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import squareform

def hierarchical_risk_parity(returns):
    """
    HRP algorithm:
    1. Tree clustering on correlation distance
    2. Quasi-diagonalization (reorder assets by cluster)
    3. Recursive bisection to allocate weights
    """
    cov = returns.cov()
    corr = returns.corr()

    # Step 1: Hierarchical clustering
    dist = np.sqrt(0.5 * (1 - corr))  # correlation distance
    link = linkage(squareform(dist.values), method='single')
    sort_ix = leaves_list(link)

    # Step 2: Quasi-diagonalization
    sorted_assets = corr.index[sort_ix].tolist()

    # Step 3: Recursive bisection
    weights = pd.Series(1.0, index=sorted_assets)
    clusters = [sorted_assets]

    while clusters:
        new_clusters = []
        for cluster in clusters:
            if len(cluster) <= 1:
                continue
            mid = len(cluster) // 2
            left = cluster[:mid]
            right = cluster[mid:]

            # Inverse-variance allocation between halves
            cov_left = cov.loc[left, left]
            cov_right = cov.loc[right, right]

            var_left = get_cluster_var(cov_left)
            var_right = get_cluster_var(cov_right)

            alpha = 1 - var_left / (var_left + var_right)

            weights[left] *= alpha
            weights[right] *= (1 - alpha)

            new_clusters.extend([left, right])
        clusters = [c for c in new_clusters if len(c) > 1]

    return weights / weights.sum()

def get_cluster_var(cov):
    """Variance of the inverse-variance portfolio of a cluster."""
    ivp = 1 / np.diag(cov)
    ivp /= ivp.sum()
    return ivp @ cov @ ivp
```

### Step 4: Leverage in Risk Parity

Risk parity portfolios typically have low expected returns (heavy bond allocation). Leverage is used to scale up the risk/return profile:

```python
def levered_risk_parity(w_rp, sigma, target_vol=0.10, borrow_cost=0.02):
    """Scale risk parity portfolio to target volatility."""
    port_vol = np.sqrt(w_rp @ sigma @ w_rp)
    leverage = target_vol / port_vol  # e.g., 2-3x for typical RP
    w_levered = w_rp * leverage

    # Cost of leverage
    excess_capital = leverage - 1  # borrowing beyond 100%
    leverage_drag = excess_capital * borrow_cost

    return w_levered, leverage, leverage_drag
```

Leverage considerations:
- Futures-based implementation avoids explicit borrowing (embedded leverage)
- Margin requirements constrain practical leverage (typically 2-3x)
- Leverage amplifies drawdowns — the 2020 COVID crash hit leveraged RP hard
- Funding costs reduce net returns and fluctuate with rate cycles

## Examples

### Multi-Asset Risk Parity

```python
# 4-asset universe: Equities, Bonds, Commodities, TIPS
assets = ['SPY', 'TLT', 'DBC', 'TIP']
ann_vol = np.array([0.16, 0.12, 0.18, 0.06])
corr_matrix = np.array([
    [1.0, -0.3, 0.3, 0.0],
    [-0.3, 1.0, -0.1, 0.5],
    [0.3, -0.1, 1.0, 0.2],
    [0.0, 0.5, 0.2, 1.0]
])
sigma = np.diag(ann_vol) @ corr_matrix @ np.diag(ann_vol)

w_rp = solve_risk_parity(sigma)
# Typical result: ~15% equities, ~35% bonds, ~12% commodities, ~38% TIPS
# (bonds and TIPS get more capital because they have lower vol)
```

### Risk Budgeting (Non-Equal)

```python
# Allocate 40% of risk to equities, 30% to bonds, 20% to commodities, 10% to TIPS
budget = np.array([0.40, 0.30, 0.20, 0.10])
w_rb = solve_risk_parity(sigma)  # modify objective to use budget
```

### Comparing RP vs 60/40 vs GMV

```python
# 60/40
w_6040 = np.array([0.60, 0.40, 0.0, 0.0])
vol_6040 = np.sqrt(w_6040 @ sigma @ w_6040)  # ~10.5%
# Equity risk contribution: ~93%

# Risk parity (unlevered)
vol_rp = np.sqrt(w_rp @ sigma @ w_rp)  # ~5-6%
# Each asset contributes 25% of risk

# To match 60/40 risk level, lever RP by ~1.8x
```

## Quality Gate

- [ ] Verified that risk contributions are actually equal (or match target budget) after optimization
- [ ] Covariance matrix estimation uses shrinkage or factor model (garbage covariance = garbage RP)
- [ ] If levered, accounted for funding/borrowing costs in return estimates
- [ ] Compared against unlevered benchmarks at matching risk levels, not matching capital
- [ ] Tested sensitivity to correlation regime changes (correlations spike in crises)
- [ ] Rebalancing frequency and cost accounted for (RP portfolios can have high turnover)
- [ ] For HRP: validated clustering stability with bootstrap or different linkage methods
- [ ] Drawdown analysis includes the levered version under stress scenarios (2008, 2020, 2022)
- [ ] Implementation uses liquid instruments (futures preferred for leverage efficiency)
- [ ] Documented the choice between ERC, inverse-vol, and HRP with rationale
