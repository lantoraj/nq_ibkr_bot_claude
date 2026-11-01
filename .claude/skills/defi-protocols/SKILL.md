---
name: defi-protocols
description: "DeFi Protocol Analysis. Use when: Analyzing DeFi protocol mechanics for trading or yield opportunities; Evaluating AMM designs (Uniswap v3, Curve), lending protocols (Aave, Compound), or staking systems; Assessing liquidity provision strategies, including concentrated liquidity and stableswap invariants."
---

# DeFi Protocol Analysis

## When to Activate
- Analyzing DeFi protocol mechanics for trading or yield opportunities
- Evaluating AMM designs (Uniswap v3, Curve), lending protocols (Aave, Compound), or staking systems
- Assessing liquidity provision strategies, including concentrated liquidity and stableswap invariants
- Comparing liquid staking solutions (Lido, Rocket Pool) or evaluating validator economics

## Core Concepts

### Automated Market Makers (AMMs)

**Constant Product (Uniswap v2):**
- Invariant: x * y = k
- Price impact is proportional to trade size relative to pool depth
- LPs provide liquidity uniformly across the entire price range (0, infinity)
- Simple but capital-inefficient — most liquidity sits unused far from current price

**Concentrated Liquidity (Uniswap v3):**
- LPs choose a price range [p_lower, p_upper] to deploy capital
- Capital efficiency gain: up to 4000x vs v2 for tight ranges
- Fee tiers: 0.01% (stablecoins), 0.05% (correlated pairs), 0.30% (standard), 1.00% (exotic)
- Position management is active — out-of-range positions earn zero fees
- Tick spacing determines granularity: 1 tick = 0.01% price change for 0.01% fee tier
- JIT (just-in-time) liquidity: sophisticated LPs add/remove liquidity around large trades in the same block

**Curve StableSwap:**
- Invariant blends constant-product and constant-sum: A * n^n * sum(x_i) + D = A * D * n^n + D^(n+1) / (n^n * prod(x_i))
- Amplification parameter A controls the flatness of the curve around the peg
- Higher A = flatter curve = lower slippage near peg, but higher risk if assets depeg
- Curve v2 (CryptoSwap) extends to volatile pairs with internal oracle and dynamic A
- Gauge system: veCRV holders vote on emission allocation; "Curve Wars" for gauge control

### Lending Protocols

**Aave/Compound Mechanics:**
- Utilization rate U = total borrows / total deposits
- Interest rate models are kinked: low rate below optimal utilization, steep rate above
  - Aave: variable rate = base + (U / U_optimal) * slope1 when U < U_optimal
  - Aave: variable rate = base + slope1 + ((U - U_optimal) / (1 - U_optimal)) * slope2 when U >= U_optimal
  - slope2 is typically 10-50x slope1 to discourage full utilization
- Collateral factors (LTV): determines max borrowing power per asset (e.g., ETH = 82.5% on Aave v3)
- Liquidation threshold > LTV — buffer zone before liquidation triggers
- Liquidation penalty: 5-10% bonus incentivizes liquidators
- Health factor = (collateral * liquidation_threshold) / debt; liquidation triggers at HF < 1.0

**Aave v3 Features:**
- Efficiency mode (e-mode): higher LTV for correlated assets (e.g., ETH/stETH at 93% LTV)
- Isolation mode: new assets listed with limited borrowing capacity
- Portal: cross-chain liquidity bridging
- Flash loans: uncollateralized single-block loans; 0.05% fee (Aave), 0% (some forks)

### Staking and Liquid Staking

**Validator Economics (Ethereum PoS):**
- 32 ETH minimum stake per validator
- Rewards: attestation rewards + block proposal rewards + MEV tips
- Current yield approximately 3-5% APR depending on total staked
- Slashing risks: double-signing, surround voting — penalty is correlated with concurrent slashing events
- Withdrawal queue: variable wait times based on churn limit

**Liquid Staking:**
- Lido (stETH): rebasing token, daily balance updates, ~90% market share risk
- Rocket Pool (rETH): exchange-rate model, accumulates value, more decentralized (permissionless node operators)
- Staking derivative pricing: should trade near 1:1 but discounts occur during market stress or withdrawal delays
- stETH/ETH peg risk: during 2022, discount reached ~5% due to 3AC forced selling and withdrawal uncertainty

## Methodology

### Protocol Evaluation Framework
1. **Mechanism design** — understand the invariant/interest model mathematically
2. **TVL analysis** — total value locked, TVL trend, TVL concentration by pool/market
3. **Revenue analysis** — protocol revenue vs token holder revenue; fee switch status
4. **Risk assessment** — smart contract risk (audits, bug bounties), oracle risk, governance risk
5. **Competitive positioning** — market share, moat, fork risk, incentive sustainability

### LP Position Management (Uniswap v3)
```
1. Select pair and fee tier based on expected volatility
2. Analyze historical price distribution to determine range
   - Tighter range = more fees when in range, more rebalancing when out
   - Rule of thumb: set range to cover 1-2 standard deviations of expected price movement
3. Calculate expected fee income vs impermanent loss
4. Monitor position: rebalance when price exits range or when IL exceeds fee income
5. Account for gas costs — rebalancing on Ethereum mainnet costs $20-100+
```

### Lending Strategy Analysis
```
1. Compare supply/borrow rates across protocols for the same asset
2. Check utilization rates — high utilization means withdrawal risk
3. Evaluate liquidation risk: model collateral drawdown scenarios
4. Consider recursive leverage: supply ETH, borrow stablecoin, buy more ETH
   - Effective leverage = 1 / (1 - LTV); at 80% LTV = 5x effective leverage
   - Risk: liquidation cascade if collateral drops sharply
5. Monitor governance proposals that could change parameters
```

## Examples

### Example 1: Curve Pool Analysis
```
Pool: 3pool (DAI/USDC/USDT)
A parameter: 2000
TVL: $500M
Daily volume: $50M
Fee: 0.01%

Analysis:
- Volume/TVL ratio: 10% daily — healthy utilization
- With A=2000, slippage on $1M trade: ~0.002%
- Base APY from fees: ~3.65% (10% * 0.01% * 365)
- CRV emissions add 5-15% depending on gauge weight and boost
- Risk: USDT depeg would break the amplification assumption
```

### Example 2: Aave Recursive Leverage
```
Strategy: Supply ETH, borrow USDC, buy ETH, repeat
ETH LTV on Aave v3: 82.5%
Liquidation threshold: 86%

3 loops:
- Deposit 10 ETH ($20,000)
- Borrow $16,500 USDC (82.5% LTV)
- Buy 8.25 ETH, deposit
- Borrow $13,612 USDC
- Buy 6.8 ETH, deposit

Effective position: ~25 ETH exposure on 10 ETH collateral (2.5x leverage)
Liquidation price: approximately 18% below entry
Borrow cost: ~3% APR on total borrowed
Net cost of leverage: ~3% * 1.5 (leverage ratio) = 4.5% annual drag

Risk: If ETH drops 15%+ rapidly, liquidation cascade. Health factor
must be monitored continuously. Consider using Aave's e-mode if
available for the pair.
```

### Example 3: Liquid Staking Arbitrage
```
Observation:
- stETH trading at 0.97 ETH on Curve
- Lido withdrawals enabled with 3-day queue
- Fair value: 1.0 ETH (minus small time value discount)

Trade:
- Buy stETH at 0.97 on Curve
- Submit withdrawal request to Lido
- Receive 1.0 ETH after withdrawal period
- Profit: 3% minus gas costs and opportunity cost of capital lockup

Risk factors:
- Withdrawal queue could extend during high demand
- Smart contract risk during withdrawal process
- stETH discount could widen further before withdrawal completes
```

## Quality Gate

Before deploying capital into DeFi protocols, verify:

- [ ] Smart contract has been audited by 2+ reputable firms and has active bug bounty
- [ ] Protocol has been live for 6+ months with no critical exploits (or exploits were patched and post-mortemed)
- [ ] Interest rate model or AMM invariant is understood mathematically, not just described
- [ ] Impermanent loss and fee income are modeled for realistic price scenarios, not just historical
- [ ] Liquidation thresholds and health factors are stress-tested against 2-3 sigma price moves
- [ ] Oracle dependencies are identified — Chainlink vs TWAP vs custom, and their failure modes
- [ ] Gas costs for position management are factored into expected returns
- [ ] Governance risk assessed — can parameters change via governance vote with short timelock?
- [ ] Concentration risk evaluated — what percentage of TVL is your position? Can you exit without moving the market?
- [ ] Regulatory risk considered — protocol jurisdiction, KYC requirements, potential for sanctions
