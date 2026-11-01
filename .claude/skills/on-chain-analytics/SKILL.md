---
name: on-chain-analytics
description: "On-Chain Analytics. Use when: Analyzing blockchain data for trading signals (whale movements, exchange flows, network health); Evaluating crypto asset fundamentals using on-chain metrics; Building or interpreting dashboards from Glassnode, Nansen, Dune Analytics, or similar platforms."
---

# On-Chain Analytics

## When to Activate
- Analyzing blockchain data for trading signals (whale movements, exchange flows, network health)
- Evaluating crypto asset fundamentals using on-chain metrics
- Building or interpreting dashboards from Glassnode, Nansen, Dune Analytics, or similar platforms
- Assessing market structure through wallet clustering and entity behavior

## Core Concepts

### Blockchain Data Layers
1. **Raw transaction data** — inputs, outputs, gas, timestamps, contract interactions
2. **Derived metrics** — aggregated statistics computed from raw data (active addresses, transfer volume)
3. **Entity-level analytics** — clustering addresses into wallets, labeling exchanges, funds, whales
4. **Behavioral signals** — interpreting entity actions as bullish/bearish indicators

### Key On-Chain Metrics

**Supply Metrics:**
- **Circulating supply** — tokens that have moved within a lookback window (e.g., 1 year)
- **Realized cap** — sum of each UTXO valued at the price when it last moved; smooths out speculative premium
- **MVRV ratio** — Market Value / Realized Value; above 3.5 historically signals overheating, below 1.0 signals deep value
- **NUPL** (Net Unrealized Profit/Loss) — aggregate unrealized gains across all holders; >0.75 = euphoria, <0 = capitulation

**Network Activity:**
- **Active addresses** — unique sending/receiving addresses per day; proxy for network adoption
- **Transaction count and volume** — raw throughput; distinguish economic transfers from spam/self-transfers
- **NVT ratio** (Network Value to Transactions) — market cap / daily on-chain transfer volume; crypto's P/E ratio equivalent
- **NVT Signal** — uses 90-day MA of transfer volume for smoother signal; >150 historically overvalued for BTC

**Mining/Staking:**
- **Hash rate** — total computational power securing PoW networks; sustained drops signal miner capitulation
- **Hash ribbons** — 30-day MA crossing below 60-day MA of hash rate; historically strong buy signal when ribbons recover
- **Staking ratio** — percentage of supply staked; higher ratio reduces liquid supply but may indicate complacency

### Exchange Flow Analysis

**Inflow/Outflow Framework:**
- **Exchange inflow** — tokens moving to exchange wallets; signals potential selling pressure
- **Exchange outflow** — tokens leaving exchanges; signals accumulation/cold storage
- **Net flow** — inflow minus outflow; sustained negative net flow is structurally bullish
- **Exchange reserve** — total tokens held on exchanges; declining reserves reduce available sell-side liquidity

**Whale Tracking:**
- Define whale thresholds by asset (BTC: >1000 BTC, ETH: >10,000 ETH)
- Track whale-to-exchange transfers as potential distribution signals
- Monitor whale accumulation addresses (exchange-to-whale flows)
- Nansen "Smart Money" labels track wallets with historically profitable behavior

### Wallet Clustering and Entity Analysis

**Clustering Methods:**
- **Common input heuristic** — addresses used as inputs in the same transaction likely belong to the same entity
- **Change address detection** — identifying change outputs to group with sending addresses
- **Timing analysis** — addresses that consistently transact together
- **Contract interaction patterns** — wallets interacting with same DeFi protocols in similar patterns

**Entity Categories:**
- Exchanges (labeled by Chainalysis, Nansen, Arkham)
- Mining pools and miners
- DeFi protocols and their treasuries
- Institutional custodians
- Known fund wallets (a16z, Paradigm, etc.)

## Methodology

### Signal Construction Process
1. **Data ingestion** — pull raw data from node, indexer (The Graph), or analytics API
2. **Metric computation** — calculate derived metrics with appropriate lookback windows
3. **Normalization** — z-score or percentile rank metrics against historical distribution
4. **Signal generation** — define thresholds or regime boundaries for actionable signals
5. **Confluence** — combine multiple on-chain signals; require 3+ confirmations for high conviction

### Practical Analysis Workflow
```
Step 1: Check exchange net flows (are tokens leaving exchanges?)
Step 2: Review MVRV and NUPL (are we in overvalued or undervalued territory?)
Step 3: Examine active address trends (is adoption growing or shrinking?)
Step 4: Monitor whale behavior (accumulating or distributing?)
Step 5: Cross-reference with funding rates and derivatives data
Step 6: Synthesize into a directional bias with confidence level
```

### Data Source Hierarchy
- **Tier 1 (most reliable):** Running your own full node, parsing raw blocks
- **Tier 2:** Indexed data providers (The Graph, Bitquery, Flipside)
- **Tier 3:** Analytics platforms (Glassnode, Nansen, CryptoQuant, IntoTheBlock)
- **Tier 4:** Social/aggregated dashboards (Dune community queries, DefiLlama)

## Examples

### Example 1: BTC Accumulation Signal
```
Observation:
- Exchange reserves declining for 30+ consecutive days
- MVRV at 0.85 (below realized value)
- Whale addresses (>1000 BTC) increasing in count
- Hash ribbons recovering after miner capitulation

Assessment: Strong accumulation phase. Multiple on-chain metrics align
with historical bear market bottoms. High conviction long bias.
```

### Example 2: ETH Distribution Warning
```
Observation:
- Large exchange inflows from top-100 wallets (3 consecutive days)
- NVT Signal at 180 (historically overvalued zone)
- NUPL at 0.72 (approaching euphoria)
- New address growth flattening despite price increase

Assessment: Distribution signals emerging. Price appreciation not
supported by network growth. Reduce position size, tighten stops.
```

### Example 3: Stablecoin Supply Expansion
```
Observation:
- USDT and USDC combined market cap increasing $2B in 7 days
- Stablecoin exchange reserves rising (dry powder accumulating)
- Stablecoin dominance declining from recent highs

Assessment: Capital inflow into crypto ecosystem via stablecoins.
Historically precedes risk-on rallies. Watch for deployment into
BTC/ETH as confirmation.
```

## Quality Gate

Before acting on on-chain signals, verify:

- [ ] Data source is reliable and up-to-date (check for indexing lag, typically 1-6 blocks)
- [ ] Metrics are calculated with appropriate lookback windows (avoid recency bias)
- [ ] Whale movements are confirmed across multiple tracking platforms (avoid false labels)
- [ ] Exchange flow data accounts for internal transfers and wallet rotations (exchanges regularly reshuffle hot/cold wallets)
- [ ] On-chain signals are corroborated by at least one other data domain (derivatives, sentiment, or price action)
- [ ] Contextual factors considered — protocol upgrades, airdrops, and bridge activity can distort on-chain metrics
- [ ] Time horizon matches the signal frequency — on-chain metrics are typically medium-term (weeks to months), not intraday
- [ ] Account for chain-specific nuances — UTXO vs account model, L1 vs L2 activity
