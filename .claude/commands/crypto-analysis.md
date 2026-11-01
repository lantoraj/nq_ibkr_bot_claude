---
description: Analyze crypto assets, DeFi protocols, on-chain metrics, and yield opportunities
---

# /crypto-analysis

## What This Command Does

Performs comprehensive cryptocurrency and DeFi analysis including on-chain metrics, protocol evaluation, tokenomics assessment, yield farming opportunities, and risk analysis. The crypto-defi-analyst agent leads, providing data-driven insights for crypto-native trading and investment decisions.

## When to Use

- You want to evaluate a crypto asset or DeFi protocol for investment
- You need on-chain analytics (active addresses, whale flows, exchange balances)
- You want to compare yield farming opportunities across protocols
- You need to assess smart contract risk, tokenomics, or protocol sustainability

## How It Works

1. **Asset overview** — Summarizes market cap, liquidity, trading venues, and market structure.
2. **On-chain analysis** — Analyzes wallet activity, whale movements, exchange flows, and network metrics.
3. **Tokenomics review** — Evaluates supply schedule, inflation, vesting, governance, and token utility.
4. **Protocol analysis** — For DeFi tokens, evaluates TVL, revenue, user growth, and competitive position.
5. **Yield opportunities** — Identifies and risk-rates yield farming, staking, and liquidity provision opportunities.
6. **Risk assessment** — Covers smart contract risk, regulatory risk, liquidity risk, and concentration risk.

## Example Usage

**Input:**
```
/crypto-analysis evaluate Ethereum ecosystem health and
top DeFi yield opportunities with risk assessment
```

**Output:**
```
## Crypto Analysis — Ethereum Ecosystem

### Network Health
| Metric                  | Current    | 30d Trend | Signal    |
|-------------------------|-----------|-----------|-----------|
| Active addresses (daily)| 542K      | +8%       | Growing   |
| Gas fees (median, gwei) | 28        | -15%      | Declining |
| ETH staked              | 31.2M     | +2%       | Growing   |
| Net ETH issuance (30d)  | -12,400   | Deflationary| Bullish |
| L2 TVL                  | $42B      | +18%      | Growing   |
| DEX volume (7d)         | $18.4B    | +5%       | Stable    |

### Exchange Flows
- Net exchange outflow: 84,000 ETH over past 30 days (bullish)
- Whale wallets (>10K ETH): accumulated 120,000 ETH in 30 days
- Stablecoin reserves on exchanges: $28B (dry powder available)

### Top DeFi Yield Opportunities (Risk-Adjusted)
| Protocol     | Strategy           | APY    | TVL    | Risk  | Score |
|-------------|--------------------| -------|--------|-------|-------|
| Aave V3     | ETH lending        | 3.8%   | $12B   | Low   | A     |
| Lido        | ETH staking        | 3.4%   | $28B   | Low   | A     |
| Curve       | stETH/ETH LP       | 4.2%   | $1.8B  | Low   | A-    |
| Uniswap V3  | ETH/USDC 0.05%    | 12-18% | $480M  | Med   | B+    |
| Pendle      | stETH yield tokens | 8.5%   | $3.2B  | Med   | B     |
| Ethena      | USDe basis trade   | 15.2%  | $4.1B  | High  | B-    |

### Risk Assessment
| Risk Category        | Level  | Details                           |
|---------------------|--------|-----------------------------------|
| Smart contract      | Low    | Aave, Lido battle-tested 3+ yrs  |
| Regulatory          | Medium | SEC ETH classification unclear    |
| Liquidity           | Low    | Deep liquidity on major DEXs      |
| Concentration       | Medium | Top 100 wallets hold 39% supply   |
| L2 bridge risk      | Medium | Cross-chain bridges remain target |
| Staking slashing    | Low    | DVT adoption reducing risk        |

### Recommendations
1. Core allocation: ETH staking via Lido (3.4%, lowest risk)
2. Enhanced yield: Curve stETH/ETH LP (4.2%, minimal IL risk)
3. Active strategy: Uniswap V3 concentrated LP (12-18%, requires management)
4. Avoid: Protocols with anonymous teams, unaudited contracts,
   or yields > 20% without clear source
```

## Related Agents

- **crypto-defi-analyst** — Primary agent, on-chain analytics and protocol evaluation
- **risk-manager** — Quantifies smart contract, liquidity, and counterparty risk
- **execution-specialist** — Plans DEX/CEX execution, gas optimization
- **quant-researcher** — Analyzes crypto factor models and on-chain signals
