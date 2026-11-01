---
name: portfolio-attribution
description: "Decomposing portfolio returns into allocation, selection, and factor contributions. Use when: User needs to explain why a portfolio outperformed or underperformed its benchmark; Implementing Brinson-Fachler attribution for equity portfolios; Building factor-based attribution using regression or risk models."
---

# Portfolio Performance Attribution

> Decomposing portfolio returns into allocation, selection, and factor contributions.

## When to Activate

- User needs to explain why a portfolio outperformed or underperformed its benchmark
- Implementing Brinson-Fachler attribution for equity portfolios
- Building factor-based attribution using regression or risk models
- Performing fixed income attribution (duration, credit, curve)
- Linking single-period attribution across multiple periods

## Core Concepts

### What Is Attribution?

Attribution decomposes the active return (portfolio return minus benchmark return) into components that explain *where* and *how* value was added or lost. Two major frameworks:

1. **Holdings-based (Brinson)**: uses portfolio and benchmark weights and returns by sector/region
2. **Returns-based (factor regression)**: regresses portfolio returns on factor returns to identify exposures
3. **Risk-model-based**: uses a multi-factor risk model to decompose returns into factor and specific components

### Brinson-Fachler Attribution

Decomposes active return into three effects for each sector s:

**Allocation Effect**: did the manager overweight sectors that outperformed?
```
AE_s = (w_p,s - w_b,s) * (R_b,s - R_b)
```

**Selection Effect**: did the manager pick better stocks within each sector?
```
SE_s = w_b,s * (R_p,s - R_b,s)
```

**Interaction Effect**: combined effect of overweighting sectors where stock picks were also good
```
IE_s = (w_p,s - w_b,s) * (R_p,s - R_b,s)
```

Total active return: R_p - R_b = ΣAE_s + ΣSE_s + ΣIE_s

Where:
- w_p,s, w_b,s: portfolio and benchmark weight in sector s
- R_p,s, R_b,s: portfolio and benchmark return in sector s
- R_b: total benchmark return

### Factor-Based Attribution

Uses a multi-factor risk model (e.g., Barra, Axioma, Northfield):

```
R_p - R_f = Σ (β_p,k - β_b,k) * f_k + α_specific
```

Where β_p,k is the portfolio's exposure to factor k, and f_k is the factor return. Decomposes into:
- **Factor timing**: return from active factor bets
- **Specific return**: stock-level alpha (idiosyncratic return)

## Methodology

### Step 1: Brinson Attribution Implementation

```python
import pandas as pd
import numpy as np

def brinson_fachler(portfolio_weights, benchmark_weights,
                     portfolio_returns, benchmark_returns):
    """
    Single-period Brinson-Fachler attribution by sector.

    All inputs are Series indexed by sector.
    """
    total_bench_return = (benchmark_weights * benchmark_returns).sum()

    allocation = (portfolio_weights - benchmark_weights) * (benchmark_returns - total_bench_return)
    selection = benchmark_weights * (portfolio_returns - benchmark_returns)
    interaction = (portfolio_weights - benchmark_weights) * (portfolio_returns - benchmark_returns)

    result = pd.DataFrame({
        'port_weight': portfolio_weights,
        'bench_weight': benchmark_weights,
        'port_return': portfolio_returns,
        'bench_return': benchmark_returns,
        'allocation': allocation,
        'selection': selection,
        'interaction': interaction,
        'total_active': allocation + selection + interaction
    })

    # Verify: sum of total_active should equal portfolio return - benchmark return
    port_return = (portfolio_weights * portfolio_returns).sum()
    bench_return = (benchmark_weights * benchmark_returns).sum()
    assert abs(result['total_active'].sum() - (port_return - bench_return)) < 1e-10

    return result
```

### Step 2: Multi-Period Linking

Single-period attribution does not compound correctly across periods. Linking methods:

**Carino Method** (logarithmic smoothing):
```python
def carino_linking(single_period_attributions, portfolio_returns, benchmark_returns):
    """
    Link single-period Brinson attribution across T periods using Carino's method.
    """
    T = len(portfolio_returns)

    # Cumulative returns
    cum_port = np.prod(1 + portfolio_returns) - 1
    cum_bench = np.prod(1 + benchmark_returns) - 1

    # Carino scaling factors
    k_t = []
    for t in range(T):
        rp = portfolio_returns[t]
        rb = benchmark_returns[t]
        if abs(rp - rb) < 1e-12:
            k_t.append(1.0 / (1 + cum_port))
        else:
            ln_ratio_t = np.log(1 + rp) - np.log(1 + rb)
            ln_ratio_total = np.log(1 + cum_port) - np.log(1 + cum_bench)
            k_t.append((ln_ratio_t / (rp - rb)) / (ln_ratio_total / (cum_port - cum_bench)))

    # Scale each period's attribution by k_t
    linked = {}
    for effect in ['allocation', 'selection', 'interaction']:
        linked[effect] = sum(
            k_t[t] * single_period_attributions[t][effect]
            for t in range(T)
        )

    return linked
```

**GRAP Method** (geometric): another popular linking approach used by major custodians.

### Step 3: Factor-Based Attribution

```python
def factor_attribution(portfolio_exposures, benchmark_exposures,
                       factor_returns, specific_returns):
    """
    Attribution using a multi-factor risk model.

    portfolio_exposures: DataFrame (dates x factors) of portfolio factor exposures
    benchmark_exposures: DataFrame (dates x factors) of benchmark factor exposures
    factor_returns: DataFrame (dates x factors) of realized factor returns
    specific_returns: Series of portfolio-level specific returns
    """
    active_exposures = portfolio_exposures - benchmark_exposures

    # Factor contribution = active exposure * factor return (each period)
    factor_contrib = active_exposures * factor_returns

    # Group by factor category
    style_factors = ['Value', 'Momentum', 'Quality', 'Size', 'Volatility']
    industry_factors = [f for f in factor_returns.columns if f.startswith('IND_')]

    attribution = {
        'style': factor_contrib[style_factors].sum(axis=1).sum(),
        'industry': factor_contrib[industry_factors].sum(axis=1).sum(),
        'specific': specific_returns.sum(),
        'total_active': factor_contrib.sum(axis=1).sum() + specific_returns.sum()
    }

    return attribution
```

### Step 4: Fixed Income Attribution

Fixed income attribution requires different decomposition:

```python
def fi_attribution(portfolio, benchmark):
    """
    Fixed income attribution components:
    1. Income return (coupon/yield carry)
    2. Treasury curve effect (parallel shift + twist + curvature)
    3. Spread change effect (credit spread widening/tightening)
    4. Selection effect (individual security alpha)
    """
    components = {}

    # Income effect: difference in portfolio vs benchmark yield
    components['income'] = portfolio['yield'] - benchmark['yield']

    # Duration effect: sensitivity to parallel rate move
    rate_change = benchmark['rate_change']
    components['duration'] = -(portfolio['duration'] - benchmark['duration']) * rate_change

    # Curve positioning: key rate duration attribution
    for tenor in ['2Y', '5Y', '10Y', '30Y']:
        krd_active = portfolio[f'krd_{tenor}'] - benchmark[f'krd_{tenor}']
        components[f'curve_{tenor}'] = -krd_active * benchmark[f'rate_change_{tenor}']

    # Spread effect
    spread_change = benchmark['spread_change']
    components['spread_duration'] = -(portfolio['spread_duration'] - benchmark['spread_duration']) * spread_change

    # Credit selection (residual)
    components['selection'] = portfolio['total_return'] - benchmark['total_return'] - sum(components.values())

    return components
```

### Step 5: Attribution Reporting

```python
def attribution_report(attribution_df, title="Performance Attribution"):
    """
    Standard attribution report format.
    """
    report = f"""
    {title}
    {'='*60}

    Portfolio Return:     {port_ret:>8.2%}
    Benchmark Return:     {bench_ret:>8.2%}
    Active Return:        {active_ret:>8.2%}

    --- Decomposition by Sector ---
    {'Sector':<20} {'Alloc':>8} {'Select':>8} {'Inter':>8} {'Total':>8}
    {'-'*60}
    """
    for sector, row in attribution_df.iterrows():
        report += f"    {sector:<20} {row['allocation']:>8.2%} {row['selection']:>8.2%} "
        report += f"{row['interaction']:>8.2%} {row['total_active']:>8.2%}\n"

    report += f"    {'-'*60}\n"
    report += f"    {'TOTAL':<20} {attribution_df['allocation'].sum():>8.2%} "
    report += f"{attribution_df['selection'].sum():>8.2%} "
    report += f"{attribution_df['interaction'].sum():>8.2%} "
    report += f"{attribution_df['total_active'].sum():>8.2%}\n"

    return report
```

## Examples

### Equity Attribution by Sector

```python
# Sector weights and returns
sectors = ['Technology', 'Healthcare', 'Financials', 'Energy', 'Consumer']
port_w = pd.Series([0.35, 0.20, 0.15, 0.10, 0.20], index=sectors)
bench_w = pd.Series([0.28, 0.15, 0.18, 0.12, 0.27], index=sectors)
port_r = pd.Series([0.08, 0.05, 0.03, -0.02, 0.04], index=sectors)
bench_r = pd.Series([0.06, 0.04, 0.04, -0.01, 0.03], index=sectors)

result = brinson_fachler(port_w, bench_w, port_r, bench_r)
# Allocation to Tech (overweight in strong sector) = positive
# Selection in Tech (8% vs 6%) = positive
```

### Interpreting Results

Key insights to surface:
- Was alpha from sector allocation (top-down) or stock selection (bottom-up)?
- Which sectors had the largest attribution? Is it consistent over time or a one-off?
- Is the interaction effect large? If so, the manager may be making correlated allocation and selection bets
- Does attribution match the stated investment process? (A bottom-up manager should show selection, not allocation)

## Quality Gate

- [ ] Attribution sums exactly to total active return (no residual beyond rounding)
- [ ] Multi-period attribution uses a proper linking method (Carino, GRAP, or Menchero)
- [ ] Sector/region classification is consistent between portfolio and benchmark
- [ ] Transaction effects excluded from holdings-based attribution (or accounted for separately)
- [ ] Currency effects separated from local returns for international portfolios
- [ ] Factor-based attribution uses a risk model consistent with the portfolio's universe
- [ ] Interaction effect interpreted correctly — not lumped into allocation or selection arbitrarily
- [ ] Reported at multiple levels: total, sector, country, and individual security
- [ ] For fixed income: duration, curve, and spread effects isolated before reporting selection
- [ ] Attribution is stable and explainable — large unexplained residuals indicate model problems
