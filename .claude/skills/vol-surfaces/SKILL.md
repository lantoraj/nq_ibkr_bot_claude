---
name: vol-surfaces
description: "Implied vol surface, smile/skew, SVI parameterization, SABR model, sticky strike vs sticky delta, surface dynamics, and arbitrage constraints. Use when: User constructing or calibrating an implied volatility surface; Analyzing volatility smile, skew, or term structure patterns; Choosing between SVI, SABR, or other surface models."
---

# Volatility Surface Construction and Analysis

> Implied vol surface, smile/skew, SVI parameterization, SABR model, sticky strike vs sticky delta, surface dynamics, and arbitrage constraints.

## When to Activate

- User constructing or calibrating an implied volatility surface
- Analyzing volatility smile, skew, or term structure patterns
- Choosing between SVI, SABR, or other surface models
- Understanding sticky strike vs sticky delta dynamics for hedging
- Checking a vol surface for arbitrage violations (butterfly, calendar spread)
- Interpolating or extrapolating implied volatilities for unlisted strikes/expiries

## Core Concepts

### Implied Volatility Surface

The implied volatility surface maps sigma_IV(K, T) for all strikes K and expiries T:

- **Smile**: IV is higher for OTM puts and OTM calls relative to ATM — typical in FX, short-dated equity index
- **Skew**: IV decreases monotonically from low strikes to high strikes — dominant pattern for equity indices
- **Term structure**: IV varies by maturity — often upward-sloping (contango), can invert in stress
- **Skew steepens in stress**: when markets sell off, the put skew becomes more pronounced
- **Term structure inverts in stress**: short-dated vol spikes above long-dated vol

### Why the Smile/Skew Exists

1. **Fat tails**: real returns have excess kurtosis — OTM options are worth more than BSM predicts
2. **Negative skewness**: equity returns are left-skewed — OTM puts are particularly valuable
3. **Supply/demand**: institutional demand for downside protection (puts) drives up put IV
4. **Leverage effect**: when stock drops, firm leverage increases, increasing volatility
5. **Jump risk**: crash risk is not captured by BSM; OTM puts compensate holders for jump risk
6. **Stochastic volatility**: spot-vol correlation (negative for equities) generates skew

### Surface Coordinates

**Strike-based**: sigma(K, T) — intuitive but scale-dependent
**Moneyness**: sigma(K/S, T) or sigma(K/F, T) where F = forward price — scale-independent
**Delta-based**: sigma(delta, T) — common in FX markets (25-delta put, ATM, 25-delta call)
**Log-moneyness**: sigma(ln(K/F), T) — symmetric, used in SVI parameterization
**Standardized moneyness**: x = ln(K/F) / (sigma_ATM * sqrt(T)) — normalizes across maturities

## Methodology

### SVI (Stochastic Volatility Inspired) Parameterization

Gatheral's SVI parameterizes total implied variance w(k) = sigma^2 * T as a function of log-moneyness k = ln(K/F):

w(k) = a + b * (rho * (k - m) + sqrt((k - m)^2 + sigma^2))

Parameters:
- a: overall variance level
- b: slope of the wings (controls how fast variance increases for OTM options)
- rho: rotation/skew (-1 to 1; negative for equity skew)
- m: translation (shifts the smile horizontally)
- sigma: smoothness of the ATM region (controls curvature at the vertex)

Properties:
- Linear in the wings: w(k) -> a + b*(rho +/- 1)*(k - m) as k -> +/- infinity
- Minimum variance at k = m - rho*sigma/sqrt(1-rho^2)
- 5 parameters per expiry slice — parsimonious but flexible

**SSVI (Surface SVI)**
- Extends SVI across the entire surface with fewer parameters
- Parameterizes theta(T) (ATM total variance) and phi(theta) (wing shape)
- Guarantees calendar spread arbitrage-free by construction
- w(k, T) = theta/2 * (1 + rho*phi*k + sqrt((phi*k + rho)^2 + (1-rho^2)))

### SABR Model

The SABR (Stochastic Alpha Beta Rho) model is standard for interest rate and FX options:

dF = sigma * F^beta * dW_1
d(sigma) = alpha * sigma * dW_2
corr(dW_1, dW_2) = rho

Parameters:
- alpha (vol of vol): controls the curvature of the smile — higher alpha = more convex smile
- beta (CEV exponent): controls the backbone (how ATM vol moves with forward) — 0 = normal, 1 = lognormal
- rho (spot-vol correlation): controls skew — negative rho = downward skew
- sigma_0 (initial vol): ATM vol level

**Hagan's Approximation** for implied vol:
sigma_B(K) = alpha / (F*K)^((1-beta)/2) * {z/x(z)} * [1 + corrections * T]

where z = (alpha/sigma_0) * (FK)^((1-beta)/2) * ln(F/K) and x(z) involves rho.

Calibration:
1. Fix beta (often 0, 0.5, or 1 based on market convention or backbone analysis)
2. Fit alpha, rho, sigma_0 to market quotes (ATM, 25-delta risk reversal, 25-delta butterfly)
3. Minimize sum of squared differences between model and market IVs

SABR limitations:
- Hagan formula can produce negative densities for very low strikes
- Extrapolation to extreme strikes requires care
- Does not capture term structure dynamics without per-expiry calibration

### Arbitrage Constraints on the Vol Surface

**No Butterfly Arbitrage (within a single expiry)**
- The call price must be convex in strike: d^2C/dK^2 >= 0
- Equivalently: the risk-neutral density must be non-negative everywhere
- In variance terms: d^2w/dk^2 > certain lower bound involving dw/dk
- SVI with b > 0 and |rho| < 1 is typically butterfly-free

**No Calendar Spread Arbitrage (across expiries)**
- Total variance w(k, T) must be non-decreasing in T for each k
- If w(k, T_2) < w(k, T_1) for T_2 > T_1, a calendar spread arbitrage exists
- SSVI handles this by construction; raw SVI per slice requires manual checking

**Combined Constraints**
- The implied vol surface must produce non-negative risk-neutral densities at all points
- In practice: check numerically on a fine grid of strikes and expiries
- Flag any violations and adjust parameters or add penalty terms in calibration

### Sticky Strike vs Sticky Delta Dynamics

How the vol surface moves when the underlying moves:

**Sticky Strike** (absolute sticky):
- sigma(K, T) stays constant as S moves
- The vol at strike K=100 does not change when S moves from 100 to 105
- The ATM vol (at the new S=105) is read from the existing surface at K=105
- Implies: ATM vol changes as spot moves along the existing smile
- Hedging: BSM delta is correct (vol does not depend on S)

**Sticky Delta** (relative sticky / sticky moneyness):
- sigma(K/S, T) stays constant — the smile moves with the underlying
- ATM vol stays the same as S moves (the smile shifts)
- An option at K=100 with S=100 (ATM) has the same IV as K=105 when S=105
- Implies: IV at a fixed strike changes as spot moves
- Hedging: BSM delta needs adjustment (dVol/dS is non-zero)
- More empirically supported for equity index options in most regimes

**Impact on Hedging**
- Under sticky strike: delta_hedge = BSM_delta
- Under sticky delta: delta_hedge = BSM_delta + vega * dIV/dS
- The adjustment dIV/dS comes from the skew slope
- For negative skew: sticky delta delta > BSM delta for calls (further from zero)

## Examples

### SVI Calibration
```
SPX 1-month options, ATM forward = 4500
Market implied vols:
  K=4050 (90%): 28.5%    K=4275 (95%): 23.2%    K=4500 (100%): 19.5%
  K=4725 (105%): 17.8%   K=4950 (110%): 17.2%

SVI fit (total variance w = IV^2 * T):
  a = 0.0029, b = 0.18, rho = -0.72, m = -0.02, sigma = 0.08

Fitted IVs: 28.4%, 23.3%, 19.5%, 17.9%, 17.1%
Max error: 0.1 vol point — excellent fit.
Negative rho captures the equity skew.
```

### SABR for Swaptions
```
5Y10Y swaption, ATM forward = 3.5%, market quotes:
  ATM vol: 45bp (normal vol)
  25d RR: -5bp (skew)
  25d BF: +2bp (smile curvature)

SABR calibration (beta = 0.5 fixed):
  sigma_0 = 0.032, alpha = 0.45, rho = -0.25

Model implied normal vols:
  F-100bp: 48.2bp    F-50bp: 46.1bp    ATM: 45.0bp
  F+50bp: 44.5bp     F+100bp: 44.8bp
```

### Arbitrage Check
```
Calendar spread check for SVI surfaces at 1M and 2M:
  At k = -0.10 (10% OTM put):
    w(1M) = 0.0092, w(2M) = 0.0198
    w(2M) > w(1M) — OK, no calendar arbitrage

  At k = -0.30 (30% OTM put):
    w(1M) = 0.0285, w(2M) = 0.0260
    w(2M) < w(1M) — VIOLATION: calendar spread arbitrage exists

Fix: increase the 2M wing parameter b or use SSVI for guaranteed consistency.
```

## Quality Gate

- Calibrated surface must fit market quotes within 0.5 vol points (or within bid-ask spread)
- No butterfly arbitrage: verify d^2C/dK^2 >= 0 on a fine strike grid (at least 100 points per slice)
- No calendar spread arbitrage: verify total variance is non-decreasing in T at every strike
- Risk-neutral density must be non-negative at all points — plot and visually inspect
- SVI: verify b > 0, |rho| < 1, and sigma > 0 after calibration
- SABR: verify Hagan formula validity range; flag if low-strike densities become negative
- Extrapolation beyond traded strikes must be documented: wing behavior (linear in variance) and bounds
- Sticky strike vs sticky delta assumption must be stated and consistently applied in hedging
- Surface must be updated intraday for liquid markets; end-of-day for less liquid
- Cross-validate against at least two independent surface construction methods
- Mark-to-market must use the calibrated surface; do not use raw BSM with a flat vol assumption
