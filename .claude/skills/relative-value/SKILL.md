---
name: relative-value
description: "Relative Value Strategies. Use when: User wants to trade price dislocations between related instruments; Designing capital structure arbitrage (equity vs credit vs CDS); Building convertible bond arbitrage strategies."
---

# Relative Value Strategies

name: relative-value
description: Relative value strategies — cross-asset, capital structure, convertible arb.
origin: ECT

## When to Activate

- User wants to trade price dislocations between related instruments
- Designing capital structure arbitrage (equity vs credit vs CDS)
- Building convertible bond arbitrage strategies
- Trading basis between cash and derivatives (bond basis, CDS-bond basis)
- Analyzing on-the-run vs off-the-run Treasury spread opportunities

## First Questions

1. Which relative value trade type (capital structure, convertible, basis, Treasury RV)?
2. What is the theoretical relationship that anchors fair value?
3. What is the convergence catalyst (maturity, corporate action, market normalization)?
4. What is the available leverage and financing cost?
5. What is the liquidity profile of each leg (can you exit under stress)?

## Core Concepts

### Relative Value Philosophy

Relative value trading exploits temporary mispricings between related securities. Unlike directional trading, RV strategies profit from convergence to fair value regardless of market direction.

```
Key principles:
  1. Identify theoretical relationship (no-arbitrage, structural, statistical)
  2. Measure deviation from fair value (spread, ratio, z-score)
  3. Establish position when deviation exceeds threshold
  4. Profit when spread reverts to fair value
  5. Hedge out systematic risks (market, sector, rates)

Risk profile:
  - Low volatility, moderate Sharpe (0.5-1.5)
  - Requires leverage to generate meaningful returns (3-10x typical)
  - Tail risk: convergence trades can diverge further before reverting
  - Liquidity risk: both legs must remain liquid for hedging
  - LTCM lesson: levered RV can be catastrophically wrong in crises
```

### Capital Structure Arbitrage

Capital structure arb exploits mispricings between different securities issued by the same company.

```
Instruments in the capital structure (senior to junior):
  Bank debt (secured) > Senior bonds > Subordinated bonds > Preferred stock > Equity

Trade types:
  1. CDS vs Equity:
     - CDS spread implies equity vol (via Merton model)
     - If CDS is "cheap" relative to equity vol: buy protection, buy equity
     - If CDS is "rich": sell protection, short equity
     - Calibrate using structural credit models (KMV, CreditGrades)

  2. Senior vs Subordinated debt:
     - Spread between senior and sub should reflect recovery difference
     - If sub spread widens excessively vs senior: buy sub, sell senior
     - Convergence driver: approaching maturity or credit improvement

  3. Equity vs Credit:
     - When equity rallies but credit spreads stay wide: buy credit
     - When equity falls but credit stays tight: sell credit
     - Use Merton distance-to-default to calibrate fair relationship
```

### Convertible Bond Arbitrage

Convertible bonds embed an equity option within a bond. Conv arb extracts the embedded option cheaply.

```
Convertible bond decomposition:
  Convertible Value = Bond Floor + Equity Option Value

  Bond floor: present value of coupon and principal (as straight bond)
  Option value: call option on underlying equity (adjusted for dilution)

Classic convertible arb:
  Long convertible bond, short delta shares of underlying equity
  Delta = dConvertible/dStock (conversion ratio * option delta)

  Profit sources:
    1. Gamma: buy low vol, scalp gamma as stock moves
    2. Carry: coupon income from bond exceeds short rebate cost
    3. Mispricing: convertible trades below theoretical value (cheap vol)

  Risks:
    - Credit: if issuer defaults, bond floor collapses
    - Borrow: short stock may be hard/expensive to borrow
    - Liquidity: convertible bond market is OTC, can become illiquid
    - Call risk: issuer calls the bond, forcing conversion

Greeks management:
  Delta: hedge by adjusting short stock position daily
  Gamma: positive gamma (long options) — profit from stock moves
  Vega: long vega (benefit from vol increase)
  Rho: sensitive to interest rate changes (affects bond floor)
  Credit: monitor credit spread changes (affects bond floor)
```

### Basis Trades

Basis trades exploit price differences between cash instruments and their derivative equivalents.

```
Bond basis (cheapest-to-deliver):
  Basis = Cash Bond Price - (Futures Price * Conversion Factor)
  If basis is negative: buy bond, sell futures (positive carry trade)
  CTD optionality: futures seller has delivery options (timing, which bond)
  Gross basis vs net basis (net = gross - carry)

CDS-bond basis:
  Basis = CDS Spread - Asset Swap Spread (Z-spread of cash bond)
  Negative basis: CDS protection is cheaper than bond spread implies
    Trade: Buy bond + Buy CDS protection = risk-free spread (theoretically)
  Positive basis: CDS is more expensive than bond spread
    Trade: Sell CDS protection + Short bond (harder to execute)

  Basis drivers:
    - Counterparty risk in CDS (affects CDS price)
    - Funding costs (affects bond price)
    - Liquidity premium (bonds less liquid = wider spread)
    - CTD optionality in CDS (restructuring triggers)
    - Supply/demand imbalances (bond issuance, CDS hedging flows)
```

### On-the-Run vs Off-the-Run Treasury Spread

```
The on-the-run (OTR) Treasury is the most recently issued bond at each maturity.
Off-the-run (OFR) bonds are previous issues.

OTR trades at a premium (lower yield) due to:
  - Superior liquidity (higher trading volume, tighter bid-ask)
  - Repo specialness (OTR can be lent at below-GC repo rates)
  - Benchmark status (used as reference in derivatives and pricing)

Spread: OTR yield - OFR yield = -2 to -15 bps (OTR yields less)

Trade:
  Short on-the-run, long off-the-run (earn spread as OTR rolls off)
  Duration-matched to be rate-neutral
  Convergence catalyst: when new OTR is issued, previous OTR becomes OFR
  Timeline: convergence occurs over 3-6 months as new issuance cycle completes

Risk:
  - Flight to quality: OTR premium widens in crises (2008, 2020)
  - Repo squeeze: OTR goes on special, short is expensive to maintain
  - Leverage: spreads are small, requires leverage for meaningful P&L
```

### Swap Spread Trades

```
Swap spread = Swap Rate - Treasury Yield (same maturity)

Historically positive (swap rate > Treasury yield) because:
  - Swap has counterparty risk (LIBOR/SOFR vs risk-free)
  - Treasury has scarcity premium
  - Balance sheet and regulatory costs favor swaps differently

Swap spread went negative in 2015 (30y) and 2020 (all tenors):
  - Treasury supply overwhelmed demand
  - Dealer balance sheet constraints prevented arbitrage
  - Basis trade unwinding amplified moves

Trading swap spreads:
  Receive fixed in swap + Short Treasury (if spread expected to narrow)
  Pay fixed in swap + Long Treasury (if spread expected to widen)
  Duration-neutral by construction
  Carry depends on funding and repo rates
```

## Detailed Methodology

### RV Signal Construction

```
Statistical relative value:
  1. Compute spread between related instruments
  2. Estimate fair value: rolling mean, cointegration residual, or model-implied
  3. Compute z-score: z = (spread - fair_value) / rolling_std
  4. Entry: |z| > 2.0 (trade mean reversion)
  5. Exit: |z| < 0.5 (spread has normalized)
  6. Stop: |z| > 4.0 (spread has blown out, cut losses)

Model-based relative value:
  1. Specify theoretical relationship (Merton model, option pricing model)
  2. Calibrate model to market data
  3. Compute model-implied fair value for each instrument
  4. Trade deviations from model value
  5. Re-calibrate model periodically (weekly or monthly)
```

### Risk Management for RV

```
Leverage management:
  Gross leverage: 3-10x for most RV strategies
  Net leverage: near zero (hedged positions)
  Monitor: gross exposure, margin requirements, funding liquidity

Liquidity risk:
  Measure bid-ask spread for both legs daily
  Stress test: what if bid-ask doubles? Can you still exit?
  Size positions relative to average daily volume (max 5-10% of ADV)

Convergence risk:
  Set maximum holding period (if convergence hasn't happened, exit)
  Stop-loss at z-score = 4.0 or specific dollar loss
  LTCM lesson: positions may be right eventually but margin calls kill you first

Correlation risk:
  In stress, correlations across RV trades increase
  Portfolio of "uncorrelated" RV trades becomes correlated in crisis
  Stress test portfolio assuming 0.5 correlation across all positions
```

## Quality Gate

Before deploying a relative value strategy:

- [ ] Theoretical relationship is well-established (no-arbitrage, structural model, or strong empirical basis)
- [ ] Convergence catalyst identified (maturity, rebalancing, issuance cycle)
- [ ] Both legs are liquid enough to enter and exit under stress
- [ ] Leverage is within risk limits and margin requirements are understood
- [ ] Funding cost is modeled accurately (repo, margin, borrow cost)
- [ ] Tail risk scenario analyzed (LTCM 1998, GFC 2008, COVID 2020)
- [ ] Correlation across concurrent RV positions stress-tested
- [ ] Transaction costs deducted (OTC instruments have wider spreads)
- [ ] Model risk assessed (structural models can be miscalibrated)
- [ ] Stop-loss and maximum holding period defined
