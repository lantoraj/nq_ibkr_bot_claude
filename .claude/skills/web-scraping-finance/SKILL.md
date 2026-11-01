---
name: web-scraping-finance
description: "Web Scraping for Financial Data. Use when: User wants to collect financial data from web sources programmatically; Scraping SEC EDGAR filings (10-K, 10-Q, 8-K, 13F, DEF 14A); Building automated pipelines for earnings data or economic calendar events."
---

# Web Scraping for Financial Data

name: web-scraping-finance
description: Web scraping for financial data — SEC filings, earnings, macro releases.
origin: ECT

## When to Activate

- User wants to collect financial data from web sources programmatically
- Scraping SEC EDGAR filings (10-K, 10-Q, 8-K, 13F, DEF 14A)
- Building automated pipelines for earnings data or economic calendar events
- Understanding legal, ethical, and technical considerations for financial scraping
- Setting up rate-limited, respectful data collection systems

## First Questions

1. What data source are you scraping (SEC EDGAR, government sites, financial portals)?
2. What is the target data (filings, earnings, economic releases, prices)?
3. What is the required frequency (real-time, daily batch, quarterly)?
4. Have you checked if an official API or data feed exists?
5. What is the legal/compliance context (personal research, commercial use)?

## Core Concepts

### SEC EDGAR

The SEC's Electronic Data Gathering, Analysis, and Retrieval system is the primary source of US public company filings. It is free, public, and has an official API.

```
EDGAR full-text search and API:
  Base URL: https://efts.sec.gov/LATEST/
  Company search: https://efts.sec.gov/LATEST/search-index?q=COMPANY_NAME
  Filing search: https://efts.sec.gov/LATEST/search-index?q=QUERY&dateRange=custom

EDGAR company filings API:
  https://data.sec.gov/submissions/CIK{cik_number}.json
  Returns: all filings for a company (type, date, accession number)

XBRL data (structured financials):
  https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_number}.json
  Returns: all financial facts in structured JSON
  Fields: revenue, net income, assets, liabilities — tagged by GAAP taxonomy

Key filing types:
  10-K:    Annual report (comprehensive financials, risk factors, MD&A)
  10-Q:    Quarterly report (interim financials)
  8-K:     Current report (material events: earnings, M&A, leadership changes)
  13F:     Institutional holdings (quarterly, 45 days after quarter end)
  DEF 14A: Proxy statement (executive comp, shareholder proposals)
  SC 13D:  Beneficial ownership >5% (activist investors)
  Form 4:  Insider transactions (within 2 business days of trade)
  S-1:     IPO registration statement

EDGAR rate limiting:
  SEC requests max 10 requests/second
  Must include User-Agent header with name and email
  User-Agent: "CompanyName admin@company.com"
  Exceeding rate limits results in IP throttling or blocking

Python access:
  sec-edgar-downloader: pip package for bulk filing download
  edgar: Python library for EDGAR API
  secedgar: another EDGAR access library
  Direct: requests + BeautifulSoup for custom parsing
```

### Earnings Data Collection

```
Sources for earnings data:

  SEC EDGAR (8-K filings):
    - Companies file 8-K with earnings results
    - Item 2.02: "Results of Operations and Financial Condition"
    - Contains press release with EPS, revenue, guidance
    - Timing: filed within 4 business days of earnings release
    - Parsing: extract from HTML/XML, XBRL tags when available

  Earnings calendars:
    - Nasdaq earnings calendar: https://www.nasdaq.com/market-activity/earnings
    - Yahoo Finance earnings calendar
    - Zacks earnings calendar
    - These are scrapeable but check terms of service

  Earnings call transcripts:
    - Seeking Alpha: free transcripts (requires account, limited scraping)
    - The Motley Fool: some free transcripts
    - Refinitiv StreetEvents: institutional (not free)
    - API services: Financial Modeling Prep, Polygon (paid plans)

Building an earnings pipeline:
  1. Maintain earnings calendar (next 2 weeks of reporting companies)
  2. Monitor 8-K filings on EDGAR for earnings releases
  3. Scrape or API-fetch earnings call transcripts within hours of release
  4. Parse: extract EPS, revenue, guidance, key metrics
  5. Compare to consensus estimates (from separate data source)
  6. Generate surprise signal within minutes of release

Challenges:
  - Timing precision: need exact release time (before/after market)
  - Non-GAAP vs GAAP: companies report non-GAAP, consensus may be GAAP
  - Guidance: extracting forward guidance requires NLP
  - Pre-announcements and revisions: must handle mid-quarter updates
```

### Macro and Economic Data

```
Free government sources:

  FRED (Federal Reserve Economic Data):
    URL: https://fred.stlouisfed.org/
    API: https://api.stlouisfed.org/fred/series/observations
    Key: Free API key required (register at FRED website)
    Data: 800,000+ economic time series
    Series examples:
      GDP, UNRATE, CPIAUCSL, FEDFUNDS, T10Y2Y, VIXCLS
    Quality: excellent, well-maintained, long history
    Rate limit: 120 requests/minute

  Bureau of Labor Statistics (BLS):
    API: https://api.bls.gov/publicAPI/v2/timeseries/data/
    Data: employment, CPI, PPI, wages, productivity
    Key: registration recommended (higher rate limits)
    Rate limit: 25 queries per day (unregistered), 500 (registered)

  Bureau of Economic Analysis (BEA):
    API: https://apps.bea.gov/api/data
    Data: GDP, personal income, trade balance, regional data
    Key: free registration required

  Treasury.gov:
    Daily Treasury yield curve rates
    Treasury auction results
    URL: https://home.treasury.gov/resource-center/data-chart-center

  Census Bureau:
    Retail sales, housing starts, trade data
    API: https://api.census.gov/data

Economic calendar pipeline:
  1. Maintain calendar of upcoming releases (BLS, BEA, Census schedules)
  2. Scrape/API-fetch data immediately on release
  3. Parse: extract headline number, revision to prior
  4. Compare to consensus (Bloomberg survey, Econoday)
  5. Generate macro surprise signal
```

### Legal and Ethical Considerations

```
Legal framework:

  Public government data (SEC EDGAR, FRED, BLS):
    - Public domain, no copyright restrictions
    - Free to scrape, store, redistribute
    - Must comply with rate limits and terms of service
    - Include proper User-Agent identification

  Financial portal websites (Yahoo, Google, MarketWatch):
    - Terms of Service typically prohibit automated scraping
    - Data may be licensed from third parties (additional restrictions)
    - Risk: IP blocking, cease-and-desist letters
    - Alternative: use official APIs when available

  Legal precedents:
    - hiQ Labs v. LinkedIn (2022): scraping public data may be permissible
    - But: each case depends on facts, terms of service, and jurisdiction
    - Computer Fraud and Abuse Act (CFAA): unauthorized access is a federal crime
    - GDPR (EU): scraping personal data has additional restrictions

  Best practices:
    - Always check for official API first (prefer API over scraping)
    - Read and respect robots.txt
    - Respect rate limits (even if not technically enforced)
    - Identify yourself in User-Agent header
    - Do not bypass authentication or CAPTCHA
    - Cache responses to minimize redundant requests
    - Consider: would the site operator object to this usage?

  Material Non-Public Information (MNPI):
    - Scraped data that reveals MNPI is a securities law risk
    - Example: scraping a private earnings webcast before public release
    - Consult compliance/legal before using scraped data for trading
    - SEC has pursued cases involving alternative data and MNPI
```

### Rate Limiting and Respectful Scraping

```
Technical best practices:

  Rate limiting:
    - Implement delays between requests (1-2 seconds minimum)
    - Use exponential backoff on errors (429, 503 status codes)
    - Respect Retry-After headers
    - Track rate limits per domain

  Implementation:
    import time
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.headers.update({'User-Agent': 'YourName your@email.com'})

  Caching:
    - Cache all responses locally (sqlite, filesystem, or Redis)
    - Check cache before making network request
    - Set cache TTL appropriate to data freshness needs
    - For EDGAR: filings never change after publishing (cache permanently)

  Robustness:
    - Handle network errors gracefully (timeout, connection refused)
    - Validate response content (check for error pages, CAPTCHAs)
    - Log all requests and responses for debugging
    - Monitor: alert on unusual error rates or empty responses

  Scheduling:
    - Run scrapers during off-peak hours when possible
    - Stagger requests across multiple sources
    - Use job schedulers (cron, Airflow, Prefect) for reliability
    - Implement idempotent jobs (safe to re-run without duplication)
```

## Detailed Methodology

### EDGAR Parsing Pipeline

```
End-to-end pipeline for SEC filings:

  1. Discover filings:
     - Full-text search: EDGAR EFTS API
     - Company filings: data.sec.gov/submissions/CIK{}.json
     - Real-time feed: EDGAR RSS feeds for new filings

  2. Download filing:
     - Get accession number from search results
     - Download filing index: /Archives/edgar/data/{cik}/{accession}/
     - Identify primary document (10-K, 10-Q HTML or XBRL)

  3. Parse structured data (XBRL):
     - Use company facts API for standardized financial data
     - XBRL tags map to GAAP line items (us-gaap:Revenue, us-gaap:NetIncome)
     - Advantage: structured, consistent, machine-readable

  4. Parse unstructured data (HTML/text):
     - Risk factors section: NLP for risk changes quarter-over-quarter
     - MD&A section: management discussion, forward-looking statements
     - Footnotes: off-balance-sheet items, contingent liabilities
     - Use BeautifulSoup for HTML, regex for section extraction

  5. Store and index:
     - Store raw filings (immutable archive)
     - Extract and store structured facts (financial database)
     - Build search index for full-text queries
     - Maintain point-in-time timestamps (filing date = knowledge date)

  6. Signal generation:
     - Quantitative: financial ratio changes, estimate vs reported
     - Textual: sentiment change in risk factors, MD&A tone shift
     - Filing characteristics: filing delay, amendment frequency, auditor change
```

### 13F Holdings Analysis

```
Tracking institutional holdings:

  Data source: SEC Form 13F (quarterly, 45 days after quarter end)
  URL: data.sec.gov XBRL API or full-text search for 13F-HR

  Analysis:
    - New positions: stocks bought for first time by institution
    - Increased/decreased positions: change in share count
    - Exited positions: stocks completely sold
    - Crowding: how many institutions hold the same stock

  Limitations:
    - 45-day delay (positions may have changed since quarter end)
    - Long positions only (no short positions disclosed)
    - Excludes some asset types (derivatives, private holdings)
    - Minimum reporting threshold ($100M AUM)

  Signal construction:
    - Smart money: track top-performing fund managers' new buys
    - Crowding risk: stocks held by many 13F filers may be crowded
    - Activist accumulation: sudden new 13F position + SC 13D filing
```

## Quality Gate

Before deploying a financial web scraping pipeline:

- [ ] Official API checked first (prefer structured API over HTML scraping)
- [ ] Terms of service reviewed for each data source
- [ ] Rate limits implemented and tested (SEC: max 10 req/sec)
- [ ] User-Agent properly configured with contact information
- [ ] Legal review completed for commercial use of scraped data
- [ ] Error handling and retry logic tested (network failures, format changes)
- [ ] Data validation checks in place (schema validation, completeness checks)
- [ ] Caching layer implemented to minimize redundant requests
- [ ] Monitoring and alerting configured (broken scrapers, data gaps)
- [ ] Point-in-time timestamps recorded for all collected data
