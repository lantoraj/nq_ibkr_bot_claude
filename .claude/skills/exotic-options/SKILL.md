---
name: exotic-options
description: "Barriers, Asians, lookbacks, digitals, cliquets, autocallables, and quanto options. Pricing, hedging, and risk management. Use when: User pricing or hedging barrier options (knock-in, knock-out); Pricing Asian options (arithmetic or geometric average); Analyzing lookback, digital/binary, or cliquet options."
---

# Exotic Options

> Barriers, Asians, lookbacks, digitals, cliquets, autocallables, and quanto options. Pricing, hedging, and risk management.

## When to Activate

- User pricing or hedging barrier options (knock-in, knock-out)
- Pricing Asian options (arithmetic or geometric average)
- Analyzing lookback, digital/binary, or cliquet options
- Understanding autocallable structures and their risks
- Quanto options and cross-currency derivative pricing
- Hedging exotic payoffs and understanding Greeks behavior

## Core Concepts

### Barrier Options

**Classification**
- **Knock-out**: option ceases to exist if barrier is hit (down-and-out, up-and-out)
- **Knock-in**: option comes into existence only if barrier is hit (down-and-in, up-and-in)
- **In-out parity**: knock-in + knock-out = vanilla (same strike and expiry)
- **Rebate**: fixed payment made when the barrier is hit (for knock-outs) or at expiry if barrier is never hit (for knock-ins)

**Pricing**
- Continuous monitoring: closed-form solutions exist under BSM (reflection principle)
- Discrete monitoring (daily, weekly): no closed-form; use MC with Brownian bridge correction or lattice methods
- Broadie-Glasserman-Kou continuity correction: shift barrier by beta * sigma * sqrt(dt) where beta = 0.5826
- Near-barrier behavior: Greeks become extreme (delta can flip sign, gamma spikes)

**Key Risks**
- Pin risk near the barrier: small moves determine whether the option exists or not
- Barrier shift risk: if the barrier is monitored at fixing times, the effective barrier differs from contractual
- Hedging difficulty: near the barrier, delta changes rapidly and gamma is very large
- Gap risk: underlying can gap through the barrier (especially over weekends, overnight)

### Asian Options

**Types**
- Fixed-strike Asian call: max(avg(S) - K, 0) — compare average price to fixed strike
- Floating-strike Asian call: max(S_T - avg(S), 0) — compare terminal price to average
- Average can be arithmetic (standard) or geometric (tractable)
- Averaging period: full life or partial (e.g., last 3 months of a 1-year option)

**Pricing**
- Geometric average Asian: closed-form under GBM (geometric average of log-normals is log-normal)
  - Geometric Asian call: BSM formula with adjusted vol (sigma/sqrt(3)) and drift
- Arithmetic average Asian: no closed-form; use MC with geometric Asian as control variate
- Turnbull-Wakeman approximation: match first two moments of arithmetic average to log-normal
- As averaging dates increase, Asian option value decreases (averaging reduces effective volatility)

**Properties**
- Cheaper than vanilla options (averaging reduces payoff volatility)
- Popular for commodity hedging (averaging reflects actual purchase/sale prices)
- Less sensitive to manipulation near expiry (one closing price cannot dominate)
- Vega is lower than vanilla; delta behavior depends on how much averaging has occurred

### Lookback Options

**Types**
- Fixed-strike lookback call: max(S_max - K, 0) — payoff based on maximum price observed
- Floating-strike lookback call: S_T - S_min — buy at the minimum, sell at current
- Floating-strike lookback put: S_max - S_T — sell at the maximum, buy at current
- Partial lookback: lookback feature applies to only part of the option's life

**Pricing**
- Closed-form under continuous monitoring (Goldman, Sosin, Gatto 1979)
- Floating-strike lookback call: S_T * N(a1) - S_min * exp(-rT) * N(a2) - S_T * sigma^2/(2r) * [...]
- Very expensive: the ability to buy at the low / sell at the high has significant value
- Typically 2-3x the price of an ATM vanilla option
- Discrete monitoring: use MC with Brownian bridge correction for continuous max/min estimation

### Digital (Binary) Options

**Types**
- Cash-or-nothing call: pays fixed amount Q if S_T > K, else 0
- Asset-or-nothing call: pays S_T if S_T > K, else 0
- Standard call = asset-or-nothing call - K * cash-or-nothing call (decomposition)

**Pricing under BSM**
- Cash-or-nothing call: Q * exp(-rT) * N(d2)
- Asset-or-nothing call: S * exp(-qT) * N(d1)
- Delta of digital: Q * exp(-rT) * phi(d2) / (S * sigma * sqrt(T)) — can be very large near ATM at expiry

**Hedging Challenges**
- Digital options have discontinuous payoff — delta approaches infinity near ATM at expiry
- In practice: replicate with tight call spread (buy K call, sell K+epsilon call, scale by Q/epsilon)
- The call spread replication has bounded delta and gamma
- Skew sensitivity: digital price is very sensitive to the vol skew (slope of IV around the strike)
- Overhedge: use call spread width that accounts for realistic hedging frequency

### Cliquet (Ratchet) Options

**Structure**
- Series of forward-starting options, each resetting at the end of the previous period
- Each period: captures return = max(0, S_{t+1}/S_t - 1), typically with local cap and floor
- Total payoff: sum of capped/floored periodic returns
- Embedded in equity-linked insurance products and structured notes

**Pricing Considerations**
- Cliquet value depends critically on forward volatility and forward skew
- Cannot be hedged with vanilla options alone — requires forward-starting option hedges
- Very sensitive to vol-of-vol and correlation structure
- Stochastic volatility models (Heston, SABR) are essential for accurate pricing
- Local vol models can misprice cliquets because they underestimate forward smile dynamics

### Autocallable Notes

**Structure**
- Periodic observation dates (e.g., quarterly, semi-annually)
- If underlying > autocall barrier (e.g., 100% of initial) on observation date: note is called, investor receives principal + coupon
- If not called and underlying > coupon barrier: investor receives coupon for that period
- At maturity, if underlying < put strike (e.g., 60% of initial): investor bears downside loss
- Most popular structured product globally (especially in Asia and Europe)

**Risk Profile**
- Short a deep OTM put (downside exposure)
- Short a series of digital options at the autocall barrier
- Correlation with dividends and rates (forward price matters for autocall probability)
- Path-dependent: early autocall eliminates remaining coupons and downside risk
- Issuer is typically net long vol and long correlation for worst-of autocallables

### Quanto Options

**Definition**
- Option on a foreign asset with payoff converted at a fixed FX rate (not the prevailing rate)
- Example: USD investor buys a call on Nikkei 225 with payoff in USD at a fixed JPY/USD rate
- Eliminates FX risk from the investor's perspective

**Pricing Adjustment**
- Under BSM, quanto adjustment modifies the drift of the foreign asset:
  - r_quanto = r_foreign - rho * sigma_S * sigma_FX
  - rho = correlation between foreign asset and FX rate
  - sigma_FX = volatility of the FX rate
- If equity and FX are negatively correlated (typical for developed markets: currency weakens when stocks fall), the quanto drift adjustment is positive — quanto option is worth more
- Volatility of the quanto option = sigma_S (no FX vol component)

## Examples

### Down-and-Out Call Pricing
```
S=100, K=100, Barrier B=85, r=5%, sigma=25%, T=0.5

Vanilla call (BSM): $7.62
Down-and-out call (closed-form): $5.84
Knock-out discount: $1.78 (23% cheaper due to barrier risk)

If S drops to 86 (1 point above barrier):
  Vanilla call value: $2.10
  D&O call value: $0.15 (nearly worthless — about to knock out)
  Delta of D&O: -2.5 (negative — further drop kills the option)
  Gamma: extremely large (discontinuity at barrier)
```

### Arithmetic Asian Option
```
S=100, K=100, r=5%, sigma=30%, T=1.0, monthly averaging (12 dates)

Vanilla call: $14.23
Geometric Asian call (closed-form): $8.42
Arithmetic Asian call (MC with control variate): $8.91

Asian discount: 37% cheaper than vanilla.
Effective vol of average: approximately 30% / sqrt(3) = 17.3% (for geometric).
```

### Worst-of Autocallable
```
Underlying: worst of SPX, EuroStoxx 50, Nikkei 225
Autocall barrier: 100%, observed quarterly
Coupon: 8% p.a. if worst-of > 70%
Put strike: 60% of initial (investor bears loss below 60%)
Maturity: 3 years

Pricing requires:
  - 3-asset correlated MC simulation
  - Calibrated local-stochastic vol model for each underlying
  - Quanto adjustment for cross-currency underlyings
  - Dividend assumptions for forward price computation

Key sensitivities:
  - Correlation: lower correlation = lower autocall probability = higher coupon value but more downside risk
  - Vol: higher vol = wider range of outcomes = more expensive embedded put
  - Dividends: higher dividends = lower forward = less likely to autocall
```

## Quality Gate

- Barrier options: verify with in-out parity (knock-in + knock-out = vanilla within tolerance)
- Barrier monitoring: specify continuous vs. discrete and apply appropriate corrections
- Asian options: arithmetic Asian price must be bounded by geometric Asian (lower) and vanilla (upper)
- Digital options: replicate with call/put spread in practice; never hedge a pure digital
- Cliquet pricing must use a stochastic vol model — local vol alone systematically misprices forward skew
- Autocallables: Monte Carlo must have sufficient paths (>100,000) and correct early termination logic
- Quanto: verify the correlation sign and magnitude between asset and FX are reasonable
- All exotic prices must be bounded by appropriate upper and lower limits (vanilla, intrinsic value)
- Greeks must be computed via bump-and-revalue with appropriately small bumps (especially near barriers)
- Model risk assessment: compare prices from at least two models (BSM, local vol, stochastic vol)
- Hedging strategy must be defined before trading: specify instruments, rebalancing frequency, Greeks targets
