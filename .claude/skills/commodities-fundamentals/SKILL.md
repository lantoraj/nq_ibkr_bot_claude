---
name: commodities-fundamentals
description: "Commodities Fundamental Analysis. Use when: Analyzing commodity futures term structure (contango, backwardation) and roll yield; Evaluating supply-demand balances for energy, metals, or agricultural commodities; Understanding seasonal patterns and their trading implications."
---

# Commodities Fundamental Analysis

## When to Activate
- Analyzing commodity futures term structure (contango, backwardation) and roll yield
- Evaluating supply-demand balances for energy, metals, or agricultural commodities
- Understanding seasonal patterns and their trading implications
- Assessing inventory data, OPEC dynamics, and production economics
- Building commodity-based macro views or trading strategies

## Core Concepts

### Futures Term Structure

**Contango:**
- Longer-dated futures > near-term futures > spot price
- Normal state for storable commodities (reflects storage costs + financing)
- Rolling long positions incurs negative roll yield (sell cheap front, buy expensive back)
- Example: WTI crude often in contango during oversupply (front month depressed)

**Backwardation:**
- Spot > near-term futures > longer-dated futures
- Indicates tight current supply or strong immediate demand
- Rolling long positions earns positive roll yield (sell expensive front, buy cheap back)
- Historically, commodities in backwardation have higher total returns

**Cost of Carry Model:**
```
F(T) = S * exp((r + c - y) * T)

Where:
F(T) = futures price at time T
S = spot price
r = risk-free rate
c = storage cost (% of commodity value)
y = convenience yield (benefit of holding physical)

Contango when: r + c > y (storage costs exceed convenience yield)
Backwardation when: y > r + c (strong convenience yield / tight supply)
```

**Convenience Yield:**
- Benefit of holding physical commodity vs futures contract
- High during supply disruptions, low inventories, strong immediate demand
- Unobservable directly — implied from futures curve
- Spikes during crises: oil refinery outages, grain droughts, metal supply shocks

### Roll Yield

**Definition:** Profit or loss from rolling futures contracts before expiry.

```
Roll yield = (F_near - F_next) / F_near * (365 / days_between_contracts)

Contango: roll yield is negative (rolling costs money)
Backwardation: roll yield is positive (rolling earns money)

Impact on total return:
Total return = spot return + roll yield + collateral yield
- Spot return: change in the front-month futures price
- Roll yield: gain/loss from rolling contracts
- Collateral yield: interest earned on margin collateral

Example: If spot return = +10%, roll yield = -8%, collateral yield = +3%
Total return = +5% (roll yield ate most of the spot appreciation)
```

### Commodity-Specific Supply-Demand

**Crude Oil:**
```
Supply sources:
- OPEC production (voluntary quotas, spare capacity)
- US shale (responsive to price, breakeven ~$40-60/bbl WTI)
- Non-OPEC conventional (declining in many regions)
- Strategic Petroleum Reserves (government releases)

Demand drivers:
- Global GDP growth (1% GDP growth ≈ 0.5% oil demand growth)
- Transportation fuel (70% of demand)
- Petrochemicals and industrial use
- Seasonal: peak driving season (June-August), heating oil (winter)

Key data releases:
- EIA Weekly Petroleum Status Report (Wednesdays, 10:30 ET)
- API Weekly Inventory Report (Tuesdays, 4:30 PM ET)
- OPEC Monthly Oil Market Report
- IEA Oil Market Report
```

**Gold:**
```
Drivers (not standard supply-demand):
- Real interest rates (negative correlation: lower real rates -> higher gold)
- USD strength (inverse relationship)
- Central bank purchases (structural demand, particularly EM central banks)
- Geopolitical risk / safe haven demand
- Inflation expectations (gold as inflation hedge narrative)
- Mine supply: ~3,500 tonnes/year, relatively stable (long lead times)
- AISC (all-in sustaining cost): ~$1,200-1,400/oz industry average

Framework: Gold = f(real_rates, USD, risk_sentiment, CB_demand)
```

**Copper:**
```
"Dr. Copper" — proxy for global industrial activity
Supply: concentrated in Chile, Peru, DRC (political risk)
Demand: construction (25%), electronics (25%), transportation (12%)
China accounts for ~55% of global copper demand
Lead times: new mines take 10-15 years from discovery to production

Key indicators:
- China PMI (especially manufacturing)
- LME warehouse inventories
- Shanghai bonded warehouse stocks
- TC/RC (treatment/refining charges) — smelter economics
- Scrap availability and pricing
```

**Natural Gas:**
```
Highly seasonal and regional (not a global commodity):
- Henry Hub (US): linked to domestic supply/demand
- TTF (Europe): linked to LNG imports, pipeline flows, storage
- JKM (Asia): linked to LNG spot market

Storage cycle:
- Injection season: April-October (build inventories)
- Withdrawal season: November-March (draw inventories)
- EIA storage report (Thursdays, 10:30 ET): key weekly catalyst

US supply revolution: shale gas made US net exporter (LNG)
Weather dominance: extreme cold/heat drives short-term price moves
```

### Seasonal Patterns

**Energy:**
- Crude: tends to strengthen in spring (refinery maintenance ends, driving season approaches)
- Natural gas: peaks in winter (heating demand), secondary peak in summer (cooling)
- Gasoline: crack spread widens before Memorial Day, narrows after Labor Day

**Agriculture:**
- Grains: "sell in May, buy in November" reflects Northern Hemisphere planting/harvest cycle
- Soybeans: weather market June-August (US growing season), South American harvest Jan-April
- Weather premium builds during key growth periods (pollination for corn: mid-July)

**Metals:**
- Gold: tends to be strong in Q1 and Q3 (Indian wedding season, Chinese New Year demand)
- Copper: seasonal strength in Q1 (Chinese restocking post-Lunar New Year)
- Aluminum: relatively flat seasonality, driven more by energy costs

### Inventory Analysis

**Interpretation Framework:**
```
Inventories falling + rising prices = demand-driven rally (bullish, sustainable)
Inventories falling + falling prices = supply disruption being resolved (neutral)
Inventories rising + falling prices = demand destruction (bearish)
Inventories rising + rising prices = speculative hoarding (unstable, reversal risk)

Key inventory data:
- EIA crude inventories (US): weekly
- LME warehouse stocks (metals): daily
- COMEX warehouse stocks (gold, silver, copper): daily
- USDA crop stocks reports (agriculture): quarterly
- IEA OECD commercial inventories: monthly
```

## Methodology

### Supply-Demand Balance Construction
1. **Map supply sources** — production by country/region, growth rates, spare capacity
2. **Estimate demand** — by sector and region, sensitivity to GDP and price
3. **Calculate balance** — surplus (supply > demand) or deficit (demand > supply)
4. **Project inventories** — cumulative balance shows inventory build or draw
5. **Compare with market pricing** — is the curve pricing in the fundamental balance?
6. **Identify catalysts** — what could shift the balance (weather, OPEC decision, sanctions)?

### Term Structure Trading
```
Strategies based on curve shape:

1. Calendar spread (time spread):
   - Long near-month, short deferred month (bullish on backwardation)
   - Risk-defined: max loss is spread between contracts
   - Lower margin than outright positions

2. Curve flattener/steepener:
   - Trade the shape of the curve beyond just front-back
   - Example: long 3-month, short 12-month if expecting tightening

3. Crack spread (oil):
   - Long crude, short refined products (gasoline, diesel)
   - Measures refining margin
   - 3:2:1 crack = 3 bbls crude vs 2 bbls gasoline + 1 bbl diesel

4. Crush spread (soybeans):
   - Long soybeans, short soybean meal + soybean oil
   - Measures processing margin
```

### OPEC Analysis
```
Key variables:
1. Compliance with quotas (historically imperfect; cheat during low prices)
2. Spare capacity (meaningful only if >2 Mb/d; below that, market is tight)
3. Fiscal breakeven prices (Saudi: ~$80/bbl, Russia: ~$70/bbl, UAE: ~$65/bbl)
4. Internal politics (Saudi vs UAE on production levels)
5. OPEC+ cohesion (non-OPEC members like Russia have different incentives)

Assessment framework:
- If prices < fiscal breakeven: OPEC likely to cut (supportive)
- If prices > $100: pressure to increase production (but spare capacity limits response)
- If non-OPEC supply growing fast: OPEC loses pricing power
- Watch for: emergency meetings, bilateral discussions, ministerial statements
```

## Examples

### Example 1: Crude Oil Contango Trade (Storage Play)
```
Situation:
- WTI front month: $45/bbl
- WTI 12-month: $55/bbl
- Contango: $10/bbl (22% annualized)
- Storage cost: $5/bbl for 12 months (tank space available)
- Financing: $2/bbl (interest on commodity value)

Trade: Cash-and-carry arbitrage
- Buy physical crude at $45
- Store for 12 months (cost: $5)
- Sell 12-month futures at $55
- Total cost: $45 + $5 + $2 = $52
- Guaranteed profit: $55 - $52 = $3/bbl (6.7% on capital, risk-free)

Constraint: requires physical storage access (tank farms, tankers)
At scale: this trade was massively profitable in 2020 COVID oversupply
```

### Example 2: Copper Demand Signal
```
Indicators:
- China manufacturing PMI: 52.5 (expansionary, rising)
- LME copper inventories: declining for 8 consecutive weeks
- Shanghai bonded warehouse stocks: near 5-year lows
- Copper term structure: shifting from contango to backwardation
- Chile production: -5% YoY (water restrictions, grade decline)

Assessment:
- Strong demand (China PMI) + constrained supply (Chile) + low inventories
- Fundamental deficit emerging
- Backwardation confirms physical tightness

Trade: Long copper futures (3-month LME or COMEX)
Entry: $8,500/tonne
Target: $9,500/tonne (supply deficit pricing)
Stop: $8,000/tonne (demand slowdown invalidation)
Roll yield: positive (backwardation)
```

### Example 3: Natural Gas Seasonal Trade
```
Setup (September):
- Henry Hub: $2.50/MMBtu
- Storage: 3,200 Bcf (5% above 5-year average)
- Weather forecast: La Nina pattern (colder than normal winter expected)
- Production: flat YoY (drilling activity stable)

Historical pattern:
- Gas rallies Oct-Jan 65% of years
- La Nina winters produce 10-15% above-average heating demand
- Average Oct-Jan rally: +25%

Trade: Long January natural gas futures
Entry: $2.50
Target: $3.50 (40% upside if cold winter materializes)
Stop: $2.20 (warm forecast shift, bearish for position)
Size: 2% portfolio risk (volatile market, wide stops needed)

Risk: above-average storage provides buffer against supply tightness
Mild winter would cap upside and potentially break support
```

## Quality Gate

Before trading commodities on fundamentals, verify:

- [ ] Supply-demand balance is sourced from multiple data providers (IEA, EIA, OPEC, USDA, industry reports)
- [ ] Inventory data is current and correctly interpreted (absolute level vs rate of change vs seasonal norm)
- [ ] Term structure shape is understood and roll yield is factored into expected return
- [ ] Seasonal patterns are contextualized — do fundamentals support or contradict the seasonal tendency?
- [ ] OPEC or cartel dynamics assessed — for energy, OPEC decisions can override fundamentals
- [ ] Weather risk is acknowledged — agricultural and gas trades are heavily weather-dependent
- [ ] Position sizing accounts for commodity volatility (crude: ~30% annualized, nat gas: ~50%, grains: ~25%)
- [ ] Physical market nuances understood — grades, delivery points, quality premiums, transportation costs
- [ ] Geopolitical risk priced in — sanctions, wars, export bans can disrupt supply suddenly
- [ ] Correlation with macro portfolio considered — commodities often correlate with inflation and growth expectations
