---
name: stablecoin-analysis
description: "Stablecoin Analysis. Use when: Evaluating stablecoin peg mechanisms, reserve compositions, and risk profiles; Assessing depeg risk factors and historical depeg events; Analyzing stablecoin yield strategies and their risk/return characteristics."
---

# Stablecoin Analysis

## When to Activate
- Evaluating stablecoin peg mechanisms, reserve compositions, and risk profiles
- Assessing depeg risk factors and historical depeg events
- Analyzing stablecoin yield strategies and their risk/return characteristics
- Comparing stablecoin designs (fiat-backed, crypto-backed, algorithmic)
- Monitoring stablecoin market dynamics as macro indicators for crypto markets

## Core Concepts

### Stablecoin Classification

**Fiat-Backed (Custodial):**
- **USDT (Tether)** — largest by market cap; reserves include cash, T-bills, commercial paper (reduced), secured loans
- **USDC (Circle)** — fully backed by cash and short-duration US Treasuries; monthly attestations by Deloitte
- **BUSD (Paxos/Binance)** — regulated by NYDFS; being wound down
- **PYUSD (PayPal)** — regulated, backed by US Treasuries and deposits
- Peg mechanism: issuer mints/redeems 1:1 with USD; arbitrageurs keep market price near $1
- Risks: custodial risk, regulatory risk, reserve composition opacity, banking relationship risk

**Crypto-Backed (Decentralized):**
- **DAI (MakerDAO/Sky)** — over-collateralized by ETH, WBTC, stablecoins, RWAs
  - Minimum collateral ratio: 150% for ETH vaults (liquidation at 145%)
  - Stability fee (interest rate) set by governance
  - DSR (DAI Savings Rate) provides yield to DAI holders
  - Increasingly backed by RWAs and USDC — centralization concerns
- **LUSD (Liquity)** — backed only by ETH, immutable contracts, no governance
  - Minimum collateral ratio: 110%
  - Redemption mechanism: anyone can redeem LUSD for $1 of ETH from riskiest vaults
  - Truly decentralized but smaller scale
- **crvUSD (Curve)** — uses LLAMMA (Lending-Liquidating AMM Algorithm)
  - Soft liquidation: gradually converts collateral to stablecoin as price drops
  - Re-collateralizes automatically if price recovers
  - Novel approach but complex risk profile
- Risks: collateral volatility, liquidation cascades, oracle failures, governance attacks

**Algorithmic (Uncollateralized or Partially Collateralized):**
- **Historical failures:** UST/LUNA (death spiral, $40B lost), IRON/TITAN, Basis Cash
- **Seigniorage model:** mint stablecoin by burning governance token; reflexive — works in expansion, fails in contraction
- **Fractional-algorithmic:** FRAX (partially collateralized, partially algorithmic); has moved toward full collateralization
- Risks: death spiral risk (loss of confidence -> redemption -> further depegging -> more redemption)

### Peg Mechanisms

**Hard Peg (Fiat-Backed):**
```
Market price > $1.00:
  - Arbitrageurs mint new tokens at $1.00 from issuer
  - Sell on market above $1.00
  - Profit drives price back to $1.00

Market price < $1.00:
  - Arbitrageurs buy on market below $1.00
  - Redeem at issuer for $1.00
  - Profit drives price back to $1.00

Requirement: issuer must honor redemptions promptly
```

**Soft Peg (Crypto-Backed):**
```
DAI above $1.00:
  - Governance lowers stability fee (cheaper to mint DAI)
  - More DAI minted and sold, pushing price down
  - DSR can be lowered to reduce DAI demand

DAI below $1.00:
  - Governance raises stability fee (more expensive to hold vaults)
  - Vault holders buy DAI to repay debt, pushing price up
  - DSR can be raised to increase DAI demand
  - Redemption mechanism (if available) provides hard floor
```

**Algorithmic Peg (UST Model — Failed):**
```
UST above $1.00:
  - Mint UST by burning $1 of LUNA
  - Sell UST above $1.00
  - Increases LUNA scarcity (bullish reflexivity)

UST below $1.00:
  - Burn UST to mint $1 of LUNA
  - Sell LUNA on market
  - But selling LUNA crashes LUNA price
  - LUNA crash reduces confidence in backing
  - More UST redemptions -> more LUNA minting -> death spiral
```

### Reserve Analysis

**Key Reserve Metrics:**
```
Reserve ratio = total reserves / total stablecoin outstanding
  >1.0: over-collateralized (safe)
  =1.0: fully backed (standard for fiat-backed)
  <1.0: under-collateralized (risky)

Reserve quality:
  Tier 1: Cash, overnight repos, short-term T-bills
  Tier 2: Longer-duration government bonds, money market funds
  Tier 3: Corporate bonds, commercial paper
  Tier 4: Secured loans, other investments, crypto assets

Higher quality = faster liquidation in stress, less mark-to-market risk
```

**Reserve Transparency Hierarchy:**
- Real-time on-chain proof of reserves (best — crypto-backed stablecoins)
- Monthly third-party attestation (USDC by Deloitte)
- Quarterly reports (Tether — historically criticized for opacity)
- No verification (worst — avoid)

### Depeg Risk Factors

**Systemic Factors:**
- Banking crisis affecting stablecoin reserve custodians (USDC/SVB: depeg to $0.87 in March 2023)
- Regulatory action against issuer (BUSD ordered to stop minting)
- Smart contract exploit draining reserves
- Oracle manipulation causing cascading liquidations

**Stablecoin-Specific Factors:**
- Reserve composition degradation (shift from T-bills to riskier assets)
- Rapid redemption outflows exceeding liquid reserves
- Counterparty risk in reserve custody
- Governance attacks on crypto-backed stablecoins
- Liquidity fragmentation across chains (bridged USDC ≠ native USDC)

### Historical Depeg Events

**UST/LUNA (May 2022):**
- Trigger: large coordinated sell of UST ($300M+) on Curve 3pool
- Mechanism failure: LUNA mint/burn created infinite supply as confidence collapsed
- Depth of depeg: UST went from $1.00 to $0.02; LUNA from $80 to $0.0001
- Loss: ~$40 billion in combined market cap destroyed
- Lesson: algorithmic stablecoins without exogenous collateral are inherently fragile

**USDC (March 2023):**
- Trigger: SVB bank failure; Circle had $3.3B of $40B reserves at SVB
- Depth of depeg: $0.87 on DEXs, $0.93 on CEXs
- Duration: 2 days (Friday evening to Monday morning when Fed backstopped deposits)
- Recovery: full repeg after Fed BTFP announcement guaranteed deposits
- Lesson: fiat-backed stablecoins carry banking system risk; weekend liquidity gaps amplify depegs

## Methodology

### Stablecoin Risk Assessment Framework
1. **Classify the peg mechanism** — fiat-backed, crypto-backed, or algorithmic
2. **Analyze reserves** — composition, quality, transparency, custody
3. **Evaluate redemption mechanism** — how quickly can you get $1 back?
4. **Assess regulatory status** — licensed? Which jurisdiction? Regulatory actions pending?
5. **Check on-chain liquidity** — Curve/Uniswap pool depth, DEX liquidity across chains
6. **Monitor market signals** — Curve pool imbalances, DEX premiums/discounts, funding rates
7. **Score and rank** — assign risk tier (1-5) across each dimension

### Depeg Early Warning Indicators
```
Watch for:
1. Curve pool imbalance >60/40 (stressed stablecoin becoming dominant in pool)
2. CEX withdrawal suspensions or delays for the stablecoin
3. Issuer communication changes (delays, vagueness, leadership changes)
4. Sustained discount >0.5% for 24+ hours
5. Large redemption queues (on-chain observable for crypto-backed)
6. Social media sentiment shift (FUD can become self-fulfilling)
7. Declining reserves in attestation reports
8. Regulatory announcements targeting the issuer
```

### Stablecoin Yield Strategies
```
Low risk:
- Supply to Aave/Compound (3-8% APY variable)
- Curve 3pool LP (2-5% base + CRV rewards)
- DSR (MakerDAO savings rate, currently 5-15% depending on governance)

Medium risk:
- Lending on newer protocols with higher rates (higher smart contract risk)
- LP in volatile/stablecoin pairs on DEXs
- Delta-neutral basis trading using stablecoin as collateral

High risk:
- Exotic stablecoin farms on new chains
- Leveraged stablecoin lending loops
- Algorithmic stablecoin incentive programs
```

## Examples

### Example 1: USDC Depeg Trade (March 2023)
```
Situation: USDC trading at $0.93 after SVB news
Analysis:
- Circle's exposure: $3.3B of $40B reserves (8.25%)
- Worst case: 8.25% haircut on reserves -> USDC worth $0.9175
- Best case: deposits recovered -> USDC worth $1.00
- Expected value at $0.93: strongly positive if deposit recovery likely

Trade: Buy USDC at $0.93
- If deposits recovered (70% probability): profit = 7.5%
- If haircut applied (30% probability): loss = 1.4%
- Expected value: 0.7 * 7.5% + 0.3 * (-1.4%) = 4.8%

Outcome: Fed backstopped all deposits. USDC repegged within 48 hours.
7.5% return in 2 days.
```

### Example 2: Curve Pool Imbalance Warning
```
Monitoring: Curve 3pool composition
Normal state: ~33% DAI / ~33% USDC / ~33% USDT

Warning signal detected:
- DAI: 25%
- USDC: 25%
- USDT: 50%

Interpretation: Market is dumping USDT into the pool, buying DAI/USDC.
This suggests concern about USDT peg or reserves.
USDT discount on Curve: 0.2%

Action:
- Reduce USDT exposure
- Monitor Tether redemption data and reserve attestations
- Set alert for >55% USDT imbalance (escalation threshold)
- Check if discount is also present on other venues (confirms systemic concern vs pool-specific flow)
```

### Example 3: Crypto-Backed Stablecoin Stress Test
```
DAI stress test scenario: ETH drops 40% in 24 hours

Current state:
- Total DAI: 5B
- ETH-backed DAI: 2B ($4B ETH collateral at 200% CR)
- USDC-backed DAI: 1.5B
- RWA-backed DAI: 1.5B

After 40% ETH drop:
- ETH collateral value: $4B * 0.6 = $2.4B
- Collateral ratio: 2.4B / 2B = 120% (below 150% threshold)
- Liquidations trigger: ~$800M of ETH vaults liquidated
- Liquidation penalty generates revenue but may cascade
- DAI supply contracts as vaults are closed

Assessment:
- USDC and RWA backing provides stability floor (3B backing 3B DAI = 100%)
- ETH liquidation cascade is contained if oracle stays live
- Key risk: oracle failure during ETH crash would prevent liquidations
- DAI should hold peg due to diversified collateral
```

## Quality Gate

Before relying on or investing in stablecoins, verify:

- [ ] Peg mechanism is understood — how does it maintain $1? What are the failure modes?
- [ ] Reserve composition is verified — recent attestation or on-chain proof of reserves reviewed
- [ ] Redemption mechanism tested — can you actually redeem for $1? What are the delays and minimums?
- [ ] On-chain liquidity is sufficient — can you exit your position size without >0.5% slippage?
- [ ] Depeg early warning indicators are being monitored (Curve pool imbalance, discount on DEXs)
- [ ] Counterparty risks identified — banking partners, custodians, oracle providers
- [ ] Regulatory status is clear — issuer jurisdiction, licenses, pending regulatory actions
- [ ] Historical performance reviewed — how did this stablecoin behave during March 2023, May 2022?
- [ ] Concentration risk managed — do not hold >50% of stablecoin allocation in a single stablecoin
- [ ] Chain-specific risks considered — bridged vs native USDC, L2 sequencer dependencies
