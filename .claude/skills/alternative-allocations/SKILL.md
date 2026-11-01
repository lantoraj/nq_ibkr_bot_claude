---
name: alternative-allocations
description: "Alternative investment allocation — PE, VC, hedge funds, real assets in portfolio context. Use when: User is allocating to private equity, venture capital, hedge funds, or real assets; Modeling illiquidity premiums and J-curve effects; Building commitment pacing models for PE/VC programs."
---

# Alternative Allocations

> Alternative investment allocation — PE, VC, hedge funds, real assets in portfolio context.

## When to Activate

- User is allocating to private equity, venture capital, hedge funds, or real assets
- Modeling illiquidity premiums and J-curve effects
- Building commitment pacing models for PE/VC programs
- Evaluating hedge fund strategies for portfolio diversification
- Integrating alternatives into a traditional stock/bond portfolio

## Core Concepts

### Why Alternatives?

Alternatives offer three potential benefits:
1. **Illiquidity premium**: compensation for locking up capital (PE, infrastructure)
2. **Diversification**: low correlation to public markets (certain hedge fund strategies, commodities)
3. **Alpha**: skill-based returns from active management (PE operational improvement, HF trading)

The cost: illiquidity, complexity, higher fees, less transparency, and survivorship-biased track records.

### Alternative Asset Classes

**Private Equity (Buyout)**:
- Expected net return: 12-15% (3-5% premium over public equity)
- Illiquidity: 7-12 year fund life, no redemptions
- J-curve: negative returns in years 1-3 as fees are paid on committed capital before realizations
- Key metrics: IRR, TVPI (Total Value to Paid-In), DPI (Distributions to Paid-In)

**Venture Capital**:
- Expected net return: highly dispersed (top quartile: 15-25%, bottom quartile: negative)
- Illiquidity: 10-15 year fund life
- Power-law returns: a few investments drive most of the return
- Vintage diversification is essential (deploy across 4-5 vintages)

**Hedge Funds**:
- Strategies span a wide range of risk/return profiles
- Equity L/S: 5-8% net, moderate equity beta (0.3-0.5)
- Global Macro: 4-7% net, low equity correlation
- Managed Futures/CTA: 3-6% net, crisis alpha (positive in equity drawdowns)
- Relative Value: 4-6% net, low vol, tail risk in credit crises

**Real Assets**:
- Real Estate (core): 6-8% total return, inflation hedge, income-oriented
- Infrastructure: 7-9% total return, long-duration, regulated cash flows
- Commodities: 0-3% real return, inflation hedge, diversification
- Timberland/Farmland: 5-7%, inflation-linked, very illiquid

### The Illiquidity Premium

Estimated at 1-3% annually for PE over public equity (after adjusting for leverage, fees, and smoothed returns). Key debate:

- **Optimistic view**: Investors earn a genuine premium for bearing illiquidity and providing patient capital
- **Skeptical view**: After proper benchmarking (PME — Public Market Equivalent), leverage adjustment, and fee drag, the net premium may be near zero for median managers
- **Resolution**: Manager selection matters enormously — top-quartile PE consistently outperforms; bottom-quartile destroys value

## Methodology

### Step 1: Determining Alternative Allocation Size

```python
def alternative_allocation_framework(portfolio_size, liquidity_needs,
                                      time_horizon, risk_tolerance):
    """
    Heuristics for alternative allocation sizing.
    """
    # Liquidity constraint: alternatives should not exceed capital
    # that can be locked up for 7-10 years
    max_illiquid = portfolio_size * (1 - liquidity_needs['annual_pct'] * 3)

    # Common institutional allocations:
    # Endowments (Yale model): 50-70% alternatives
    # Pension funds: 15-30% alternatives
    # Family offices: 20-40% alternatives
    # Retail (via interval funds): 5-15% alternatives

    if time_horizon < 5:
        alt_pct = 0.05  # minimal
    elif time_horizon < 10:
        alt_pct = 0.15
    elif time_horizon < 20:
        alt_pct = 0.25
    else:
        alt_pct = 0.35  # long-horizon endowment style

    # Sub-allocation
    allocation = {
        'private_equity': alt_pct * 0.35,
        'venture_capital': alt_pct * 0.10,
        'hedge_funds': alt_pct * 0.25,
        'real_estate': alt_pct * 0.15,
        'infrastructure': alt_pct * 0.10,
        'commodities': alt_pct * 0.05,
    }

    return allocation
```

### Step 2: Commitment Pacing for PE/VC

```python
def commitment_pacing_model(target_nav, fund_life=10, j_curve_years=3,
                             deployment_rate=0.25, distribution_rate=0.20,
                             growth_rate=0.12, years=20):
    """
    Model PE/VC NAV build-up through commitment pacing.

    The challenge: you commit capital today but it's drawn down over 3-5 years
    and returned over 5-10 years. To maintain a steady NAV allocation,
    you must over-commit.
    """
    nav = 0
    annual_commitment = target_nav * 0.30  # initial estimate, iterate

    unfunded = 0  # total unfunded commitments
    history = []

    for year in range(years):
        # New commitment
        unfunded += annual_commitment

        # Capital calls (drawn from unfunded)
        calls = min(unfunded, annual_commitment * deployment_rate * fund_life / j_curve_years)
        unfunded -= calls

        # Growth on existing NAV
        nav *= (1 + growth_rate)
        nav += calls

        # Distributions (after J-curve period)
        if year >= j_curve_years:
            distributions = nav * distribution_rate
            nav -= distributions
        else:
            distributions = 0

        history.append({
            'year': year,
            'nav': nav,
            'unfunded': unfunded,
            'calls': calls,
            'distributions': distributions,
            'total_exposure': nav + unfunded  # economic exposure
        })

    return pd.DataFrame(history)
```

### Step 3: Hedge Fund Allocation

```python
def hedge_fund_portfolio(target_return=0.06, target_vol=0.05,
                          max_equity_beta=0.25):
    """
    Construct a hedge fund portfolio across strategies.
    """
    strategies = {
        'equity_ls': {'ret': 0.07, 'vol': 0.08, 'eq_beta': 0.40, 'fees': '1.5/15'},
        'global_macro': {'ret': 0.05, 'vol': 0.07, 'eq_beta': 0.10, 'fees': '1.5/15'},
        'cta': {'ret': 0.04, 'vol': 0.10, 'eq_beta': -0.10, 'fees': '1.5/20'},
        'relative_value': {'ret': 0.05, 'vol': 0.04, 'eq_beta': 0.15, 'fees': '1.0/15'},
        'event_driven': {'ret': 0.06, 'vol': 0.06, 'eq_beta': 0.30, 'fees': '1.5/15'},
        'credit': {'ret': 0.06, 'vol': 0.05, 'eq_beta': 0.20, 'fees': '1.0/15'},
    }

    # Diversified allocation across strategies
    # CTAs provide crisis alpha (positive when equities crash)
    # Relative value provides steady low-vol returns
    # Equity L/S provides equity-like returns with lower beta
    allocation = {
        'equity_ls': 0.25,
        'global_macro': 0.20,
        'cta': 0.15,
        'relative_value': 0.20,
        'event_driven': 0.10,
        'credit': 0.10,
    }

    # Portfolio-level metrics
    port_beta = sum(allocation[s] * strategies[s]['eq_beta'] for s in allocation)
    port_ret = sum(allocation[s] * strategies[s]['ret'] for s in allocation)

    return allocation, port_beta, port_ret
```

### Step 4: Adjusting Returns for Smoothing and Leverage

```python
def unsmooth_returns(reported_returns, smoothing_param=0.5):
    """
    Private asset returns are smoothed by appraisal-based valuation.
    Unsmooth to get economic volatility.

    Getmansky, Lo, Makarov (2004) model:
    R_observed = theta * R_true + (1-theta) * R_true_lagged
    """
    unsmoothed = pd.Series(index=reported_returns.index, dtype=float)
    unsmoothed.iloc[0] = reported_returns.iloc[0]

    for t in range(1, len(reported_returns)):
        unsmoothed.iloc[t] = (
            (reported_returns.iloc[t] - (1 - smoothing_param) * unsmoothed.iloc[t-1])
            / smoothing_param
        )

    return unsmoothed

def leverage_adjusted_return(pe_return, pe_leverage=1.5, rf=0.04):
    """
    PE funds use leverage. To compare with public equity:
    Adjusted_return = RF + (PE_return - RF) / Leverage
    """
    return rf + (pe_return - rf) / pe_leverage

def public_market_equivalent(pe_cashflows, public_index_returns):
    """
    PME (Kaplan-Schoar): discount PE cash flows at public market return.
    PME > 1 means PE outperformed public markets.
    """
    fv_contributions = 0
    fv_distributions = 0
    index_level = 1.0

    for cf in pe_cashflows:
        if cf['type'] == 'call':
            fv_contributions += cf['amount'] * (public_index_returns.iloc[-1] / index_level)
        elif cf['type'] == 'distribution':
            fv_distributions += cf['amount'] * (public_index_returns.iloc[-1] / index_level)
        index_level *= (1 + cf['period_return'])

    pme = fv_distributions / fv_contributions
    return pme
```

### Step 5: Portfolio Integration

```python
def integrate_alternatives(public_weights, alt_weights, public_sigma,
                           alt_sigma, cross_corr):
    """
    Combine public and alternative allocations.
    Challenges:
    1. Alt return data is smoothed (underestimates vol and correlation)
    2. Different reporting frequencies
    3. Illiquidity means you can't rebalance freely
    """
    # Build full covariance matrix
    n_pub = len(public_weights)
    n_alt = len(alt_weights)
    n = n_pub + n_alt

    sigma_full = np.zeros((n, n))
    sigma_full[:n_pub, :n_pub] = public_sigma
    sigma_full[n_pub:, n_pub:] = alt_sigma  # USE UNSMOOTHED
    sigma_full[:n_pub, n_pub:] = cross_corr
    sigma_full[n_pub:, :n_pub] = cross_corr.T

    full_weights = np.concatenate([public_weights, alt_weights])
    port_vol = np.sqrt(full_weights @ sigma_full @ full_weights)

    return port_vol, sigma_full
```

## Examples

### Yale Endowment Model

```python
yale_allocation = {
    'US_Equity': 0.025,
    'Intl_Equity': 0.115,
    'Fixed_Income': 0.075,
    'Absolute_Return': 0.235,  # Hedge funds
    'Venture_Capital': 0.235,
    'Leveraged_Buyouts': 0.175,
    'Real_Estate': 0.095,
    'Natural_Resources': 0.045,
}
# Total alternatives: ~78%
# Only viable with 20+ year horizon and no liquidity needs
```

### Pension Fund Allocation

```python
pension_allocation = {
    'US_Equity': 0.25,
    'Intl_Equity': 0.15,
    'Fixed_Income': 0.30,
    'Private_Equity': 0.10,
    'Real_Estate': 0.08,
    'Infrastructure': 0.05,
    'Hedge_Funds': 0.07,
}
# Constraint: need to meet annual benefit payments (liquidity)
# Alternatives limited to ~30%
```

## Quality Gate

- [ ] Private asset returns unsmoothed before covariance estimation
- [ ] PE/VC returns leverage-adjusted before comparing to public equity
- [ ] PME used for PE benchmarking, not raw IRR
- [ ] Commitment pacing model accounts for over-commitment needed to maintain target NAV
- [ ] Fee impact quantified: 2/20 fees consume 3-5% of gross returns
- [ ] Manager selection risk acknowledged — alternatives are NOT an asset class, they are a fee structure
- [ ] Liquidity budget checked: can the portfolio meet obligations without forced alternative sales?
- [ ] Vintage diversification planned for PE/VC (commit across 4-5 years minimum)
- [ ] Survivorship bias in hedge fund databases acknowledged (2-3% upward bias)
- [ ] Denominator effect modeled: if public markets crash, alternative allocation mechanically increases
