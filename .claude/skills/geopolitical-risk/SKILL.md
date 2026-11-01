---
name: geopolitical-risk
description: "Geopolitical Risk for Trading. Use when: Assessing the market impact of geopolitical events (conflicts, sanctions, elections); Building scenario analysis frameworks for geopolitical uncertainty; Trading supply chain disruptions caused by geopolitical events."
---

# Geopolitical Risk for Trading

## When to Activate
- Assessing the market impact of geopolitical events (conflicts, sanctions, elections)
- Building scenario analysis frameworks for geopolitical uncertainty
- Trading supply chain disruptions caused by geopolitical events
- Evaluating safe haven flows and war premiums in commodities
- Analyzing sanctions regimes and their impact on markets and capital flows

## Core Concepts

### Geopolitical Risk Measurement

**GPR Index (Caldara & Iacoviello):**
- Text-based index counting geopolitical risk references in major newspapers
- Two components: geopolitical threats (forward-looking) and geopolitical acts (realized events)
- Historical average: ~100; spikes above 200 = elevated risk (9/11, Iraq War, Ukraine invasion)
- Correlation with assets: negative for equities (risk-off), positive for gold and oil
- Limitations: media attention bias, does not quantify severity or duration

**Other Risk Measures:**
- **Political risk indices** — Eurasia Group, EIU country risk scores
- **Implied volatility** — VIX, OVX (oil), GVZ (gold) spike during geopolitical events
- **CDS spreads** — sovereign CDS prices reflect country-specific political risk
- **Safe haven flows** — price of gold, UST, JPY, CHF as proxy for risk appetite
- **Shipping insurance rates** — war risk premiums for specific shipping lanes

### Scenario Analysis Framework

**Structured Approach:**
```
Step 1: Define the geopolitical event or risk
Step 2: Identify plausible scenarios (3-5, from best to worst case)
Step 3: Assign probability to each scenario
Step 4: Map market impact per scenario across asset classes
Step 5: Calculate expected impact (probability-weighted)
Step 6: Identify asymmetries (which scenario is most underpriced?)
Step 7: Design trades that profit from underpriced scenarios

Scenario structure:
- Base case (40-60%): most likely outcome, usually partially priced
- Bull case (15-25%): de-escalation, resolution
- Bear case (15-25%): escalation, widening conflict
- Tail case (5-10%): extreme outcome, major market dislocation
```

**Key Principles:**
- Markets price geopolitical risk inefficiently — tend to under-react to slowly building risks, over-react to sudden events
- "Buy the invasion, sell the war" — markets often bottom on the event itself and recover
- Duration matters more than intensity — short sharp events are absorbed quickly; prolonged uncertainty drags on growth
- Second-order effects are often more important than direct impact (sanctions -> supply chains -> inflation)

### Supply Chain Disruption Trading

**Critical Chokepoints:**
```
Strait of Hormuz:
- 20% of global oil supply transits through
- Iran-related risk: closure would spike oil $30-50/bbl
- Insurance costs for tankers reflect real-time risk assessment

Strait of Malacca:
- 25% of global trade by value
- Choke point for oil shipments to China, Japan, Korea
- South China Sea tensions affect risk pricing

Suez Canal:
- 12% of global trade
- 2021 Ever Given blockage: short-term disruption, limited price impact
- Houthi attacks (2024): Red Sea rerouting added 10-14 days transit, raised shipping costs 5-10x

Taiwan Strait:
- 90%+ of advanced semiconductor manufacturing
- TSMC disruption would be catastrophic for global tech supply chains
- Most consequential geopolitical risk for markets
```

**Commodity Supply Disruption Framework:**
```
Impact severity = f(market share, substitutability, inventory buffer, duration)

High impact (>10% price move expected):
- Major producer sanctions (Russia oil/gas, Iran)
- Chokepoint closure (Hormuz, Malacca)
- Multi-month conflict in producing region

Medium impact (5-10% price move):
- Temporary export restrictions (Indonesia nickel, India wheat)
- Targeted sanctions on specific companies
- Regional conflict near production areas

Low impact (<5% price move):
- Verbal threats without action
- Short-term transit disruptions with alternatives
- Sanctions with significant waivers/enforcement gaps
```

### Sanctions Impact Analysis

**Sanctions Framework:**
```
Types:
1. Targeted/smart sanctions: individuals, entities (freeze assets, travel bans)
2. Sectoral sanctions: specific industries (energy, finance, technology)
3. Comprehensive sanctions: entire country embargo (Iran, North Korea, Cuba)
4. Secondary sanctions: penalize third parties dealing with sanctioned entities
5. SWIFT exclusion: cut off from international payment system

Market impact assessment:
- Direct impact: trade flows disrupted, commodity supply reduced
- Indirect impact: compliance costs, supply chain restructuring
- Financial impact: capital flight, currency collapse in sanctioned country
- Evasion dynamics: sanctioned goods find alternative routes (discounted pricing)

Example — Russia (2022):
- Oil: price cap at $60/bbl; Russian crude trades at discount to Brent
- Gas: pipeline flows to Europe reduced 80%+
- LNG: Europe pivoted to US/Qatar LNG (structural shift)
- Financial: SWIFT exclusion for major banks, asset freezes
- Secondary: "shadow fleet" of tankers for Russian oil transport
- Market impact: energy price spike, European recession risk, LNG infrastructure buildout
```

### Safe Haven Flows

**Safe Haven Asset Hierarchy:**
```
During geopolitical crisis:
1. US Treasuries (strongest safe haven; "full faith and credit")
2. Gold (traditional store of value, no counterparty risk)
3. USD (reserve currency, liquidity premium)
4. JPY (current account surplus, risk-off repatriation)
5. CHF (neutrality premium, current account surplus)

Asset behavior during geopolitical events:
- Equities: sell off (risk premium increases)
- Credit spreads: widen (flight to quality)
- Oil: rallies if supply threatened; mixed if demand at risk
- VIX: spikes (demand for hedges)
- EM assets: sell off (capital flight to safety)
- Crypto: mixed (sometimes safe haven, sometimes risk asset)
```

**"Buy the Invasion" Pattern:**
```
Historical pattern analysis:
- Markets tend to sell off in anticipation of conflict
- Actual onset of conflict often marks the bottom (uncertainty resolved)
- Recovery begins within days to weeks unless conflict fundamentally alters economic trajectory

Examples:
- Gulf War (1990-91): S&P bottomed on invasion, rallied 30% in 12 months
- Iraq War (2003): S&P bottomed day before invasion, rallied 45% in 12 months
- Ukraine (2022): S&P sold off 8% in February, bottomed in March
  Exception: energy crisis and inflation made recovery slower

Caveats:
- Pattern works for localized conflicts with limited global economic impact
- If conflict escalates to world power confrontation: different outcome entirely
- Never trade this pattern mechanically — assess each situation on merits
```

### Election Trading

**Election Risk Framework:**
```
Key variables:
1. Polling accuracy: margin of error, trend direction, poll bias
2. Policy platform: which sectors benefit/suffer under each candidate?
3. Market positioning: consensus expectations vs actual uncertainty
4. Transition risk: contested elections, delayed results

Historical US election patterns:
- Pre-election uncertainty suppresses risk-taking (VIX rises)
- Post-election clarity triggers rally (usually regardless of winner)
- Sector rotation: defense, energy, healthcare, tech most policy-sensitive
- Policy implementation lags election by months (legislative process)

Trading approach:
- Before election: buy volatility (straddles), reduce directional risk
- After result: position for expected policy impact on sectors
- Beware consensus trades: if "everyone" expects X outcome, different outcome causes larger move
```

**International Elections:**
- EM elections can be existential for currencies (Argentina, Turkey, Brazil)
- European elections: impact on EU cohesion, fiscal policy, ECB independence
- Key risk: populist/anti-establishment outcomes that threaten institutional stability

## Methodology

### Geopolitical Event Trading Process
1. **Assess the event** — what is happening, who are the actors, what are their objectives?
2. **Build scenarios** — 3-5 outcomes with probabilities
3. **Map market impact** — for each scenario, across equities, rates, FX, commodities
4. **Identify mispricings** — which scenario is the market not pricing?
5. **Design asymmetric trades** — risk $1 to make $3+ if underpriced scenario materializes
6. **Monitor and adapt** — geopolitical situations are fluid; update probabilities in real-time

### Portfolio Hedging for Geopolitical Risk
```
Standing hedges (always-on):
- 5-10% gold allocation (permanent geopolitical hedge)
- Long-dated put options on equity portfolio (tail risk protection)
- Diversification across currencies and geographies

Event-specific hedges:
- Oil call options ahead of Middle East escalation risk
- VIX call spreads before elections or known risk events
- EM CDS or put options for country-specific risk
- Commodity-specific hedges for supply chain disruptions

Cost management:
- Hedge cost should not exceed 1-2% of portfolio value annually
- Use spreads (call spreads, put spreads) to reduce premium
- Roll hedges systematically, not in panic
```

## Examples

### Example 1: Middle East Escalation Scenario
```
Event: Tensions between Iran and Gulf states escalating

Scenario A — De-escalation (35%):
- Diplomatic resolution, tensions ease
- Oil: -$5/bbl, Gold: -2%, Equities: +1%

Scenario B — Proxy conflict (40%):
- Regional conflict but no direct Iran engagement
- Oil: +$15/bbl, Gold: +5%, Equities: -3%

Scenario C — Strait of Hormuz disruption (20%):
- Iran threatens shipping, insurance rates spike
- Oil: +$30/bbl, Gold: +10%, Equities: -8%

Scenario D — Full confrontation (5%):
- Direct US-Iran military engagement
- Oil: +$50/bbl, Gold: +20%, Equities: -15%

Expected oil impact: 0.35*(-5) + 0.40*(15) + 0.20*(30) + 0.05*(50) = +12.8/bbl
Current oil: $80; market pricing ~$5 geopolitical premium
Underpriced by ~$8

Trade: Buy crude oil call options (3-month expiry)
- $90 calls: profit on scenarios B, C, D
- Cost: $2/bbl premium
- Risk/reward: $2 risk for $10-40 potential payoff
```

### Example 2: Taiwan Contingency
```
Risk assessment:
- Timeline: medium-term risk (years, not months)
- Impact: most consequential geopolitical risk for global markets
- Market pricing: very low implied probability in asset prices

Impact mapping:
- Semiconductors: TSMC disruption -> global chip shortage -> 50%+ decline in semis stocks
- Technology: every major tech company dependent on TSMC for advanced chips
- Shipping: South China Sea disruption affects 25% of global trade
- FX: USD rally (safe haven), CNY collapse, JPY mixed (safe haven vs regional risk)
- Commodities: industrial metals crash (demand destruction), energy spike (supply routes)

Portfolio preparation:
- Diversify semiconductor exposure (favor companies with fab diversification)
- Maintain US Treasury allocation (safe haven)
- Gold allocation: 10%+ for tail risk protection
- Avoid concentrated Asia-Pacific equity exposure
- Consider long-dated SPX put options as catastrophic hedge
```

### Example 3: Election Volatility Trade
```
Setup: US presidential election in 4 weeks
- Polls: extremely tight race, within margin of error
- Market: VIX at 22 (elevated but not extreme)
- Options: November expiry vol elevated vs September (event premium)

Trade: Buy VIX call spread
- Buy VIX 25 call, Sell VIX 35 call (November expiry)
- Cost: $2.00
- Max profit: $8.00 (if VIX spikes to 35+)
- Risk/reward: 4:1

Complementary trade: S&P 500 iron condor (December expiry)
- After election, regardless of outcome, vol should crush
- Sell 5% OTM put and call spreads
- Profit from post-election vol decline
- Risk: contested result extends uncertainty (define stop)

Historical: VIX has declined an average of 4 points in the week
following election resolution, regardless of winner.
```

## Quality Gate

Before trading geopolitical events, verify:

- [ ] Scenario analysis is written down with explicit probabilities — avoid anchoring on a single outcome
- [ ] Market pricing of risk is assessed — what is already priced in vs what is not?
- [ ] Trade is asymmetric — defined risk with outsized reward if underpriced scenario materializes
- [ ] Second-order effects are considered — sanctions -> supply chains -> inflation -> central bank response
- [ ] Safe haven correlation is understood — will your portfolio benefit or suffer from risk-off flows?
- [ ] Liquidity risk during event is planned for — spreads widen, slippage increases during geopolitical shocks
- [ ] Position sizing is conservative — geopolitical outcomes are inherently unpredictable
- [ ] Hedge cost is reasonable — not spending >2% annualized on geopolitical hedges
- [ ] Information sources are diversified — avoid relying on single narrative or news source
- [ ] Exit plan exists — define what would change your view and how you would close positions
