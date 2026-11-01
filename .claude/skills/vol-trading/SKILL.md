---
name: vol-trading
description: "Volatility Trading. Use when: User wants to trade volatility as an asset class; Analyzing realized vs implied volatility and the vol risk premium; Pricing or trading variance swaps and vol swaps."
---

# Volatility Trading

name: vol-trading
description: Volatility trading — straddles, variance swaps, dispersion, VIX.
origin: ECT

## When to Activate

- User wants to trade volatility as an asset class
- Analyzing realized vs implied volatility and the vol risk premium
- Pricing or trading variance swaps and vol swaps
- Designing dispersion trades (index vol vs single-stock vol)
- Trading VIX futures, options, or VIX-related products
- Building systematic vol selling strategies with tail protection

## First Questions

1. Are you trading vol directionally (long/short vol) or relative value (term structure, skew)?
2. What is the underlying (single stock, equity index, FX, rates)?
3. What is the target holding period (intraday, days, weeks, months)?
4. What is the risk tolerance for tail events (vol strategies have extreme tails)?
5. Is this a systematic or discretionary vol strategy?

## Core Concepts

### Realized vs Implied Volatility

```
Realized volatility (RV):
  Historical volatility measured from past returns
  Close-to-close: sigma = sqrt(252 * (1/N) * sum((r_t - r_bar)^2))
  High-low (Parkinson): more efficient estimator using intraday range
  Yang-Zhang: combines open-close and high-low for drift-independent estimate

Implied volatility (IV):
  Market's expectation of future vol, extracted from option prices
  Model-dependent: typically Black-Scholes implied vol
  Represents the vol that equates model price to market price

Key relationships:
  IV - RV = Volatility Risk Premium (VRP)
  VRP is positive on average: options are systematically "expensive"
  SPX VRP: ~3-5 vol points (IV ~18%, RV ~15% long-term average)
  VRP compensates for: jump risk, volatility-of-volatility risk, crash risk

Measuring the VRP:
  VRP_realized = IV(t-30) - RV(t-30, t)   (ex-post)
  VRP is positive ~80% of months for SPX
  VRP is largest for short-dated options (front month)
  VRP shrinks during sustained low-vol regimes (2017) and inverts in crises (2008, 2020)
```

### Variance Swaps

Variance swaps provide pure exposure to realized variance without delta or gamma management.

```
Mechanics:
  At expiry, payoff = Notional_variance * (Realized_Variance - Strike_Variance)

  Notional_variance = Vega_notional / (2 * K_vol)
  Where K_vol = strike in volatility terms

  Fair strike (K_var):
    K_var = (2/T) * integral[exp(rT) * (OTM_put_price/K^2 + OTM_call_price/K^2) dK]
    This is the VIX^2 formula: var swap strike = risk-neutral expected variance
    Requires a continuum of OTM option prices (in practice, interpolated)

  Variance swap vs vol swap:
    Variance swap: payoff linear in variance (sigma^2)
    Vol swap: payoff linear in volatility (sigma) — harder to replicate
    Convexity adjustment: K_vol_swap < K_var_swap (Jensen's inequality)
    Var swap always has higher strike than vol swap

P&L example:
  Strike: 20% vol (400 variance points)
  Realized vol: 25% (625 variance points)
  Vega notional: $100,000
  Variance notional: $100,000 / (2 * 20) = $2,500 per variance point
  P&L = $2,500 * (625 - 400) = $562,500

Key features:
  - No delta hedging required (pure vol exposure)
  - Mark-to-market: sensitive to both remaining implied vol and realized vol to date
  - Convexity: variance swap has convex payoff in vol (benefits from vol spikes)
  - Tail risk: unlimited downside for short variance (realized vol can spike to 80%+)
```

### VIX Futures and Options

```
VIX Index:
  VIX = sqrt((2/T) * sum(delta_K/K_i^2 * e^(rT) * Q(K_i)) * 100^2)
  Where Q(K_i) = OTM option prices on SPX
  VIX measures 30-day expected variance of SPX (annualized, in vol terms)
  VIX is NOT directly tradeable (it's a calculation, not a security)

VIX Futures:
  VIX futures converge to VIX at expiration
  Term structure: usually in contango (longer-dated > shorter-dated)
    Normal contango: ~5% per month (VIX = 15, 2nd month = 16.5)
    Backwardation: during vol spikes (VIX = 35, 2nd month = 30)

  Roll yield:
    In contango: long VIX futures bleeds ~5% per month (negative roll yield)
    In backwardation: long VIX futures gains from roll (positive roll yield)
    This is why long VIX ETPs (VXX, UVXY) lose ~60-80% annually in calm markets

VIX Options:
  Options on VIX futures (not VIX spot)
  VIX calls: often used as tail hedges (portfolio insurance)
  VIX puts: sell to harvest VRP (risky if vol spikes)
  VIX options have their own vol surface (vol-of-vol)
  VIX call skew is extremely steep (upside calls are very expensive)

Trading the VIX term structure:
  Calendar spread: long front month, short back month (or reverse)
  Thesis: term structure will flatten (long front) or steepen (short front)
  Carry: depends on contango/backwardation slope
  Risk: front-month VIX is extremely volatile (can move 30-50% in a day)
```

### Dispersion Trading

Dispersion trades exploit the difference between index implied vol and the implied vols of index constituents.

```
Concept:
  Index variance = weighted average stock variance + covariance terms
  sigma_index^2 = sum(w_i^2 * sigma_i^2) + sum_i_neq_j(w_i * w_j * sigma_i * sigma_j * rho_ij)

  If implied correlation is "too high":
    Sell index straddles (or variance swaps)
    Buy single-stock straddles (or variance swaps)
    Profit = index vol sold - vega-weighted stock vol bought

  Why index vol is usually "rich":
    - Index options are in high demand (portfolio hedging)
    - This bids up index implied vol relative to constituent vols
    - Implied correlation > realized correlation most of the time

Dispersion trade P&L:
  P&L = (implied_correlation - realized_correlation) * correlation_vega
  Positive most of the time (implied corr > realized corr)
  Negative in crises (correlations spike to 0.7-0.9, dispersion loses)

Implementation:
  Sell index variance swap, buy variance swaps on top 20-50 constituents
  Vega-weight to be correlation-neutral at entry
  Or: sell index straddle, buy constituent straddles (delta-hedge all)
  Risk: correlation spike (2008: realized corr hit 0.8, dispersion lost heavily)

Typical P&L profile:
  Win rate: ~70-75% of months
  Average win: 0.3-0.5% of notional
  Average loss: 1-3% of notional
  Sharpe: 0.4-0.8 (before tail events)
  Max loss: 5-15% of notional in crisis (must size accordingly)
```

### Systematic Vol Selling with Tail Protection

```
Core strategy: harvest the volatility risk premium systematically

  Naked vol selling (no protection):
    Sell 30-day SPX straddles or strangles, delta-hedge
    Expected return: VRP * exposure (~3-5% annualized for modest sizing)
    Risk: unlimited in theory, -30% to -50% in practice (2008, 2018 Volmageddon)
    Sharpe: 0.5-0.8 but extreme negative skew (-3 to -5)

  Vol selling with tail protection approaches:

  1. OTM put purchase (put spread collar):
     Sell ATM straddle, buy 10-15% OTM puts
     Cost of protection: 1-2% of notional per month
     Reduces VRP harvest by 30-50% but caps max loss
     Net Sharpe: 0.3-0.5 with much better skew

  2. VIX call hedge:
     Sell SPX puts (short vol), buy VIX calls (tail hedge)
     VIX calls are expensive, but convexity is high
     Use 20-30 delta VIX calls, 2-3 months out
     Hedge ratio: spend 10-20% of premium received on VIX calls

  3. Managed vol selling (conditional):
     Sell vol only when VRP is above threshold (e.g., IV - RV > 3 vol points)
     Reduce or exit when VIX term structure inverts (backwardation = stress signal)
     Stop loss: exit all short vol if portfolio down > X% in a month
     Improves Sharpe to 0.6-1.0 vs unconditional selling

  4. Variance swap with cap:
     Sell capped variance swap (max payout capped at 2.5x strike)
     Standard exchange-traded product (listed on some exchanges)
     Cap limits tail risk explicitly
     Strike is slightly lower than uncapped (compensation for cap)

  5. Risk reversal overlay:
     Sell OTM puts (vol selling), buy further OTM puts (tail protection)
     Net: put spread, not naked short
     Collect ~60-70% of naked put premium with bounded risk
```

## Detailed Methodology

### Vol Surface Relative Value

```
Skew trades:
  Risk reversal: sell 25-delta call, buy 25-delta put (or reverse)
  Butterfly: buy 25-delta call + buy 25-delta put, sell 2x ATM
  Thesis: skew is too steep or too flat relative to fair value

Term structure trades:
  Calendar spread: sell front vol, buy back vol (or reverse)
  Thesis: term structure shape will change
  Carry: front vol decays faster (higher theta per unit vega)

  Metrics:
    Skew richness: current 25d skew vs historical percentile
    Term structure slope: 3M - 1M implied vol vs historical
    Vol-of-vol: VVIX level relative to VIX (regime indicator)
```

### Sizing Vol Positions

```
Key principle: size for the tail, not the average

  Variance swap notional:
    Max loss scenario: realized vol = 80% (crisis), strike = 20%
    P&L = vega_notional / (2 * 20) * (6400 - 400) = vega * 150
    If max acceptable loss = $1M: vega_notional = $1M / 150 = $6,667

  Straddle/strangle position:
    Compute max loss under stress (e.g., -20% move with vol at 60%)
    Size so that stress loss < risk limit (typically 2-5% of NAV)

  Rule of thumb for short vol:
    Allocate max 3-5% of portfolio NAV as potential loss
    This limits notional short vol exposure significantly
    Volmageddon (Feb 2018): XIV lost 96% in one day
```

## Quality Gate

Before deploying a volatility trading strategy:

- [ ] VRP measured correctly (IV vs RV comparison over relevant period)
- [ ] Tail risk quantified: max historical loss modeled (2008, 2018, 2020)
- [ ] Position sized for tail scenario, not average scenario
- [ ] Tail hedge in place if selling vol (OTM puts, VIX calls, or capped variance)
- [ ] Greeks managed: delta-hedge frequency and cost estimated
- [ ] Roll cost calculated for VIX futures strategies (contango bleed)
- [ ] Dispersion correlation risk stress-tested (crisis correlation = 0.8+)
- [ ] Margin requirements modeled under stress (exchanges raise margins in vol spikes)
- [ ] Kill switch defined: exit triggers for drawdown, VIX level, or term structure inversion
- [ ] P&L attribution separates: VRP harvest, gamma scalping, theta decay, and mark-to-market
