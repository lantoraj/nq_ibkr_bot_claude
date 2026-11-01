---
description: Detect and classify the current market regime for strategy selection
---

# /market-regime

## What This Command Does

Classifies the current market regime using statistical methods (hidden Markov models, change-point detection, volatility clustering) to determine whether markets are trending, mean-reverting, or in a high-volatility crisis state. The quant-researcher agent leads with quantitative regime detection.

## When to Use

- You want to know if current market conditions favor trend-following or mean-reversion strategies
- You need to detect regime changes before they impact portfolio performance
- You want to adjust strategy parameters or allocations based on the current regime
- You are building a regime-aware trading system that switches strategies

## How It Works

1. **Feature extraction** — Computes regime-relevant features: realized vol, vol-of-vol, trend strength, correlation structure, dispersion, and market breadth.
2. **Regime classification** — Applies hidden Markov model or threshold-based classifier to identify the current regime.
3. **Historical context** — Shows how current regime compares to historical periods and typical regime durations.
4. **Transition probabilities** — Estimates probability of transitioning to other regimes.
5. **Strategy implications** — Maps regime to expected strategy performance and recommended adjustments.
6. **Monitoring triggers** — Sets alerts for regime change indicators.

## Example Usage

**Input:**
```
/market-regime US equity market, classify current regime
and recommend strategy adjustments
```

**Output:**
```
## Market Regime Detection — US Equities

### Current Regime: TRENDING (Bullish, Low Volatility)
Confidence: 78% | Duration: 4.2 months | Typical duration: 3-8 months

### Regime Indicators
| Indicator              | Current | Signal            |
|------------------------|---------|-------------------|
| SPX 200d trend         | +14.2%  | Strong uptrend    |
| Realized vol (20d)     | 12.4%   | Below median      |
| VIX level              | 14.8    | Low               |
| VIX term structure     | Contango| Complacent        |
| Advance-decline line   | Rising  | Broad participation|
| Cross-asset correlation| 0.28    | Low (healthy)     |
| Dispersion (stock)     | 18%     | Above average     |
| Credit spreads         | 320bps  | Tight             |
| Put-call ratio         | 0.72    | Slightly bullish  |

### Regime Probabilities (HMM, 3-State)
| Regime              | Probability | Historical Avg Duration |
|---------------------|-------------|------------------------|
| Trending (current)  | 78%         | 5.4 months             |
| Mean-Reverting      | 15%         | 3.1 months             |
| Crisis/High-Vol     | 7%          | 1.8 months             |

### Transition Probabilities (Next Month)
| From Trending To    | Probability |
|---------------------|-------------|
| Stay Trending       | 72%         |
| Mean-Reverting      | 22%         |
| Crisis              | 6%          |

### Historical Regime Comparison
Current period most similar to:
1. Oct 2016 - Jan 2018 (similarity: 0.84) — low vol melt-up
2. Apr 2013 - Dec 2014 (similarity: 0.79) — steady trend
3. Mar 2024 - Aug 2024 (similarity: 0.76) — AI-driven rally

### Strategy Implications
| Strategy Type        | Expected Performance | Recommendation    |
|---------------------|---------------------|-------------------|
| Trend-following     | Strong              | Full allocation   |
| Momentum            | Strong              | Full allocation   |
| Mean-reversion      | Weak                | Reduce allocation |
| Short volatility    | Good (but fragile)  | Moderate size     |
| Pairs trading       | Below average       | Selective only    |
| Tail risk hedging   | Cheap (buy now)     | Add protection    |

### Early Warning Signals (Monitor Daily)
- VIX above 20 for 3 consecutive days
- SPX breaks below 50-day moving average
- Credit spreads widen > 50bps in a week
- Cross-asset correlation spikes above 0.50
- Advance-decline line diverges from price
```

## Related Agents

- **quant-researcher** — Primary agent, runs regime detection models
- **algo-strategist** — Adjusts strategy parameters for detected regime
- **risk-manager** — Monitors regime-related risk and sets hedging triggers
- **volatility-trader** — Provides vol regime context and vol surface signals
