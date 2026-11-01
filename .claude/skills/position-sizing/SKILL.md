---
name: position-sizing
description: "Kelly criterion, optimal-f, fixed fractional, volatility targeting, risk parity position sizing, and practical implementation. Use when: User designing position sizing rules for a trading strategy; Applying Kelly criterion or fractional Kelly to determine bet size; Volatility-based position sizing for systematic strategies."
---

# Position Sizing Methodologies

> Kelly criterion, optimal-f, fixed fractional, volatility targeting, risk parity position sizing, and practical implementation.

## When to Activate

- User designing position sizing rules for a trading strategy
- Applying Kelly criterion or fractional Kelly to determine bet size
- Volatility-based position sizing for systematic strategies
- Risk budgeting and risk parity allocation across strategies or assets
- Evaluating the tradeoff between position size, expected return, and drawdown risk
- Comparing position sizing methods for a given strategy profile

## Core Concepts

### Kelly Criterion

**Original Kelly (Binary Outcomes)**
- f* = (bp - q) / b, where b = odds, p = probability of win, q = 1-p
- f* = fraction of capital to wager
- Maximizes long-run geometric growth rate (log wealth)
- Example: p = 0.55, b = 1 (even money) -> f* = (1*0.55 - 0.45)/1 = 0.10 (bet 10% of capital)

**Continuous Kelly (Normal Returns)**
- f* = (mu - r_f) / sigma^2, where mu = expected return, sigma = volatility
- For a strategy with 15% expected excess return and 20% vol: f* = 0.15/0.04 = 3.75x leverage
- This is the leverage that maximizes geometric growth
- Equivalent to maximizing E[ln(1 + f*r)] over the return distribution

**Multi-Asset Kelly**
- f* = Sigma^{-1} * mu (vector of optimal fractions = inverse covariance times expected excess returns)
- Equivalent to mean-variance optimization with risk aversion = 1 (maximizing log utility)
- Requires estimation of expected returns and covariance matrix — both noisy

### Practical Problems with Full Kelly

- Full Kelly produces extreme drawdowns: probability of 50% drawdown is approximately 50%
- Parameter estimation error: overestimated mu or underestimated sigma leads to overleveraging
- Non-normal returns: fat tails make full Kelly even more dangerous
- Strategy capacity: full Kelly may imply positions that exceed market liquidity
- Result: essentially no professional trader uses full Kelly

### Fractional Kelly

- Use f = c * f_Kelly where c is typically 0.20 to 0.50 (quarter to half Kelly)
- Half Kelly (c = 0.5): 75% of the growth rate but dramatically lower drawdowns
- Quarter Kelly (c = 0.25): 44% of the growth rate but very stable equity curve
- Fractional Kelly is equivalent to full Kelly with a blended estimate (mixing with zero-return prior)
- Fractional Kelly is more robust to parameter estimation error

### Optimal-f (Ralph Vince)

- Generalization of Kelly for non-binary outcomes
- f* = the fraction that maximizes terminal wealth factor (TWR) over historical trades
- TWR = product of (1 + f * return_i / |worst_loss|) over all trades
- Find f* numerically by testing f from 0 to 1 in small increments
- Related to Kelly but does not assume a distribution — uses empirical trade history
- Danger: optimal-f is computed on in-sample data and may overfit
- Like full Kelly, produces severe drawdowns; use fractional optimal-f in practice

## Methodology

### Fixed Fractional Position Sizing

1. Risk a fixed percentage of capital per trade (e.g., 1-2%)
2. Position size = (risk_per_trade * capital) / (entry - stop_loss)
3. Example: $1M capital, 1% risk, entry $50, stop $48
   - Risk amount = $10,000
   - Position size = $10,000 / $2 = 5,000 shares
4. Automatically sizes down after losses and up after gains (anti-martingale)
5. Prevents ruin: no single trade can lose more than the fixed fraction
6. Simple and widely used in systematic and discretionary trading

### Volatility-Based Position Sizing

**Volatility Targeting**
1. Set target portfolio volatility (e.g., 10% annualized)
2. For each position: weight_i = target_vol / (N * sigma_i) where sigma_i is asset volatility
3. More volatile assets get smaller positions; less volatile get larger
4. Rebalance when realized vol deviates significantly from target
5. Equalizes risk contribution from each position (if uncorrelated)

**ATR-Based Sizing (Turtle Traders)**
1. Compute N = 20-day ATR (Average True Range) for each instrument
2. Dollar volatility = N * point_value
3. Unit size = (1% of equity) / dollar_volatility
4. Each "unit" represents approximately 1% equity risk per day
5. Maximum units per market: 4 (maximum 4% of equity at risk per position)
6. Maximum units per correlated group: 6-8

### Risk Parity Position Sizing

1. Target equal risk contribution from each asset/strategy
2. In the simple (uncorrelated) case: w_i proportional to 1/sigma_i
3. With correlations: solve for w such that w_i * (Sigma * w)_i = RC_target for all i
4. Risk contribution of asset i: RC_i = w_i * (Sigma * w)_i / (w' * Sigma * w)
5. Equal risk contribution: RC_i = 1/N for all i
6. Requires leverage for low-vol assets (bonds) to equalize with high-vol assets (equities)
7. Bridgewater All Weather is the canonical risk parity portfolio

### Risk Budgeting

1. Assign risk budgets to each strategy or asset class (need not be equal)
2. Risk budget = percentage of total portfolio risk attributed to each component
3. Example: equities 40%, fixed income 30%, alternatives 30% of total risk
4. Solve for weights that achieve the target risk allocation
5. Component risk = w_i * marginal_risk_i = w_i * (Sigma * w)_i / sigma_portfolio
6. Iterate or use optimization to find weights matching target risk budgets

### Kelly with Parameter Uncertainty

**Bayesian Kelly**
1. Instead of point estimates of mu and sigma, use posterior distributions
2. Optimal bet size accounts for parameter uncertainty
3. Results in smaller positions than plug-in Kelly — natural shrinkage
4. With diffuse priors, Bayesian Kelly approximately equals 0.5 * plug-in Kelly

**Shrinkage Approaches**
1. Shrink expected return estimates toward zero (or grand mean)
2. Shrink covariance toward structured estimator (Ledoit-Wolf)
3. Effective position size decreases as uncertainty increases
4. More robust to estimation error than naive Kelly

## Examples

### Kelly Criterion for a Trading Strategy
```
Strategy backtest: annual excess return = 12%, annual volatility = 18%
Full Kelly: f* = 0.12 / 0.18^2 = 3.7x leverage
Expected growth rate at full Kelly: mu - 0.5*sigma^2*f = 12% - 0.5*3.24%*3.7 = 6%
Expected max drawdown at full Kelly: approximately 50%+

Half Kelly: f = 1.85x leverage
Expected growth rate: approximately 4.5%
Expected max drawdown: approximately 25%

Quarter Kelly: f = 0.93x leverage (no leverage needed)
Expected growth rate: approximately 3%
Expected max drawdown: approximately 12%

Recommendation: half Kelly (1.85x) if drawdown tolerance is 25%;
quarter Kelly (0.93x) if more conservative.
```

### ATR-Based Position Sizing
```
Account equity: $500,000
Risk per unit: 1% = $5,000

Crude oil (CL): ATR(20) = $2.50, point value = $1,000/point
  Dollar vol = $2.50 * $1,000 = $2,500
  Unit size = $5,000 / $2,500 = 2 contracts

E-mini S&P (ES): ATR(20) = 45 points, point value = $50/point
  Dollar vol = 45 * $50 = $2,250
  Unit size = $5,000 / $2,250 = 2 contracts (round down)

Gold (GC): ATR(20) = $25, point value = $100/point
  Dollar vol = $25 * $100 = $2,500
  Unit size = $5,000 / $2,500 = 2 contracts

Each position risks approximately $5,000 (1% of equity) per ATR move.
Maximum 4 units per market = 4% equity risk per market.
```

### Risk Parity Allocation
```
Three-asset portfolio: Equities (vol=16%), Bonds (vol=5%), Commodities (vol=20%)
Assuming zero correlations (simplification):

Equal risk contribution target: 33.3% each
w_equity proportional to 1/16 = 0.0625
w_bonds proportional to 1/5 = 0.2000
w_commod proportional to 1/20 = 0.0500

Normalized: w_equity = 20%, w_bonds = 63%, w_commod = 16%
Sum = 99% (approximately 1x leverage)

To target 10% portfolio vol:
Unlevered portfolio vol = sqrt(0.20^2*16^2 + 0.63^2*5^2 + 0.16^2*20^2) = 5.4%
Leverage = 10% / 5.4% = 1.85x
Levered weights: equities 37%, bonds 117%, commodities 30%
```

## Quality Gate

- Kelly fraction must be computed with realistic (after-cost, after-slippage) return estimates
- Never use full Kelly in practice — maximum recommended is half Kelly for well-estimated strategies
- Parameter uncertainty must be accounted for: use Bayesian Kelly or fractional Kelly
- Position sizes must respect market liquidity constraints (max % of ADV)
- Volatility estimates for sizing must use appropriate lookback (20-60 day realized vol or EWMA)
- Risk parity weights must be rebalanced when volatility or correlation estimates change materially
- Total portfolio leverage must be within acceptable bounds regardless of what Kelly implies
- Sizing rules must be backtested with transaction costs and slippage included
- Maximum position size limits must exist as a hard constraint independent of the sizing formula
- Document the sizing methodology and parameters; review quarterly
