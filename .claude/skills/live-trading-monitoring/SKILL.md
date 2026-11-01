---
name: live-trading-monitoring
description: "Live Trading Monitoring. Use when: User is transitioning a strategy from backtest to live trading; Designing live monitoring dashboards and alerting systems; Building kill switches and automated risk controls."
---

# Live Trading Monitoring

name: live-trading-monitoring
description: Live trading monitoring — drift detection, performance tracking, kill switches.
origin: ECT

## When to Activate

- User is transitioning a strategy from backtest to live trading
- Designing live monitoring dashboards and alerting systems
- Building kill switches and automated risk controls
- Detecting strategy drift (live performance deviating from backtest expectations)
- Setting up daily reconciliation and P&L tracking processes

## First Questions

1. What type of strategy is going live (systematic equity, CTA, options, stat arb)?
2. What is the expected Sharpe, drawdown, and turnover from the backtest?
3. What broker/execution platform is being used?
4. What is the risk budget and maximum acceptable drawdown?
5. Who is responsible for monitoring (automated, manual, or hybrid)?

## Core Concepts

### Live vs Backtest Performance Gap

Every strategy performs differently live than in backtest. Understanding the sources of divergence is critical.

```
Common sources of live-backtest divergence:

  1. Execution slippage:
     - Backtest assumes fill at close/VWAP; live fills at actual market price
     - Market impact: large orders move price against you
     - Timing: signal generated at close, executed next day at open
     - Expected cost: 5-50 bps per trade depending on liquidity

  2. Data differences:
     - Live data feed differs from historical data source
     - Corporate actions applied differently
     - Vendor switches or data corrections in backtest period
     - Missing data handled differently in live vs backtest

  3. Look-ahead bias leakage:
     - Subtle biases not caught in backtest review
     - Features that used future data inadvertently
     - Only becomes apparent when live returns underperform

  4. Regime change:
     - Market regime shifts between backtest period and live trading
     - Correlations change, volatility regime changes, crowding effects
     - Strategy may have been overfit to backtest regime

  5. Operational errors:
     - Position sizing errors, wrong ticker, order entry mistakes
     - API failures, missed signals, stale data
     - Timezone issues, holiday calendar mismatches

Expected divergence benchmarks:
  Good: live Sharpe within 70-80% of backtest Sharpe
  Acceptable: live Sharpe within 50-70% of backtest Sharpe
  Concerning: live Sharpe below 50% of backtest Sharpe
  Action required: live Sharpe negative when backtest was positive
```

### P&L Tracking

```
P&L decomposition framework:

  Gross P&L:
    Total return from positions before costs
    Track daily, weekly, monthly, yearly
    Compare to backtest expected return

  Net P&L:
    Gross P&L - commissions - slippage - financing costs - data costs
    This is the real return; always monitor net, not gross

  Attribution:
    By signal/factor: which signals contributed to P&L?
    By asset/sector: which positions drove returns?
    By time: when did P&L accrue (overnight vs intraday)?
    By trade type: long vs short contribution

Daily P&L tracking:
  Mark-to-market: value all positions at current market prices
  Realized P&L: from closed trades (known)
  Unrealized P&L: from open positions (mark-to-market)
  Total P&L = Realized + Unrealized
  Reconcile: total P&L should match broker statement

Key metrics to track daily:
  - P&L (dollar and percentage)
  - Sharpe ratio (rolling 30-day, 90-day, inception)
  - Max drawdown (inception and trailing 12-month)
  - Gross and net exposure
  - Beta exposure (to market, sectors, factors)
  - Number of positions, turnover
  - Largest single-position P&L (concentration risk)
```

### Drift Detection

Drift detection identifies when a live strategy's behavior deviates significantly from its backtest expectations.

```
Statistical drift detection methods:

  1. Return distribution comparison:
     H0: live returns come from same distribution as backtest returns
     Test: Kolmogorov-Smirnov test or Anderson-Darling test
     Window: rolling 60-90 trading days
     Alert: p-value < 0.05 (distribution has shifted)

  2. Cumulative return deviation:
     Expected cumulative return path (from backtest)
     Actual cumulative return path (live)
     Deviation = actual - expected
     Alert: deviation exceeds 2-sigma band around expected path

  3. Sharpe ratio monitoring:
     Rolling Sharpe (30-day, 90-day, 252-day)
     Backtest expected Sharpe: S_expected
     Alert threshold: rolling Sharpe < S_expected - 2 * SE(S)
     Where SE(S) = sqrt((1 + S^2/2) / T) (standard error of Sharpe)

  4. Factor exposure drift:
     Monitor rolling factor betas (market, value, momentum, etc.)
     Compare to backtest expected exposures
     Alert: any beta deviates by > 2 standard deviations from expected

  5. Turnover drift:
     Expected monthly turnover from backtest
     Alert: actual turnover > 2x expected (signals may be noisy or unstable)
     Alert: actual turnover < 0.5x expected (data or signal pipeline may be broken)

  6. Signal quality monitoring:
     Track IC (information coefficient) of signals in real-time
     Rolling IC should be consistent with backtest IC
     Alert: IC turns negative or drops below IC_expected - 2*SE(IC)

CUSUM (Cumulative Sum) for change detection:
  S_t = max(0, S_{t-1} + (r_t - mu) - k)
  Where mu = expected return, k = allowable slack
  Alert: S_t > threshold h
  Advantage: detects gradual drift, not just sudden breaks
```

### Kill Switch Design

Kill switches are automated rules that halt or reduce trading when predefined conditions are met.

```
Kill switch hierarchy:

  Level 1 — Warning (automated alert, human reviews):
    - Daily P&L loss > 1.5% of NAV
    - Rolling 5-day P&L < -3% of NAV
    - Single position loss > 2% of NAV
    - Signal quality (IC) drops below threshold
    - Data feed staleness > 15 minutes during market hours

  Level 2 — Reduce (automated position reduction):
    - Daily P&L loss > 2.5% of NAV: reduce all positions by 50%
    - Rolling 10-day loss > 5% of NAV: reduce to 25% of target exposure
    - Drawdown from peak > 10%: reduce to 50% of target exposure
    - VIX > 40: reduce gross exposure by 50%
    - Market circuit breaker triggered: flatten all intraday positions

  Level 3 — Halt (automated full stop):
    - Daily P&L loss > 5% of NAV: flatten all positions
    - Drawdown from peak > 15%: halt all new trades, begin orderly unwind
    - System error: unreconciled positions, API failure, pricing error
    - Data integrity: more than 10% of universe with stale or missing data
    - Any position exceeds hard risk limits (concentration, sector, factor)

Implementation:
  - Kill switches must be independent of the trading system
  - Run on separate server/process (survives trading system crash)
  - Pre-market check: verify all systems operational before market open
  - Real-time monitoring: check P&L and risk every 1-5 minutes during market hours
  - Post-market check: full reconciliation after market close
  - Manual override: require two-person authorization to disable kill switch
```

### Alert System

```
Alert design principles:
  - Actionable: every alert should have a defined response procedure
  - Prioritized: not all alerts are equal (P&L breach vs data delay)
  - Non-redundant: avoid alert fatigue from duplicate/noisy alerts
  - Escalating: Level 1 to analyst, Level 2 to PM, Level 3 to CRO

Alert channels:
  - Slack/Teams: for Level 1 warnings (informational)
  - SMS/phone call: for Level 2 and Level 3 (requires immediate action)
  - Email: for daily summaries and non-urgent issues
  - Dashboard: real-time display for continuous monitoring

Key alerts to implement:
  Performance:
    - P&L breach at daily/weekly/monthly thresholds
    - Drawdown breach (trailing and inception)
    - Sharpe deviation from expected (rolling window)

  Risk:
    - Gross/net exposure outside target range
    - Factor exposure drift beyond tolerance
    - Concentration: single position > X% of NAV
    - Leverage approaching limit

  Operations:
    - Order rejection or partial fill
    - Data feed latency or gap
    - Reconciliation break (positions or cash mismatch)
    - System resource issues (memory, disk, connectivity)

  Market:
    - VIX spike above threshold
    - Market circuit breaker triggered
    - Liquidity deterioration (bid-ask widening in key holdings)
```

### Daily Reconciliation

```
End-of-day reconciliation process:

  1. Position reconciliation:
     Internal system positions vs broker statement positions
     Check: every ticker matches, every quantity matches
     Threshold: zero tolerance for position mismatches
     Common causes: missed fills, corporate actions, settlement errors

  2. Cash reconciliation:
     Internal cash balance vs broker cash balance
     Include: settled and unsettled transactions
     Threshold: < $100 difference (rounding, timing)
     Common causes: dividend accruals, interest, fee timing

  3. P&L reconciliation:
     Internal P&L calculation vs broker-reported P&L
     Difference should be < 0.5% of daily P&L
     Common causes: pricing source differences, corporate action timing

  4. Risk metric reconciliation:
     Verify: exposure calculations match risk system
     Verify: margin requirements within limits
     Verify: factor exposures consistent with targets

  5. Data quality check:
     Verify: all signals computed (no NaN or stale values)
     Verify: universe membership up to date
     Verify: corporate actions applied correctly
     Verify: no look-ahead contamination in live signals

Reconciliation workflow:
  T+0 (market close): automated reconciliation runs
  T+0 + 30min: automated report generated with breaks highlighted
  T+0 + 1hr: analyst reviews breaks, resolves or escalates
  T+1 (pre-market): all breaks resolved before trading resumes
  Monthly: full audit trail reviewed by risk management
```

## Detailed Methodology

### Monitoring Dashboard Components

```
Real-time dashboard layout:

  Panel 1 — P&L
    - Intraday P&L curve (ticking, updated every minute)
    - MTD, QTD, YTD, ITD cumulative return
    - P&L by strategy, asset class, sector
    - Comparison to benchmark and backtest expected path

  Panel 2 — Risk
    - Gross and net exposure (current vs target)
    - Factor exposures (beta, sector, style factors)
    - VaR (1-day 99%) and CVaR
    - Largest single-name exposures (top 10)

  Panel 3 — Execution
    - Orders in flight (pending, partial, filled)
    - Slippage vs arrival price
    - Rejected orders and errors
    - Fill rate and execution quality

  Panel 4 — System Health
    - Data feed status (green/yellow/red per source)
    - Signal pipeline status (last run time, success/failure)
    - System resources (CPU, memory, disk, network)
    - API connectivity to broker (latency, error rate)

  Panel 5 — Drift
    - Rolling IC of each signal
    - Rolling Sharpe vs expected Sharpe (with confidence bands)
    - Factor exposure drift chart
    - Turnover: actual vs expected
```

### Paper Trading and Phased Rollout

```
Transition from backtest to live:

  Phase 1 — Paper trading (2-4 weeks):
    Run live signals, generate orders, but do not execute
    Compare paper P&L to backtest expected P&L
    Verify: data pipeline, signal computation, order generation
    Criteria to advance: no system errors, P&L within expected range

  Phase 2 — Scaled live (4-8 weeks):
    Trade at 10-25% of target size
    Measure: actual slippage, fill rates, execution quality
    Compare: live returns vs backtest, track divergence
    Criteria to advance: Sharpe within 50% of backtest, no operational issues

  Phase 3 — Full deployment:
    Ramp to 100% of target size over 2-4 weeks
    Full monitoring and kill switches active
    First 90 days: heightened monitoring (daily PM review)
    After 90 days: standard monitoring if performance is within expectations

  Rollback criteria:
    - Any Phase: system error or data integrity issue = halt, fix, restart phase
    - Phase 2: live Sharpe < 0 for 20+ trading days = return to Phase 1
    - Phase 3: drawdown > 50% of backtest max drawdown = reduce to Phase 2 sizing
```

## Quality Gate

Before going live with a trading strategy:

- [ ] Paper trading completed with no system errors (2+ weeks)
- [ ] Live P&L tracking system verified against broker statements
- [ ] Kill switches tested (simulate each trigger level)
- [ ] Alert system configured and tested (all channels verified)
- [ ] Daily reconciliation process automated and tested
- [ ] Drift detection thresholds calibrated to backtest distribution
- [ ] Data pipeline monitoring in place (staleness, gaps, quality checks)
- [ ] Execution quality measurement operational (slippage, fill rate)
- [ ] Disaster recovery plan documented (system failure, data loss, broker outage)
- [ ] Escalation chain defined (who to call at each alert level, 24/7 coverage)
