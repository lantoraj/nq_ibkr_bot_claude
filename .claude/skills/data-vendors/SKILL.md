---
name: data-vendors
description: "Financial Data Vendors. Use when: User needs to choose a financial data provider for a project; Comparing data vendors by coverage, quality, cost, and API design; Setting up data ingestion pipelines from vendor APIs."
---

# Financial Data Vendors

name: data-vendors
description: Financial data vendors — Bloomberg, Refinitiv, Polygon, Alpha Vantage.
origin: ECT

## When to Activate

- User needs to choose a financial data provider for a project
- Comparing data vendors by coverage, quality, cost, and API design
- Setting up data ingestion pipelines from vendor APIs
- Evaluating data quality differences across providers
- Understanding vendor-specific data formats and conventions

## First Questions

1. What data types are needed (equities, options, futures, FX, fundamentals, alternative)?
2. What is the frequency requirement (tick, minute, daily, quarterly)?
3. What is the budget (free tier, $100/month, $10K/month, enterprise)?
4. What is the technical integration requirement (REST API, WebSocket, FTP, terminal)?
5. What is the geographical coverage requirement (US only, global)?

## Core Concepts

### Vendor Comparison Matrix

```
Vendor          | Coverage    | Frequency  | Cost           | API Quality | Best For
----------------|-------------|------------|----------------|-------------|------------------
Bloomberg       | Global, all | Tick-daily | $24K+/yr term  | Excellent   | Institutional, research
Refinitiv/LSEG  | Global, all | Tick-daily | $15K+/yr       | Good        | Enterprise, FX/rates
Polygon.io      | US equities | Tick-daily | $29-$199/mo    | Excellent   | US equity/options algo
Alpha Vantage   | US+global   | Min-daily  | Free-$50/mo    | Basic       | Learning, prototyping
Yahoo Finance   | Global      | Daily      | Free           | Unofficial  | Screening, basic research
IEX Cloud       | US equities | Daily      | $9-$500/mo     | Good        | US equities, affordable
Nasdaq Data Link| Mixed       | Daily      | Free-$500/mo   | Good        | Quant research, alt data
EODHD           | Global      | Daily      | $20-$80/mo     | Decent      | Global equities on budget
Tiingo          | US equities | Daily-IEX  | Free-$30/mo    | Good        | Hobbyist, basic needs
Databento       | US futures  | Tick       | Usage-based     | Excellent   | Futures algo trading
Norgate         | US+global   | Daily      | $50-$150/mo    | File-based  | Backtesting (survivorship-free)
WRDS            | Academic    | Mixed      | Academic license| Database    | Academic research
```

### Bloomberg Terminal and Data

```
Bloomberg Professional (Terminal):
  - Cost: ~$24,000/year per seat
  - Coverage: most comprehensive — equities, fixed income, commodities, FX, derivatives, economics
  - Unique data: consensus estimates (BEst), credit ratings, corporate actions, supply chain
  - Bloomberg Data License (BDL): enterprise feed for systematic strategies
  - BLPAPI: programmatic access via Python, Java, C++

Key Bloomberg data fields:
  PX_LAST:        Last price
  PX_OPEN/HIGH/LOW/CLOSE: OHLC data
  VOLUME:         Trading volume
  BEST_EPS:       Consensus EPS estimate
  CUR_MKT_CAP:    Market capitalization
  TRAIL_12M_EPS:  Trailing 12-month EPS
  DVD_YIELD:      Dividend yield
  PX_TO_BOOK_RATIO: Price-to-book
  TOT_RETURN_INDEX_GROSS_DVDS: Total return index (includes dividends)

Bloomberg advantages:
  - Point-in-time fundamental data (BEST estimates are timestamped)
  - Corporate action adjustments built in
  - Survivorship-bias-free equity universe histories
  - Global coverage including EM, fixed income, derivatives
  - Reference data: sector classification, index membership history

Bloomberg limitations:
  - Expensive ($24K/seat minimum)
  - Data redistribution restrictions (licensing)
  - API has learning curve (BLPAPI, BQL)
  - Not ideal for high-frequency tick data (use dedicated feeds instead)
```

### Refinitiv / LSEG Data

```
Refinitiv (now part of London Stock Exchange Group):
  - Formerly Thomson Reuters financial data
  - Eikon terminal: ~$15K-22K/year
  - Refinitiv Data Platform: cloud-based API access
  - Tick History: comprehensive tick data archive (decades of history)

Key products:
  Eikon / Workspace: terminal for research and trading
  Refinitiv Data Platform API: REST/WebSocket for programmatic access
  DataScope: bulk data delivery for quantitative research
  Tick History: institutional-grade tick data (25+ years)
  StarMine: quantitative analytics (analyst revision models, intrinsic value)
  I/B/E/S: consensus estimates (industry standard for academic research)

Refinitiv advantages:
  - Strong in FX and fixed income data
  - I/B/E/S estimates are the academic standard
  - Tick History is comprehensive for backtesting microstructure
  - ESG data (one of the largest ESG datasets)
  - Good for global coverage, especially non-US markets

Refinitiv limitations:
  - Pricing complex and opaque
  - API migration from legacy (Eikon) to new platform ongoing
  - Data quality varies by market and asset class
  - Less community/open-source support than Bloomberg
```

### Polygon.io

```
Polygon.io:
  - Focus: US equities, options, forex, crypto
  - Plans: Starter ($29/mo), Developer ($79/mo), Advanced ($199/mo), Enterprise
  - REST API + WebSocket for real-time streaming
  - Historical data: tick-level for equities and options

Key features:
  - Aggregated bars: 1-min to daily OHLCV
  - Tick-level data: individual trades and quotes
  - Options data: all listed US options (quotes, trades, Greeks)
  - Reference data: tickers, exchanges, dividends, splits
  - Flat files: bulk download for backtesting

API patterns:
  REST: /v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}
  WebSocket: wss://socket.polygon.io/stocks (real-time trades, quotes)
  Rate limits: varies by plan (unlimited on Advanced+)

Polygon advantages:
  - Clean REST API with good documentation
  - Affordable tick data (vs $50K+ for institutional tick feeds)
  - Options data included (unusual at this price point)
  - Good for algorithmic trading development
  - Flat file access for bulk historical analysis

Polygon limitations:
  - US-only coverage (no international equities)
  - No fundamental data (no earnings, financial statements)
  - Data quality: occasional gaps, delayed corrections
  - No point-in-time fundamental data
```

### Alpha Vantage

```
Alpha Vantage:
  - Free tier: 25 API calls/day
  - Premium: $50/month for 75 calls/minute
  - Coverage: US + global equities, FX, crypto, economic indicators

Key endpoints:
  TIME_SERIES_DAILY: daily OHLCV
  TIME_SERIES_INTRADAY: 1-min to 60-min bars
  GLOBAL_QUOTE: latest price snapshot
  OVERVIEW: company fundamentals (balance sheet, income statement)
  EARNINGS: quarterly EPS data
  ECONOMIC indicators: GDP, CPI, interest rates

Alpha Vantage advantages:
  - Free tier available (good for learning and prototyping)
  - Simple API with JSON/CSV output
  - Includes basic fundamental data
  - Technical indicators built in (SMA, EMA, RSI, MACD)

Alpha Vantage limitations:
  - Aggressive rate limiting (25 calls/day on free tier)
  - Data quality issues (gaps, delayed corporate action adjustments)
  - No tick data
  - Limited historical depth for some series
  - Not suitable for production systematic trading
```

### Data Types and What to Expect

```
End-of-day (EOD) price data:
  Fields: date, open, high, low, close, volume, adjusted_close
  Adjusted close: accounts for splits and dividends
  Quality range: high (Bloomberg, Norgate) to variable (free sources)
  Key issue: adjustment methodology differs across vendors

Intraday / tick data:
  Fields: timestamp, price, size, exchange, conditions
  Timestamp resolution: microseconds (exchanges) to seconds (aggregators)
  Data volume: ~1-2 GB/day for all US equities (trades only)
  Quality: exchange direct feeds are best; aggregators may miss trades

Fundamental data:
  Fields: financial statement items, ratios, estimates
  Frequency: quarterly (10-Q), annual (10-K), as-reported vs restated
  Key issue: point-in-time availability (when was data first available?)
  Quality: Bloomberg/Refinitiv best; free sources often have look-ahead bias

Reference data:
  Fields: ticker, CUSIP, ISIN, SEDOL, exchange, sector, index membership
  Key issue: identifier changes over time (ticker changes, mergers)
  Critical: index constituent history (for survivorship-free backtesting)

Corporate actions:
  Types: splits, dividends, spin-offs, mergers, ticker changes
  Key issue: adjustment factors must be applied correctly
  Vendor differences: adjustment methodology varies (total return vs price return)
```

## Detailed Methodology

### API Integration Patterns

```
Best practices for data ingestion:

  1. Rate limiting:
     - Respect vendor rate limits (implement exponential backoff)
     - Cache responses locally (don't re-fetch unchanged data)
     - Use bulk/batch endpoints when available

  2. Data storage:
     - Store raw vendor responses (immutable archive)
     - Build processed/clean layer on top
     - Timestamp each data point with retrieval time (point-in-time)

  3. Error handling:
     - Validate response schema (fields present, types correct)
     - Handle partial data (some fields missing)
     - Log and alert on data quality anomalies
     - Retry with exponential backoff on transient errors

  4. Corporate action handling:
     - Subscribe to corporate action feed (or poll daily)
     - Apply adjustments to historical data retroactively
     - Maintain both adjusted and unadjusted price series
     - Test: total return calculation should match vendor's total return index

  5. Multi-vendor reconciliation:
     - Cross-check prices across vendors (flag discrepancies > 1%)
     - Use one vendor as primary, another as validation
     - Especially important for: corporate actions, delisted securities, thin markets
```

### Cost-Effective Data Stack

```
Budget-conscious data architecture:

  Tier 1 — Free/cheap (prototyping and learning):
    Price data: Yahoo Finance (unofficial API), Alpha Vantage free tier
    Fundamentals: SEC EDGAR (XBRL filings), Alpha Vantage
    Economic: FRED (Federal Reserve Economic Data)
    Cost: $0-50/month

  Tier 2 — Serious hobbyist / small fund:
    Price data: Polygon.io ($79-199/month) or Tiingo ($30/month)
    Fundamentals: SimFin, Financial Modeling Prep ($30-100/month)
    Alternative: Nasdaq Data Link free datasets, Google Trends
    Cost: $150-400/month

  Tier 3 — Professional / small hedge fund:
    Price data: Polygon.io Advanced + Norgate for clean historical
    Fundamentals: S&P Capital IQ or FactSet ($5-15K/year)
    Tick data: Databento or Polygon flat files
    Alternative: selected alt data vendor ($50-200K/year)
    Cost: $2-20K/month

  Tier 4 — Institutional:
    Bloomberg Data License or Refinitiv DataScope
    Multiple alt data vendors
    Direct exchange feeds for latency-sensitive
    Cost: $50K+/month
```

## Quality Gate

Before relying on a data vendor for trading:

- [ ] Data quality validated against independent source (cross-vendor check)
- [ ] Corporate action handling tested (splits, dividends, mergers)
- [ ] Point-in-time availability confirmed (no look-ahead bias in fundamentals)
- [ ] Survivorship bias assessed (does vendor include delisted securities?)
- [ ] Coverage sufficient for target universe (check specific tickers, date ranges)
- [ ] API reliability measured (uptime, latency, error rate over trial period)
- [ ] Rate limits compatible with data refresh requirements
- [ ] Data licensing terms reviewed (redistribution, derived data, compliance)
- [ ] Backup data source identified (single vendor dependency is risky)
- [ ] Total cost calculated including engineering time for integration
