---
name: structured-products
description: "Structured Products. Use when: User wants to understand or price structured products; Analyzing autocallable notes, reverse convertibles, or capital-protected products; Decomposing a structured product into its embedded options."
---

# Structured Products

name: structured-products
description: Structured products — autocallables, reverse convertibles, capital protected.
origin: ECT

## When to Activate

- User wants to understand or price structured products
- Analyzing autocallable notes, reverse convertibles, or capital-protected products
- Decomposing a structured product into its embedded options
- Evaluating structured product risk from an investor or issuer perspective
- Building payoff diagrams or pricing structured notes

## First Questions

1. Which product type (autocallable, reverse convertible, capital protected, range accrual)?
2. What is the underlying (single stock, index, basket, rates)?
3. What is the investor objective (yield enhancement, capital protection, leveraged upside)?
4. Are you pricing, risk-managing, or evaluating suitability?
5. What is the term and currency?

## Core Concepts

### Structured Product Taxonomy

```
By investor objective:

  Yield enhancement:
    - Reverse convertibles (short put + bond)
    - Autocallables (conditional coupon + barriers)
    - Discount certificates (covered call equivalent)
    Higher coupon in exchange for downside risk

  Capital protection:
    - Principal-protected notes (zero-coupon bond + call option)
    - Protected participation (bond floor + upside exposure)
    - Guarantee certificates
    Capital preserved at maturity, limited upside

  Participation:
    - Tracker certificates (delta-one exposure)
    - Leveraged certificates (geared upside)
    - Outperformance certificates (call spread on outperformance)
    Direct or amplified exposure to underlying

  Exotic payoffs:
    - Range accruals (coupon accrues only when underlying is in range)
    - Worst-of products (payoff determined by worst performer in basket)
    - Cliquet / ratchet (periodic resets, path-dependent)
    Complex payoffs requiring sophisticated pricing
```

### Common Structures in Detail

#### Autocallable Notes

The most popular structured product globally by issuance volume.

```
Mechanics:
  - Periodic observation dates (monthly, quarterly, semi-annual)
  - At each observation: if underlying >= autocall barrier, note is called
  - On autocall: investor receives principal + accumulated coupon
  - If never autocalled: at maturity, check knock-in barrier
    - If underlying never breached knock-in barrier: return principal + final coupon
    - If underlying breached knock-in barrier: return underlying performance (loss)

Typical terms (equity index autocallable):
  Underlying: Euro Stoxx 50
  Term: 3 years (callable every 6 months)
  Coupon: 8% p.a. (memory coupon — missed coupons paid on next autocall)
  Autocall barrier: 100% of initial level
  Knock-in barrier: 60% of initial level (European or American observation)
  Notional: EUR 1,000

Payoff scenarios:
  Best case: Autocalled at first observation, receive 104% (6-month coupon)
  Middle case: Called at year 2, receive 100% + 16% accumulated coupon
  Worst case: Never called, knock-in breached, lose (1 - final_level/initial_level)

Risk decomposition:
  Investor is effectively:
    - Long a zero-coupon bond (issuer credit risk)
    - Short a down-and-in put (knock-in barrier)
    - Short a series of digital options (autocall feature)
    - The coupon compensates for these embedded short options
```

#### Reverse Convertibles

```
Mechanics:
  - Fixed coupon (higher than market rate)
  - At maturity: if underlying >= strike, return principal
  - If underlying < strike: deliver shares (or cash equivalent at lower price)
  - Investor is long a bond + short a put option

Typical terms:
  Underlying: Single stock (AAPL, NVDA, etc.)
  Term: 6-12 months
  Coupon: 12-20% p.a. (depending on underlying vol and strike)
  Strike: 80-100% of spot (lower strike = lower coupon but more protection)

Decomposition:
  Reverse convertible = Zero coupon bond + Short put
  Coupon = Risk-free rate + Put premium received / Notional

Why the coupon is high:
  - Investor is selling a put option to the issuer
  - Higher underlying volatility = higher put premium = higher coupon
  - Single stock reverse convertibles pay more than index (higher vol)
  - Short-dated products pay less than long-dated (less time value)
```

#### Capital-Protected Notes

```
Mechanics:
  - Principal guaranteed at maturity (subject to issuer credit risk)
  - Participation in upside of underlying asset
  - Participation rate typically 50-100% (depends on rates and vol)

Construction:
  Capital protection = Zero coupon bond maturing at par
  Upside participation = Call option on underlying

  Budget for option = 100% - PV(zero coupon bond)
  Higher rates = more budget for options = higher participation rate
  Higher vol = more expensive options = lower participation rate

Example (5-year, rates at 4%):
  Zero coupon bond cost: 100 / (1.04)^5 = 82.2%
  Option budget: 100% - 82.2% = 17.8%
  ATM 5-year call option cost: ~25% of notional
  Participation rate: 17.8% / 25% = 71%
  Investor gets 100% principal back + 71% of index upside

Low-rate environment impact:
  At 1% rates: ZCB cost = 95.1%, option budget = 4.9%
  Participation rate drops to ~20% (product becomes unattractive)
  This is why capital-protected products disappeared in ZIRP era
```

### Payoff Diagrams

```
Reverse Convertible (strike = 100):

  Payoff
  |         ___________
  |        /
  |       /
  |      /
  |_____/
  |
  0   60   80   100  120  140  Underlying at maturity

  Below strike: payoff = underlying level (loss)
  Above strike: payoff = 100 + coupon (capped)

Autocallable (simplified, at maturity):

  Payoff
  |              |--- Principal + coupon (if above autocall level)
  |              |
  |              |
  |          ____|
  |         /    (knock-in barrier not breached: return principal)
  |        /
  |_______/      (knock-in breached: underlying performance)
  |
  0   40   60   80   100  Underlying at maturity

Capital Protected:

  Payoff
  |              /  (participation rate * upside)
  |             /
  |            /
  |___________/     (100% principal floor)
  |
  0   60   80   100  120  140  Underlying at maturity
```

### Pricing Approach

```
General framework:
  1. Decompose product into vanilla components (bonds, options, barriers)
  2. Price each component using appropriate model
  3. Sum components, add issuer margin

Pricing models by complexity:
  Simple (reverse convertible): Black-Scholes for embedded put
  Moderate (autocallable): Monte Carlo with local/stochastic vol
  Complex (worst-of autocallable): Multi-asset Monte Carlo with correlation

Key pricing inputs:
  - Underlying spot price and forward curve (dividends, repo)
  - Volatility surface (skew matters for barrier products)
  - Correlation matrix (for basket/worst-of products)
  - Interest rate curve (for discounting and bond floor)
  - Issuer credit spread (for counterparty risk adjustment)

Issuer margin:
  - Typical: 1-5% of notional (embedded in coupon or participation rate)
  - Higher margin for retail products (less price-transparent)
  - Lower margin for institutional (competitive bidding)
  - Margin covers: hedging costs, structuring fee, distribution fee, profit
```

### Investor Risk Assessment

```
Key risks for investors:

  1. Market risk:
     - Downside exposure if barriers are breached
     - Worst-of products: risk is driven by weakest performer
     - Correlation risk: low correlation increases worst-of risk

  2. Issuer credit risk:
     - Capital protection is only as good as the issuer (Lehman lesson)
     - Autocallable coupons depend on issuer solvency
     - Mitigant: collateralization, COSI (SIX Swiss Exchange)

  3. Liquidity risk:
     - Secondary market may not exist or bid-ask is wide (3-5%)
     - Early exit is expensive (investor pays unwinding costs)
     - Hold-to-maturity bias in product design

  4. Complexity risk:
     - Path-dependent features are hard for investors to evaluate
     - Memory coupons, barrier observations, worst-of — compounding complexity
     - Behavioral: investors underestimate tail risk of barrier products

  5. Reinvestment risk:
     - Autocallable: money returned early, must reinvest (potentially at lower rates)
     - In low-vol environments, autocall quickly, leaving investor searching for yield
```

### Issuer Perspective and Hedging

```
Issuer economics:
  - Issue structured note at par (100%)
  - Invest proceeds: buy bond (fund the principal) + buy/sell options (hedge payoff)
  - Margin = par - cost of hedging components
  - P&L recognized upfront or amortized over product life

Hedging the book:
  Autocallable hedging:
    - Delta: adjust equity hedge daily (sign flips near barriers)
    - Gamma: concentrated near autocall barriers (hard to hedge)
    - Vega: short vega (issued product benefits from low vol)
    - Correlation (worst-of): short correlation (hedged with correlation swaps or proxy)
    - Dividend risk: long dividends (if underlying falls, fewer dividends expected)
    - Rates: duration exposure from bond component

  Pin risk near barriers:
    - As underlying approaches autocall barrier, gamma spikes
    - Hedging costs increase dramatically near barriers
    - Can cause "magnet effect" — large hedging flows push underlying toward barrier

  Restriking risk:
    - If product autocalls, issuer must issue new product at current levels
    - In rising markets: new products have higher barriers, harder to hedge
    - Autocall clustering: many products autocall simultaneously, causing flow imbalance
```

## Quality Gate

Before investing in or pricing structured products:

- [ ] Product decomposed into constituent components (bond + options)
- [ ] Each embedded option priced with appropriate model (barrier options need vol smile)
- [ ] Issuer credit risk assessed (no capital protection without creditworthy issuer)
- [ ] Worst-case payoff understood and tolerable (not just expected case)
- [ ] Barrier levels stress-tested against historical drawdowns
- [ ] Correlation assumptions validated for multi-asset products
- [ ] Liquidity terms understood (early exit cost, secondary market availability)
- [ ] Issuer margin estimated (compare to replicating the payoff directly)
- [ ] Dividend and funding assumptions checked (affect forward price and hedging)
- [ ] Regulatory suitability confirmed (MiFID II target market, PRIIPs KID)
