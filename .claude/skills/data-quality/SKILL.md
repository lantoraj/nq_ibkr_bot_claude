---
name: data-quality
description: "Financial Data Quality. Use when: User is building a backtest and needs to ensure data integrity; Evaluating data for survivorship bias, look-ahead bias, or other distortions; Setting up point-in-time databases for fundamental data."
---

# Financial Data Quality

name: data-quality
description: Financial data quality — survivorship bias, look-ahead bias, point-in-time.
origin: ECT

## When to Activate

- User is building a backtest and needs to ensure data integrity
- Evaluating data for survivorship bias, look-ahead bias, or other distortions
- Setting up point-in-time databases for fundamental data
- Designing data cleaning and validation procedures
- Diagnosing suspicious backtest results that may stem from data issues

## First Questions

1. What data types are being used (price, fundamental, alternative)?
2. Is this for backtesting or live trading (different quality requirements)?
3. What is the source of the data (vendor, scraped, academic dataset)?
4. Has the data been adjusted for corporate actions?
5. Are delisted securities included in the historical universe?

## Core Concepts

### Bias Taxonomy

Financial data has specific biases that can invalidate backtests and lead to false alpha discovery. Understanding and correcting these biases is foundational to quantitative research.

```
Major bias types:

  1. Survivorship bias
  2. Look-ahead bias
  3. Time-period bias
  4. Selection bias
  5. Backfill bias (incubation bias)
  6. Reporting bias
  7. Restatement bias
  8. Timestamp bias
```

### Survivorship Bias

The most common and dangerous bias in financial backtesting.

```
What it is:
  Backtesting on a universe that includes only stocks that survived to today
  Excludes: bankruptcies, delistings, acquisitions, privatizations

Impact:
  - Overestimates returns by 1-3% annually for US equity strategies
  - Worse for small-cap and value strategies (more delistings)
  - S&P 500 backtest using today's constituents: biased
    (today's S&P 500 is the 500 winners; losers were removed along the way)

Example:
  Backtesting a value strategy (buy low P/E stocks) 2000-2020:
  - With survivorship bias: stocks that went to P/E = 2 then went bankrupt are excluded
  - These bankruptcies are exactly the tail risk of value investing
  - Biased backtest Sharpe: 0.8. Unbiased Sharpe: 0.4

Sources of survivorship-free data:
  - CRSP (academic, gold standard for US equities)
  - Compustat with delisting returns
  - Norgate Data (includes delisted securities)
  - Bloomberg with point-in-time index membership
  - Refinitiv DataScope with dead company coverage

Correction:
  - Use point-in-time index/universe membership
  - Include delisted securities with their delisting returns
  - For delistings without final return data, assume -30% to -100%
    depending on delisting reason (acquired vs bankrupt)
```

### Look-Ahead Bias

Using information that was not available at the time the decision would have been made.

```
Common sources:

  1. Fundamental data timing:
     Company reports Q4 earnings on Feb 15
     Data vendor shows Q4 data as of Dec 31 (fiscal year end)
     If backtest uses Q4 data as of Dec 31, it looks 45 days into the future
     Fix: use data as of the announcement date, not fiscal period end

  2. Revised / restated data:
     Initial GDP report: +2.1%
     Revised GDP (3 months later): +1.8%
     If backtest uses revised data on initial release date: look-ahead bias
     Fix: use point-in-time data (data as initially reported)

  3. Index membership:
     S&P 500 added TSLA in December 2020
     Backtest includes TSLA in S&P 500 universe from 2015: look-ahead bias
     Fix: use point-in-time index membership lists

  4. Feature normalization:
     Standardizing features using full-sample mean and std (including future data)
     Fix: use expanding window or rolling window statistics only

  5. Optimal parameter selection:
     Choosing lookback = 12 months because it performed best over full sample
     The "best" parameter was only knowable with future data
     Fix: walk-forward optimization with out-of-sample validation

Impact:
  - Look-ahead bias can inflate Sharpe by 0.5-2.0
  - Often invisible in standard backtest frameworks
  - Single largest source of false alpha in quantitative research
```

### Point-in-Time Databases

```
What they are:
  Databases that store data exactly as it was known on each historical date
  Every data point has two timestamps:
    1. Reference date (what period it describes)
    2. Knowledge date (when it became available to market participants)

Why they matter:
  - Earnings are reported weeks after quarter end
  - Economic data is revised multiple times
  - Analyst estimates change daily
  - Index constituents change periodically

Implementation:

  Table structure:
    | ticker | field      | ref_date   | knowledge_date | value  |
    |--------|------------|------------|----------------|--------|
    | AAPL   | EPS        | 2023-12-31 | 2024-02-01     | 2.18   |
    | AAPL   | EPS        | 2023-12-31 | 2024-04-15     | 2.19   | (restated)

  Query for backtest:
    "What was the latest known EPS for AAPL as of 2024-03-01?"
    Answer: 2.18 (the 2024-02-01 release, not the April restatement)

  Vendors with PIT data:
    Bloomberg (BEST estimates are point-in-time)
    Refinitiv I/B/E/S (PIT estimates)
    Compustat Point-in-Time
    S&P Capital IQ (some PIT fields)
    FactSet (PIT fundamental data)

  DIY point-in-time:
    Start collecting data daily, store with retrieval timestamp
    After 3-5 years, you have your own PIT database
    Costly in storage but invaluable for unbiased backtesting
```

### Other Bias Types

```
Time-period bias:
  Results depend heavily on start/end dates
  2009-2020 backtests: everything looks good (long bull market)
  Include 2008 and 2022: many strategies fail
  Fix: test across multiple market regimes, report by sub-period

Selection bias (data snooping):
  Testing 1000 strategies and reporting the best one
  5% of random strategies will appear significant at 95% confidence
  Fix: Bonferroni correction, control for multiple comparisons
  Harvey, Liu, Zhu (2016): require t-stat > 3.0 for new factors (not 2.0)

Backfill bias:
  Hedge fund databases add funds retroactively
  Fund launched in 2015, added to database in 2018, backfills 2015-2018 track record
  Creates upward bias: only funds with good track records self-report
  Impact: hedge fund index returns overstated by 2-4% annually

Reporting bias:
  Companies choose what to disclose (non-GAAP vs GAAP earnings)
  Non-GAAP consistently higher than GAAP (exclusions are always negative items)
  Fix: use GAAP data or be consistent in metric choice

Restatement bias:
  Financial data is restated months or years later
  Revenue recognition changes, accounting standard changes
  Fix: use as-reported data, not restated, for backtesting
```

### Data Cleaning Procedures

```
Price data cleaning:

  1. Missing data detection:
     - Check for gaps in trading dates (holidays vs actual missing data)
     - Forward-fill for genuine non-trading days (weekend, holiday)
     - Flag and investigate gaps on trading days (data issue)

  2. Outlier detection:
     - Daily return > 50%: verify against other sources (may be stock split)
     - Price drops to near zero: verify (may be delisting)
     - Volume = 0 on trading day: investigate (may be trading halt)

  3. Corporate action verification:
     - After split adjustment: continuous returns should be smooth
     - Dividend adjustment: total return index should be monotonically close to price
     - Check: adjusted_close_{t-1} * (1 + return_t) = adjusted_close_t

  4. Cross-validation:
     - Compare prices across 2+ vendors for same security/date
     - Flag discrepancies > 1% (typically corporate action issues)
     - Resolve manually or use most reliable source

Fundamental data cleaning:

  1. Reasonableness checks:
     - P/E ratio: flag if < 0 (losses), > 100 (extreme), or = 0 (division error)
     - Market cap: flag sudden changes > 50% (may be split or data error)
     - Revenue: flag negative revenue (rare, usually data error)
     - Debt/equity: flag negative equity (possible, but verify)

  2. Currency consistency:
     - Ensure all monetary fields are in same currency
     - Check for currency mismatches in cross-listed securities

  3. Fiscal period alignment:
     - Companies have different fiscal year ends
     - Normalize to calendar quarters for cross-sectional comparison
     - Be careful: fiscal Q4 for Jan FYE is Oct-Dec, not same as Dec FYE
```

### Quality Checks

```
Automated quality checks for production data pipeline:

  Daily checks:
    [ ] Expected number of securities received (vs prior day count)
    [ ] No securities with zero or negative prices
    [ ] Volume plausibility (not zero for liquid securities, not 100x average)
    [ ] Timestamp consistency (data for today, not stale)
    [ ] Corporate actions applied (check against announcement calendar)

  Weekly checks:
    [ ] Cross-vendor price reconciliation (flag discrepancies > 50 bps)
    [ ] New tickers / delisted tickers properly handled
    [ ] Fundamental data updates received for recent filings
    [ ] Universe membership changes applied

  Quarterly checks:
    [ ] Full universe integrity check (all expected securities present)
    [ ] Survivorship bias check (delisted securities retained in history)
    [ ] Point-in-time integrity (fundamental data not backdated)
    [ ] Total return reconciliation against known index returns

  Alert thresholds:
    - Price change > 30% without corporate action: ALERT
    - More than 5% of universe missing data: CRITICAL
    - Vendor feed delayed > 1 hour past expected time: WARNING
    - Cross-vendor discrepancy > 1% for > 10 securities: ALERT
```

## Detailed Methodology

### Backtest Data Validation Checklist

```
Before trusting any backtest result:

  1. Universe construction:
     - Is the universe defined point-in-time? (not today's constituents)
     - Are delisted securities included with delisting returns?
     - Is the universe rebalanced at the correct frequency?

  2. Signal computation:
     - Are fundamentals lagged appropriately (report date, not period end)?
     - Are estimates point-in-time (not latest revised estimate)?
     - Are features normalized using only past data?

  3. Execution assumptions:
     - Are prices used for execution realistic (not close if trading at open)?
     - Are transaction costs applied?
     - Is market impact modeled for illiquid securities?

  4. Statistical validity:
     - Is the sample period long enough (multiple regimes)?
     - Is the strategy tested out-of-sample?
     - Are multiple comparisons controlled for?

  5. Data integrity:
     - Has price data been checked for corporate action errors?
     - Are there suspicious returns on specific dates (data errors)?
     - Has the data been cross-validated against a second source?

Red flags that suggest data issues:
  - Sharpe ratio > 2.0 for a simple long-short equity strategy
  - No significant drawdowns during 2008 or 2020
  - Performance significantly better than published academic results
  - Strategy works only on one specific parameter setting
  - Returns concentrate on a few dates (may be data errors on those dates)
```

## Quality Gate

Before using a dataset for trading or backtesting:

- [ ] Survivorship bias addressed (delisted securities included)
- [ ] Look-ahead bias eliminated (point-in-time data, proper lagging)
- [ ] Corporate actions correctly applied (splits, dividends, mergers verified)
- [ ] Missing data quantified and handling methodology documented
- [ ] Outliers identified and treated (winsorization, verification against second source)
- [ ] Cross-vendor validation performed for critical data fields
- [ ] Time-period tested across multiple regimes (not just one bull market)
- [ ] Point-in-time database used for fundamental and estimate data
- [ ] Automated quality checks running on data pipeline
- [ ] Data quality monitoring alerts configured for production systems
