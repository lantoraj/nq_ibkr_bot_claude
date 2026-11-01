---
name: credit-derivatives
description: "Credit Derivatives. Use when: User wants to price or trade credit default swaps (CDS); Working with credit indices (CDX, iTraxx); Analyzing CDO tranches and default correlation."
---

# Credit Derivatives

name: credit-derivatives
description: Credit derivatives — CDS, CDO, credit indices, default correlation.
origin: ECT

## When to Activate

- User wants to price or trade credit default swaps (CDS)
- Working with credit indices (CDX, iTraxx)
- Analyzing CDO tranches and default correlation
- Building credit curve models or estimating default probabilities
- Evaluating CDS-bond basis trades or credit relative value

## First Questions

1. Single-name CDS or index/tranche products?
2. What is the reference entity or index (CDX IG, CDX HY, iTraxx Europe)?
3. Are you pricing, hedging, or constructing a relative value trade?
4. What is the recovery rate assumption (standard 40% for IG, 25% for HY)?
5. What is the tenor (1Y, 3Y, 5Y, 7Y, 10Y)?

## Core Concepts

### CDS Mechanics

A Credit Default Swap is a bilateral contract where the protection buyer pays a periodic premium (spread) and receives a contingent payment if the reference entity experiences a credit event.

```
CDS cash flows:
  Protection buyer pays: CDS spread (in bps) * Notional, quarterly (ACT/360)
  Protection seller receives: premium payments until maturity or credit event
  On credit event: seller pays (1 - Recovery Rate) * Notional to buyer

Credit events (ISDA definitions):
  - Bankruptcy (most common for corporates)
  - Failure to pay (missed coupon or principal)
  - Restructuring (debt terms changed unfavorably — different protocols apply)
  - Obligation acceleration / default
  - Repudiation / moratorium (sovereign CDS)

Standard conventions (post-2009 Big Bang Protocol):
  - Fixed coupons: 100 bps (IG) or 500 bps (HY)
  - Upfront payment adjusts for difference between fixed coupon and market spread
  - Upfront = PV of (Market Spread - Fixed Coupon) over contract life
  - Quarterly payment dates: Mar 20, Jun 20, Sep 20, Dec 20
  - Accrued premium paid on credit event (no more "short stub" risk)
```

### CDS Pricing

```
Survival-based pricing:

  CDS spread S makes the PV of premium leg = PV of protection leg

  Premium leg (what buyer pays):
    PV_premium = S * sum(Delta_i * DF_i * Q_i)
    Where:
      Delta_i = accrual fraction for period i
      DF_i = risk-free discount factor to period i
      Q_i = survival probability to period i

  Protection leg (what buyer receives on default):
    PV_protection = (1 - R) * sum(DF_i * (Q_{i-1} - Q_i))
    Where:
      R = recovery rate (40% standard for IG)
      Q_{i-1} - Q_i = default probability in period i

  Par spread:
    S_par = PV_protection / Risky_Annuity
    Risky_Annuity = sum(Delta_i * DF_i * Q_i)

  Hazard rate (continuous):
    Q(t) = exp(-lambda * t) for flat hazard rate
    lambda = S / (1 - R) approximately (first-order approximation)

  Example: 5Y CDS at 150 bps, R = 40%
    lambda = 0.0150 / 0.60 = 2.5% annual default probability
    5-year cumulative default probability = 1 - exp(-0.025 * 5) = 11.8%
```

### Credit Indices: CDX and iTraxx

```
CDX (North America):
  CDX.NA.IG: 125 investment-grade names, 5Y most liquid
  CDX.NA.HY: 100 high-yield names
  CDX.NA.IG rolls every 6 months (March and September)
  New series replaces fallen angels and adds new IG names

iTraxx (Europe/Asia):
  iTraxx Europe: 125 IG European names
  iTraxx Crossover: 75 sub-IG European names (high-yield proxy)
  iTraxx Asia: various regional indices

Index mechanics:
  - Equal-weight basket of single-name CDS
  - Trades with standard fixed coupon + upfront
  - On credit event: name removed, index notional reduced by 1/N
  - Index skew: index spread vs average of single-name spreads
    Usually index trades tighter (cheapest-to-deliver effect in single names)

Index roll:
  - New series every 6 months with updated composition
  - Off-the-run series continue to trade but with declining liquidity
  - Roll trade: sell old series, buy new series
```

### CDO Tranches

A CDO (Collateralized Debt Obligation) tranches the credit risk of a portfolio into slices with different seniority.

```
Standard CDX IG tranches:
  0-3%   Equity tranche (first loss, highest risk, highest spread)
  3-7%   Mezzanine
  7-10%  Senior mezzanine
  10-15% Senior
  15-30% Super senior
  30-100% (remaining, rarely traded)

Tranche mechanics:
  Equity tranche: absorbs first 3% of portfolio losses
    If 2 names default (2/125 = 1.6% loss at 60% LGD): equity tranche loses 53%
    Equity tranche buyer receives very high premium (upfront + running)
    Delta to index: very high (levered exposure to first few defaults)

  Super senior tranche: only hit if losses exceed 15%
    Extremely unlikely in normal markets
    Very low spread (5-20 bps historically)
    But: GFC proved "super senior" is not risk-free (AIG lesson)

Tranche pricing requires:
  1. Marginal default probabilities for each name (from CDS curves)
  2. Default correlation between names
  3. Recovery rate assumptions
  4. Monte Carlo simulation or copula-based analytics
```

### Default Correlation

Default correlation is the key parameter for tranche pricing. It measures the tendency of defaults to cluster.

```
Correlation impact on tranches:
  High correlation:
    - Defaults are clustered (all-or-nothing scenarios)
    - Equity tranche value increases (more scenarios with zero defaults)
    - Senior tranche value decreases (more scenarios with extreme losses)

  Low correlation:
    - Defaults are independent (diversified)
    - Equity tranche value decreases (steady trickle of defaults erodes equity)
    - Senior tranche value increases (diversification protects senior)

  Correlation smile:
    - Different tranches imply different correlations (when using Gaussian copula)
    - Equity tranche implies low correlation (10-20%)
    - Senior tranches imply high correlation (30-50%)
    - This inconsistency is the "correlation smile" — reveals model inadequacy

Gaussian copula model (Li 2000):
  For each name i: Z_i = sqrt(rho) * M + sqrt(1-rho) * epsilon_i
  Where M = common factor, epsilon_i = idiosyncratic factor
  Default if Z_i < Phi^{-1}(PD_i)
  Single parameter rho = pairwise default correlation
  Model limitations: static correlation, thin tails, no contagion dynamics
```

### Base Correlation

```
Base correlation framework (JP Morgan, 2004):
  Instead of compound correlation per tranche, compute base correlation

  Base tranche [0, K]: absorbs all losses up to attachment point K
  Base correlation: the single flat correlation that prices the base tranche

  Standard base tranches: [0,3%], [0,7%], [0,10%], [0,15%], [0,30%]

  Advantages:
    - Monotonically increasing (unlike compound correlation)
    - Can be interpolated to price non-standard tranches
    - Market standard for quoting and risk management

  Base correlation curve (typical for CDX IG):
    [0,3%]:  15-25%
    [0,7%]:  25-35%
    [0,10%]: 30-40%
    [0,15%]: 35-45%
    [0,30%]: 40-55%
```

### Recovery Rate Assumptions

```
Standard recovery assumptions:
  Investment grade corporates: 40% (ISDA standard)
  High yield corporates: 25-30%
  Sovereigns: 25% (standard) but highly variable
  Financials: 40% standard but GFC showed much lower realized

Recovery and spread relationship:
  CDS spread = hazard_rate * (1 - Recovery)
  Same spread can imply different hazard rates depending on recovery assumption
  For trading: use market-standard recovery for consistency
  For risk management: stress recovery rate (e.g., 20% instead of 40%)

Fixed recovery CDS (recovery locks):
  Trade where recovery is fixed at a specific level
  Used to isolate pure default probability from recovery uncertainty
  Recovery swap: exchange actual recovery for fixed recovery on default
```

## Detailed Methodology

### CDS Curve Construction

```
Building a credit curve:
  1. Collect CDS spreads at standard tenors (6M, 1Y, 2Y, 3Y, 5Y, 7Y, 10Y)
  2. Bootstrap survival probabilities from shortest to longest tenor
  3. Interpolate hazard rates between nodes (piecewise constant or linear)
  4. Use ISDA standard model for consistency with market

  ISDA Standard Model:
    - Flat hazard rate between CDS tenor points
    - ACT/365 for hazard rate, ACT/360 for premium
    - Quarterly premium payments with accrual on default
    - Standard recovery = 40% for IG, 25% for HY

  Mark-to-market:
    MTM = (S_current - S_trade) * Risky_Duration * Notional
    Risky Duration (DV01): change in CDS value per 1bp spread move
    Typically 4.0-4.5 for 5Y IG CDS
```

### Credit Relative Value

```
Single-name vs Index:
  Skew = Average single-name spread - Index spread
  Trade: if skew is wide, sell single-name protection, buy index protection
  Convergence: skew tends to mean-revert

Curve trades:
  CDS curve steepener: sell 5Y protection, buy 10Y protection
  Thesis: long-dated risk is underpriced relative to short-dated
  Duration-weighted to be spread-neutral at entry

Cross-currency basis:
  Same issuer, different currency CDS: should be equivalent (after basis adjustment)
  Deviations occur due to liquidity, investor base, and funding differences
```

## Quality Gate

Before trading credit derivatives:

- [ ] CDS pricing model validated against ISDA standard calculator
- [ ] Recovery rate assumption is market-standard and sensitivity tested
- [ ] Counterparty risk assessed (CDS is bilateral OTC — use CSA/collateral)
- [ ] Credit event definitions understood (restructuring protocol matters)
- [ ] Basis risk quantified for index vs single-name hedges
- [ ] For tranches: correlation model limitations acknowledged
- [ ] Jump-to-default risk quantified (large single-name exposure)
- [ ] Roll risk understood (index rolls change composition)
- [ ] Liquidity assessed (off-the-run CDS and bespoke tranches can be illiquid)
- [ ] Regulatory capital impact calculated (Basel III CVA, SA-CCR)
