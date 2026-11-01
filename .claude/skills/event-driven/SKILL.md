---
name: event-driven
description: "Event-Driven Trading. Use when: User wants to trade around corporate events (earnings, M&A, spin-offs); Designing a merger arbitrage or event arbitrage strategy; Evaluating index rebalancing trades (additions/deletions)."
---

# Event-Driven Trading

name: event-driven
description: Event-driven trading — earnings, M&A arb, index rebalancing, spin-offs.
origin: ECT

## When to Activate

- User wants to trade around corporate events (earnings, M&A, spin-offs)
- Designing a merger arbitrage or event arbitrage strategy
- Evaluating index rebalancing trades (additions/deletions)
- Analyzing post-earnings announcement drift (PEAD)
- Building an event study framework for backtesting catalysts

## First Questions

1. Which event type (earnings, M&A, index rebalancing, spin-off, restructuring)?
2. What asset class and geography (US equities, European credit, global futures)?
3. Are you trading the pre-event anticipation or post-event drift?
4. What is the target holding period (intraday, days, weeks)?
5. Long-only, long-short, or hedged implementation?

## Core Concepts

### Post-Earnings Announcement Drift (PEAD)

PEAD is the tendency for stock prices to drift in the direction of the earnings surprise for 60-90 days after the announcement. It is one of the most robust anomalies in finance.

- Standardized Unexpected Earnings (SUE): `SUE = (EPS_actual - EPS_forecast) / std(forecast_errors)`
- Academic evidence: Ball and Brown (1968), Bernard and Thomas (1989)
- Drift magnitude: top decile SUE outperforms bottom decile by 4-8% over 60 days
- The anomaly persists because of underreaction to earnings news, analyst forecast stickiness, and investor inattention
- Decay: strongest in first 5 days, continues for 60-90 days at diminishing rate
- Enhanced by combining SUE with revenue surprise, guidance change, and earnings call tone

### Merger Arbitrage

Merger arb involves buying the target and (in stock deals) shorting the acquirer after a deal announcement.

```
Cash deal:
  Spread = (Offer Price - Current Target Price) / Current Target Price
  Annualized = Spread * (365 / Expected Days to Close)

Stock deal:
  Long target shares, short (exchange ratio * acquirer shares)
  Spread = (Exchange Ratio * Acquirer Price - Target Price) / Target Price

Key variables:
  - Completion probability (80-95% for friendly deals, lower for hostile)
  - Time to close (3-12 months typical)
  - Break risk: downside if deal fails (target drops 20-40%)
  - Regulatory risk: antitrust review, CFIUS, sector-specific
  - Financing risk: leveraged buyouts sensitive to credit markets
```

### Deal Completion Probability Estimation

```
Factors increasing completion probability:
  - Definitive agreement signed (vs. letter of intent)
  - Board recommendation (unanimous stronger)
  - Shareholder vote scheduled
  - Regulatory approvals received (HSR, EU Commission)
  - Financing committed (firm commitment letters)
  - Strategic rationale is clear

Factors decreasing completion probability:
  - Hostile bid without board support
  - Antitrust concerns (high HHI, concentrated market)
  - Cross-border regulatory complexity
  - Material adverse change (MAC) clauses triggered
  - Competing bidders (good for target price, bad for spread capture)
  - Financing contingencies in uncertain credit markets
```

### Index Rebalancing Trades

When an index adds or removes a constituent, passive funds must buy or sell. This creates predictable demand imbalances.

```
S&P 500 additions:
  - Announced ~5 trading days before effective date
  - Addition stocks rise 3-7% between announcement and effective date
  - Part of the return reverses over the following 30 days
  - Volume spikes on effective date (index funds rebalance at close)

Strategy:
  - Buy on announcement day, sell on effective date (or day after)
  - Hedge market risk with index futures
  - Expected Sharpe per event: high, but only ~25-30 events/year

Russell reconstitution:
  - Annual in late June, based on market cap rankings
  - Largest rebalancing event globally (~$9T benchmarked)
  - Additions/deletions predictable 2-4 weeks in advance
  - Front-running is competitive; alpha has decayed over time
```

### Spin-Off Investing

Corporate spin-offs create value through several mechanisms:

- Forced selling: index funds sell spin-offs that fall below size thresholds
- Neglect: small spin-offs receive no analyst coverage initially
- Incentive alignment: management of spin-off gets equity-based comp tied to new entity
- Operational focus: separated businesses can optimize independently
- Historical returns: spin-offs outperform the market by 10-15% annualized in first 2 years (Cusatis, Miles, Woolridge 1993)

### Event Study Methodology

```
Standard event study framework:
  1. Define event window: [-T1, +T2] around event date
  2. Define estimation window: [-T3, -T1] for normal return model
  3. Estimate normal returns: market model, Fama-French, or DGTW
  4. Compute abnormal return: AR_t = R_t - E[R_t]
  5. Cumulative abnormal return: CAR = sum(AR_t) over event window
  6. Test significance: t-stat = CAR / (sigma_AR * sqrt(T))

Statistical considerations:
  - Event-induced variance: use Boehmer, Musumeci, Poulsen (1991) test
  - Cross-sectional clustering: adjust standard errors when events cluster in time
  - Thin trading: use trade-to-trade returns for illiquid securities
```

## Detailed Methodology

### Special Situations Universe Screening

```
Daily screening criteria:
  Earnings:
    - Companies reporting within next 5 trading days
    - Filter: historical earnings surprise dispersion > threshold
    - Filter: options implied move vs historical average implied move

  M&A:
    - Announced deals with spread > risk-free rate + minimum premium
    - Filter: deal size, regulatory jurisdiction, financing type
    - Monitor: SEC filings (SC 13D, DEFM14A, HSR filings)

  Index changes:
    - Monitor index provider announcements (S&P, MSCI, FTSE Russell)
    - Predict changes using publicly known methodology and market cap data

  Spin-offs:
    - SEC Form 10 filings (registration of new entity)
    - When-issued trading begins (price discovery opportunity)
    - Filter: spin-off size, sector, management incentive structure
```

### Merger Arb Portfolio Construction

```
Position sizing:
  Kelly fraction: f* = (p * payoff - (1-p) * loss) / payoff
  Where:
    p = completion probability
    payoff = spread if deal closes
    loss = downside if deal breaks

  Practical sizing:
    Half-Kelly or less for single deals
    Maximum 5-8% of portfolio in any single deal
    Diversify across 15-30 concurrent deals

  Hedging:
    Market hedge: short index futures for portfolio beta
    Sector hedge: short sector ETF for sector-specific risk
    Rate hedge: duration-match for rate-sensitive deals
```

### Earnings Drift Strategy

```
Signal construction:
  1. Compute SUE = (EPS_actual - EPS_consensus) / historical_std
  2. Normalize across universe (z-score)
  3. Combine with: revenue surprise, guidance revision, estimate revision breadth
  4. Enter position: close of earnings day or next open
  5. Hold: 5-60 days (shorter for liquid large-cap, longer for small-cap)
  6. Exit: fixed holding period or next earnings cycle

Enhancement signals:
  - Earnings call NLP sentiment (FinBERT or LLM-based)
  - Insider buying/selling post-earnings
  - Short interest changes
  - Options flow (unusual activity)
  - Analyst revision speed (fast revisors vs slow)
```

### Risk Management for Event-Driven

```
Key risks by strategy:
  PEAD:
    - Crowding: many quant funds trade PEAD, alpha has decayed
    - Restatement risk: earnings later revised
    - Sector concentration: earnings cluster by sector

  Merger arb:
    - Deal break: 5-20% of deals fail, causing 20-40% loss on position
    - Correlation: multiple deals break in market stress (2008: 15 deals broke)
    - Liquidity: target stock liquidity dries up if deal is in doubt

  Index rebalancing:
    - Front-running competition: many participants, shrinking alpha
    - Implementation shortfall: large trades move prices

  Spin-offs:
    - Illiquidity: small spin-offs may have limited float
    - Information vacuum: limited financial history for new entity
```

## Quality Gate

Before deploying an event-driven strategy:

- [ ] Event definition is precise and unambiguous (exact timestamp, data source)
- [ ] Look-ahead bias eliminated (use point-in-time announcement dates, not ex-post)
- [ ] Survivorship bias addressed (include delisted targets, failed deals)
- [ ] Transaction costs modeled realistically (earnings drift has high urgency cost)
- [ ] Capacity assessed (event-driven strategies are inherently capacity-constrained)
- [ ] Deal break scenarios stress-tested (2008 scenario: multiple concurrent breaks)
- [ ] Correlation across concurrent positions analyzed (deals correlated in crises)
- [ ] Slippage on event-day entries estimated (earnings releases cause wide spreads)
- [ ] Holding period optimized with out-of-sample validation
- [ ] Regulatory compliance verified (insider trading rules, position disclosure)
