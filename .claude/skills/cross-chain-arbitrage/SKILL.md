---
name: cross-chain-arbitrage
description: "Cross-Chain and CEX-DEX Arbitrage. Use when: Identifying and evaluating arbitrage opportunities between centralized and decentralized exchanges; Analyzing cross-chain price discrepancies and bridge-based arbitrage; Designing triangular or multi-hop arbitrage strategies."
---

# Cross-Chain and CEX-DEX Arbitrage

## When to Activate
- Identifying and evaluating arbitrage opportunities between centralized and decentralized exchanges
- Analyzing cross-chain price discrepancies and bridge-based arbitrage
- Designing triangular or multi-hop arbitrage strategies
- Assessing execution risk, latency, gas costs, and bridge risks for arbitrage operations
- Building or evaluating atomic arbitrage strategies using flash loans

## Core Concepts

### CEX-DEX Arbitrage

**Price Discrepancy Sources:**
- CEX prices update via order book; DEX prices update via AMM formula on each trade
- During volatile periods, DEX prices lag because they require on-chain transactions to update
- Stale liquidity on DEXs creates arbitrage until arbitrageurs align prices
- Typical discrepancy: 0.1-0.5% in calm markets, 1-5% during volatility spikes

**Execution Flow:**
```
1. Monitor CEX order books and DEX pool prices simultaneously
2. Detect discrepancy exceeding threshold (gas + fees + slippage)
3. Execute simultaneously:
   a. Buy on cheaper venue
   b. Sell on more expensive venue
4. Net inventory to zero

Two modes:
- Atomic (DEX-only): single transaction using flash loans, no capital risk
- Non-atomic (CEX-DEX): requires capital on both venues, execution risk between legs
```

**CEX-DEX Specific Challenges:**
- **Latency asymmetry** — CEX APIs respond in milliseconds; DEX transactions take 12+ seconds (Ethereum) to confirm
- **Inventory management** — must pre-fund both CEX and DEX sides; capital is fragmented
- **Settlement mismatch** — CEX fills are instant; DEX fills are probabilistic until block confirmation
- **Gas price spikes** — during volatile periods when arb opportunities are largest, gas prices also spike
- **MEV competition** — on-chain leg is visible to searchers who may frontrun or sandwich

### Cross-Chain Arbitrage

**Bridge Arbitrage:**
- Same asset trades at different prices on different chains
- Opportunity: buy on cheap chain, bridge to expensive chain, sell
- Bottleneck: bridge latency (minutes to hours) and bridge fees (0.1-0.5%)
- Risk: price can converge during bridge transit, erasing profit
- Bridge liquidity limits: large arbs may exceed bridge capacity

**Types of Cross-Chain Price Discrepancies:**
```
1. Native token pricing: ETH on Ethereum vs ETH on Arbitrum
   - Usually tight (<0.1%) due to fast bridging

2. Wrapped/bridged tokens: USDC on Ethereum vs USDC.e on Avalanche
   - Can diverge during bridge congestion or depeg events

3. DEX pool pricing: Uniswap (Ethereum) vs Trader Joe (Avalanche)
   - Different pool depths create persistent small discrepancies

4. Synthetic assets: cross-chain synthetics may diverge from underlying
```

**Bridge Risk Categories:**
- **Smart contract risk** — bridge contracts are high-value targets; $2B+ stolen from bridges historically
- **Validator/relayer risk** — multisig or validator set can be compromised
- **Liquidity risk** — bridge may not have enough liquidity for your trade size
- **Finality risk** — reorgs on source chain can invalidate bridge message
- **Censorship risk** — bridge operators can delay or block transactions

### Triangular Arbitrage

**Concept:** Exploit pricing inconsistencies across three or more trading pairs that form a cycle.

**On-Chain Triangular Arbitrage:**
```
Example cycle: ETH -> USDC -> DAI -> ETH

Pool 1 (ETH/USDC): 1 ETH = 2000 USDC
Pool 2 (USDC/DAI): 1 USDC = 1.002 DAI
Pool 3 (DAI/ETH):  2000 DAI = 1.003 ETH

Execution:
1. Start with 10 ETH
2. Swap 10 ETH -> 20,000 USDC (Pool 1)
3. Swap 20,000 USDC -> 20,040 DAI (Pool 2)
4. Swap 20,040 DAI -> 10.03 ETH (Pool 3)
5. Profit: 0.03 ETH minus gas costs

Profitability condition:
product(exchange_rates_around_cycle) > 1 + total_fees + gas_cost/trade_size
```

**Multi-Hop Optimization:**
- More hops = more potential inefficiency to capture
- But also more gas costs and slippage per hop
- Optimal path finding is a graph problem: Bellman-Ford algorithm detects negative cycles (profitable arbitrage loops)
- DEX aggregators (1inch, Paraswap) solve this for users but extract some value

### Atomic Arbitrage with Flash Loans

**Flash Loan Arbitrage Pattern:**
```
Single transaction:
1. Borrow X tokens from Aave/dYdX (flash loan, no collateral)
2. Execute arbitrage trades across DEX pools
3. Repay loan + fee (0.05% on Aave, 0% on dYdX)
4. Keep profit

Advantages:
- Zero capital requirement (borrow and repay in same tx)
- Zero market risk (atomic execution — all or nothing)
- No inventory to manage

Constraints:
- Must complete within single transaction (single block)
- Cannot cross chains (flash loans are same-chain only)
- Gas costs can be high for complex multi-hop routes
- Competitive — many searchers target same opportunities
```

## Methodology

### Opportunity Detection
1. **Price monitoring** — maintain real-time price feeds for same asset across venues
2. **Threshold calculation** — minimum spread = gas_cost + bridge_fee + slippage + risk_premium
3. **Liquidity check** — verify sufficient depth on both sides to execute at expected prices
4. **Path optimization** — for multi-hop, find the optimal route maximizing net profit
5. **Execution decision** — only proceed if expected profit exceeds minimum threshold after all costs

### Profitability Calculation
```
Atomic (flash loan) arbitrage:
Net profit = gross_spread * trade_size - gas_cost - flash_loan_fee - slippage

CEX-DEX arbitrage:
Net profit = gross_spread * trade_size - gas_cost - CEX_fees - slippage
           - capital_cost * execution_time - hedge_cost

Cross-chain arbitrage:
Net profit = gross_spread * trade_size - gas_cost_chain_A - gas_cost_chain_B
           - bridge_fee - slippage - bridge_time_risk_premium

Break-even spread:
min_spread = (total_costs) / trade_size
```

### Latency and Infrastructure
```
Competitive advantage sources:
1. Co-located nodes (reduces block propagation latency)
2. Private mempool access (Flashbots, MEV-boost builders)
3. Pre-signed transactions ready to submit
4. Multi-chain node infrastructure
5. Custom DEX routing algorithms
6. Direct builder relationships for bundle inclusion

Latency hierarchy:
- HFT on CEX: microseconds
- MEV searcher on-chain: milliseconds to submit, 12s to confirm
- Cross-chain arb: minutes to hours (bridge dependent)
```

### Risk Management for Arbitrage
```
Position limits:
- Max single arb size: limited by pool depth (aim for <2% price impact)
- Max bridge exposure: never bridge more than you can afford to lose
- Max inventory imbalance: for CEX-DEX, delta-neutral within 5 minutes

Stop conditions:
- Gas price >3x normal: pause (costs eat profits)
- Bridge delays >2x normal: stop bridging (increased risk)
- Failed transaction rate >20%: investigate and halt
- Cumulative loss exceeds daily profit: halt and review
```

## Examples

### Example 1: CEX-DEX ETH Arbitrage
```
CEX (Binance): ETH/USDT bid = $2,005.00
DEX (Uniswap): ETH/USDC pool price = $2,000.00
Spread: $5.00 (0.25%)

Costs:
- Uniswap fee: 0.05% = $1.00 per ETH
- Gas for DEX swap: $8 (20 ETH batch)
- Binance taker fee: 0.075% = $1.50 per ETH
- Slippage estimate: 0.02% = $0.40 per ETH

Net profit per ETH: $5.00 - $1.00 - $0.40 - $1.50 - $0.40 = $1.70
For 20 ETH batch: $34.00 - $8 gas = $26.00 net

Execution: Buy 20 ETH on Uniswap, sell 20 ETH on Binance simultaneously
Capital required: $40,000 USDC on-chain + 20 ETH on Binance
Annualized return on capital depends on frequency of opportunities.
```

### Example 2: Cross-Chain Stablecoin Arbitrage
```
USDC on Ethereum: $1.000
USDC on Arbitrum (via Curve): $0.997 (slight discount)

Strategy:
1. Buy USDC on Arbitrum Curve pool at $0.997
2. Bridge to Ethereum via native bridge (free, but 7-day delay)
   Or use fast bridge (Across, Hop) for ~0.05% fee, 2 min

Fast bridge execution:
- Gross profit: 0.3%
- Bridge fee: 0.05%
- Gas (Arbitrum swap): $0.50
- Gas (Ethereum receive): $5
- Net profit: 0.25% - ($5.50 / trade_size)

Break-even trade size: $5.50 / 0.0025 = $2,200 minimum
For $50,000 trade: $125 - $5.50 = $119.50 profit

Risk: USDC discount could widen during transit. Bridge smart contract risk.
```

### Example 3: Triangular Flash Loan Arbitrage
```
Detected opportunity on Uniswap v3 (Ethereum):

Pool A (WETH/USDC 0.05%): 1 WETH = 2,001 USDC
Pool B (USDC/DAI 0.01%): 1 USDC = 1.0008 DAI
Pool C (DAI/WETH 0.30%): 2,000 DAI = 1.001 WETH

Cycle product: (1/2001) * (1/1.0008) * (2000 * 1.001) = 1.00089
Gross profit per cycle: 0.089%

Flash loan execution:
1. Borrow 100 WETH from Aave
2. Swap 100 WETH -> 200,100 USDC (Pool A, fee: 100 USDC)
3. Swap 200,100 USDC -> 200,260 DAI (Pool B, fee: 20 USDC equiv)
4. Swap 200,260 DAI -> 100.16 WETH (Pool C, fee: 600 DAI equiv)
5. Repay 100 WETH + 0.05 WETH (flash loan fee)
6. Profit: 0.11 WETH (~$220)
7. Gas cost: ~$30

Net profit: ~$190 in a single atomic transaction
Submit via Flashbots to prevent frontrunning.
```

## Quality Gate

Before executing arbitrage strategies, verify:

- [ ] All costs are precisely calculated — gas, fees, slippage, bridge fees, capital costs
- [ ] Liquidity depth is verified on both sides — check order book / pool reserves at trade size
- [ ] Execution risk is quantified — what happens if one leg fails (CEX-DEX) or bridge delays (cross-chain)?
- [ ] Smart contract interactions are tested on testnet or fork before mainnet deployment
- [ ] Flash loan logic includes revert-on-loss safety check (transaction reverts if unprofitable)
- [ ] Bridge risks are assessed and exposure limited — never bridge more than acceptable loss amount
- [ ] Competition level is understood — if margins are sub-$10, likely not worth manual execution
- [ ] Gas estimation includes priority fees during volatile periods when arb opportunities are most common
- [ ] Monitoring and alerting systems are in place for live arbitrage bots
- [ ] Regulatory considerations: market manipulation concerns for certain arbitrage strategies
