---
name: trend-following
description: "Trend Following. Use when: User wants to build a systematic trend-following or CTA-style strategy; Designing moving average crossover or channel breakout systems; Implementing Turtle Trading rules or similar mechanical systems."
---

# Trend Following

name: trend-following
description: Trend-following strategies — CTA-style, moving averages, breakout systems, Turtle Trading. Use when designing trend-based systems.

## When to Activate

- User wants to build a systematic trend-following or CTA-style strategy
- Designing moving average crossover or channel breakout systems
- Implementing Turtle Trading rules or similar mechanical systems
- Position sizing with ATR or volatility-based methods
- Constructing multi-asset trend portfolios across futures markets

## First Questions

1. Which markets and instruments (managed futures, equities, FX, crypto)?
2. What trend definition — moving averages, breakouts, or momentum?
3. What time horizon for trends — short (days), medium (weeks), or long (months)?
4. Is this a single-instrument system or a diversified multi-market portfolio?
5. What is the risk budget and maximum acceptable drawdown?

## Core Concepts

### Why Trend Following Works

Trend following exploits serial correlation in asset prices. It works because:

- **Behavioral biases:** Anchoring, herding, disposition effect create slow price adjustment
- **Institutional flows:** Pension fund rebalancing, central bank interventions, index tracking
- **Risk premia:** Trend following is akin to being long a straddle — it profits from large moves in either direction
- **Crisis alpha:** Tends to perform well during sustained market dislocations (2008, 2022)

### The CTA Model

Commodity Trading Advisors (CTAs) are the primary institutional implementation of trend following:

```
Typical CTA structure:
- 50-100 liquid futures markets across 4 asset classes
- Trend signals: moving averages, breakouts, or time-series momentum
- Position sizing: risk parity / volatility targeting
- Rebalancing: daily
- Typical Sharpe: 0.5-0.8 (gross), 0.3-0.5 (net)
- Key advantage: positive skew, crisis alpha, low correlation to equities
```

### Trend Strength and ADX

Average Directional Index (ADX) measures trend strength (not direction):

```
ADX calculation:
1. +DM = High_t - High_{t-1} (if positive and > -DM, else 0)
2. -DM = Low_{t-1} - Low_t (if positive and > +DM, else 0)
3. ATR = 14-period average true range
4. +DI = 100 * EMA(+DM, 14) / ATR
5. -DI = 100 * EMA(-DM, 14) / ATR
6. DX = 100 * |+DI - -DI| / (+DI + -DI)
7. ADX = 14-period EMA of DX

Interpretation:
  ADX > 25: Strong trend (trend-following systems perform well)
  ADX 20-25: Developing trend
  ADX < 20: No trend (mean-reversion may be better)
  Rising ADX: Trend strengthening
  Falling ADX: Trend weakening
```

## Detailed Methodology

### Moving Average Systems

**Single Moving Average:**
```
Buy when Price > MA(N)
Sell/Short when Price < MA(N)

Common periods: MA(50), MA(100), MA(200)
MA(200) is the most widely followed — institutional benchmark for bull/bear
```

**Moving Average Crossover:**
```
Buy when Fast MA > Slow MA (golden cross)
Sell when Fast MA < Slow MA (death cross)

Classic combinations:
  Fast/Slow: 10/50, 20/50, 50/200
  Shorter = more responsive but more whipsaws
  Longer = fewer signals, less whipsaw, more lag

MA types:
  SMA: Simple. Equal weight to all periods. More lag.
  EMA: Exponential. More weight on recent. Less lag.
  DEMA/TEMA: Double/Triple EMA. Further lag reduction.
  KAMA: Kaufman Adaptive. Adjusts speed to market noise.
  Hull MA: Uses WMA to reduce lag significantly.
```

**Multiple MA Envelope (Faber style):**
```
Compute N moving averages: MA(20), MA(50), MA(100), MA(150), MA(200)
Signal = fraction of MAs below current price
  5/5: Strong uptrend — full position
  3/5 or 4/5: Moderate trend — partial position
  0/5 or 1/5: Strong downtrend — flat or short
```

### Channel Breakout Systems

**Donchian Channel (Turtle Trading):**
```
Upper channel: Highest high of last N periods
Lower channel: Lowest low of last N periods
Middle: (Upper + Lower) / 2

Entry: Buy when price breaks above N-period high
       Sell when price breaks below N-period low
Exit:  Exit long when price breaks below M-period low (M < N)
       Exit short when price breaks above M-period high

Turtle Trading original rules:
  System 1: N=20 (entry), M=10 (exit)
  System 2: N=55 (entry), M=20 (exit)
  Skip rule: If last breakout was profitable, skip next System 1 signal
```

**Keltner Channel:**
```
Middle: EMA(20)
Upper: EMA(20) + 2 * ATR(10)
Lower: EMA(20) - 2 * ATR(10)

Breakout above upper channel = trend entry
Uses volatility-adaptive bands (ATR) vs fixed standard deviation (Bollinger)
```

### ATR-Based Position Sizing

The Average True Range controls risk per position:

```
True Range = max(High-Low, |High-PrevClose|, |Low-PrevClose|)
ATR(N) = N-period average of True Range

Position size calculation:
  Dollar risk per trade = Account * risk_fraction
  Dollars per ATR = ATR(20) * point_value
  Position size = Dollar risk per trade / (stop_distance_ATR * Dollars per ATR)

Example:
  Account: $1,000,000
  Risk fraction: 1% ($10,000 per trade)
  ATR(20) of crude oil: $2.50
  Point value: $1,000 per $1 move
  Stop distance: 2 ATR = $5,000 per contract
  Position: $10,000 / $5,000 = 2 contracts

Turtle Trading unit:
  1 unit = 1% of account / (ATR * point_value)
  Maximum 4 units per market, 10 units per correlated group
```

### Volatility Scaling

```
Target volatility approach:
  target_vol = 10% annualized (typical for CTA)
  current_vol = realized_vol or ATR-implied vol
  position_scalar = target_vol / current_vol

  Higher vol → smaller positions
  Lower vol → larger positions
  Keeps risk contribution constant across instruments and time

Application to multi-asset trend portfolio:
  For each instrument i:
    signal_i = sign(trend indicator)
    vol_i = realized vol of instrument i
    weight_i = signal_i * (target_vol / vol_i) / N_instruments
```

### CTA Portfolio Construction

```
Market selection criteria:
  - Sufficient liquidity (open interest, volume)
  - Data availability (10+ years minimum)
  - Reasonable transaction costs
  - Low correlation to existing portfolio markets

Typical allocation across sectors:
  Equities:     20-25% risk budget (5-8 markets: ES, NQ, NK, SX5E, HSI, etc.)
  Fixed Income: 25-30% (5-8 markets: ZN, ZB, Bund, Gilt, JGB, etc.)
  FX:           20-25% (6-10 pairs: EUR, GBP, JPY, AUD, CAD, CHF, etc.)
  Commodities:  20-25% (10-15 markets: CL, GC, SI, NG, Corn, Soy, etc.)

Risk parity principle:
  Each instrument contributes equal risk (volatility-weighted)
  Each sector contributes roughly equal risk
  Prevents any single market or sector from dominating

Correlation management:
  Trend signals across markets are correlated (all go long in risk-on)
  Monitor portfolio-level correlation
  Consider offsetting correlated positions (reduce NQ if ES already long)
```

### Managing Whipsaws

Whipsaws (false breakouts that reverse quickly) are the primary cost of trend following:

```
Whipsaw mitigation:
1. Confirmation delay: Wait 1-3 days after signal before entering
2. Filter: Only trade in direction of longer-term trend (e.g., only buy if above MA(200))
3. Volatility filter: Avoid entries when ADX < 20 (no trend)
4. Band filter: Require price to move X% beyond MA before triggering
5. Multiple timeframe: Enter only when short, medium, and long trends agree
6. Reduced position on initial entry, add on confirmation

Cost of whipsaw mitigation:
  - Every filter reduces whipsaws BUT also delays valid entries
  - Some of the best trades are rapid moves that filters would miss
  - Diversification across many markets is the best whipsaw mitigation
```

## Templates / Examples

### Trend-Following Strategy Report

```
Strategy: Dual MA Crossover (50/200 EMA) + ATR Position Sizing
Universe: 40 liquid futures (equities, FI, FX, commodities)
Period: 2005-2024

--- Performance ---
Annualized Return:     9.5%
Annualized Volatility: 12.0%
Sharpe Ratio:          0.79
Max Drawdown:          -18.5%
Calmar Ratio:          0.51
Skewness:              +0.35 (positive skew — crisis alpha)
Win Rate (trades):     38% (low win rate, high payoff ratio)
Avg Win / Avg Loss:    2.8x

--- Crisis Performance ---
2008 GFC:              +22% (equities short, bonds long)
2020 COVID March:      -5% (whipsaw, then recovered)
2022 Rate Hikes:       +18% (short bonds, long commodities)

--- Sector Contribution ---
Equities:              2.1% annualized
Fixed Income:          3.2%
FX:                    1.8%
Commodities:           2.4%

--- Cost Analysis ---
Average trades/year:   320 (across all markets)
Estimated slippage:    $850K on $100M
Commission:            $320K
Net Sharpe:            0.62
```

### System Parameter Sensitivity

```
Fast MA | Slow MA | Sharpe | Max DD  | Trades/yr | Win Rate
10      | 50      | 0.55   | -22%    | 580       | 35%
20      | 100     | 0.68   | -20%    | 380       | 37%
50      | 200     | 0.79   | -18%    | 220       | 38%
100     | 300     | 0.72   | -16%    | 150       | 40%

Observation: Slower systems have higher Sharpe and lower drawdown
but fewer trades. The 50/200 combination is a robust sweet spot.
```

## Quality Gate

Before deploying a trend-following strategy:

- [ ] Trend signal produces positive skew (more large wins than large losses)
- [ ] System tested across multiple asset classes and time periods
- [ ] ATR or volatility-based position sizing implemented
- [ ] Whipsaw cost is quantified and acceptable
- [ ] Transaction costs (slippage + commission) deducted from performance
- [ ] Portfolio is diversified across 20+ markets and 4+ asset classes
- [ ] Correlation between trend positions monitored at portfolio level
- [ ] Maximum position limits defined per market and per sector
- [ ] Drawdown management plan in place (reduce risk after X% drawdown)
- [ ] System parameters are robust to small perturbations (no cliff effects)
