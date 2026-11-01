---
name: markowitz-optimization
description: "Mean-variance optimization and efficient frontier construction for portfolio allocation. Use when: User needs to construct an optimal portfolio from a universe of assets; Building efficient frontiers or finding minimum-variance portfolios; Implementing constrained portfolio optimization (long-only, sector limits, turnover)."
---

# Markowitz Optimization

> Mean-variance optimization and efficient frontier construction for portfolio allocation.

## When to Activate

- User needs to construct an optimal portfolio from a universe of assets
- Building efficient frontiers or finding minimum-variance portfolios
- Implementing constrained portfolio optimization (long-only, sector limits, turnover)
- Dealing with estimation error in expected returns and covariance matrices
- Comparing robust optimization techniques (shrinkage, resampling, Bayesian)

## Core Concepts

### Mean-Variance Optimization (MVO)

The foundational framework introduced by Markowitz (1952). The investor selects portfolio weights w to:

```
minimize    w'Σw                (portfolio variance)
subject to  w'μ = μ_target     (target return)
            w'1 = 1             (full investment)
```

Key inputs:
- **μ**: vector of expected returns (N x 1)
- **Σ**: covariance matrix of returns (N x N)
- The output is a set of optimal weights for each target return level

### Efficient Frontier

The set of portfolios offering maximum return for each level of risk. Key points on the frontier:
- **Global Minimum Variance (GMV)**: lowest-risk portfolio, does not require return estimates
- **Maximum Sharpe Ratio (tangency portfolio)**: optimal risky portfolio when a risk-free asset exists
- **Maximum return**: trivially the single highest-expected-return asset

### The Estimation Error Problem

MVO is notoriously sensitive to input estimates. Small changes in expected returns produce wildly different allocations. This is the single most important practical challenge:
- Expected returns are estimated with far less precision than covariances
- MVO tends to overweight assets with high estimated returns and low estimated variance — often artifacts of estimation noise
- Resulting portfolios are concentrated, unstable, and perform poorly out-of-sample

Chopra and Ziemba (1993) showed that errors in means are roughly 10x more damaging than errors in variances, and 20x more than errors in covariances.

## Methodology

### Step 1: Estimate Inputs

**Expected Returns** — approaches ranked by robustness:
1. Historical mean returns (worst — very noisy for short histories)
2. CAPM equilibrium returns (better — anchored to market)
3. Factor model implied returns (good — structured estimation)
4. Black-Litterman posterior returns (best for active views)
5. Shrinkage toward equal returns or global mean (simple, effective)

**Covariance Matrix** — approaches:
1. Sample covariance (requires T >> N, otherwise singular or ill-conditioned)
2. Ledoit-Wolf shrinkage toward structured target (e.g., single-factor model, constant correlation)
3. Factor model covariance: Σ = BFB' + D where B is factor loadings, F is factor covariance, D is diagonal residual
4. Exponentially weighted covariance (half-life 60-120 days typical for equities)
5. DCC-GARCH for time-varying correlations

### Step 2: Apply Constraints

Practical portfolios always require constraints beyond full investment:

```python
# Common constraint types
constraints = {
    'long_only': w >= 0,                          # No short selling
    'box': lb <= w <= ub,                          # Position limits (e.g., 0-5%)
    'sector': A_sector @ w <= sector_max,          # Sector exposure caps
    'turnover': sum(|w - w_current|) <= turnover_max,  # Turnover limit
    'tracking_error': sqrt((w-w_b)'Σ(w-w_b)) <= TE_max,  # TE budget
    'cardinality': sum(w > 0) <= K,                # Max number of holdings
    'min_holding': w_i >= w_min if w_i > 0,        # Minimum position size
}
```

Cardinality and minimum holding constraints make the problem mixed-integer, requiring specialized solvers (Gurobi, CPLEX) or heuristic approaches.

### Step 3: Robust Optimization Techniques

**Shrinkage Estimators (Ledoit-Wolf)**:
- Shrink sample covariance toward a structured target
- Optimal shrinkage intensity minimizes expected out-of-sample loss
- `sklearn.covariance.LedoitWolf` implements the standard approach

**Resampled Efficient Frontier (Michaud, 1998)**:
1. Estimate μ and Σ from data
2. Simulate M sets of returns from N(μ, Σ)
3. For each simulation, compute the efficient frontier
4. Average the portfolio weights across simulations at each return level
5. Result: smoother, more diversified portfolios — but still debated theoretically

**Robust Optimization (worst-case)**:
- Define uncertainty sets around μ and Σ
- Solve: max over uncertainty set of the worst-case portfolio variance
- Leads to more conservative but stable allocations
- Equivalent to adding a regularization penalty in many cases

### Step 4: Solve and Validate

```python
import numpy as np
from scipy.optimize import minimize

def mean_variance_optimize(mu, sigma, target_return, long_only=True):
    n = len(mu)
    w0 = np.ones(n) / n

    bounds = [(0, 1)] * n if long_only else [(None, None)] * n

    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
        {'type': 'eq', 'fun': lambda w: w @ mu - target_return}
    ]

    result = minimize(
        lambda w: w @ sigma @ w,
        w0, method='SLSQP',
        bounds=bounds, constraints=constraints
    )
    return result.x

# For production, use cvxpy for convex formulation:
import cvxpy as cp

def mvo_cvxpy(mu, sigma, gamma=1.0):
    """gamma controls risk aversion: higher = more conservative"""
    n = len(mu)
    w = cp.Variable(n)
    ret = mu @ w
    risk = cp.quad_form(w, sigma)
    objective = cp.Maximize(ret - gamma * risk)
    constraints = [cp.sum(w) == 1, w >= 0]
    prob = cp.Problem(objective, constraints)
    prob.solve()
    return w.value
```

## Examples

### Constructing a Long-Only Efficient Frontier

```python
import numpy as np
import cvxpy as cp

# 5-asset universe
mu = np.array([0.08, 0.10, 0.12, 0.06, 0.09])  # expected annual returns
# Use Ledoit-Wolf shrinkage for covariance
from sklearn.covariance import LedoitWolf
lw = LedoitWolf().fit(historical_returns)
sigma = lw.covariance_

# Trace out the frontier
target_returns = np.linspace(0.06, 0.12, 50)
frontier_risk = []
frontier_weights = []

for tr in target_returns:
    w = cp.Variable(5)
    prob = cp.Problem(
        cp.Minimize(cp.quad_form(w, sigma)),
        [cp.sum(w) == 1, w >= 0, mu @ w == tr]
    )
    prob.solve()
    if prob.status == 'optimal':
        frontier_risk.append(np.sqrt(w.value @ sigma @ w.value))
        frontier_weights.append(w.value)
```

### Handling Turnover Constraints

```python
w_current = np.array([0.20, 0.25, 0.15, 0.20, 0.20])
max_turnover = 0.10  # 10% one-way turnover limit

w = cp.Variable(5)
turnover = cp.norm(w - w_current, 1)  # L1 norm = total turnover
prob = cp.Problem(
    cp.Maximize(mu @ w - gamma * cp.quad_form(w, sigma)),
    [cp.sum(w) == 1, w >= 0, turnover <= 2 * max_turnover]
    # Factor of 2 because L1 norm double-counts buys and sells
)
```

### Shrinkage Toward Equal Weights

When you distrust return estimates entirely, shrink toward 1/N:
```python
alpha = 0.5  # shrinkage intensity
mu_shrunk = alpha * mu + (1 - alpha) * np.mean(mu) * np.ones(n)
# Then optimize with mu_shrunk
```

DeMiguel, Garlappi, and Uppal (2009) showed 1/N outperforms many optimized portfolios out-of-sample for typical estimation windows. This is a humbling baseline.

## Quality Gate

- [ ] Covariance matrix is positive semi-definite (check eigenvalues > -epsilon)
- [ ] Used shrinkage or factor model for covariance — never raw sample covariance with N > T/2
- [ ] Expected return estimates come from a structured model, not raw historical means
- [ ] Applied realistic constraints (long-only, position limits, turnover)
- [ ] Validated that portfolio weights are not concentrated in 1-3 assets
- [ ] Compared optimized portfolio against 1/N and other naive benchmarks
- [ ] Tested sensitivity: perturb inputs by 1-2 standard errors and check weight stability
- [ ] Out-of-sample backtest with rolling or expanding window (not just in-sample frontier)
- [ ] Transaction costs included in any return comparison
- [ ] Documented the risk aversion parameter (gamma) choice and its impact
