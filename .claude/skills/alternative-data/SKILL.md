---
name: alternative-data
description: "Alternative Data. Use when: User wants to incorporate alternative data into trading strategies; Evaluating alternative data vendors or datasets; Building signals from satellite imagery, credit card data, or web traffic."
---

# Alternative Data

name: alternative-data
description: Alternative data for trading — satellite, credit card, web traffic, app usage.
origin: ECT

## When to Activate

- User wants to incorporate alternative data into trading strategies
- Evaluating alternative data vendors or datasets
- Building signals from satellite imagery, credit card data, or web traffic
- Assessing alpha potential, coverage, and cost of alternative data sources
- Designing an alternative data evaluation framework

## First Questions

1. What is the trading strategy the data will support (earnings prediction, nowcasting, sentiment)?
2. What asset class and universe (US equities, global macro, commodities)?
3. What is the data budget (alt data ranges from free to $500K+/year)?
4. What is the required history depth (backtesting needs years, live needs current)?
5. What is the technical infrastructure for ingesting and processing the data?

## Core Concepts

### Alternative Data Taxonomy

```
Data by source:

  Individuals (exhaust data from human activity):
    - Credit/debit card transactions (consumer spending)
    - App usage and downloads (mobile engagement)
    - Social media posts and sentiment (Twitter/X, Reddit, StockTwits)
    - Web browsing and search trends (Google Trends, clickstream)
    - Geolocation / foot traffic (store visits, mall traffic)
    - Job postings and employee reviews (Glassdoor, LinkedIn)

  Business processes (corporate exhaust):
    - SEC filings (13F, 10-K, 8-K, insider transactions)
    - Patent filings and citations
    - Supply chain data (shipping manifests, bill of lading)
    - Government contracts and procurement data
    - Corporate jet tracking (executive travel patterns)

  Sensors (physical world observation):
    - Satellite imagery (parking lots, oil storage, crop health)
    - IoT sensor data (industrial activity, energy grid)
    - Weather data (agricultural commodities, energy demand)
    - AIS shipping data (tanker tracking, trade flows)
    - Environmental monitoring (emissions, water usage)

  Derived / processed:
    - News NLP sentiment scores
    - Earnings transcript analysis
    - ESG scores from multiple data points
    - Nowcasting models (real-time GDP/inflation estimates)
```

### Satellite Imagery

```
Applications in trading:

  Retail foot traffic:
    Count cars in retailer parking lots (Walmart, Target, Home Depot)
    Correlate with quarterly revenue before earnings announcement
    Providers: Orbital Insight, RS Metrics, SpaceKnow
    Alpha: 2-5 day edge before earnings release
    Limitations: weather, seasonal patterns, small sample (not all stores visible)

  Oil storage:
    Measure floating-roof oil tank levels from satellite shadows
    Estimate crude oil inventory changes in real-time
    Providers: Kayrros, Orbital Insight, Ursa Space
    Alpha: estimate EIA inventory report before release (1-3 day edge)
    Coverage: Cushing OK, major global storage hubs

  Agricultural:
    Normalized Difference Vegetation Index (NDVI) from multispectral imagery
    Estimate crop yields before USDA reports
    Providers: Descartes Labs, Gro Intelligence, Planet Labs
    Alpha: commodity futures positioning ahead of WASDE reports

  Construction and infrastructure:
    Track construction progress on factories, data centers, mines
    Estimate capex execution and project timelines
    Used for: mining companies, real estate, infrastructure REITS

Processing pipeline:
  Raw imagery -> Cloud/shadow removal -> Feature extraction -> Time series
  ML models: CNNs for object detection, change detection algorithms
  Frequency: daily revisit for most commercial providers
  Resolution: 30cm-3m (sufficient for car counting, tank measurement)
```

### Credit Card Data

```
What it provides:
  Aggregated, anonymized consumer spending data by merchant
  Panel-based: sample of cardholders extrapolated to population
  Granularity: daily or weekly, by merchant, category, geography

Key providers:
  Earnest Research (now part of Morningstar)
  Second Measure (now part of Bloomberg)
  Facteus (formerly 1010data)
  Mastercard SpendingPulse
  Bloomberg Second Measure

Signal construction:
  1. Aggregate daily spend by company (e.g., all Starbucks transactions)
  2. Compute YoY growth rate (seasonally adjusted)
  3. Compare to consensus revenue estimate
  4. Generate surprise signal: data_implied_revenue - consensus
  5. Position: long if positive surprise, short if negative

Alpha characteristics:
  - IC: 0.03-0.06 for revenue surprise prediction
  - Horizon: 1-30 days before earnings
  - Coverage: consumer-facing companies (retail, restaurants, ecommerce)
  - Decay: alpha peaks at earnings announcement, decays within 5 days post
  - Limitations: sample bias, panel changes, only captures card spend (not cash, B2B)

Data quality issues:
  - Panel representativeness: does the sample match the population?
  - Merchant mapping: correctly attributing transactions to public companies
  - Seasonal adjustment: holiday patterns, store openings/closings
  - Backfill bias: vendors may revise historical data
```

### App Usage and Download Data

```
What it provides:
  - App downloads (daily installs by app, country, device)
  - Daily/monthly active users (DAU/MAU)
  - Session duration, engagement metrics
  - In-app purchase revenue estimates

Providers:
  Sensor Tower, App Annie (now data.ai), Apptopia, SimilarWeb

Applications:
  Gaming companies: predict DAU trends for EA, Take-Two, Activision
  Social media: track engagement trends for Meta, Snap, Pinterest
  Fintech: measure adoption of Cash App, Robinhood, Coinbase
  Streaming: estimate subscriber growth for Netflix, Spotify, Disney+
  Ride-sharing: track Uber/Lyft usage patterns

Signal construction:
  Download momentum: 30-day change in daily downloads vs prior period
  Engagement trend: DAU/MAU ratio change (stickiness metric)
  Revenue nowcast: in-app purchase estimates vs consensus

Limitations:
  - Panel-based estimates (not census data)
  - iOS data quality declined after App Tracking Transparency (ATT)
  - Android data more available but iOS users spend more
  - Not all revenue comes from app (web, enterprise, hardware)
```

### Evaluation Framework

```
The ALPHA framework for evaluating alternative data:

  A - Alpha potential:
    Does the data predict future returns or fundamental outcomes?
    Test: IC (information coefficient) between data signal and forward returns
    Minimum viable IC: > 0.02 for large-cap equities
    Test on out-of-sample period (data vendor backtest is not sufficient)

  L - Latency:
    How quickly is the data available after the underlying event?
    Real-time: satellite imagery, app data (minutes to hours)
    Delayed: credit card (T+2 to T+7), SEC filings (same day)
    Historical only: some academic datasets (no live feed)

  P - Point-in-time:
    Is the data available as-of each historical date (no backfill)?
    Critical for backtesting: vendor may revise history
    Demand: point-in-time database with timestamps for each data delivery

  H - History:
    How many years of historical data exist?
    Minimum for strategy development: 5+ years (ideally 10+)
    Many alt datasets start in 2015-2018 (limited history)
    Short history = overfitting risk in strategy development

  A - Accessibility:
    API availability, data format, delivery frequency
    Integration effort: days (clean API) vs months (raw unstructured)
    Exclusivity: widely available data has less alpha (already priced in)

Cost considerations:
  Tier 1 (free/cheap): Google Trends, SEC filings, open satellite — $0-$5K/year
  Tier 2 (moderate): news sentiment, basic credit card — $50-200K/year
  Tier 3 (premium): detailed credit card, satellite analytics — $200-500K/year
  Tier 4 (enterprise): exclusive datasets, custom analytics — $500K+/year

  Rule of thumb: alt data cost must be < 10% of expected alpha generation
```

### Vendor Landscape Overview

```
Major alt data aggregators:
  Bloomberg Enterprise Data: broad catalog, integrated with terminal
  Refinitiv DataScope: alternative datasets via API
  Nasdaq Data Link (formerly Quandl): marketplace model, many free datasets
  Eagle Alpha: alt data sourcing and evaluation advisory

Specialized providers by category:
  Sentiment: RavenPack, Alexandria Technology, Refinitiv MarketPsych
  Credit card: Second Measure, Earnest, Facteus
  Satellite: Orbital Insight, SpaceKnow, RS Metrics, Kayrros
  Web/app: SimilarWeb, Sensor Tower, data.ai
  Employment: Revelio Labs, LinkUp, Glassdoor
  Geolocation: SafeGraph, Placer.ai, Advan Research
  Supply chain: Panjiva (S&P Global), ImportGenius
  ESG: MSCI ESG, Sustainalytics, Trucost
```

## Detailed Methodology

### Building an Alt Data Signal

```
Step 1: Data ingestion and cleaning
  - Ingest via API or flat file delivery
  - Handle missing data (interpolation, forward-fill, or exclude)
  - Map to securities (ticker mapping is error-prone — validate carefully)
  - Store with timestamps (point-in-time)

Step 2: Feature construction
  - Compute growth rates (YoY, MoM, WoW)
  - Normalize across companies (z-score within sector)
  - Lag appropriately (account for data delivery delay)
  - Combine with traditional data (earnings estimates, price momentum)

Step 3: Alpha testing
  - Compute IC and ICIR against forward returns (1d, 5d, 20d, 60d)
  - Decile analysis: monotonic return spread across signal deciles?
  - Factor-adjusted alpha: regress on Fama-French + momentum
  - Out-of-sample: split data temporally, never use future data

Step 4: Strategy integration
  - Combine with existing alpha signals (ensemble or linear combination)
  - Weight by IC, ICIR, or Bayesian shrinkage
  - Backtest full strategy with alt data signal included
  - Measure marginal Sharpe improvement from adding alt data
```

## Quality Gate

Before integrating alternative data into a strategy:

- [ ] Alpha tested on true out-of-sample period (not vendor-provided backtest)
- [ ] Point-in-time data delivery confirmed (no look-ahead bias)
- [ ] Coverage is sufficient for the target universe (avoid selection bias)
- [ ] Data quality validated: missing data rate, mapping errors, outliers
- [ ] History is long enough for meaningful statistical testing (5+ years preferred)
- [ ] Cost justified relative to expected alpha improvement
- [ ] Legal and compliance review completed (data sourcing, PII, MNPI concerns)
- [ ] Data delivery reliability assessed (SLA, failover, backup sources)
- [ ] Exclusivity evaluated: is this data widely available? (crowded alpha decays fast)
- [ ] Integration pipeline built and tested (ingestion, cleaning, signal generation, monitoring)
