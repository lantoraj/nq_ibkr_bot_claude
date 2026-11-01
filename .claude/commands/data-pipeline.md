---
description: Design and validate financial data ingestion, cleaning, and transformation pipelines
---

# /data-pipeline

## What This Command Does

Designs a financial data pipeline covering data sourcing, ingestion, cleaning, validation, storage, and transformation for quantitative analysis. The financial-data-scientist agent ensures data quality, handles corporate actions, and builds reliable data infrastructure.

## When to Use

- You need to set up a market data pipeline for backtesting or live trading
- You want to validate an existing data pipeline for quality issues
- You need to integrate alternative data sources (sentiment, satellite, web scraping)
- You want to design a real-time data infrastructure for live trading systems

## How It Works

1. **Requirements gathering** — Defines data types, frequency, history depth, latency requirements, and quality standards.
2. **Source selection** — Evaluates data providers for coverage, quality, cost, and API reliability.
3. **Ingestion design** — Designs the data ingestion pipeline with error handling, retry logic, and monitoring.
4. **Cleaning rules** — Specifies data cleaning procedures for gaps, outliers, corporate actions, and symbol changes.
5. **Validation framework** — Builds automated quality checks (completeness, consistency, timeliness, accuracy).
6. **Storage and access** — Designs the storage schema optimized for analytical queries and backtesting.

## Example Usage

**Input:**
```
/data-pipeline design a US equity market data pipeline for
systematic trading, daily frequency, 20-year history
```

**Output:**
```
## Data Pipeline Design — US Equity Market Data

### Requirements
| Parameter        | Specification                        |
|------------------|--------------------------------------|
| Asset class      | US equities (NYSE, NASDAQ, AMEX)     |
| Universe         | All listed, including delisted        |
| Frequency        | Daily OHLCV + adjustments            |
| History          | 20 years (2006-2026)                 |
| Latency          | T+1 (end of day)                     |
| Update frequency | Daily after market close             |
| Quality standard | Point-in-time, survivorship-bias free|

### Data Sources
| Source          | Data Type              | Cost     | Quality |
|-----------------|------------------------|----------|---------|
| Polygon.io      | Daily OHLCV, splits    | $199/mo  | Good    |
| Alpha Vantage   | Fundamentals, earnings | Free/API | Moderate|
| SEC EDGAR       | Filings, insider trades| Free     | High    |
| FRED             | Macro indicators       | Free     | High    |
| Index providers | Constituent history    | Varies   | High    |

### Pipeline Architecture
```
Source APIs → Ingestion Layer → Raw Storage → Cleaning →
Validated Storage → Feature Engineering → Analytics DB
```

### Ingestion Layer
- Scheduler: Daily at 18:00 ET (30 min after close)
- Retry logic: 3 retries with exponential backoff
- Error handling: Alert on failure, use previous day on 3rd failure
- Rate limiting: Respect API limits, queue requests
- Logging: Full audit trail of all API calls and responses

### Cleaning Rules
| Rule                    | Implementation                      |
|-------------------------|-------------------------------------|
| Split adjustment        | Apply CRSP-style cumulative factor  |
| Dividend adjustment     | Total return adjustment factor      |
| Gap detection           | Flag gaps > 1 day (non-holiday)     |
| Outlier detection       | Flag daily returns > 25% for review |
| Volume validation       | Flag zero-volume days on liquid names|
| Symbol change tracking  | Map ticker changes to permanent ID  |
| Delisting handling      | Include delisting return, mark final|
| IPO handling            | Include from first full trading day |

### Validation Checks (Automated Daily)
| Check              | Threshold        | Action on Fail     |
|--------------------|------------------|--------------------|
| Completeness       | > 99.5% symbols  | Alert + investigate|
| Timeliness         | By 19:00 ET      | Alert + retry      |
| Price continuity   | < 50% gap        | Flag for review    |
| Volume consistency | > 0 for liquid   | Flag for review    |
| Cross-source match | < 1% divergence  | Alert + reconcile  |

### Storage Schema
- Format: Parquet files, partitioned by date
- Primary key: (date, permanent_id)
- Columns: open, high, low, close, volume, adj_factor,
  split_flag, dividend, market_cap, sector, index_membership
- Retention: Full history, append-only with versioning
- Backup: Daily to cloud storage with 30-day retention

### Point-in-Time Considerations
- Index membership: Use historical constituent lists, not current
- Fundamentals: Use filing dates, not period-end dates
- Estimates: Use consensus as-of date, not revision date
- Corporate actions: Apply forward, never backfill adjustments
```

## Related Agents

- **financial-data-scientist** — Primary agent, designs data infrastructure
- **quant-researcher** — Defines data requirements for research
- **backtesting-engineer** — Validates data quality for backtest integrity
- **algo-strategist** — Specifies real-time data needs for live trading
