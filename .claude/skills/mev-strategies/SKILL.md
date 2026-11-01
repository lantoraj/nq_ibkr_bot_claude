---
name: mev-strategies
description: "MEV Strategies. Use when: Analyzing Maximal Extractable Value (MEV) opportunities or risks in DeFi transactions; Understanding frontrunning, sandwich attacks, and DEX arbitrage mechanics; Evaluating MEV mitigation strategies (Flashbots, MEV-boost, private mempools)."
---

# MEV Strategies

## When to Activate
- Analyzing Maximal Extractable Value (MEV) opportunities or risks in DeFi transactions
- Understanding frontrunning, sandwich attacks, and DEX arbitrage mechanics
- Evaluating MEV mitigation strategies (Flashbots, MEV-boost, private mempools)
- Designing transactions to minimize MEV extraction or to participate in MEV capture
- Assessing proposer-builder separation (PBS) and its implications for protocol design

## Core Concepts

### MEV Taxonomy

**Definition:** MEV is the maximum value that can be extracted from block production beyond the standard block reward and gas fees, by including, excluding, or reordering transactions within a block.

**Primary MEV Types:**

1. **DEX Arbitrage** — exploiting price differences between DEXs or between DEX pools
   - Atomic: execute in a single transaction using flash loans
   - Cross-DEX: Uniswap pool price differs from SushiSwap
   - Cross-pool: triangular arbitrage across 3+ pools (ETH->USDC->DAI->ETH)
   - Estimated 60-70% of all MEV by volume

2. **Sandwich Attacks** — frontrunning and backrunning a victim's swap
   - Attacker sees pending swap in mempool
   - Frontrun: buy the token before victim, pushing price up
   - Victim's swap executes at worse price
   - Backrun: sell the token after victim at higher price
   - Profit = price impact created minus gas costs
   - Victim loses: their effective slippage exceeds expected slippage

3. **Liquidation MEV** — racing to liquidate undercollateralized positions
   - Monitor health factors on Aave, Compound, MakerDAO
   - First to call liquidate() captures the liquidation bonus (5-10%)
   - Gas priority auctions among competing liquidation bots
   - Flash loans enable liquidation without upfront capital

4. **NFT MEV** — sniping underpriced listings, frontrunning mints
   - Less systematic, more event-driven
   - Mint sniping during popular launches

5. **Long-tail MEV** — protocol-specific extraction (governance, oracle manipulation)

### Sandwich Attack Mechanics (Detailed)

```
Mempool state: Victim wants to swap 10 ETH -> USDC on Uniswap
Pool state: 1000 ETH / 2,000,000 USDC (price = 2000 USDC/ETH)
Victim slippage tolerance: 1%

Attacker frontrun:
- Buy with 50 ETH -> receives ~95,238 USDC
- New pool: 1050 ETH / 1,904,762 USDC (price = 1814 USDC/ETH)

Victim swap executes:
- 10 ETH -> receives ~17,878 USDC (vs ~19,802 without sandwich)
- Victim loses ~$1,924

Attacker backrun:
- Sell 95,238 USDC -> receives ~51.8 ETH
- Profit: ~1.8 ETH minus gas costs (~0.1 ETH)
- Net MEV extracted: ~1.7 ETH ($3,400)
```

### Flashbots and MEV Infrastructure

**Flashbots Ecosystem:**
- **Flashbots Protect** — private transaction submission, bypasses public mempool
- **Flashbots Auction (MEV-Auction)** — searchers bid for bundle inclusion
- **MEV-boost** — out-of-protocol PBS implementation for Ethereum
- **MEV-Share** — redistributes MEV back to users who originated the transactions

**MEV-Boost Architecture:**
```
Transaction flow:
User -> Mempool -> Searchers (find MEV) -> Builders (construct blocks)
  -> Relays (validate blocks) -> Proposers (select highest-bid block)

Key actors:
- Searchers: find MEV opportunities, create bundles
- Builders: aggregate bundles into full blocks, bid for inclusion
- Relays: trusted intermediaries that validate builder blocks
- Proposers: validators who select the winning block
```

**Proposer-Builder Separation (PBS):**
- Separates block building (selecting/ordering transactions) from block proposing (validating)
- Prevents validators from directly extracting MEV
- Enables competitive block building market
- Enshrined PBS: protocol-level implementation (in Ethereum roadmap)
- Current MEV-boost is out-of-protocol, trusted relay model

### MEV Mitigation Strategies

**For Users:**
- Use Flashbots Protect or MEV-blocker for private transaction submission
- Set tight slippage tolerance (but not so tight trades fail)
- Use limit orders instead of market swaps where possible
- Break large trades into smaller chunks via TWAP
- Use DEX aggregators that route through private pools (CoW Swap, 1inch Fusion)

**For Protocols:**
- **Batch auctions** — CoW Protocol: all trades in a batch settle at uniform clearing price
- **Encrypted mempools** — threshold encryption, commit-reveal schemes
- **Fair ordering** — Chainlink FSS (Fair Sequencing Services)
- **MEV redistribution** — MEV-Share, protocol-owned MEV capture
- **Time-weighted average pricing** — reduce single-block manipulation
- **Backrunning-only auctions** — allow beneficial arbitrage, block harmful frontrunning

## Methodology

### MEV Opportunity Assessment
1. **Identify the MEV type** — arbitrage, liquidation, sandwich, or protocol-specific
2. **Estimate gross revenue** — price discrepancy * trade size, liquidation bonus * position size
3. **Calculate costs** — gas cost, priority fee/bid, flash loan fee, capital cost
4. **Assess competition** — how many other searchers target this opportunity? Profit margins compress with competition
5. **Evaluate risk** — failed transactions cost gas, smart contract risk, inventory risk for non-atomic strategies
6. **Determine infrastructure** — latency requirements, builder relationships, private mempool access

### Searcher Profitability Analysis
```
Expected profit per opportunity:
E[profit] = P(win_auction) * (gross_MEV - gas - bid) - P(lose_auction) * wasted_gas

Where:
- P(win_auction) decreases as more searchers compete
- Bid converges toward gross_MEV in competitive markets
- Wasted gas = cost of failed/reverted transactions
- Mature MEV types (DEX arb) have thin margins; novel types have wide margins
```

### MEV Risk Assessment for DeFi Users
```
1. Estimate trade size relative to pool liquidity
2. Calculate expected price impact without MEV
3. Add MEV extraction estimate (typically 20-80% of available sandwich profit)
4. Compare total execution cost vs. using private transaction channels
5. For large trades: evaluate TWAP, RFQ, or batch auction alternatives
```

## Examples

### Example 1: Atomic DEX Arbitrage
```
Opportunity:
- Uniswap ETH/USDC pool: ETH price = $2,010
- SushiSwap ETH/USDC pool: ETH price = $2,000
- Price discrepancy: $10 per ETH

Execution:
1. Flash loan 100 ETH from Aave
2. Sell 100 ETH on Uniswap at $2,010 = $201,000
3. Buy ~100.5 ETH on SushiSwap for $201,000
4. Repay 100 ETH flash loan + 0.05 ETH fee
5. Profit: 0.45 ETH (~$900) minus gas and builder tip

Bundle submission:
- Submit via Flashbots to avoid mempool exposure
- Bid 60% of profit to builder ($540) to ensure inclusion
- Net profit: ~$360 per opportunity
```

### Example 2: Liquidation Bot Strategy
```
Monitoring:
- Track 10,000+ Aave positions continuously
- Pre-compute liquidation prices for each position
- Subscribe to pending block headers for price updates

Execution when position becomes liquidatable:
- Health factor drops below 1.0
- Flash loan the debt asset
- Call liquidate() repaying debt, receiving collateral + bonus
- Swap collateral back to debt asset
- Repay flash loan

Economics:
- Average liquidation bonus: 5%
- Average liquidation size: $50,000
- Gross profit: $2,500
- Gas + builder tip: $500-1,000
- Net profit: $1,500-2,000 per liquidation
- Competition: high, latency-sensitive (sub-block timing)
```

### Example 3: MEV Protection Comparison
```
Trade: Swap 50 ETH -> USDC

Route 1 — Public mempool (Uniswap directly):
- Expected output: 99,500 USDC
- Sandwich extraction: -$800 (estimated)
- Actual output: ~98,700 USDC

Route 2 — Flashbots Protect:
- Expected output: 99,500 USDC
- No sandwich possible (private submission)
- Actual output: ~99,400 USDC (normal slippage only)

Route 3 — CoW Swap (batch auction):
- Expected output: 99,600 USDC (surplus from batch matching)
- No MEV extraction + potential price improvement
- Actual output: ~99,550 USDC

Recommendation: For trades >$10K, always use MEV protection.
CoW Swap provides best execution for large stablecoin swaps.
```

## Quality Gate

Before engaging with MEV strategies or assessing MEV risk, verify:

- [ ] MEV type is correctly identified — arbitrage is constructive (improves pricing), sandwich is extractive
- [ ] All costs are accounted for — gas, priority fees, builder bids, flash loan fees, failed transaction costs
- [ ] Competition level is assessed — mature MEV types have razor-thin margins, often negative EV for new entrants
- [ ] Smart contract interactions are audited — flash loan callbacks and complex multi-hop swaps carry exploit risk
- [ ] Regulatory considerations noted — some MEV activities may face legal scrutiny (particularly sandwich attacks)
- [ ] Infrastructure requirements are realistic — sub-second latency, dedicated builder relationships, custom node setup
- [ ] MEV protection recommendations for users match their trade size and frequency
- [ ] PBS architecture understanding is current — the MEV supply chain evolves rapidly
- [ ] Cross-chain MEV is considered — bridges and L2 sequencers introduce new MEV dynamics
