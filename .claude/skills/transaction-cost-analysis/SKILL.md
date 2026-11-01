---
name: transaction-cost-analysis
description: "Transaction cost analysis (TCA) — slippage, market impact, benchmarks for measuring execution quality. Use when: User needs to measure and decompose execution costs; Evaluating broker or algorithm performance; Building market impact models (Almgren-Chriss, square-root model)."
---

# Transaction Cost Analysis

> Transaction cost analysis (TCA) — slippage, market impact, benchmarks for measuring execution quality.

## When to Activate

- User needs to measure and decompose execution costs
- Evaluating broker or algorithm performance
- Building market impact models (Almgren-Chriss, square-root model)
- Comparing execution against benchmarks (VWAP, arrival price, close)
- Conducting pre-trade cost estimation for portfolio rebalancing

## Core Concepts

### What TCA Measures

TCA quantifies the total cost of transforming an investment decision into executed trades. This includes everything from the moment a portfolio manager decides to trade until the last share is filled.

### Cost Taxonomy

**Explicit Costs** (directly observable):
- Commissions: $0.001-0.005/share for institutional equity (declining toward zero)
- Exchange fees: $0.0003-0.003/share (varies by venue, maker/taker)
- Stamp duty / FTT: 0.5% UK, 0.1% HK, varies by jurisdiction
- Clearing fees: negligible for equities, meaningful for derivatives

**Implicit Costs** (estimated from market data):
- Bid-ask spread cost: half-spread on average for market orders
- Market impact: permanent price movement caused by the trade
- Timing cost: price drift between decision and execution
- Opportunity cost: cost of not executing (unexecuted portion)

### Implementation Shortfall Decomposition

Perold (1988) defined implementation shortfall as the difference between paper portfolio return and actual portfolio return:

```
IS = Paper Return - Actual Return

Decomposed into:
IS = Delay Cost + Market Impact + Spread Cost + Opportunity Cost + Commissions

Where:
- Delay Cost = price move from decision to order release
- Market Impact = price move from order release to execution (attributable to our trading)
- Spread Cost = half the bid-ask spread at execution
- Opportunity Cost = return on unexecuted shares (for partial fills)
- Commissions = explicit fees
```

## Methodology

### Step 1: Single-Order TCA

```python
import pandas as pd
import numpy as np

def implementation_shortfall(decision_price, arrival_price, exec_price,
                              close_price, exec_qty, order_qty,
                              side, commission_per_share=0.003):
    """
    Full IS decomposition for a single order.

    decision_price: price when PM made the decision
    arrival_price: price when order reached the trading desk
    exec_price: volume-weighted average execution price
    close_price: closing price on the day
    """
    direction = 1 if side == 'BUY' else -1
    fill_rate = exec_qty / order_qty

    # Component costs (in bps of notional)
    delay_cost = direction * (arrival_price - decision_price) / decision_price * 10000
    market_impact = direction * (exec_price - arrival_price) / arrival_price * 10000
    spread_cost = abs(exec_price - arrival_price) / arrival_price * 10000  # approximate
    commissions = commission_per_share / exec_price * 10000

    # Opportunity cost: return on unfilled shares
    if fill_rate < 1:
        opp_cost = (1 - fill_rate) * direction * (close_price - decision_price) / decision_price * 10000
    else:
        opp_cost = 0

    total_is = delay_cost + market_impact + commissions + opp_cost

    return {
        'delay_cost_bps': delay_cost,
        'market_impact_bps': market_impact,
        'commissions_bps': commissions,
        'opportunity_cost_bps': opp_cost,
        'total_is_bps': total_is,
        'fill_rate': fill_rate,
    }
```

### Step 2: Benchmark Comparisons

```python
def benchmark_analysis(executions, market_data):
    """
    Compare execution price against standard benchmarks.
    """
    results = {}

    for order_id, exec in executions.iterrows():
        day_data = market_data.loc[exec['date']]

        # VWAP benchmark
        vwap = day_data['vwap']
        vwap_slippage = exec['side_sign'] * (exec['avg_price'] - vwap) / vwap * 10000

        # Arrival price benchmark
        arrival = exec['arrival_price']
        arrival_slippage = exec['side_sign'] * (exec['avg_price'] - arrival) / arrival * 10000

        # Close benchmark
        close = day_data['close']
        close_slippage = exec['side_sign'] * (exec['avg_price'] - close) / close * 10000

        # Interval VWAP (during execution window only)
        interval_vwap = compute_interval_vwap(
            day_data['trades'], exec['first_fill_time'], exec['last_fill_time']
        )
        interval_slippage = exec['side_sign'] * (exec['avg_price'] - interval_vwap) / interval_vwap * 10000

        results[order_id] = {
            'vs_vwap_bps': vwap_slippage,
            'vs_arrival_bps': arrival_slippage,
            'vs_close_bps': close_slippage,
            'vs_interval_vwap_bps': interval_slippage,
        }

    return pd.DataFrame(results).T
```

### Step 3: Market Impact Models

```python
def square_root_impact_model(order_size, adv, sigma, spread):
    """
    Industry-standard market impact model (Barra, ITG, Kissell):

    Impact = spread/2 + sigma * k * sqrt(order_size / ADV)

    Where k is a calibration constant (typically 0.1-0.3 for equities).
    Square-root law is empirically robust across markets and time periods.
    """
    participation_rate = order_size / adv
    k = 0.15  # calibration constant

    temporary_impact = spread / 2
    permanent_impact = sigma * k * np.sqrt(participation_rate)
    total_impact = temporary_impact + permanent_impact

    return {
        'temporary_impact_bps': temporary_impact * 10000,
        'permanent_impact_bps': permanent_impact * 10000,
        'total_impact_bps': total_impact * 10000,
    }

def almgren_chriss_impact(order_size, adv, sigma, eta, gamma, T, lambda_risk):
    """
    Almgren-Chriss optimal execution cost for given parameters.

    Expected cost = gamma * X^2 / 2 + eta * X * kappa / (2 * tanh(kappa*T/2))
    Where kappa = sqrt(lambda * sigma^2 / eta)
    """
    X = order_size
    kappa = np.sqrt(lambda_risk * sigma**2 / eta)

    permanent_cost = 0.5 * gamma * X**2
    temporary_cost = 0.5 * eta * X * kappa / np.tanh(0.5 * kappa * T)

    expected_cost = permanent_cost + temporary_cost

    return expected_cost

def pre_trade_cost_estimate(orders_df, market_data):
    """
    Estimate execution costs before trading for a portfolio rebalance.
    """
    total_cost = 0
    estimates = []

    for _, order in orders_df.iterrows():
        symbol = order['symbol']
        mkt = market_data.loc[symbol]

        impact = square_root_impact_model(
            order_size=order['shares'],
            adv=mkt['adv_20d'],
            sigma=mkt['daily_vol'],
            spread=mkt['avg_spread_bps'] / 10000
        )

        cost_dollars = impact['total_impact_bps'] / 10000 * order['shares'] * mkt['price']
        estimates.append({
            'symbol': symbol,
            'shares': order['shares'],
            'pct_adv': order['shares'] / mkt['adv_20d'],
            'est_impact_bps': impact['total_impact_bps'],
            'est_cost_dollars': cost_dollars,
        })

    return pd.DataFrame(estimates)
```

### Step 4: Broker Comparison

```python
def broker_scorecard(executions_by_broker, market_data):
    """
    Compare broker execution quality across multiple dimensions.
    """
    scorecards = {}

    for broker, execs in executions_by_broker.groupby('broker'):
        benchmarks = benchmark_analysis(execs, market_data)

        scorecard = {
            'n_orders': len(execs),
            'total_notional': execs['notional'].sum(),
            'avg_is_bps': benchmarks['vs_arrival_bps'].mean(),
            'median_is_bps': benchmarks['vs_arrival_bps'].median(),
            'vs_vwap_bps': benchmarks['vs_vwap_bps'].mean(),
            'fill_rate': execs['fill_rate'].mean(),
            'avg_time_to_fill': execs['time_to_fill'].mean(),
            'pct_price_improvement': (benchmarks['vs_arrival_bps'] < 0).mean(),
        }

        # Breakdown by order difficulty
        for difficulty in ['easy', 'medium', 'hard']:
            mask = execs['difficulty'] == difficulty
            scorecard[f'is_{difficulty}'] = benchmarks.loc[mask, 'vs_arrival_bps'].mean()

        scorecards[broker] = scorecard

    return pd.DataFrame(scorecards).T
```

### Step 5: Portfolio-Level TCA

```python
def portfolio_tca(trades, portfolio_value, benchmark_return):
    """
    Aggregate TCA at the portfolio level.
    """
    total_notional = trades['notional'].sum()
    turnover = total_notional / portfolio_value

    # Weighted average cost
    trades['cost_contribution'] = trades['is_bps'] * trades['notional'] / total_notional
    avg_cost_bps = trades['cost_contribution'].sum()

    # Cost as fraction of alpha
    gross_alpha = (benchmark_return - trades['benchmark_return']).mean()
    cost_as_pct_alpha = avg_cost_bps / (gross_alpha * 10000) if gross_alpha != 0 else float('inf')

    return {
        'turnover': turnover,
        'avg_cost_bps': avg_cost_bps,
        'total_cost_dollars': (avg_cost_bps / 10000) * total_notional,
        'cost_pct_of_alpha': cost_as_pct_alpha,
        'n_trades': len(trades),
    }
```

## Examples

### Interpreting TCA Results

```python
# Order: Buy 200,000 AAPL at $150, ADV = 50M shares
# Decision price: $149.80 (when PM decided)
# Arrival price: $150.00 (when order hit desk — 20 bps delay)
# VWAP execution: $150.25 (avg fill)
# Day VWAP: $150.15
# Close: $150.50

result = implementation_shortfall(
    decision_price=149.80, arrival_price=150.00,
    exec_price=150.25, close_price=150.50,
    exec_qty=200000, order_qty=200000, side='BUY'
)
# Delay cost: ~13 bps (PM decision to desk)
# Market impact: ~17 bps (desk to fill)
# Total IS: ~30 bps + commissions
```

### Cost Estimation for Rebalance

```python
# Planning a portfolio rebalance across 50 names
rebalance_orders = pd.DataFrame({
    'symbol': symbols,
    'shares': shares_to_trade,
    'notional': notional_values,
})

estimates = pre_trade_cost_estimate(rebalance_orders, market_data)
print(f"Estimated total cost: ${estimates['est_cost_dollars'].sum():,.0f}")
print(f"Weighted avg impact: {estimates['est_impact_bps'].mean():.1f} bps")
# Use this to decide: is the expected alpha worth the trading cost?
```

## Quality Gate

- [ ] Benchmark choice appropriate for the trading context (arrival for alpha, VWAP for agency)
- [ ] IS decomposition sums correctly to total shortfall
- [ ] Market impact model calibrated to recent data (parameters drift over time)
- [ ] Pre-trade estimates validated against post-trade actuals
- [ ] Broker comparison controls for order difficulty (size, spread, volatility)
- [ ] Opportunity cost included for partially filled orders
- [ ] Cost analysis includes explicit costs (commissions, fees) — not just implicit impact
- [ ] TCA sample size sufficient for statistical significance (>30 orders per group)
- [ ] Outlier orders investigated individually (extreme slippage may indicate information leakage)
- [ ] Portfolio-level TCA links costs to alpha — are we paying more to trade than we earn?
