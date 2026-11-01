---
name: yield-farming
description: "Yield Farming Analysis. Use when: Evaluating DeFi yield opportunities across protocols and chains; Calculating true APY/APR including impermanent loss and compounding effects; Assessing risk-adjusted returns for liquidity provision strategies."
---

# Yield Farming Analysis

## When to Activate
- Evaluating DeFi yield opportunities across protocols and chains
- Calculating true APY/APR including impermanent loss and compounding effects
- Assessing risk-adjusted returns for liquidity provision strategies
- Comparing real yield (from protocol revenue) vs emission-subsidized yield
- Designing LP position management strategies including entry, exit, and rebalancing

## Core Concepts

### APY vs APR

**APR (Annual Percentage Rate):**
- Simple interest rate without compounding
- APR = (periodic_rate) * (periods_per_year)
- Used for borrowing costs and base emission rates

**APY (Annual Percentage Yield):**
- Includes compounding effects
- APY = (1 + periodic_rate)^periods_per_year - 1
- Daily compounding: APY = (1 + APR/365)^365 - 1
- At 50% APR: daily compounding yields ~64.8% APY
- At 100% APR: daily compounding yields ~171.5% APY
- At 1000% APR: daily compounding yields ~2,191,614% APY (illustrates why extreme APYs are misleading)

**Auto-compounding Cost/Benefit:**
- Gas cost per compound on Ethereum: $5-50 depending on complexity
- Break-even: only compound when yield earned > gas cost
- Optimal frequency = sqrt(2 * gas_cost * periods_per_year / (principal * APR))
- Yield aggregators (Yearn, Beefy) socialize gas costs across depositors

### Impermanent Loss (IL)

**Definition:** The difference in portfolio value between holding tokens in an LP vs simply holding them in a wallet.

**Constant Product AMM (Uniswap v2) IL Formula:**
```
IL = 2 * sqrt(price_ratio) / (1 + price_ratio) - 1

Where price_ratio = new_price / initial_price

Price change -> IL:
  1.25x (25% up) -> -0.6%
  1.50x (50% up) -> -2.0%
  2.00x (2x up)  -> -5.7%
  3.00x (3x up)  -> -13.4%
  5.00x (5x up)  -> -25.5%
  0.50x (50% down) -> -5.7% (symmetric with 2x up)
  0.20x (80% down) -> -25.5%
```

**Concentrated Liquidity IL (Uniswap v3):**
- IL is amplified proportionally to capital efficiency
- For range [p_lower, p_upper], IL multiplier ~ sqrt(p_upper/p_lower)
- A position with 10x capital efficiency has ~10x the IL of a v2 position
- If price exits range: position becomes 100% one asset (maximum IL for that direction)

**IL vs Fee Income Decision:**
```
Net position P&L = fee_income - impermanent_loss - gas_costs

LP is profitable when:
fee_income > IL + gas_costs

Fee income depends on:
- Trading volume through the pool
- Fee tier (0.01% to 1%)
- Your share of liquidity in the active price range
- Duration of the position
```

### Real Yield vs Emission Yield

**Emission Yield (Unsustainable):**
- Protocol mints new tokens and distributes to LPs/stakers
- Funded by inflation, not revenue — dilutes existing holders
- Typical lifecycle: high initial APY -> token price declines -> APY declines -> TVL exodus
- "Yield farming death spiral": sell emissions -> price drops -> APY drops -> more selling

**Real Yield (Sustainable):**
- Generated from actual protocol revenue (trading fees, borrowing interest, liquidation fees)
- Real yield = protocol_revenue_to_stakers / staked_value
- Protocols with strong real yield: GMX (30-40% real yield), Gains Network, protocol-owned liquidity models
- Benchmark: if emission yield is 5x+ real yield, the token is likely overvalued

### Risk Assessment Framework

**Smart Contract Risk:**
- Audit status: unaudited = extreme risk, 1 audit = high risk, 2+ audits + bug bounty = moderate risk
- Code complexity: composability layers multiply risk (yield aggregator -> lending protocol -> AMM)
- Upgrade mechanisms: immutable contracts safer but harder to patch; proxy patterns introduce admin key risk
- Time in production: Lindy effect — protocols surviving 2+ years without exploit are lower risk

**Market Risk:**
- Impermanent loss from price divergence
- Depeg risk for stablecoin pools
- Correlation breakdown between paired assets
- Black swan events causing cascading liquidations

**Liquidity Risk:**
- Can you exit your position without significant slippage?
- Lock-up periods and withdrawal delays
- Protocol TVL concentration — if you are >5% of pool, exit impact is material
- Bridge risk for cross-chain yield farming

**Operational Risk:**
- Oracle manipulation leading to incorrect reward calculations
- Governance attacks changing reward parameters
- Front-end compromise (DNS hijack, malicious contract approval)
- Chain-specific risks (L2 sequencer downtime, bridge hacks)

## Methodology

### Yield Opportunity Evaluation Process
1. **Identify the yield source** — is it real revenue, emissions, or a combination?
2. **Calculate true APY** — account for compounding frequency, gas costs, and IL
3. **Estimate impermanent loss** — model expected price movement over investment horizon
4. **Assess risk** — smart contract, market, liquidity, and operational risk
5. **Risk-adjust the return** — apply haircuts based on risk assessment
6. **Compare alternatives** — benchmark against simple staking, lending, or holding
7. **Size appropriately** — higher risk = smaller allocation; never concentrate in a single farm

### IL Hedging Strategies
```
Strategy 1: Delta-neutral LP
- Provide liquidity in ETH/USDC pool
- Short ETH perpetual equal to 50% of position value
- IL is offset by perp profit/loss (imperfect hedge but reduces variance)
- Net return = fee income - funding rate cost - residual IL

Strategy 2: Options-based hedge
- Buy put options on the volatile asset in the pair
- Protects against large downside moves that amplify IL
- Cost: option premium reduces net yield

Strategy 3: Correlated pair farming
- Farm pairs with high correlation (stETH/ETH, WBTC/renBTC)
- IL is minimal when prices move together
- Lower yield but much lower risk
```

### Position Sizing Framework
```
Risk tier allocation:
- Blue chip farms (Aave, Uniswap major pairs): up to 30% of DeFi allocation
- Mid-tier (established protocols, new chains): up to 15%
- Degen farms (unaudited, high APY, new protocols): max 5%
- Never >5% of total portfolio in any single farm
- Emergency exit plan for each position documented
```

## Examples

### Example 1: Stablecoin Yield Comparison
```
Strategy A — Curve 3pool LP:
- Base APY from fees: 2.5%
- CRV emissions: 8% (at current CRV price)
- Total APY: 10.5%
- IL risk: minimal (all stablecoins)
- Smart contract risk: low (Curve is battle-tested)
- Risk-adjusted yield: ~9%

Strategy B — Aave USDC lending:
- Supply APY: 3.5%
- No IL risk
- Smart contract risk: low
- Risk-adjusted yield: ~3.2%

Strategy C — New protocol stablecoin farm:
- Advertised APY: 50%
- Emission-funded (token has no revenue)
- Smart contract risk: high (unaudited, 2 weeks old)
- Expected real APY after token decline: ~5-10%
- Risk-adjusted yield: ~2% (high probability of loss)

Decision: Strategy A offers best risk-adjusted return.
Strategy C's headline APY is misleading.
```

### Example 2: ETH/USDC Concentrated Liquidity
```
Uniswap v3 ETH/USDC position:
- ETH price: $2,000
- Range: $1,700 - $2,300 (±15%)
- Capital efficiency: ~6.7x vs full range
- Fee tier: 0.30%

Scenario analysis (30-day horizon):
- If ETH stays in range: ~25% APY from fees
- If ETH goes to $2,500: position is 100% USDC, IL = -8.2% (amplified)
- If ETH drops to $1,500: position is 100% ETH, IL = -11.3% (amplified)

Expected outcome (historical vol = 80% annualized):
- Probability of staying in range: ~65%
- Expected fee income: $1,200 on $50,000 position
- Expected IL: -$400
- Net expected return: $800 / $50,000 = 1.6% monthly = ~19% APY

Gas costs for rebalancing: ~$80 per rebalance (2-3 times per month)
Net after gas: ~17% APY
```

### Example 3: Farm-and-Dump Detection
```
Red flags identified:
- Protocol launched 5 days ago, no audit
- APY: 2,000% on native token LP
- Token price: down 60% from launch
- TVL growing but token price declining (people farming and selling)
- No revenue source — 100% emission funded
- Anonymous team, forked code

Analysis:
- Current APY in USD terms: 2000% * 0.4 (token decline) = ~800%
- But token is declining ~10% per day
- Daily yield: 800% / 365 = 2.2%
- Daily token decline: 10%
- Net daily return: -7.8%

Conclusion: Negative expected value despite headline APY.
Classic farm-and-dump dynamics. Avoid.
```

## Quality Gate

Before entering yield farming positions, verify:

- [ ] APY source is identified — real yield vs emissions; sustainable vs temporary
- [ ] True APY calculated after compounding, gas costs, and impermanent loss
- [ ] Smart contract risk assessed — audits, time in production, code complexity, upgrade mechanisms
- [ ] Impermanent loss modeled for realistic price scenarios (not just historical)
- [ ] Position sized according to risk tier — never over-concentrate in high-risk farms
- [ ] Exit plan defined — what triggers exit (IL threshold, APY decline, security concern)?
- [ ] Token emission schedule reviewed — will emissions decline soon, crashing APY?
- [ ] Protocol TVL trend is stable or growing — declining TVL may signal smart money exiting
- [ ] Your share of the pool is small enough to exit without significant market impact
- [ ] Gas costs for entry, compounding, and exit are factored into net return calculation
