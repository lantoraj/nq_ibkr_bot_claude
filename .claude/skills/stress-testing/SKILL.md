---
name: stress-testing
description: "Historical, hypothetical, and reverse stress testing. Scenario design, regulatory frameworks, crisis replay, and integration with risk management. Use when: User needs to design stress test scenarios for a portfolio or trading desk; Regulatory stress testing requirements (CCAR, DFAST, EBA, PRA); Evaluating portfolio resilience to specific market dislocations."
---

# Stress Testing Methodologies

> Historical, hypothetical, and reverse stress testing. Scenario design, regulatory frameworks, crisis replay, and integration with risk management.

## When to Activate

- User needs to design stress test scenarios for a portfolio or trading desk
- Regulatory stress testing requirements (CCAR, DFAST, EBA, PRA)
- Evaluating portfolio resilience to specific market dislocations
- Reverse stress testing to identify scenarios that cause business failure
- Post-crisis analysis and scenario library construction
- Board-level risk reporting requiring scenario-based loss estimates

## Core Concepts

### Types of Stress Tests

**Historical Stress Testing**
Replay actual market moves from past crises onto the current portfolio:

- 1987 Black Monday: S&P 500 -22.6% in one day, VIX spike to 150+
- 1998 LTCM/Russian crisis: credit spread blowout, liquidity evaporation, correlation convergence
- 2000-2002 Dot-com bust: Nasdaq -78%, sustained equity drawdown, credit deterioration
- 2008 GFC: Lehman default, credit spreads 600bp+, equity -55%, liquidity freeze, correlation spike to 0.9+
- 2010 Flash Crash: intraday S&P -9%, immediate recovery, market microstructure failure
- 2011 Euro sovereign crisis: peripheral spreads blowout, EUR weakness, bank funding stress
- 2015 CNY devaluation / Swiss franc de-peg: FX moves of 10-20% in minutes
- 2020 COVID crash: S&P -34% in 23 days, VIX >80, oil briefly negative, Treasury liquidity impaired
- 2022 rates shock: 425bp Fed hike cycle, 60/40 portfolio failure, UK gilt crisis (LDI), crypto collapse

Advantage: scenarios are realistic and internally consistent (cross-asset correlations embedded).
Limitation: future crises will not exactly replicate past ones.

**Hypothetical Stress Testing**
Construct plausible but unprecedented scenarios:

- Geopolitical: Taiwan conflict, major cyber attack on financial infrastructure, SWIFT disconnection
- Macro: stagflation with simultaneous equity/bond sell-off, sudden USD collapse, hyperinflation
- Market structure: central clearing failure, major market maker default, flash crash in rates
- Climate: disorderly transition, physical risk event triggering insurance losses and credit defaults
- Design requires expert judgment and cross-asset consistency checks

**Reverse Stress Testing**
Identify scenarios that would cause unacceptable losses or business failure:

- Start from a defined loss threshold (e.g., loss exceeding capital buffer, margin call cascade)
- Work backward to find market conditions that produce that loss
- Reveals hidden vulnerabilities and concentration risks
- Required by PRA (UK), part of ICAAP for banks
- Methods: optimization-based search, expert-driven scenario construction, Monte Carlo filtering

### Scenario Design Principles

1. **Internal consistency**: if equities crash, credit spreads widen, vol spikes, safe-haven flows occur
2. **Severity calibration**: scenarios should be severe but plausible — typically 3-5 sigma events
3. **Transmission channels**: identify first-order effects and second-order cascading effects
4. **Time horizon**: instantaneous shock vs. prolonged stress (matters for path-dependent positions and margin)
5. **Granularity**: major risk factors first, then sector/name-level detail

## Methodology

### Historical Scenario Implementation

1. **Select reference period**: choose start and end dates of the historical crisis
2. **Extract risk factor moves**: collect actual changes in all relevant risk factors (equities, rates, credit, FX, vol, commodities)
3. **Apply to current portfolio**: reprice all positions under the stressed risk factor values
4. **Full repricing vs. sensitivity**: full repricing preferred for non-linear positions; sensitivity-based acceptable for linear books
5. **Compute P&L impact**: aggregate across desks, asset classes, legal entities
6. **Decompose losses**: identify which positions and risk factors drive the largest losses

### Hypothetical Scenario Construction

1. **Define narrative**: articulate the economic/geopolitical story driving the scenario
2. **Identify primary risk factors**: which markets move first and by how much
3. **Model transmission**: use historical betas, regression models, or expert judgment to propagate shocks
4. **Cross-asset consistency check**: verify that rate, equity, credit, FX, and commodity moves are mutually plausible
5. **Calibrate severity**: benchmark against historical moves (e.g., "credit spread move equivalent to 2008 severity")
6. **Multi-period scenarios**: for prolonged stress, define time steps (e.g., month 1, month 3, month 12)
7. **Include second-order effects**: margin calls forcing liquidation, counterparty defaults, liquidity withdrawal

### Reverse Stress Testing Process

1. **Define failure threshold**: capital depletion, liquidity shortfall, regulatory breach, margin call exceeding capacity
2. **Identify key vulnerabilities**: largest positions, concentrated exposures, illiquid holdings, leveraged positions
3. **Construct candidate scenarios**: brainstorm market conditions that exploit vulnerabilities
4. **Quantify**: compute P&L under each candidate scenario to verify it reaches the failure threshold
5. **Assess plausibility**: assign rough probabilities or historical precedents
6. **Remediation**: develop action plans to reduce vulnerability to the most plausible failure scenarios

### Regulatory Stress Testing Frameworks

**US — CCAR/DFAST (Federal Reserve)**
- Severely adverse, adverse, and baseline scenarios provided by the Fed
- Banks must project losses, revenue, and capital ratios over 9 quarters
- Qualitative assessment of risk management and governance
- Binding capital constraint: post-stress CET1 must remain above minimum

**EU — EBA Stress Test**
- Baseline and adverse scenarios covering 3 years
- Static balance sheet assumption
- Coordinated across EU banks, results published
- Focus on credit losses, market risk losses, NII impact

**UK — PRA Annual Cyclical Scenario**
- Scenarios tailored to current macro risks
- Exploratory scenarios for emerging risks (e.g., climate)
- Reverse stress testing required as part of ICAAP

### Sensitivity Analysis vs. Stress Testing

- Sensitivity: single risk factor move (e.g., rates +100bp) — useful for understanding marginal risk
- Stress test: multi-factor, correlated move with a narrative — captures interaction effects
- Both are complementary; sensitivity analysis is faster but misses cross-asset dynamics

## Examples

### 2008 GFC Replay
```
Scenario: Apply Sep-Nov 2008 market moves to current portfolio.
Risk factor shocks:
  S&P 500: -40%
  Investment grade spreads: +350bp
  High yield spreads: +1200bp
  10Y UST yield: -150bp (flight to quality)
  VIX: from 25 to 80
  USD/EUR: +15% (USD strength)

Portfolio impact:
  Equity long/short book: -$12M (beta exposure despite hedges)
  Credit book: -$28M (spread widening on corporate bonds)
  Rates book: +$5M (long duration benefiting from flight to quality)
  Vol book: +$8M (long gamma/vega positions)
  Total: -$27M against $100M capital (-27% drawdown)
```

### Reverse Stress Test
```
Failure threshold: loss exceeding $50M (50% of capital).
Key vulnerability: concentrated long position in IG credit, levered 3x.
Scenario found: IG spreads widen 500bp (beyond 2008 levels) with
simultaneous 200bp rate rise (unusual — typically rates fall in credit stress).
This combined move produces -$55M loss.
Plausibility: low but non-zero (2022 showed rates and credit can sell off together).
Action: reduce credit leverage from 3x to 2x, add rate hedge overlay.
```

### Multi-Period Hypothetical Scenario
```
Narrative: Stagflationary shock — persistent inflation forces central bank tightening
while economy enters recession.

Month 1: Rates +75bp, equities -10%, credit spreads +50bp, oil +20%
Month 3: Rates +150bp, equities -25%, credit spreads +200bp, oil +30%
Month 12: Rates +200bp, equities -35%, HY defaults spike to 8%,
          property values -20%, USD +10%

Portfolio loss trajectory: -$5M, -$18M, -$42M
Capital ratio trajectory: 14%, 11.5%, 8.2% (approaching minimum requirement of 8%)
```

## Quality Gate

- Scenario library must cover at least 5 historical crises and 3 hypothetical scenarios
- All scenarios must demonstrate cross-asset consistency (no contradictory moves)
- Reverse stress tests must identify at least 2 plausible failure scenarios
- Full repricing required for any portfolio with >10% options or structured products
- P&L decomposition must identify top 5 risk factor contributors for each scenario
- Scenarios must be reviewed and updated at least semi-annually or after major market events
- Hypothetical scenario severity must be benchmarked against historical precedents
- Management actions and remediation plans must be documented for high-severity scenarios
- Results must be presented to senior management and board with clear implications
- Sensitivity analysis must accompany stress tests to show marginal risk factor contributions
