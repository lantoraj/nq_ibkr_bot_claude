---
name: carry-strategies
description: "Carry Strategies. Use when: User wants to build a carry-based systematic strategy; Designing FX carry trades (long high-yield, short low-yield currencies); Analyzing yield curve roll-down and carry in fixed income."
---

# Carry Strategies

name: carry-strategies
description: Carry strategies across asset classes — FX carry, yield curve carry, commodity roll.
origin: ECT

## When to Activate

- User wants to build a carry-based systematic strategy
- Designing FX carry trades (long high-yield, short low-yield currencies)
- Analyzing yield curve roll-down and carry in fixed income
- Evaluating commodity roll yield as a return source
- Building multi-asset carry portfolios with tail risk hedging

## First Questions

1. Which asset class (FX, rates, commodities, credit, or multi-asset)?
2. Is the strategy systematic or discretionary?
3. What is the risk budget and drawdown tolerance?
4. Is tail risk hedging required (crash risk is the primary carry risk)?
5. What is the target Sharpe and capacity requirement?

## Core Concepts

### What Is Carry?

Carry is the expected return of holding a position assuming prices remain unchanged. It is the income you earn (or cost you pay) simply for holding the position over time.

```
Carry decomposition:
  Total Expected Return = Carry + Expected Price Change

  Carry is observable today (known income/cost)
  Price change is uncertain (requires forecasting)

By asset class:
  FX:         Interest rate differential between currencies
  Bonds:      Coupon income + roll-down return - financing cost
  Commodities: Convenience yield - storage cost = roll yield
  Credit:     Credit spread - expected default loss
  Equities:   Dividend yield - financing cost
```

### FX Carry Trade

The most well-known carry trade. Go long high-yielding currencies, short low-yielding currencies.

- Violates Uncovered Interest Parity (UIP): high-rate currencies do NOT depreciate as much as UIP predicts
- Fama (1984) forward premium puzzle: forward premium is a negative predictor of depreciation
- Typical implementation: rank G10 (or EM) currencies by short-term interest rate
- Long top 3 currencies, short bottom 3
- Sharpe ratio: 0.5-0.8 for G10, higher for EM (with higher crash risk)
- Monthly rebalancing on rate differentials

```
FX carry signal:
  carry_i = interest_rate_i - interest_rate_base
  Or equivalently: carry_i = forward_discount_i = (F - S) / S

  Where F = forward rate, S = spot rate
  A negative forward discount means the currency trades at a forward premium
  (low interest rate currency — this is the funding leg)

G10 carry portfolio:
  Long: AUD, NZD, NOK (historically high rates)
  Short: JPY, CHF, EUR (historically low rates)
  Hedge: Delta-hedged via FX forwards, roll monthly
```

### Yield Curve Carry (Fixed Income)

Bond carry consists of two components: coupon carry and roll-down return.

```
Carry = (Bond Yield - Repo Rate) * Duration
Roll-down = Change in yield from aging * Duration

Example (normal yield curve):
  Buy 5-year Treasury yielding 4.2%, finance at repo rate 3.8%
  Carry = (4.2% - 3.8%) * 4.5 = 1.8% annualized
  Roll-down: 5y yields 4.2%, 4y yields 4.0%
  After 1 year, bond "rolls down" to 4y point
  Roll-down return = (4.2% - 4.0%) * 4.5 = 0.9%
  Total carry + roll = 2.7% (assuming no curve shift)

Curve positioning:
  Steep curve: Carry is positive (borrow short, lend long)
  Flat curve: Carry is near zero (little reward for duration)
  Inverted curve: Carry is negative (paying to hold duration)
```

### Commodity Roll Yield

Commodity futures have roll yield from the term structure shape.

```
Backwardation: Near futures > Far futures
  Positive roll yield: you sell expensive near contract, buy cheap far
  Commodities in backwardation: often energy, precious metals during supply stress

Contango: Near futures < Far futures
  Negative roll yield: you sell cheap near, buy expensive far
  Commodities in contango: storable commodities with high inventory

Roll yield signal:
  roll_yield_i = (F1 - F2) / F1
  Where F1 = front month, F2 = second month

  Long commodities with highest roll yield (backwardation)
  Short commodities with lowest roll yield (contango)

  Sharpe: 0.4-0.7 across diversified commodity basket
  Gorton and Rouwenhorst (2006): roll yield explains most commodity futures risk premium
```

### Carry Measurement Framework

```
Unified carry measure across assets:

  FX:          carry = r_foreign - r_domestic
  Bonds:       carry = (yield - repo) + roll_down
  Commodities: carry = (F_near - F_far) / F_near  (annualized)
  Credit:      carry = spread - expected_default_loss
  Equities:    carry = dividend_yield - risk_free_rate

Cross-asset carry portfolio:
  1. Compute carry for each asset in each class
  2. Standardize within asset class (z-score or rank)
  3. Weight across asset classes by inverse volatility
  4. Rebalance monthly

  Koijen et al. (2018): "Carry" — unified carry factor across all asset classes
  Sharpe: ~0.7 for diversified multi-asset carry
```

### Crash Risk in Carry

Carry strategies exhibit negative skewness and fat tails. The dominant risk is a sharp unwind during risk-off episodes.

```
FX carry crash characteristics:
  - Carry currencies crash during global risk-off events
  - JPY and CHF rally as safe havens, AUD/NZD/EM sell off
  - October 1998: LTCM crisis, JPY rallied 15% in 3 days
  - October 2008: GFC, carry lost 30%+ in weeks
  - January 2015: CHF unpegging, carry hit hard
  - March 2020: COVID, EM carry collapsed

Crash risk metrics:
  - Maximum drawdown: 20-40% for unhedged carry
  - Skewness: -1.0 to -2.0 (strongly left-skewed)
  - Kurtosis: 6-10 (fat tails)
  - Correlation to VIX: -0.3 to -0.5 (carry suffers when vol spikes)
```

## Detailed Methodology

### Hedged Carry Strategies

```
Tail risk hedging approaches:

1. Options overlay:
   Buy OTM puts on carry basket (e.g., 10-delta puts on AUD/JPY)
   Cost: 1-3% annually, reduces max drawdown by 40-60%
   Net Sharpe: drops from 0.7 to 0.4-0.5, but Sortino improves

2. Volatility filter:
   Reduce carry exposure when VIX > 25 or FX implied vol > threshold
   Binary: full position below threshold, zero above
   Graduated: scale position inversely with vol
   Improves Sharpe from 0.6 to 0.8 with lower max drawdown

3. Momentum overlay:
   Exit carry positions that have negative 1-month returns
   Combines carry (positive expected return) with trend (crash avoidance)
   Carry + momentum Sharpe: 0.8-1.0 across FX

4. Regime-conditional carry:
   Run carry only in "risk-on" regimes (expanding economy, low vol)
   Use regime detection (HMM, Markov switching) to identify state
   Reduces time in market but dramatically improves risk-adjusted returns
```

### Multi-Asset Carry Portfolio Construction

```
Asset class weights:
  Method 1: Equal risk contribution (risk parity within carry)
    w_i = (1/vol_i) / sum(1/vol_j)
    Each asset class contributes equal volatility

  Method 2: Maximize Sharpe subject to constraints
    Optimize: max(E[r] / vol) subject to max 30% per asset class

  Method 3: Equal weight with volatility targeting
    Equal nominal weight across asset classes
    Scale total portfolio to target vol (e.g., 8-10%)

Correlation benefits:
  FX carry and bond carry: 0.1-0.3 correlation
  Commodity carry and equity carry: 0.1-0.2
  Cross-asset diversification Sharpe boost: 30-50%

Rebalancing:
  Monthly for FX and commodities (carry signals change slowly)
  Quarterly for bonds (yield curve shifts are gradual)
  Consider transaction costs: carry is low-turnover by nature
```

### Carry Signal Enhancements

```
Beyond raw carry:

1. Adjusted carry:
   Subtract forward-looking risk estimate from raw carry
   Carry_adj = carry - beta * VRP (volatility risk premium)
   Removes "fool's carry" from overly risky positions

2. Relative carry:
   Rank within asset class, z-score standardize
   Removes level effects (all EM rates are high, but relative ranking matters)

3. Carry momentum:
   Combine carry signal with 3-month price momentum
   Assets with positive carry AND positive momentum: highest Sharpe
   Assets with positive carry but negative momentum: avoid (crash signal)

4. Value-adjusted carry:
   In FX, combine carry with PPP-based valuation
   High carry + undervalued currency: best expected returns
   High carry + overvalued currency: crash-prone
```

## Quality Gate

Before deploying a carry strategy:

- [ ] Carry signal is computed correctly (verify against known sources)
- [ ] Crash risk is quantified: max drawdown, skewness, VaR at 99%
- [ ] Tail risk hedge is in place (options, vol filter, or momentum overlay)
- [ ] Transaction costs deducted (FX carry is low-cost; commodity roll can be expensive)
- [ ] Funding cost is accurate (repo rate for bonds, margin cost for futures)
- [ ] Correlation to existing portfolio understood (carry is short vol, check overlap)
- [ ] Regime sensitivity tested (carry underperforms in risk-off, quantify this)
- [ ] Multi-asset diversification validated (not just FX carry concentration)
- [ ] Rebalancing frequency justified (monthly is standard, test sensitivity)
- [ ] Capacity is sufficient for target AUM (FX carry has high capacity; commodity carry is more limited)
