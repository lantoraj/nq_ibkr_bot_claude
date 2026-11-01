---
name: fx-fundamentals
description: "FX Fundamental Analysis. Use when: Analyzing currency valuation using fundamental models (PPP, interest rate parity, balance of payments); Evaluating central bank policy divergence and its impact on exchange rates; Assessing terms of trade shifts, current account dynamics, and capital flows."
---

# FX Fundamental Analysis

## When to Activate
- Analyzing currency valuation using fundamental models (PPP, interest rate parity, balance of payments)
- Evaluating central bank policy divergence and its impact on exchange rates
- Assessing terms of trade shifts, current account dynamics, and capital flows
- Understanding FX intervention mechanics and their effectiveness
- Building medium-to-long term FX views based on macro fundamentals

## Core Concepts

### Purchasing Power Parity (PPP)

**Absolute PPP:**
- Exchange rate should equalize price levels: S = P_domestic / P_foreign
- The Economist's Big Mac Index is the popular approximation
- Rarely holds in practice due to non-tradeable goods, tariffs, transportation costs
- Useful as long-term anchor: currencies 20%+ below PPP tend to appreciate over 5-10 years

**Relative PPP:**
- Change in exchange rate = inflation differential
- delta_S = pi_domestic - pi_foreign
- Better predictor than absolute PPP but still imprecise over short horizons
- Works reasonably well for high-inflation countries (Turkey, Argentina)

**PPP-Based Valuation:**
```
OECD PPP estimates provide fair value benchmarks:
- If spot rate is 20%+ above PPP: currency is overvalued
- If spot rate is 20%+ below PPP: currency is undervalued

Example: If EUR/USD PPP = 1.30 and spot = 1.08
- EUR is 17% undervalued vs USD on PPP basis
- Suggests long-term EUR appreciation potential
- But PPP convergence can take years; not a timing tool
```

### Interest Rate Parity

**Covered Interest Rate Parity (CIP):**
```
F/S = (1 + r_domestic) / (1 + r_foreign)

Where F = forward rate, S = spot rate
Forward premium/discount reflects interest rate differential

In practice: CIP holds tightly due to arbitrage
Post-2008 exception: cross-currency basis emerged
Basis = deviation from CIP; reflects USD funding premium
Persistent basis in JPY, EUR reflects structural USD demand
```

**Uncovered Interest Rate Parity (UIP):**
```
Expected change in spot = interest rate differential
E[delta_S] = r_domestic - r_foreign

Implication: high-yielding currencies should depreciate
Reality: UIP consistently fails — "forward premium puzzle"
Carry trade exploits this: borrow low-rate, invest high-rate
Carry works until it doesn't: violent unwind during risk-off (JPY carry unwinds)
```

**Carry Trade Mechanics:**
```
Return = yield differential - spot depreciation
Sharpe ratio of carry: historically 0.5-0.8 (attractive)
Risk: left-tail events (carry crashes 3-5x faster than it builds)
Risk management: size carry trades to survive 3-sigma moves
JPY carry unwind (Aug 2024): JPY appreciated 12% in 3 weeks
```

### Balance of Payments Approach

**Current Account:**
- Trade balance: exports - imports of goods and services
- Primary income: investment income flows (interest, dividends)
- Current account surplus = net capital exporter = structural currency demand
- Chronic deficit countries rely on capital inflows to fund the gap

**Capital Account / Financial Account:**
- Portfolio flows: foreign purchases of stocks and bonds
- FDI: direct investment in businesses and real estate
- Reserve changes: central bank FX reserve accumulation/depletion
- Hot money vs sticky capital: portfolio flows are flighty, FDI is stable

**Flow-Based FX Framework:**
```
Currency strengthens when:
1. Current account surplus is large and growing
2. Positive rate differentials attract capital inflows
3. FDI inflows are strong (structural demand)
4. Central bank is accumulating reserves (intervention)

Currency weakens when:
1. Current account deficit is widening
2. Rate differential narrows or reverses
3. Capital flight (portfolio outflows)
4. Central bank depleting reserves to defend currency
```

### Monetary Models

**Monetary Approach:**
```
S = (m_d - m_f) - phi*(y_d - y_f) + lambda*(r_d - r_f)

Where:
m = money supply, y = real income, r = interest rate
d = domestic, f = foreign

Predicts depreciation when:
- Money supply grows faster than foreign (expansionary policy)
- Real income grows slower than foreign
- Interest rates rise (due to expected inflation, not real tightening)
```

**Real Interest Rate Differential:**
```
Most practically useful model for medium-term FX:
Real rate = Nominal rate - Inflation expectations

Currency appreciation when:
- Real rate differential widens in country's favor
- Both nominal rates and inflation expectations matter
- Central bank credibility affects inflation expectations

Example: If US real rate = 2.5% and EU real rate = 0.5%
- 200bp real rate advantage favors USD
- But if rates are converging, direction matters more than level
```

### FX Intervention

**Types:**
- **Sterilized intervention** — CB buys/sells FX and offsets money supply impact with bond operations
- **Unsterilized intervention** — CB changes money supply directly (more effective but has monetary policy implications)
- **Verbal intervention** — officials talk currency direction (cheapest, first line of defense)
- **Capital controls** — restrict capital flows directly (last resort)

**Effectiveness Framework:**
```
Intervention is more effective when:
1. Consistent with monetary policy direction
2. Coordinated across multiple central banks (Plaza Accord)
3. Reserves are ample relative to daily FX turnover
4. Market is not already extremely positioned in the direction CB wants

Intervention fails when:
1. Fighting fundamental forces (unsustainable peg)
2. Reserves are depleted (triggers speculative attack)
3. One-sided without coordination
4. Market size overwhelms CB resources ($7.5T daily FX turnover)
```

### Central Bank Policy Impact on FX

**Hawkish vs Dovish:**
```
Hawkish surprise (tighter than expected):
- Short rates rise, front-end of curve sells off
- Currency appreciates (higher carry, capital inflows)
- Largest impact on closely-watched data: NFP, CPI, FOMC

Dovish surprise (easier than expected):
- Short rates fall, front-end rallies
- Currency depreciates
- Impact is larger when positioning is crowded against the move
```

**Policy Divergence Trading:**
```
Strongest FX trends occur during policy divergence:
- 2014-2015: Fed tightening while ECB/BOJ easing -> USD rallied 25%
- 2022: Fed hiking aggressively, BOJ maintaining YCC -> USD/JPY rallied to 151
- 2023-2024: Fed pivot expectations vs BOJ tightening -> JPY recovery

Monitor: rate differential trajectory, not just current level
```

## Methodology

### FX Fundamental Assessment Process
1. **Valuation** — where is the currency relative to PPP and REER (Real Effective Exchange Rate)?
2. **Rate differentials** — current levels and expected trajectory (policy divergence)
3. **Current account** — surplus/deficit trend, terms of trade
4. **Capital flows** — portfolio flows, FDI, reserve accumulation
5. **Positioning** — CFTC IMM data (speculative positioning), risk reversals (options skew)
6. **Central bank stance** — current policy, forward guidance, intervention risk
7. **Risk sentiment** — safe haven flows (USD, JPY, CHF strengthen in risk-off)

### Trade Construction
```
Combine fundamental view with:
- Spot FX position (simplest, most direct)
- FX forwards (embed rate differential, no carry cost)
- FX options (defined risk, express views on vol + direction)
- Cross-currency basis swaps (exploit funding dislocations)

Position sizing:
- Size based on stop distance and portfolio risk budget
- FX is leveraged market: 1% daily moves are common (20% annualized vol for G10)
- Max 2% portfolio risk per FX trade
- EM FX: higher vol (30-50% annualized), size accordingly
```

## Examples

### Example 1: Rate Differential Trade
```
Setup:
- US Fed funds: 5.25%, Fed likely to hold for 6 months
- ECB deposit rate: 3.75%, ECB likely to cut next meeting
- EUR/USD spot: 1.0850
- 2Y rate differential: US +175bps over Germany

Trade: Short EUR/USD
- Entry: 1.0850
- Target: 1.0500 (divergence continues)
- Stop: 1.1100 (invalidates rate divergence thesis)
- Carry: earn ~175bps annualized (positive carry on short EUR)

Risk/reward: 350 pips reward / 250 pips risk = 1.4:1
Plus positive carry improves effective risk/reward over time
```

### Example 2: Terms of Trade Shift
```
Scenario: Oil price rises from $70 to $100/barrel

Winners (oil exporters): CAD, NOK, RUB (if tradeable)
Losers (oil importers): JPY, INR, TRY

Trade: Long CAD/JPY
- Canada benefits from terms of trade improvement
- Japan's energy import bill increases, worsening current account
- Rate differential: Bank of Canada > BOJ
- Technical: CAD/JPY near support, positive carry

Entry: 107.00
Target: 115.00 (8 big figures)
Stop: 104.00 (3 big figures)
Risk/reward: 2.7:1 plus positive carry
```

### Example 3: PPP Mean Reversion
```
Analysis: NOK is 30% undervalued vs USD on PPP basis
Cheapest in 30 years on REER (real effective exchange rate)

Fundamental backdrop:
- Norway: current account surplus (oil revenues)
- Norges Bank: rates near US levels
- Oil price elevated (supports NOK)

Challenge: PPP mean reversion is slow (multi-year)
Approach: use NOK undervaluation as part of diversified carry basket
Allocate 15% of FX portfolio to long NOK/USD
Hedge with NOK put options for tail risk protection
Expected holding period: 1-3 years
```

## Quality Gate

Before implementing FX fundamental trades, verify:

- [ ] Fundamental model is specified — which model drives the view (rates, flow, valuation)?
- [ ] Timeframe matches the signal — PPP is multi-year, rate differentials are multi-month, flows are multi-week
- [ ] Positioning data checked — CFTC IMM, options risk reversals; crowded positions increase reversal risk
- [ ] Carry is calculated correctly — include both spot direction view and carry (positive or negative)
- [ ] Central bank intervention risk assessed — is the CB likely to intervene at current levels?
- [ ] Risk-off correlation understood — will your FX position gain or lose during a market crash?
- [ ] Liquidity conditions normal — FX liquidity drops significantly during holidays, year-end, and stress events
- [ ] Correlation with other portfolio positions mapped — FX trades can amplify or hedge existing exposures
- [ ] Stop loss is based on fundamental invalidation, not just pips — what would change your thesis?
- [ ] Event risk calendar checked — major data releases, central bank meetings, elections
