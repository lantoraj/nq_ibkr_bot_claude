---
name: tokenomics
description: "Tokenomics Analysis. Use when: Evaluating a token's supply dynamics, emission schedule, and value accrual mechanisms; Assessing vesting unlock schedules and their potential market impact; Analyzing inflation/deflation mechanics and burn mechanisms."
---

# Tokenomics Analysis

## When to Activate
- Evaluating a token's supply dynamics, emission schedule, and value accrual mechanisms
- Assessing vesting unlock schedules and their potential market impact
- Analyzing inflation/deflation mechanics and burn mechanisms
- Comparing governance token designs and fee distribution models
- Due diligence on new token launches, airdrops, or protocol incentive programs

## Core Concepts

### Supply Framework

**Supply Definitions:**
- **Max supply** — hard cap on total tokens that will ever exist (BTC: 21M, not all tokens have a cap)
- **Total supply** — tokens minted minus tokens burned (includes locked/unvested tokens)
- **Circulating supply** — tokens available for trading on the open market
- **Fully diluted valuation (FDV)** — price * max supply (or total supply if no max); represents worst-case dilution
- **MC/FDV ratio** — circulating market cap / FDV; low ratio means significant future dilution

**Critical Insight:** A token with $100M market cap and $2B FDV has 95% of supply yet to enter circulation. This overhang suppresses long-term price appreciation unless demand growth outpaces supply inflation.

### Emission and Inflation

**Emission Schedules:**
- **Fixed schedule** — predetermined, immutable (BTC halving every 210,000 blocks)
- **Governance-controlled** — community votes on emission rates (many DeFi protocols)
- **Demand-based** — emissions adjust based on protocol metrics (Ethereum post-merge: issuance ~ staking participation)
- **Tail emission** — small perpetual inflation after initial distribution (Monero: 0.6 XMR/block forever)

**Inflation Rate Calculation:**
```
Annual inflation = (new tokens minted per year) / circulating supply
Real inflation = nominal inflation - burn rate
Effective inflation = real inflation adjusted for staking lockup
```

**Inflation Impact Framework:**
- <2% annual: negligible impact, comparable to gold
- 2-10% annual: moderate dilution, must be offset by demand growth or staking yield
- 10-50% annual: aggressive dilution, common in early-stage DeFi; price usually declines unless TVL grows faster
- >50% annual: unsustainable; typically farm-and-dump dynamics

### Vesting Schedules

**Standard Vesting Components:**
- **Cliff** — period before any tokens unlock (typically 6-12 months)
- **Linear vesting** — tokens unlock proportionally over time after cliff
- **Unlock events** — discrete large unlocks (e.g., 25% at TGE, then monthly for 24 months)

**Market Impact Assessment:**
```
Unlock impact score = (tokens unlocking / daily trading volume) * recipient_sell_probability

Recipient sell probability by category:
- Team/founders: 30-50% (incentivized to hold, but need liquidity)
- VCs/investors: 50-80% (mandate to return capital, often hedge)
- Ecosystem/community: 10-30% (typically smaller holders, mixed behavior)
- Treasury: 5-15% (usually programmatic spending, not market selling)
```

**Red Flags in Vesting:**
- Multiple large unlocks clustered in same month
- Team allocation >25% of total supply
- Investor cost basis far below current price (high incentive to sell)
- No lockup for advisory tokens
- Vesting acceleration clauses tied to token price milestones

### Value Accrual Mechanisms

**Fee Distribution Models:**
- **Direct fee sharing** — protocol fees distributed to token stakers (e.g., GMX: 30% of fees to GMX stakers)
- **Buyback and distribute** — protocol buys tokens on market, distributes to stakers
- **Buyback and burn** — protocol buys and burns tokens, reducing supply (deflationary)
- **Fee switch** — governance can activate fee sharing (Uniswap: fee switch exists but not activated)
- **veToken model** — lock tokens for voting power and fee share (Curve: veCRV)

**Value Accrual Analysis:**
```
Protocol P/E = FDV / annualized protocol revenue
Protocol P/S = FDV / annualized protocol fees
Token holder yield = fees distributed to stakers / staked token market cap
Real yield = yield from actual revenue (not token emissions)
```

### Governance Token Economics

**Governance Token Functions:**
1. Voting on protocol parameters (interest rates, collateral factors)
2. Fee distribution rights
3. Treasury allocation decisions
4. Protocol upgrade approval
5. Gauge/emission directing (Curve model)

**Governance Token Valuation Drivers:**
- Revenue capture (current and potential via fee switch)
- Treasury value per token
- Voting power value (bribery markets like Votium price governance power directly)
- Growth optionality (new products, chains, partnerships)

## Methodology

### Token Evaluation Process
1. **Map the supply schedule** — chart tokens entering circulation over 5 years
2. **Identify unlock events** — mark major vesting cliffs on calendar, calculate volume-relative impact
3. **Calculate real inflation** — subtract burns and permanent lockups from gross emission
4. **Assess value accrual** — quantify fee revenue, distribution mechanism, and token holder capture rate
5. **Compare valuations** — benchmark P/E, P/S, and FDV/revenue against comparable protocols
6. **Model scenarios** — bull case (demand grows faster than supply), base case, bear case (emission dumping)

### Supply Shock Analysis
```
1. Calculate daily emission rate in USD terms
2. Compare to average daily trading volume
3. Emission/volume ratio > 5%: significant sell pressure
4. Identify natural buyers (stakers, governance lockers, treasury)
5. Net selling pressure = emission - natural absorption
6. Project supply schedule against demand growth scenarios
```

## Examples

### Example 1: Deflationary Analysis (ETH Post-Merge)
```
Pre-merge ETH inflation: ~4.3% annually (PoW issuance)
Post-merge ETH:
- PoS issuance: ~0.5% annually (varies with staking ratio)
- EIP-1559 burn: ~0.5-2.0% annually (varies with network usage)
- Net inflation: -0.5% to +0.3% (often deflationary during high usage)

Assessment: ETH achieved "ultrasound money" narrative.
Supply is structurally declining during high-activity periods.
Positive feedback loop: more usage = more burn = less supply = higher price.
Key risk: if L2s capture most activity, L1 burn decreases.
```

### Example 2: Vesting Unlock Impact
```
Token: PROJECT_X
Current price: $5.00
Circulating supply: 100M tokens ($500M MC)
FDV: $2.5B (500M max supply)
Daily volume: $20M

Upcoming unlock: 50M tokens (VC round at $0.50/token)
VC cost basis: $0.50 (10x profit at current price)
Expected sell pressure: 50M * $5 * 60% sell probability = $150M

Analysis:
- $150M selling into $20M daily volume = 7.5 days of volume
- Even with 20% market impact absorption, price pressure is severe
- Historical pattern: similar unlocks cause 20-40% drawdowns
- Strategy: reduce position 2 weeks before unlock, re-enter after
  selling pressure subsides (typically 2-4 weeks post-unlock)
```

### Example 3: veToken Model Valuation
```
Protocol: Curve Finance
Annual trading fees: $150M
CRV staker share: 50% = $75M to veCRV holders
Total veCRV: 500M CRV locked (average 3 years)
veCRV market cap: $250M

Staking yield: $75M / $250M = 30% real yield
Additional value: bribe revenue ($100M+ annually on Votium)
Total yield: ($75M + $100M) / $250M = 70%

Assessment: High real yield suggests undervaluation OR
high risk premium. Risks include governance attacks,
competing AMMs, and regulatory uncertainty around
the bribery mechanism.
```

## Quality Gate

Before making investment decisions based on tokenomics, verify:

- [ ] Supply schedule data sourced from verified smart contracts, not just whitepaper claims
- [ ] Vesting contracts are immutable or have transparent governance for changes
- [ ] FDV calculation includes all possible supply sources (treasury, ecosystem fund, future emissions)
- [ ] Burn mechanism is verifiable on-chain, not just claimed in documentation
- [ ] Fee distribution is live and auditable, not a future "fee switch" promise
- [ ] Inflation calculations account for all emission sources (staking rewards, liquidity mining, grants)
- [ ] Governance centralization assessed — can a small group of holders control key decisions?
- [ ] Comparable protocol valuations are on an apples-to-apples basis (same metrics, same chain, similar stage)
- [ ] Token utility is genuine and not easily replicated without the token
- [ ] Legal/regulatory status of fee distribution mechanism is considered (securities classification risk)
