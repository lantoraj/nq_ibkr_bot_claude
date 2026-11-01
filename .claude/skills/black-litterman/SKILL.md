---
name: black-litterman
description: "Black-Litterman model for portfolio allocation — combining equilibrium returns with investor views. Use when: User wants to incorporate subjective or model-driven views into portfolio optimization; Standard MVO produces extreme or unintuitive weights and the user needs a better starting point; Building a tactical overlay on top of a strategic benchmark allocation."
---

# Black-Litterman Model

> Black-Litterman model for portfolio allocation — combining equilibrium returns with investor views.

## When to Activate

- User wants to incorporate subjective or model-driven views into portfolio optimization
- Standard MVO produces extreme or unintuitive weights and the user needs a better starting point
- Building a tactical overlay on top of a strategic benchmark allocation
- Combining quantitative signals with an equilibrium prior
- Blending views of different confidence levels into a single allocation

## Core Concepts

### The Problem BL Solves

Mean-variance optimization requires expected return estimates, but:
- Historical means are extremely noisy (standard error of ~16%/sqrt(T) for equities)
- Small changes in expected returns produce wildly different portfolios
- Investors rarely have views on every asset — yet MVO forces estimates for all

Black and Litterman (1992) proposed starting from **equilibrium returns** (the market-implied view) and blending in investor views with explicit confidence levels.

### Equilibrium Returns (Prior)

The implied excess returns that make the current market portfolio optimal under MVO:

```
π = δ Σ w_mkt
```

Where:
- **δ**: risk aversion coefficient (typically 2.5, or calibrated from market Sharpe ratio: δ = SR_mkt / σ_mkt)
- **Σ**: covariance matrix of excess returns
- **w_mkt**: market capitalization weights

These equilibrium returns serve as the neutral starting point — if you have no views, you hold the market portfolio.

### Investor Views

Views are expressed as linear combinations of expected returns:

**Absolute view**: "Equity A will return 8% per year"
```
P = [1, 0, 0, ..., 0],  Q = [0.08]
```

**Relative view**: "Equity A will outperform Equity B by 2%"
```
P = [1, -1, 0, ..., 0],  Q = [0.02]
```

**Sector view**: "Tech will outperform Utilities by 3%"
```
P = [w_tech_1, w_tech_2, ..., -w_util_1, -w_util_2, ...],  Q = [0.03]
```

Each view k has an associated confidence expressed through the uncertainty matrix **Ω** (K x K diagonal matrix).

### The BL Formula

Posterior expected returns:

```
μ_BL = [(τΣ)^(-1) + P'Ω^(-1)P]^(-1) [(τΣ)^(-1)π + P'Ω^(-1)Q]
```

Posterior covariance:

```
Σ_BL = Σ + [(τΣ)^(-1) + P'Ω^(-1)P]^(-1)
```

Where:
- **τ**: scalar uncertainty on the prior (typically 0.025-0.05, reflects uncertainty in mean vs observation variance)
- **P**: view matrix (K x N)
- **Q**: view return vector (K x 1)
- **Ω**: view uncertainty matrix (K x K)

### Calibrating View Confidence (Ω)

This is the critical practical step. Approaches:

1. **Proportional to prior**: Ω = diag(P(τΣ)P') — Meucci's approach, ties view uncertainty to asset uncertainty
2. **Idzorek's method**: specify confidence as a percentage (0-100%), solve for Ω entry that produces the desired tilt
3. **From signal strength**: if views come from a quantitative model, use the model's prediction variance
4. **He and Litterman (1999)**: set Ω_kk = τ * p_k' Σ p_k (each view's uncertainty proportional to the variance of that portfolio)

## Methodology

### Step 1: Compute Equilibrium Returns

```python
import numpy as np

def implied_returns(delta, sigma, w_mkt):
    """Reverse-optimize to get equilibrium excess returns."""
    return delta * sigma @ w_mkt

# Calibrate delta from market Sharpe ratio
market_return = 0.07  # expected excess return
market_vol = 0.15
delta = market_return / (market_vol ** 2)  # approximately 3.1

# Market cap weights (example: 5 assets)
w_mkt = np.array([0.30, 0.25, 0.20, 0.15, 0.10])

pi = implied_returns(delta, sigma, w_mkt)
```

### Step 2: Specify Views

```python
# View 1: Asset 0 will return 10% (absolute)
# View 2: Asset 1 will outperform Asset 3 by 3% (relative)
K = 2  # number of views
N = 5  # number of assets

P = np.zeros((K, N))
P[0, 0] = 1.0                    # absolute view on asset 0
P[1, 1] = 1.0; P[1, 3] = -1.0   # relative view: asset 1 vs asset 3

Q = np.array([0.10, 0.03])

# View uncertainty (He-Litterman approach)
tau = 0.05
omega = np.diag([
    tau * P[0] @ sigma @ P[0],  # view 1 uncertainty
    tau * P[1] @ sigma @ P[1],  # view 2 uncertainty
])
```

### Step 3: Compute Posterior Returns

```python
def black_litterman(pi, sigma, P, Q, omega, tau=0.05):
    """Compute BL posterior expected returns and covariance."""
    tau_sigma_inv = np.linalg.inv(tau * sigma)
    omega_inv = np.linalg.inv(omega)

    # Posterior precision and mean
    posterior_precision = tau_sigma_inv + P.T @ omega_inv @ P
    posterior_cov = np.linalg.inv(posterior_precision)
    posterior_mean = posterior_cov @ (tau_sigma_inv @ pi + P.T @ omega_inv @ Q)

    # Full posterior covariance for optimization
    sigma_BL = sigma + posterior_cov

    return posterior_mean, sigma_BL

mu_BL, sigma_BL = black_litterman(pi, sigma, P, Q, omega, tau)
```

### Step 4: Optimize with BL Outputs

```python
import cvxpy as cp

w = cp.Variable(N)
ret = mu_BL @ w
risk = cp.quad_form(w, sigma_BL)
prob = cp.Problem(
    cp.Maximize(ret - delta * risk),
    [cp.sum(w) == 1, w >= 0]
)
prob.solve()
optimal_weights = w.value
```

### Step 5: Analyze Weight Tilts

The power of BL is that weights move intuitively from the benchmark:
- Assets with positive absolute views get overweighted
- In relative views, the outperformer gets overweighted and the underperformer gets underweighted
- Assets with no views stay near market-cap weights
- Higher confidence views produce larger tilts

## Examples

### Factor-Based Views in BL

Instead of asset-level views, express views on factors:

```python
# Factor exposures: B is N x F matrix (N assets, F factors)
# View: "Value factor will return 3% next year" with moderate confidence
# Convert factor view to asset-space: P_factor = B[:, value_col].T
P_factor = factor_loadings[:, 0].reshape(1, -1)  # value factor
Q_factor = np.array([0.03])
omega_factor = np.array([[tau * P_factor @ sigma @ P_factor.T]])
```

### Idzorek Confidence Calibration

```python
def idzorek_omega(P, sigma, tau, Q, pi, delta, w_mkt, confidence_pct):
    """
    confidence_pct: array of confidences from 0 (no view) to 1 (certainty)
    Returns diagonal omega matrix.
    """
    omega_diag = np.zeros(len(Q))
    for k in range(len(Q)):
        # At 100% confidence: omega_kk -> 0 (certain view)
        # At 0% confidence: omega_kk -> inf (no view, stay at equilibrium)
        p_k = P[k:k+1, :]
        alpha = 1.0 / confidence_pct[k] - 1.0
        omega_diag[k] = alpha * (p_k @ (tau * sigma) @ p_k.T).item()
    return np.diag(omega_diag)

confidence = np.array([0.75, 0.50])  # 75% confident in view 1, 50% in view 2
omega = idzorek_omega(P, sigma, tau, Q, pi, delta, w_mkt, confidence)
```

### Full Workflow with Real Data

```python
import pandas as pd

# Load market data
prices = pd.read_csv('prices.csv', index_col=0, parse_dates=True)
returns = prices.pct_change().dropna()
market_caps = pd.Series({'SPY': 4.5e12, 'EFA': 2.1e12, 'EEM': 0.8e12,
                         'AGG': 1.5e12, 'TLT': 0.3e12})

w_mkt = (market_caps / market_caps.sum()).values

from sklearn.covariance import LedoitWolf
sigma = LedoitWolf().fit(returns).covariance_ * 252  # annualize

pi = implied_returns(delta=2.5, sigma=sigma, w_mkt=w_mkt)

# Views: EM will outperform DM by 2%, Bonds underweight
P = np.array([
    [0, -1, 1, 0, 0],    # EEM - EFA
    [0, 0, 0, -0.5, -0.5] # underweight bonds (won't sum to 0 — need asset on other side)
])
# Better: relative view needs both sides
P = np.array([
    [0, -1, 1, 0, 0],    # EEM outperforms EFA by 2%
    [0.5, 0.5, 0, -0.5, -0.5]  # equities outperform bonds by 4%
])
Q = np.array([0.02, 0.04])
```

## Quality Gate

- [ ] Equilibrium returns computed from market-cap weights and a calibrated risk aversion parameter
- [ ] Views expressed correctly — relative views have P rows summing to zero
- [ ] View confidence (Ω) calibrated using a principled method (He-Litterman, Idzorek, or signal-based)
- [ ] τ chosen appropriately (0.025-0.05 range, or calibrated from data)
- [ ] Posterior returns are between the prior (equilibrium) and the views — sanity check
- [ ] Weight tilts are directionally consistent with views
- [ ] Assets without views remain near benchmark weights
- [ ] Covariance matrix used for both equilibrium computation and BL formula is the same
- [ ] Out-of-sample evaluation: do BL-informed portfolios improve on equilibrium allocation?
- [ ] Compared against simpler approaches (e.g., direct signal-to-weight mapping) to justify BL complexity
