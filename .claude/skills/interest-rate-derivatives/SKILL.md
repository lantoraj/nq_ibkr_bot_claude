---
name: interest-rate-derivatives
description: "Swaps, swaptions, caps/floors, curve construction, OIS discounting, and multi-curve framework. Use when: User pricing interest rate swaps or computing swap rates; Constructing yield curves from market instruments (bootstrapping); Pricing swaptions, caps, or floors."
---

# Interest Rate Derivatives

> Swaps, swaptions, caps/floors, curve construction, OIS discounting, and multi-curve framework.

## When to Activate

- User pricing interest rate swaps or computing swap rates
- Constructing yield curves from market instruments (bootstrapping)
- Pricing swaptions, caps, or floors
- Implementing multi-curve framework with OIS discounting
- Understanding convexity adjustments for non-standard rate products
- Analyzing interest rate risk and DV01/duration for derivatives portfolios

## Core Concepts

### Interest Rate Swap (IRS) Mechanics

**Plain Vanilla IRS**
- Exchange fixed rate for floating rate on a notional principal
- Fixed leg: pays C * delta_i * N at each period (C = swap rate, N = notional)
- Floating leg: pays L_i * delta_i * N at each period (L = LIBOR/SOFR, set in advance or arrears)
- No exchange of notional (hence "notional" principal)
- At inception: swap rate is set so PV(fixed leg) = PV(floating leg) — zero NPV

**Swap Rate Calculation**
- Par swap rate: C = [1 - DF(T_N)] / sum(delta_i * DF(T_i))
- DF(T_i) = discount factor to time T_i
- Numerator: difference between initial and final discount factors
- Denominator: sum of discounted accrual factors (the annuity or PV01)

**DV01 and Duration**
- DV01 = change in swap value for 1bp parallel shift in the curve
- For a swap: DV01 approximately = notional * PV01 * 0.0001
- PV01 (annuity) = sum of delta_i * DF(T_i)
- A 10Y swap on $100M has DV01 approximately $85K-$95K depending on the rate environment

### Yield Curve Construction (Bootstrapping)

**Instruments Used**
- Short end (0-2Y): deposit rates, FRAs, or overnight rate futures (SOFR futures)
- Medium term (2-5Y): interest rate swaps (or futures for liquid tenors)
- Long end (5-30Y+): interest rate swaps
- Convexity adjustments needed for futures-based curves

**Bootstrapping Process**
1. Start with the shortest maturity deposit rate: DF(T_1) = 1 / (1 + r_1 * T_1)
2. Use successive swap rates to solve for each discount factor:
   - C_n * sum(delta_i * DF(T_i)) + DF(T_n) = 1
   - DF(T_n) = (1 - C_n * sum(delta_i * DF(T_i) for i<n)) / (1 + C_n * delta_n)
3. Interpolate between pillar points: log-linear on discount factors or monotone convex on zero rates
4. Result: a complete discount factor curve DF(T) for any maturity T

**Interpolation Methods**
- Linear on zero rates: simple but can produce non-smooth forwards
- Log-linear on discount factors: ensures positive forwards
- Cubic spline on zero rates: smooth but can oscillate
- Monotone convex: smooth and produces well-behaved forward rates — preferred in practice
- Tension splines: control oscillation with a tension parameter

### Multi-Curve Framework (Post-2008)

Before 2008, LIBOR was used for both discounting and projection. Post-crisis:

**OIS Discounting**
- Collateralized derivatives earn the overnight rate (SOFR/ESTR/SONIA) on posted collateral
- Therefore, discount using the OIS curve, not the LIBOR/swap curve
- OIS-LIBOR basis: LIBOR > OIS due to bank credit risk (was ~10bp pre-crisis, spiked to 350bp in 2008)

**Projection Curves**
- Each tenor (1M, 3M, 6M LIBOR or SOFR) has its own forward curve
- Forward 3M rate is read from the 3M projection curve
- Discount factor for present value comes from the OIS curve
- Basis swaps (e.g., 3M vs 6M) calibrate the relationship between projection curves

**LIBOR to SOFR Transition**
- LIBOR ceased publication (USD: June 2023 for most tenors)
- SOFR (Secured Overnight Financing Rate) replaced USD LIBOR
- SOFR is an overnight rate; term SOFR derived from futures
- Compounded SOFR in arrears replaces forward-looking LIBOR
- Legacy LIBOR contracts: fallback spread adjustments (ISDA protocol)

## Methodology

### Swaption Pricing

**Black's Model for Swaptions**
- Swaption gives the right to enter a swap at a predetermined fixed rate
- Payer swaption: right to pay fixed (benefits from rising rates)
- Receiver swaption: right to receive fixed (benefits from falling rates)
- Under Black's model: swaption price = A * Black76(F, K, sigma_N * sqrt(T), T)
  - A = annuity factor (PV01 of the underlying swap)
  - F = forward swap rate
  - K = strike swap rate
  - sigma_N = normal (Bachelier) vol or sigma_LN = lognormal vol
  - T = option expiry

**Normal vs. Lognormal Quoting**
- Normal (Bachelier) vol: quoted in bp; payoff proportional to (F - K)
- Lognormal (Black) vol: quoted in %; payoff proportional to F * (F/K - 1)
- Normal vol is now market standard for rates (handles negative rates naturally)
- Conversion: sigma_N approximately = sigma_LN * F for ATM

**Swaption Cube**
- Three dimensions: option expiry, underlying swap tenor, strike (or moneyness)
- ATM swaption matrix: expiry (1M to 30Y) x tenor (1Y to 30Y)
- Smile: parameterized by SABR at each expiry-tenor point
- The swaption cube drives pricing for all rate-exotic products

### Caps and Floors

**Cap**: portfolio of caplets, each paying max(L_i - K, 0) * delta_i * N at time T_{i+1}
**Floor**: portfolio of floorlets, each paying max(K - L_i, 0) * delta_i * N at time T_{i+1}
**Cap-Floor Parity**: Cap - Floor = Swap (payer)

**Caplet Pricing**
- Each caplet is a European call on the forward rate
- Black's formula: Caplet = DF(T_{i+1}) * delta_i * N * [F_i * N(d1) - K * N(d2)]
- Or normal model: Caplet = DF(T_{i+1}) * delta_i * N * [(F_i - K)*N(d) + sigma*sqrt(T)*phi(d)]

**Flat Vol vs. Spot Vol**
- Flat vol: a single vol that prices the entire cap correctly (not individual caplets)
- Spot vol: individual caplet vols — the term structure of caplet volatilities
- Stripping spot vols from flat vols: bootstrap forward from the shortest cap
- Spot vol term structure typically humps around 1-3 years then declines

### Convexity Adjustments

**Futures vs. Forward Rate**
- Eurodollar/SOFR futures prices imply rates that differ from forward rates
- Convexity adjustment: Forward = Futures_rate - 0.5 * sigma^2 * T_1 * T_2
- Adjustment is positive: forward rate < futures-implied rate
- Larger for longer-dated futures (can be 10-20bp for 5Y+ futures)

**CMS (Constant Maturity Swap) Convexity**
- CMS rate = swap rate observed at a future date, paid with a delay
- CMS rate expectation differs from the forward swap rate due to convexity
- CMS convexity adjustment: depends on the swaption smile (particularly the curvature/vol of vol)
- Replication approach: express CMS payoff as an integral over swaptions across all strikes
- CMS adjustment can be 5-30bp depending on tenor and market conditions

### Interest Rate Risk Measures

**DV01 (Dollar Value of 01)**
- Change in PV for a 1bp parallel shift in the zero curve
- DV01 = -dV/dy * 0.0001

**Key Rate Duration (KRD)**
- Sensitivity to shifts at specific tenor points (2Y, 5Y, 10Y, 30Y)
- Sum of key rate durations approximately = effective duration
- Reveals curve exposure: a portfolio can be duration-neutral but have significant curve risk

**Gamma (Convexity in Rates)**
- Second-order sensitivity: d^2V/dy^2
- Positive convexity: bonds, receiver swaptions (benefit from both rate rises and falls)
- Negative convexity: callable bonds, mortgage-backed securities (lose from big moves)

## Examples

### Swap Rate Bootstrapping
```
Market instruments:
  6M deposit: 4.50%
  1Y swap: 4.60%
  2Y swap: 4.70%
  5Y swap: 4.80%

DF(0.5) = 1/(1 + 0.045 * 0.5) = 0.97799

1Y swap (semi-annual): 0.046/2 * DF(0.5) + (1 + 0.046/2) * DF(1.0) = 1
  0.023 * 0.97799 + 1.023 * DF(1.0) = 1
  DF(1.0) = (1 - 0.02249) / 1.023 = 0.95553

2Y swap: 0.023 * [DF(0.5) + DF(1.0) + DF(1.5) + DF(2.0)] + DF(2.0) = 1
  Interpolate DF(1.5), solve for DF(2.0) = 0.91098

Zero rate at 2Y: -ln(0.91098)/2 = 4.66% (continuously compounded)
```

### Swaption Pricing (Normal Model)
```
1Y expiry into 5Y swap (1Y5Y swaption)
Forward swap rate: 4.50%
Strike: 4.50% (ATM)
Normal vol: 85bp (0.0085)
Annuity factor (PV01): 4.35 per 100 notional
Notional: $50M

ATM normal model: Payer swaption = A * sigma * sqrt(T) * phi(0) * N
  = 4.35 * 0.0085 * 1.0 * 0.3989 * $50M
  = $737,700

Receiver swaption = same price (ATM put-call parity for normal model)
```

### Cap Stripping
```
1Y cap (2 caplets, semi-annual): flat vol = 80bp, price = $42,000 on $10M
2Y cap (4 caplets): flat vol = 82bp, price = $98,000

First 2 caplets are known from 1Y cap.
Remaining 2 caplets: $98,000 - $42,000 = $56,000
Spot vol for 1.5Y and 2.0Y caplets: solve for vol that prices $56,000 using 2 caplets.
Spot vol (1.5Y-2.0Y): 84bp (higher than flat vol — term structure is upward sloping).
```

## Quality Gate

- Bootstrapped curve must reprice all input instruments to within 0.1bp
- Discount factors must be monotonically decreasing; forward rates must be non-negative (post-negative rate era: floors at reasonable levels)
- OIS discounting must be used for all collateralized derivatives — single-curve pricing is incorrect post-2008
- Swaption prices must satisfy put-call parity: payer - receiver = forward swap value
- Cap-floor parity must hold: cap - floor = swap at the same strike
- SABR calibration for swaptions must fit ATM vol, risk reversal, and butterfly within market bid-ask
- Convexity adjustments must be applied for futures-based curve construction and CMS products
- Interpolation method must produce smooth and well-behaved forward curves (check visually)
- Key rate durations must sum to approximately the effective duration (within 5%)
- Multi-curve framework must use consistent OIS curve for discounting across all tenor projection curves
