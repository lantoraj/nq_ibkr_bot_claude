---
name: counterparty-risk
description: "Margin, collateral, CVA/DVA/FVA, central clearing, netting, wrong-way risk, and credit support framework. Use when: User evaluating counterparty exposure in OTC derivative portfolios; Computing CVA, DVA, or FVA for derivative pricing; Designing collateral agreements (CSA) and margin frameworks."
---

# Counterparty Credit Risk

> Margin, collateral, CVA/DVA/FVA, central clearing, netting, wrong-way risk, and credit support framework.

## When to Activate

- User evaluating counterparty exposure in OTC derivative portfolios
- Computing CVA, DVA, or FVA for derivative pricing
- Designing collateral agreements (CSA) and margin frameworks
- Assessing the impact of central clearing mandates
- Analyzing wrong-way risk in derivative portfolios
- Managing bilateral vs. cleared counterparty risk

## Core Concepts

### Counterparty Exposure Fundamentals

**Credit Exposure**
- The loss if a counterparty defaults today = max(0, mark-to-market of all trades with that counterparty)
- Only positive MTM creates exposure (you lose if they owe you and default)
- Negative MTM: no credit risk to you (but you are their credit risk — DVA perspective)

**Expected Exposure (EE)**
- EE(t) = E[max(0, V(t))] — expected positive exposure at future time t
- Computed via Monte Carlo simulation of risk factor paths
- EE profile: typically hump-shaped for swaps (increases then decreases as payments are exchanged)

**Potential Future Exposure (PFE)**
- PFE(t) = quantile of the positive exposure distribution at time t (e.g., 97.5%)
- Represents a worst-case exposure measure analogous to VaR
- Used for credit limit monitoring: ensures exposure stays within approved counterparty limits

**Expected Positive Exposure (EPE)**
- EPE = (1/T) * integral of EE(t) dt from 0 to T — time-averaged expected exposure
- Used in regulatory capital calculations (SA-CCR, IMM)
- Effective EPE: non-decreasing version of EPE (captures roll-off risk)

### Netting and Close-Out

**Close-Out Netting**
- ISDA Master Agreement allows netting of all trades with a counterparty upon default
- Net exposure = max(0, sum of MTM across all trades) — dramatically reduces exposure
- Without netting: exposure = sum of max(0, MTM_i) — each positive trade is at risk
- Netting benefit is greatest when portfolio has offsetting trades (some positive, some negative MTM)
- Legal enforceability: netting must be legally valid in the counterparty's jurisdiction

**Payment Netting**
- Net cashflows on the same date in the same currency
- Reduces settlement risk (Herstatt risk) but smaller impact than close-out netting

### Margin Framework

**Initial Margin (IM)**
- Posted at trade inception to cover potential future exposure during close-out period
- Covers the expected change in portfolio value during the margin period of risk (MPOR)
- Bilateral: ISDA SIMM (Standard Initial Margin Model) based on sensitivities
- Cleared: CCP-determined, typically based on historical simulation VaR at 99%+ confidence
- Two-way exchange: both parties post IM (segregated at a third-party custodian)

**Variation Margin (VM)**
- Daily (or intraday) mark-to-market settlement
- Winning party receives VM; losing party posts VM
- Reduces credit exposure to approximately one day's potential move
- Minimum transfer amount (MTA): typically $500K-$1M to avoid operational burden
- Threshold: exposure level below which no VM is exchanged (reduces to zero under new bilateral rules)

**Margin Period of Risk (MPOR)**
- Time from last margin exchange to close-out of defaulted portfolio
- Bilateral: typically 10 business days
- Cleared: typically 5 business days (more liquid, standardized products)
- Includes: margin call, dispute resolution, close-out/replacement of trades

## Methodology

### Credit Valuation Adjustment (CVA)

CVA is the market price of counterparty credit risk — the expected loss due to counterparty default:

**Unilateral CVA**
- CVA = (1 - R) * integral from 0 to T of EE(t) * dPD(t)
- R = recovery rate (typically 40% for senior unsecured)
- PD(t) = cumulative default probability (from CDS spreads or internal ratings)
- EE(t) = expected exposure at time t (from Monte Carlo)
- Discrete approximation: CVA = (1-R) * sum over time buckets of EE_i * (PD_{i} - PD_{i-1})

**Bilateral CVA (with DVA)**
- DVA = debit valuation adjustment = value of own default to the counterparty
- DVA = (1 - R_own) * integral of ENE(t) * dPD_own(t)
- ENE = expected negative exposure (exposure from counterparty's perspective)
- Net adjustment: CVA - DVA
- DVA is controversial: own credit deterioration appears as a profit

**CVA Sensitivities**
- CVA spread sensitivity: how CVA changes with counterparty CDS spread
- CVA exposure sensitivity: how CVA changes with underlying risk factors
- CVA must be hedged: CDS on counterparty (for spread risk), underlying hedges (for exposure risk)

### Funding Valuation Adjustment (FVA)

- FVA captures the cost of funding uncollateralized derivative positions
- FVA = integral of (funding_spread) * (expected_funding_needs(t)) dt
- Uncollateralized trades require funding; collateralized trades are self-funding
- FVA is debated: some argue it is a real cost, others argue it double-counts with DVA
- In practice: most dealers include FVA in pricing, adding 1-10bp to uncollateralized derivative prices

### SA-CCR (Standardized Approach for Counterparty Credit Risk)

Basel III replacement for CEM (Current Exposure Method):

1. **Replacement cost (RC)**: max(V - C, 0) where V = portfolio MTM, C = collateral held
2. **Potential future exposure (PFE)**: aggregated add-on based on trade notionals, maturity, and asset class
3. **Exposure at default**: EAD = alpha * (RC + PFE), where alpha = 1.4
4. **Add-on calculation**: notional * supervisory factor * maturity factor * delta adjustment
5. Supervisory factors by asset class: IR (0.5%), FX (4%), equity (32%), credit (0.54-6%), commodity (18-40%)
6. Netting benefit captured through hedging set aggregation

### Wrong-Way Risk

**Specific Wrong-Way Risk (SWWR)**
- Exposure increases when counterparty credit quality deteriorates due to a direct link
- Example: sold a put option to a bank on its own stock — if stock crashes, counterparty is more likely to default AND the option is deep ITM
- Must be identified trade by trade; cannot be modeled statistically

**General Wrong-Way Risk (GWWR)**
- Positive correlation between counterparty default probability and market exposure
- Example: interest rate swap with a corporate — if rates rise, corporate may struggle AND swap MTM increases
- Modeled by correlating the exposure simulation with the default process
- Increases CVA significantly: can be 50-200% higher than independent case

### Central Counterparty (CCP) Clearing

**Advantages**
- Multilateral netting: reduces total system exposure
- Standardized margining: IM and VM rules, daily settlement
- Default management: CCP has established waterfall for member default
- Transparency: standardized products, centralized reporting

**CCP Default Waterfall**
1. Defaulting member's initial margin
2. Defaulting member's default fund contribution
3. CCP's own capital (skin in the game)
4. Non-defaulting members' default fund contributions
5. CCP's remaining capital
6. Assessment powers (additional calls on members)

**Risks of CCP Clearing**
- CCP concentration risk: "too big to fail" CCPs create systemic risk
- Procyclical margin calls: IM increases in stress, forcing liquidation
- Default fund mutualization: surviving members bear losses of defaulting member
- CCP interoperability: multiple CCPs can fragment netting

## Examples

### CVA Calculation
```
Interest rate swap with Corporate X:
  Notional: $100M, 5-year maturity
  Expected exposure profile: EE = [$0, $2M, $3.5M, $4M, $3M] (annual)
  CDS spread of Corporate X: 200bp (implies PD approximately 3.3%/year)
  Recovery rate: 40%

CVA = (1-0.40) * sum of EE_i * delta_PD_i
    = 0.60 * ($0*0.033 + $2M*0.033 + $3.5M*0.032 + $4M*0.031 + $3M*0.030)
    = 0.60 * ($0 + $66K + $112K + $124K + $90K)
    = 0.60 * $392K = $235K

CVA = $235K or 2.35bp of notional.
This cost is embedded in the swap pricing as a spread adjustment.
```

### ISDA SIMM Initial Margin
```
Portfolio with counterparty Y:
  IR delta: $5M DV01 in USD
  FX delta: $2M sensitivity to EUR/USD
  Equity vega: $500K sensitivity to S&P vol

SIMM calculation (simplified):
  IR risk charge: $5M * risk_weight(USD_2Y) = $5M * 61bp = $305K
  FX risk charge: $2M * risk_weight(EUR/USD) = $2M * 7.5% = $150K
  Equity risk charge: $500K * risk_weight(large_cap) = $500K * 25% = $125K
  Aggregated (with diversification): sqrt($305K^2 + $150K^2 + $125K^2) = $370K

Initial margin requirement: $370K posted by each party (two-way).
```

### Wrong-Way Risk Impact
```
CDS sold to Bank Z on a correlated reference entity:
  Standard CVA (independent default): $180K
  Correlation between Bank Z default and reference entity spread: 0.60

Wrong-way adjusted CVA:
  Increase EE by factor reflecting correlation: EE_wwr = EE * (1 + rho * stress_factor)
  With rho=0.6 and stress_factor=1.5: EE_wwr = EE * 1.9
  Wrong-way CVA = $180K * 1.9 = $342K (90% increase)

This demonstrates why wrong-way risk identification is critical for pricing.
```

## Quality Gate

- All OTC counterparties must have approved credit limits with PFE monitoring
- CVA must be computed for all uncollateralized or partially collateralized counterparties
- CVA calculations must use market-implied default probabilities (CDS spreads) where available
- Netting must be validated: ISDA Master Agreement and netting opinion must be in place
- Margin agreements (CSA terms) must be accurately reflected in exposure calculations
- Wrong-way risk must be assessed for every new trade: screen for specific and general WWR
- IM calculations under SIMM must be validated against the counterparty's independent calculation
- CCP exposure must include default fund contribution in total counterparty risk assessment
- Exposure simulations must use at least 1,000 Monte Carlo paths with appropriate time steps
- CVA hedging effectiveness must be monitored: track CVA P&L vs. hedge P&L
- Collateral eligibility, haircuts, and rehypothecation rights must be documented per CSA
