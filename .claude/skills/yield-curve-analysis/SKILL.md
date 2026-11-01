---
name: yield-curve-analysis
description: "Yield Curve Analysis. Use when: Analyzing term structure of interest rates for trading signals or macro assessment; Designing curve trades (steepeners, flatteners, butterflies); Interpreting yield curve inversions and their economic implications."
---

# Yield Curve Analysis

## When to Activate
- Analyzing term structure of interest rates for trading signals or macro assessment
- Designing curve trades (steepeners, flatteners, butterflies)
- Interpreting yield curve inversions and their economic implications
- Calculating key rate durations and understanding curve risk
- Evaluating central bank policy impact on different parts of the curve

## Core Concepts

### Yield Curve Shapes

**Normal (Upward Sloping):**
- Short rates < long rates
- Reflects term premium (compensation for holding longer duration) and expected rate path
- Typical in healthy economic expansion
- Spread (10Y - 2Y) historically averages 100-150 bps

**Inverted:**
- Short rates > long rates
- 2s10s inversion has preceded every US recession since 1955 (with variable lead time of 6-24 months)
- Reflects market expectation that rates will be cut due to economic slowdown
- Can be driven by aggressive Fed tightening (front end) or flight to safety (long end)
- False positives are rare but exist (1966, arguably 1998)

**Flat:**
- Minimal spread between short and long rates
- Transition state between normal and inverted, or vice versa
- Reduces bank profitability (banks borrow short, lend long)

**Humped (Bear Flattener):**
- Belly of the curve (5Y-7Y) yields higher than both ends
- Can occur during transitional monetary policy periods
- Less common, but creates butterfly trade opportunities

### Term Structure Theories

**Pure Expectations Theory:**
- Forward rates equal expected future spot rates
- Long rates are geometric average of expected short rates
- Implication: inverted curve = market expects rate cuts
- Reality: ignores risk premium, but useful as baseline

**Liquidity Premium Theory:**
- Investors demand extra compensation for holding longer maturities
- Term premium should always be positive (not always true empirically)
- Term premium estimation: Adrian-Crump-Moench (ACM) model, Kim-Wright model
- Current term premium is observable via Fed models

**Preferred Habitat Theory:**
- Different investors have preferred maturities (pension funds want long, banks want short)
- Supply/demand imbalances at specific tenors drive relative pricing
- Explains humps and kinks in the curve
- QE disrupts natural supply/demand by removing duration from the market

### Key Curve Metrics

**Spreads:**
```
2s10s = 10Y yield - 2Y yield (most watched recession indicator)
2s30s = 30Y yield - 2Y yield (steeper, more sensitive to term premium)
3m10Y = 10Y yield - 3M T-bill yield (Fed's preferred recession indicator)
5s30s = 30Y yield - 5Y yield (long-end steepness)
Fed funds - 2Y = front-end tightness
```

**Term Premium:**
```
10Y yield = Expected average of short rates over 10 years + Term premium

Term premium drivers:
- Inflation uncertainty (higher uncertainty = higher premium)
- Supply of duration (more Treasury issuance = higher premium)
- Central bank holdings (QE reduces premium, QT increases it)
- Foreign demand (strong foreign demand compresses premium)
- Historically: -0.5% to +2.5% range; negative term premium from 2015-2021 due to QE
```

**Key Rate Durations:**
- Sensitivity of a bond's price to a 1 bp change at a specific maturity point
- Used to decompose curve risk: how much do I lose if the 5Y rate rises 10 bps but 10Y stays flat?
- Essential for hedging: match key rate duration profile, not just overall duration

### Curve Fitting Methods

**Bootstrapping:**
- Derive zero-coupon (spot) rates from observed coupon bond prices
- Sequential: use shortest maturity first, solve for each spot rate
- Produces exact fit to observed prices

**Nelson-Siegel Model:**
- Parameterizes the curve with 4 parameters: level, slope, curvature, decay
- y(tau) = beta0 + beta1 * ((1-exp(-tau/lambda))/(tau/lambda)) + beta2 * ((1-exp(-tau/lambda))/(tau/lambda) - exp(-tau/lambda))
- Smooth, parsimonious, widely used by central banks
- Svensson extension adds a second hump parameter

**Spline Methods:**
- Cubic splines fit piecewise polynomials through observed points
- More flexible but can overfit
- Used when precision at specific tenors matters

## Methodology

### Curve Trade Construction

**Bull Steepener (expect rate cuts, long end stable):**
```
View: Fed will cut rates; front end rallies more than long end
Trade: Long 2Y futures, Short 10Y futures (duration-weighted)
DV01 ratio: 2Y DV01 / 10Y DV01 to equalize interest rate sensitivity
Profit if 2s10s spread widens (steepens)
Risk: if long end sells off more than front end (bear steepener)
```

**Bear Flattener (expect rate hikes, long end anchored):**
```
View: Fed tightening; front end sells off, long end anchored by slowing growth expectations
Trade: Short 2Y futures, Long 10Y futures (duration-weighted)
Profit if 2s10s spread narrows (flattens)
Risk: if curve steepens instead (growth surprises to upside)
```

**Butterfly:**
```
View: belly of curve is mispriced relative to wings
Trade: 2s5s10s butterfly
- Long wings (2Y and 10Y), Short belly (5Y)
- Or vice versa

Weighting: match DV01 so total portfolio duration is zero
Example: Long 1x 2Y, Short 2x 5Y, Long 1x 10Y (approximate weights)
Profit: if 5Y yield moves relative to interpolated 2Y-10Y line

Barbell vs bullet: butterfly trades express view on curvature
```

### Curve Signal Analysis
1. **Plot current curve** against historical percentiles for each tenor
2. **Decompose moves** into level, slope, and curvature using PCA (first 3 components explain ~99%)
3. **Compare implied forwards** with market expectations (Fed funds futures, OIS)
4. **Assess term premium** using ACM or Kim-Wright models
5. **Monitor curve momentum** — curve steepening/flattening trends tend to persist
6. **Cross-reference with macro** — leading indicators, PMI, inflation expectations

### Recession Probability from Curve
```
Models:
- NY Fed model: uses 3m10Y spread to estimate recession probability
  Probit regression: P(recession in 12 months) = Phi(beta0 + beta1 * spread)
  When 3m10Y inverts: ~30-40% recession probability
  When 3m10Y at -100bps: ~60-80% recession probability

- 2s10s alternative: similar signal but historically less reliable than 3m10Y

Caveats:
- Lead time varies: 6-24 months from inversion to recession
- QE may distort term premium, making inversions less meaningful
- "This time is different" arguments emerge every cycle (and are usually wrong)
```

## Examples

### Example 1: Post-Inversion Steepener
```
Scenario: 2s10s has been inverted at -80bps for 6 months
3-month T-bill: 5.25%, 2Y: 4.80%, 10Y: 4.00%
Fed signaling end of tightening cycle

Trade: Bull steepener
- Long 2Y Treasury futures (2 contracts, DV01 = $40/bp each)
- Short 10Y Treasury futures (1 contract, DV01 = $80/bp)
- Net DV01: zero (duration neutral)

Thesis: 2Y will rally more than 10Y as Fed pivots to cuts
Target: 2s10s moves from -80bps to 0bps
P&L: 80bps * $80 DV01 = $6,400 per unit

Risk: if Fed delays cuts and front end stays elevated
Stop: if 2s10s widens to -120bps (loss = $3,200 per unit)
Risk/reward: 2:1
```

### Example 2: Butterfly on Humped Curve
```
Current yields: 2Y = 4.50%, 5Y = 4.70%, 10Y = 4.40%
5Y looks rich relative to wings
Implied 5Y rate from 2Y-10Y interpolation: 4.45%
5Y is 25bps above theoretical (butterfly spread = +25bps)
Historical average butterfly: +5bps

Trade: Sell the butterfly (short belly, long wings)
- Long 1x 2Y futures
- Short 2.2x 5Y futures
- Long 1x 10Y futures
- DV01 neutral overall

Target: butterfly normalizes to +5bps (20bps profit)
Stop: butterfly widens to +40bps (15bps loss)
Catalyst: front-end rally on dovish Fed, or long-end selloff on supply concerns
```

### Example 3: Curve and Equity Signal
```
Signal analysis:
- 2s10s inverted 14 months ago (currently at -20bps, steepening)
- Historical pattern: equities peak 3-6 months after inversion
- Steepening from inversion = recession approaching (Fed about to cut)
- S&P 500 has been flat for 3 months (topping pattern?)

Framework:
- Phase 1: Curve inverts -> equities continue rising (6-18 months)
- Phase 2: Curve begins steepening from inversion -> equities peak
- Phase 3: Recession begins -> curve steepens aggressively -> equities decline 20-40%
- Phase 4: Recovery -> curve normalizes -> equities bottom

Current assessment: Late Phase 2. Reduce equity exposure.
Position for further steepening. Build cash for Phase 3 opportunities.
```

## Quality Gate

Before implementing curve trades, verify:

- [ ] Duration-weighted properly — curve trades should be DV01-neutral unless intentionally taking directional risk
- [ ] Carry and roll-down calculated — what does the trade earn if curve stays unchanged?
- [ ] Financing costs included — repo rates for funded positions, margin costs for futures
- [ ] Macro thesis is explicit — what economic scenario drives the trade? What would invalidate it?
- [ ] Historical context checked — where is the spread relative to historical range and percentiles?
- [ ] Term premium decomposition performed — is the spread driven by rate expectations or term premium?
- [ ] Central bank positioning assessed — QE/QT schedule, forward guidance, and how they affect specific tenors
- [ ] Liquidity considered — on-the-run vs off-the-run, auction cycle effects on pricing
- [ ] Roll dates accounted for — futures rolls create basis risk and transaction costs
- [ ] Cross-market confirmation — do credit spreads, equity vol, and FX carry confirm the macro view?
