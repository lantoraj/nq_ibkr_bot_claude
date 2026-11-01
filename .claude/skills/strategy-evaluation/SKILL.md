---
name: strategy-evaluation
description: "Strategy Evaluation Framework. Use when: Conducting comprehensive evaluation of a trading strategy before deployment; Adjusting Sharpe ratios for autocorrelation, non-normality, and multiple testing; Assessing parameter stability and regime robustness."
---

# Strategy Evaluation Framework

## When to Activate
- Conducting comprehensive evaluation of a trading strategy before deployment
- Adjusting Sharpe ratios for autocorrelation, non-normality, and multiple testing
- Assessing parameter stability and regime robustness
- Estimating strategy capacity and transaction cost sensitivity
- Making go/no-go decisions on strategy deployment

## Core Concepts

### Strategy Evaluation Checklist

**Five Pillars of Strategy Evaluation:**
```
1. Statistical Significance — Is the edge real or noise?
2. Robustness — Does it survive regime changes, parameter perturbation, and alternative data?
3. Capacity — How much capital can the strategy absorb before degrading?
4. Implementation — Can it be executed at realistic costs?
5. Risk Profile — Are the drawdowns and tail risks acceptable?
```

### Sharpe Ratio Adjustments

**Adjustment for Autocorrelation:**
```
Many strategies have autocorrelated returns (momentum strategies: positive,
mean reversion: negative). Standard Sharpe assumes IID returns.

Adjusted annualization:
SR_adjusted = SR_daily * sqrt(252 / (1 + 2*sum(rho_k for k=1..n)))

Where rho_k is the autocorrelation at lag k

Positive autocorrelation (momentum): SR is OVERSTATED
- If lag-1 autocorrelation = 0.1:
  SR_adjusted ≈ SR_standard * sqrt(252/(1+2*0.1+2*0.05+...)) ≈ SR * 0.85
  15% overstatement from ignoring autocorrelation

Negative autocorrelation (mean reversion): SR is UNDERSTATED
- If lag-1 autocorrelation = -0.1:
  SR_adjusted ≈ SR_standard * sqrt(252/(1-0.2-0.1+...)) ≈ SR * 1.10
  Mean reversion strategies are slightly better than they appear

Always compute ACF of strategy returns and apply this correction.
```

**Adjustment for Non-Normality:**
```
Sharpe ratio assumes normally distributed returns.
Real trading returns have:
- Negative skewness (fat left tail, common in equity strategies)
- Excess kurtosis (fatter tails than normal in both directions)

Adjusted Sharpe (Lo, 2002):
SR_adjusted = SR * [1 - (skewness/6)*SR + ((kurtosis-3)/24)*SR^2]^(-1/2)

Example:
SR = 1.5, skewness = -1.0, kurtosis = 6 (excess = 3)
Adjustment factor ≈ 0.88
SR_adjusted = 1.5 * 0.88 = 1.32

Strategies that appear to have high Sharpe but negative skew
(selling options, carry trades) are less attractive after adjustment.
```

**Adjustment for Multiple Testing:**
```
See overfitting-prevention skill for full treatment.

Quick reference:
If N strategies tested, minimum Sharpe for significance:
N=1:   0.40
N=10:  0.70
N=50:  0.95
N=100: 1.10

Apply Deflated Sharpe Ratio (DSR) for formal testing.
```

### Parameter Stability

**Assessment Methods:**

1. **Walk-Forward Stability:**
```
Record optimal parameters in each walk-forward window
Calculate coefficient of variation (CV) for each parameter
CV < 0.15: stable (good)
CV 0.15-0.30: moderately stable (acceptable)
CV > 0.30: unstable (concerning)
```

2. **Parameter Heatmap:**
```
For strategies with 2 parameters:
- Create a grid of parameter combinations
- Color by performance metric (Sharpe, return)
- Robust strategy: broad warm region (plateau)
- Overfit strategy: narrow hot spot (peak)
```

3. **Performance Degradation Test:**
```
Perturb each parameter by ±10%, ±20%
If performance drops >30% with ±20% perturbation: fragile
If performance drops <15% with ±20% perturbation: robust
```

### Regime Robustness

**Regime Classification:**
```
Define regimes by:
1. Trend regime: trending (ADX>25) vs ranging (ADX<20)
2. Volatility regime: low vol (VIX<15), medium (15-25), high (>25)
3. Correlation regime: normal correlation vs correlation breakdown
4. Macro regime: expansion, slowdown, recession, recovery

Evaluate strategy in each regime independently:
- Sharpe ratio per regime
- Max drawdown per regime
- Hit rate per regime

Red flag: strategy performs well in only one regime
(e.g., only works in bull markets -> not a strategy, just beta exposure)
```

**Regime-Conditional Analysis:**
```
Regime         | Sharpe | Max DD | % of Time | Contribution to P&L
Bull/Low Vol   | 1.8    | 5%     | 35%       | 45%
Bull/High Vol  | 0.9    | 12%    | 15%       | 15%
Bear/Low Vol   | 0.3    | 8%     | 20%       | 5%
Bear/High Vol  | -0.2   | 22%    | 15%       | -10%
Sideways       | 0.6    | 10%    | 15%       | 10%

Assessment: Strategy is primarily a bull market strategy.
45% of P&L from 35% of time (bull/low vol). Negative in bear/high vol.
If deployed, needs bear market hedge or position reduction trigger.
```

### Capacity Estimation

**Definition:** Maximum capital the strategy can manage before transaction costs, market impact, and liquidity constraints erode performance.

**Estimation Framework:**
```
Capacity factors:
1. Average daily volume of traded instruments
2. Strategy turnover (annual turnover = trades per year * average position)
3. Market impact model
4. Target impact threshold (e.g., max 10% of daily volume)

Simple capacity estimate:
Capacity = ADV * max_participation_rate / daily_turnover

Where:
- ADV = average daily dollar volume of traded instrument
- max_participation_rate = 1-5% (higher for liquid markets)
- daily_turnover = strategy's daily trading volume as % of AUM

Example:
- Trading SPY: ADV = $30B
- Participation rate: 1%
- Daily turnover: 20% of AUM
- Capacity = $30B * 0.01 / 0.20 = $1.5B

For less liquid instruments:
- Small cap stocks: capacity might be $10-50M
- Crypto altcoins: capacity might be $1-5M
- FX G10: capacity effectively unlimited for most strategies
```

**Market Impact Models:**
```
Square root impact model:
Impact (bps) = sigma * sqrt(V_trade / V_daily) * C

Where:
sigma = daily volatility (bps)
V_trade = trade volume
V_daily = average daily volume
C = constant (~1 for equities)

Example: sigma=100bps, V_trade=1M shares, V_daily=10M shares
Impact = 100 * sqrt(0.1) * 1 = 31.6 bps one-way
Round-trip impact: ~63 bps

For 200% annual turnover (daily turnover ≈ 0.8%):
Annual impact cost: 63 bps * 200% / 100 = 126 bps
If gross Sharpe = 1.5 and vol = 15%: gross return = 22.5%
Net of impact: 22.5% - 1.26% = 21.24%
Impact is manageable at this AUM level.
```

### Transaction Cost Sensitivity

**Cost Components:**
```
Total round-trip cost = commission + spread + market impact + slippage

Commission: mostly negligible now ($0 for retail, $0.002-0.005/share institutional)
Spread: bid-ask spread, varies by instrument
  - SPY: ~$0.01 (~0.002%)
  - Small caps: $0.05-0.50 (0.1-1.0%)
  - Crypto (BTC): ~0.01% on major venues
  - Crypto (altcoins): 0.1-1.0%
Market impact: from square root model above
Slippage: execution price vs decision price (latency-dependent)
```

**Sensitivity Analysis:**
```
Run backtest at multiple cost assumptions:
Cost scenario | Sharpe | CAGR  | Assessment
Zero cost     | 1.80   | 25%   | Theoretical upper bound (meaningless)
Low (5 bps)   | 1.55   | 21%   | Best case realistic
Medium (10bps)| 1.30   | 18%   | Base case
High (20 bps) | 0.85   | 12%   | Conservative / stress case
Very high(50) | 0.15   | 3%    | Capacity-constrained scenario

Critical cost threshold: the cost level where Sharpe drops below 0.5
If critical threshold < 15 bps: strategy is cost-sensitive, needs low-cost execution
If critical threshold > 50 bps: strategy is cost-robust
```

## Methodology

### Comprehensive Evaluation Process

**Phase 1: Statistical Validation**
1. Calculate raw performance metrics (Sharpe, drawdown, etc.)
2. Adjust Sharpe for autocorrelation and non-normality
3. Apply DSR for multiple testing correction
4. Run walk-forward analysis and calculate WFE
5. Run CPCV and assess path distribution
6. Determine statistical significance

**Phase 2: Robustness Testing**
1. Parameter stability across walk-forward windows
2. Parameter sensitivity (perturbation analysis)
3. Regime-conditional performance breakdown
4. Alternative asset/universe testing
5. Alternative time period testing
6. Monte Carlo simulation for confidence intervals

**Phase 3: Practical Assessment**
1. Capacity estimation
2. Transaction cost sensitivity
3. Execution feasibility (latency, infrastructure requirements)
4. Operational risk assessment
5. Regulatory and compliance review
6. Correlation with existing portfolio strategies

**Phase 4: Go/No-Go Decision**
```
Deploy (full allocation) when ALL of:
- Adjusted Sharpe > 0.8
- DSR significant at p < 0.05
- WFE > 0.6
- CPCV: >80% paths profitable
- Robust across 2+ regimes
- Capacity > 2x planned allocation
- Net-of-cost Sharpe > 0.5
- Economic rationale documented

Paper trade when:
- Adjusted Sharpe > 0.5
- Some robustness concerns
- Limited out-of-sample history
- Capacity may be constrained

Reject when:
- Adjusted Sharpe < 0.5 or DSR not significant
- WFE < 0.4
- Only works in one regime
- Transaction costs erode most of the edge
- No clear economic rationale
```

### Correlation with Existing Strategies
```
Before adding a new strategy to a portfolio:
1. Calculate correlation of returns with each existing strategy
2. Calculate correlation during stress periods (may differ from average)
3. Assess marginal Sharpe contribution:
   Marginal SR = (SR_new - rho * SR_existing) / sqrt(1 - rho^2)
   If marginal SR < 0.3: strategy does not add enough diversification
4. Run portfolio optimization including new strategy
5. Check if new strategy displaces existing strategies or adds new capacity
```

## Examples

### Example 1: Full Evaluation Report
```
Strategy: Mean reversion on S&P 500 sector ETFs
Backtest: Jan 2010 - Dec 2024 (15 years, daily)

Raw metrics:
- CAGR: 14.2%, Vol: 10.5%, Sharpe: 1.35
- Max DD: 11.3%, Calmar: 1.26
- Win rate: 54%, Avg Win/Loss: 1.3x

Adjustments:
- Autocorrelation (lag-1 = -0.08): adjusted SR = 1.42 (slight boost, mean reversion)
- Non-normality (skew=-0.5, kurt=4.2): adjusted SR = 1.28
- Multiple testing (15 variants tested): DSR significant at p=0.03

Walk-forward (4Y IS, 1Y OOS, rolling):
- Average OOS Sharpe: 0.88
- WFE: 0.65 (acceptable)
- All 11 OOS windows positive

Parameter stability:
- Lookback: CV=0.12 (stable)
- Threshold: CV=0.18 (moderately stable)

Regime analysis:
- Bull markets: SR=1.1 (good)
- Bear markets: SR=0.6 (acceptable, not negative)
- High vol: SR=1.4 (excellent — mean reversion thrives)
- Low vol: SR=0.7 (lower but still positive)

Capacity: ~$500M (sector ETFs are liquid)
Cost sensitivity: Sharpe at 20bps cost = 1.05 (robust)

Decision: DEPLOY at 75% target allocation. Paper trade for 3 months
to verify live execution matches backtest assumptions.
```

### Example 2: Rejected Strategy
```
Strategy: Earnings momentum on small caps
Backtest: Jan 2015 - Dec 2024 (10 years, monthly)

Raw metrics:
- CAGR: 22%, Vol: 18%, Sharpe: 1.22
- Max DD: 28%

Red flags identified:
- 45 parameter combinations tested -> DSR requires SR > 1.05
- SR of 1.22 passes marginally, but:
- Walk-forward WFE: 0.32 (poor — significant OOS degradation)
- CPCV: 14/28 paths profitable (50% — coin flip)
- Regime analysis: SR=2.1 in bull markets, SR=-0.3 in bear markets
  -> Strategy is leveraged beta exposure, not alpha
- Cost sensitivity: at 30bps (realistic for small caps), Sharpe = 0.55

Decision: REJECT
Rationale: Poor WFE, regime-dependent performance (only works in bull),
and CPCV shows 50% chance of loss. The "edge" is market exposure
disguised as alpha by favorable backtest period.
```

### Example 3: Transaction Cost Impact
```
Strategy: Intraday mean reversion on SPY (5-minute bars)
Backtest period: 2020-2024

Performance at different cost levels:
Cost (bps/side) | Sharpe | Trades/Year | Annual Return
0               | 3.20   | 12,000      | 35%
1               | 2.45   | 12,000      | 28%
2               | 1.70   | 12,000      | 21%
3               | 0.95   | 12,000      | 14%
5               | -0.55  | 12,000      | -1%

Analysis:
- Strategy is extremely cost-sensitive
- Each 1 bps increase in round-trip cost reduces Sharpe by ~0.75
- Break-even cost: ~4.2 bps round-trip
- Realistic cost for institutional: 2-3 bps (SPY is very liquid)
- Realistic cost for retail: 5-10 bps (wider spreads, worse execution)

Recommendation:
- Viable for institutional traders with direct market access (Sharpe ~1.7)
- NOT viable for retail traders (negative Sharpe at realistic costs)
- Capacity: ~$50M before market impact becomes significant
  (intraday strategies have limited capacity)
```

## Quality Gate

Before deploying a strategy, verify:

- [ ] Sharpe ratio adjusted for autocorrelation and non-normality
- [ ] Deflated Sharpe Ratio is significant after accounting for ALL strategies tested
- [ ] Walk-forward efficiency ratio (WFE) exceeds 0.6
- [ ] CPCV shows >80% of paths are profitable
- [ ] Parameter stability verified — CV < 0.20 for all key parameters
- [ ] Regime robustness tested — positive performance in at least 3/4 regimes
- [ ] Capacity estimated and exceeds planned allocation by 2x+
- [ ] Transaction cost sensitivity analyzed — net Sharpe > 0.5 at realistic costs
- [ ] Monte Carlo confidence intervals calculated — 90th percentile drawdown acceptable
- [ ] Economic rationale documented — strategy exploits an identifiable and persistent inefficiency
- [ ] Correlation with existing strategies assessed — adds diversification benefit
- [ ] Implementation plan documented — infrastructure, data, execution, monitoring requirements
