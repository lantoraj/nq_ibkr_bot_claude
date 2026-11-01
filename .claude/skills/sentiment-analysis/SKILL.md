---
name: sentiment-analysis
description: "Sentiment Analysis for Trading. Use when: User wants to build sentiment-based trading signals from text data; Applying NLP to financial news, earnings calls, or social media; Evaluating FinBERT or other financial language models for alpha generation."
---

# Sentiment Analysis for Trading

name: sentiment-analysis
description: Sentiment analysis for trading — news NLP, social media, earnings calls.
origin: ECT

## When to Activate

- User wants to build sentiment-based trading signals from text data
- Applying NLP to financial news, earnings calls, or social media
- Evaluating FinBERT or other financial language models for alpha generation
- Constructing sentiment indices or contrarian sentiment signals
- Analyzing earnings call tone for forward return prediction

## First Questions

1. What text source (news articles, social media, earnings transcripts, SEC filings)?
2. What is the target signal (directional, event-driven, risk indicator)?
3. What is the asset universe (single stock, sector, index, macro)?
4. What is the signal horizon (intraday, daily, weekly)?
5. Is this a standalone signal or combined with other alpha factors?

## Core Concepts

### NLP for Finance

Natural language processing extracts structured signals from unstructured financial text. Financial text has domain-specific vocabulary, tone, and conventions that require specialized models.

```
Evolution of financial NLP:

  Dictionary-based (2000s):
    - Loughran-McDonald Financial Sentiment Dictionary (2011)
    - 354 negative words, 75 positive words specific to finance
    - "Liability" is negative in finance but neutral in general English
    - Simple: count positive/negative words, compute ratio
    - Limitation: ignores context, negation, sarcasm

  Machine learning (2010s):
    - Naive Bayes, SVM, Random Forest on bag-of-words features
    - TF-IDF features with labeled financial text
    - Better than dictionaries but still context-limited

  Transformer models (2019+):
    - BERT, FinBERT, GPT-based models
    - Pre-trained on general text, fine-tuned on financial corpus
    - Capture context, negation, complex sentence structures
    - State of the art for financial sentiment classification

  LLM-based (2023+):
    - GPT-4, Claude for zero-shot or few-shot sentiment analysis
    - Can handle nuanced analysis without fine-tuning
    - Flexible: extract sentiment, entities, key topics simultaneously
    - Cost: API pricing per token, latency for real-time applications
```

### FinBERT and Financial Language Models

```
FinBERT (Araci 2019 / Huang et al. 2020):
  - BERT model fine-tuned on financial text (news, earnings calls, analyst reports)
  - Three-class output: positive, negative, neutral
  - Accuracy: ~85-90% on financial sentiment benchmarks
  - Captures financial nuance: "revenue declined less than expected" = positive

Usage:
  Input: "The company reported a significant decline in operating margins"
  Output: {negative: 0.89, neutral: 0.08, positive: 0.03}

  Input: "Despite headwinds, management raised full-year guidance"
  Output: {positive: 0.82, neutral: 0.12, negative: 0.06}

Other financial LMs:
  - BloombergGPT: trained on Bloomberg's proprietary financial data
  - FinGPT: open-source financial language model
  - SEC-BERT: fine-tuned on SEC filings
  - ChatGPT/Claude: general LLMs with strong financial comprehension

Signal construction from FinBERT:
  1. Process each news article/headline through FinBERT
  2. Compute sentiment score: S = P(positive) - P(negative)
  3. Aggregate by company: daily sentiment = mean(S) over all articles for company
  4. Normalize: z-score across universe
  5. Signal: buy positive sentiment, sell negative sentiment
  IC: 0.02-0.04 for daily sentiment on US equities
```

### Social Media Sentiment

```
Sources:
  Twitter/X: real-time, high volume, noisy
  Reddit (r/wallstreetbets, r/stocks): retail sentiment, meme stock signals
  StockTwits: dedicated stock discussion, ticker-tagged
  Seeking Alpha: longer-form, semi-professional analysis
  Telegram/Discord: crypto-focused communities

Signal types from social:

  Volume-based:
    - Abnormal mention volume: spike in mentions of a ticker
    - Volume z-score: (mentions_today - mean_30d) / std_30d
    - High volume often precedes large price moves (either direction)

  Sentiment-based:
    - Bullish/bearish ratio of posts mentioning a ticker
    - Weighted by author credibility (follower count, historical accuracy)
    - Combined sentiment: volume * average_sentiment

  Engagement-based:
    - Retweet/like ratios (viral content = extreme sentiment)
    - Comment-to-post ratio (controversy indicator)

  Network-based:
    - Who is posting (smart money accounts vs noise)
    - Information cascade detection (when does a narrative go viral)

Performance:
  Social sentiment alpha: IC 0.01-0.03 (weak but additive)
  Best for: small/mid-cap stocks with retail following
  Horizon: 1-5 days (very short-lived alpha)
  Risk: meme stock episodes (GME Jan 2021) cause extreme outliers
  Limitation: manipulable (bot armies, coordinated pumps)
```

### Earnings Call Tone Analysis

```
Why earnings calls matter:
  - Managers' spoken tone reveals information beyond the numbers
  - Tone in Q&A section is more informative than prepared remarks
  - Deviation from historical tone is more predictive than absolute tone
  - Academic evidence: Mayew and Venkatachalam (2012), Price et al. (2012)

Analysis approaches:

  Text-based (NLP on transcript):
    - Apply FinBERT or dictionary to each sentence
    - Compute: avg sentiment in prepared remarks vs Q&A
    - Q&A tone change: current call vs last 4 calls (deviation signal)
    - Hedging language: "approximately," "potentially," "might" = uncertainty
    - Forward-looking vs backward-looking sentence ratio

  Audio-based (voice analysis):
    - Vocal stress: pitch variation, speaking rate changes
    - Hesitation markers: "um," "uh," pauses before answering
    - Emotion detection: confidence, anxiety, evasion
    - Requires audio processing (not just transcripts)

  Combined signals:
    - Text sentiment + audio stress = stronger predictor
    - Disagreement between what is said (positive) and how it sounds (stressed)
      is a particularly strong negative signal

Signal construction:
  1. Process transcript within hours of call completion
  2. Score: overall tone, Q&A tone, tone change from prior quarter
  3. Combine with earnings surprise (SUE) for enhanced PEAD signal
  4. Holding period: 5-20 days post-call
  IC: 0.03-0.05 for tone change combined with SUE
```

### Sentiment Indices

```
Market-level sentiment indicators:

  AAII Investor Sentiment Survey:
    - Weekly survey of individual investors (bullish/bearish/neutral)
    - Contrarian indicator: extreme bullishness precedes pullbacks
    - Bull-bear spread > 30: historically bearish for forward returns

  Put/Call Ratio:
    - CBOE equity put/call ratio
    - High ratio (>1.0): excessive fear, contrarian bullish
    - Low ratio (<0.5): excessive complacency, contrarian bearish

  CNN Fear & Greed Index:
    - Composite of 7 indicators (momentum, strength, breadth, put/call, junk bonds, vol, safe haven)
    - 0-100 scale: <25 extreme fear, >75 extreme greed

  News Sentiment Index (Federal Reserve):
    - Daily index based on NLP of major financial news articles
    - Aggregated positive/negative economic news
    - Leading indicator of economic activity

Contrarian signal construction:
  1. Compute sentiment indicator (AAII bull-bear, put/call, etc.)
  2. Calculate z-score relative to trailing 52-week distribution
  3. Contrarian: go long when z < -2 (extreme fear), short when z > +2 (extreme greed)
  4. Combine multiple sentiment indicators for robustness
  Historical: contrarian sentiment has IC 0.02-0.04 at monthly horizon
```

## Detailed Methodology

### Building a News Sentiment Pipeline

```
Architecture:

  Data ingestion:
    - News API: RavenPack, Benzinga, NewsAPI, Reuters Machine Readable News
    - Frequency: real-time streaming or batch (every 5-15 minutes)
    - Filter: financial news only, deduplicate (same story from multiple sources)

  NLP processing:
    - Entity extraction: identify which companies are mentioned (NER)
    - Relevance scoring: is the company the subject or just mentioned?
    - Sentiment scoring: FinBERT or LLM-based classification
    - Novelty detection: is this new information or recycled content?

  Signal aggregation:
    - Per company: exponentially weighted sentiment (halflife = 3 days)
    - Cross-sectional: z-score sentiment within sector
    - Event detection: flag extreme sentiment shifts (>3 sigma)

  Alpha integration:
    - Combine with price momentum, earnings estimates, other factors
    - Optimal weight: determined by IC contribution and correlation to existing signals
    - Rebalance: daily for short-horizon sentiment strategies

  Monitoring:
    - Track IC over time (sentiment alpha decays as more funds use NLP)
    - Monitor for data quality issues (missing feeds, entity mapping errors)
    - A/B test: sentiment model A vs model B on live data
```

### Avoiding Sentiment Traps

```
Common pitfalls:

  1. Look-ahead bias in news timestamps:
     - News article published time vs first available time
     - Some APIs backdate articles; use API receipt timestamp

  2. Survivorship in ticker mapping:
     - Delisted companies may not map correctly in historical data
     - Ensure NER handles ticker changes, M&A, spin-offs

  3. Regime dependency:
     - Sentiment alpha works differently in bull vs bear markets
     - Contrarian signals fail during secular trends
     - Adapt: use momentum sentiment in trends, contrarian at extremes

  4. Crowding:
     - As more funds use the same NLP models, alpha decays
     - Differentiate: custom models, unique data sources, proprietary processing
     - Edge comes from speed (real-time), depth (multi-source), or novelty

  5. Manipulation:
     - Social media can be manipulated (bots, coordinated posts)
     - Filter: author credibility scoring, bot detection, anomaly detection
     - Weight by source quality (WSJ headline > random tweet)
```

## Quality Gate

Before deploying a sentiment-based trading strategy:

- [ ] NLP model validated on labeled financial text (accuracy > 80%)
- [ ] Sentiment signal tested out-of-sample with positive IC
- [ ] Look-ahead bias eliminated (use data receipt timestamps, not publication dates)
- [ ] Entity mapping validated (correct company attribution, handle ambiguity)
- [ ] Signal horizon matched to strategy holding period
- [ ] Contrarian vs momentum sentiment regime identified and handled
- [ ] Data quality monitoring in place (missing feeds, model drift, mapping errors)
- [ ] Crowding risk assessed (is this signal widely used by other quant funds?)
- [ ] Transaction costs deducted (sentiment signals often require fast execution)
- [ ] Manipulation risk mitigated (social media bot filtering, source quality weighting)
