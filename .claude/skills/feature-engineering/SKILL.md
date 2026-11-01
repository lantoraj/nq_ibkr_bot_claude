---
name: feature-engineering
description: "Feature Engineering for Financial ML. Use when: User is building ML models for financial prediction; Constructing features from price, volume, fundamental, or alternative data; Applying cross-sectional standardization or time-series transformations."
---

# Feature Engineering for Financial ML

name: feature-engineering
description: Feature engineering for financial ML — lag features, rolling stats, ranks.
origin: ECT

## When to Activate

- User is building ML models for financial prediction
- Constructing features from price, volume, fundamental, or alternative data
- Applying cross-sectional standardization or time-series transformations
- Performing feature selection to reduce dimensionality and multicollinearity
- Designing feature pipelines that respect temporal constraints (no leakage)

## First Questions

1. What is the prediction target (returns, volatility, direction, factor exposure)?
2. What is the prediction horizon (intraday, daily, weekly, monthly)?
3. What raw data is available (OHLCV, fundamentals, alternative data)?
4. What ML model will consume the features (linear, tree-based, neural network)?
5. What is the universe size and rebalancing frequency?

## Core Concepts

### Financial Feature Types

```
Price-based features:
  Returns: r_t = (P_t / P_{t-1}) - 1 (arithmetic) or ln(P_t / P_{t-1}) (log)
  Momentum: cumulative return over lookback (5d, 21d, 63d, 252d)
  Mean reversion: distance from moving average (P_t / SMA_20 - 1)
  Volatility: rolling standard deviation of returns (21d, 63d)
  Range: (High - Low) / Close (intraday range as vol proxy)
  Gap: (Open_t - Close_{t-1}) / Close_{t-1} (overnight return)

Volume-based features:
  Volume ratio: V_t / SMA(V, 20) (relative volume)
  Volume-price trend: cumulative(sign(r_t) * V_t) (OBV variant)
  Volume-weighted price: VWAP deviation
  Amihud illiquidity: |r_t| / V_t (price impact per unit volume)
  Volume profile: volume distribution across price levels

Fundamental features:
  Valuation: P/E, P/B, EV/EBITDA, FCF yield
  Quality: ROE, ROA, gross margin, debt/equity
  Growth: revenue growth, earnings growth, estimate revisions
  Payout: dividend yield, buyback yield, shareholder yield

Microstructure features:
  Bid-ask spread: (ask - bid) / mid
  Order imbalance: (buy_volume - sell_volume) / total_volume
  Trade size distribution: large vs small trade ratio
  Quote updates: frequency of quote changes (information flow)

Cross-asset features:
  Sector relative: stock return - sector return
  Beta-adjusted: stock return - beta * market return
  Correlation: rolling correlation to market, sector, or factors
  Macro sensitivity: rolling beta to rates, oil, USD
```

### Transformations

```
Stationarity transformations:
  - Use returns, not prices (prices are non-stationary)
  - Log returns for multiplicative processes
  - Differences for integrated series (GDP level -> GDP change)
  - Fractional differencing: preserve memory while achieving stationarity
    (de Prado 2018: minimum d that passes ADF test)

Normalization:
  Z-score: (x - mean) / std (assumes normal distribution)
  Rank: percentile rank within cross-section (robust to outliers)
  Sigmoid: 1 / (1 + exp(-x)) (bounds to [0, 1])
  Winsorization: cap at percentile (e.g., 1st/99th) before normalization

  When to use which:
    Linear models: z-score (features should be on similar scale)
    Tree models: rank or raw (trees are invariant to monotonic transforms)
    Neural networks: z-score or min-max normalization
    Robust: rank normalization (handles fat tails, outliers)

Rolling window features:
  Rolling mean: SMA_n = mean(x_{t-n+1}, ..., x_t)
  Rolling std: vol_n = std(x_{t-n+1}, ..., x_t)
  Rolling skewness: asymmetry of return distribution
  Rolling kurtosis: tail heaviness of return distribution
  Rolling quantile: rolling 5th/95th percentile
  Rolling correlation: between asset and factor over window
  Exponentially weighted: more weight on recent observations (halflife parameter)

  Window length selection:
    Short (5-21 days): captures recent dynamics, noisy
    Medium (63-126 days): quarterly patterns, moderate noise
    Long (252-504 days): annual cycles, smooth but lagged
    Multi-scale: use multiple windows as separate features (let model learn)
```

### Cross-Sectional Standardization

```
Why cross-sectional normalization matters:
  Raw features have different distributions across stocks
  A P/E of 15 is cheap for tech but expensive for utilities
  Cross-sectional normalization makes features comparable

Methods:

  Cross-sectional z-score:
    z_{i,t} = (x_{i,t} - mean_j(x_{j,t})) / std_j(x_{j,t})
    Mean and std computed across all stocks j at time t
    Effect: centers and scales feature within each cross-section

  Sector-neutralized z-score:
    z_{i,t} = (x_{i,t} - mean_{sector}(x_{j,t})) / std_{sector}(x_{j,t})
    Normalize within sector (removes sector-level biases)
    Useful when sector-neutral portfolio is the target

  Cross-sectional rank:
    rank_{i,t} = percentile_rank(x_{i,t}) among all stocks at time t
    Maps to uniform [0, 1] distribution
    Most robust to outliers and non-normality

  Conditional normalization:
    Group by size (large/mid/small) and normalize within group
    Or group by volatility quintile
    Controls for known confounders

Temporal considerations:
  - Always standardize at time t using only data available at time t
  - Never use future cross-sectional statistics (look-ahead bias)
  - Expanding window is safer than rolling window for mean/std estimates
```

### Feature Selection

```
Why feature selection matters:
  - Financial data is low signal-to-noise: most features are noise
  - More features = more overfitting risk (curse of dimensionality)
  - Correlated features inflate model complexity without adding information
  - Simpler models generalize better in non-stationary financial markets

Methods:

  Univariate:
    - Information Coefficient (IC): rank correlation between feature and forward return
    - IC significance: t-stat > 2.0, or ICIR > 0.5 (IC / std(IC))
    - Mutual information: captures non-linear relationships
    - Keep features with |IC| > 0.02 and ICIR > 0.3

  Model-based:
    - Feature importance from Random Forest or Gradient Boosting
    - SHAP values: Shapley additive explanations for feature contribution
    - Permutation importance: drop in performance when feature is shuffled
    - Recursive feature elimination (RFE): iteratively remove least important

  Regularization-based:
    - Lasso (L1): drives coefficients to zero (automatic selection)
    - Elastic net: L1 + L2 (handles correlated features better)
    - Bayesian variable selection: posterior probability of inclusion

  Stability-based:
    - Run feature selection on multiple time periods
    - Keep features that are consistently selected (stable importance)
    - Avoid features that only work in one regime

Feature selection pipeline:
  1. Remove features with >20% missing data
  2. Remove features with near-zero variance
  3. Remove features with |correlation| > 0.90 (keep one from each cluster)
  4. Univariate filter: keep features with ICIR > 0.3
  5. Model-based selection: top 20-50 features by importance
  6. Cross-validate: confirm selection is stable across folds
```

### Multicollinearity

```
Problem:
  Highly correlated features cause instability in linear models
  Coefficients become unreliable, signs can flip
  Not a problem for tree models but still wastes capacity

Detection:
  Correlation matrix: |r| > 0.7 between pairs = concern
  Variance Inflation Factor (VIF): VIF_i = 1 / (1 - R^2_i)
    VIF > 5: moderate multicollinearity
    VIF > 10: severe (consider removing)

  Eigenvalue analysis of feature correlation matrix:
    Condition number > 30: multicollinearity present
    Small eigenvalues indicate near-linear dependencies

Treatment:
  1. Drop one from each highly correlated pair (keep higher IC)
  2. PCA: transform to orthogonal principal components
     Use top k components explaining 90-95% of variance
     Disadvantage: components lose interpretability
  3. Cluster features, then select one representative per cluster
  4. Ridge regression (L2): tolerates multicollinearity by shrinking coefficients
  5. Partial least squares: projects to latent factors that maximize covariance with target
```

## Detailed Methodology

### Feature Engineering Pipeline

```
End-to-end pipeline:

  1. Raw data ingestion:
     - OHLCV, fundamentals, alternative data
     - Point-in-time alignment (no look-ahead)
     - Handle corporate actions (splits, dividends, mergers)

  2. Base feature computation:
     - Price features: returns, momentum, volatility at multiple scales
     - Fundamental features: ratios, growth rates, revisions
     - Alternative: sentiment scores, alternative data signals
     - Time-stamp each feature with computation date

  3. Transformation:
     - Log-transform skewed features (volume, market cap)
     - Winsorize at 1st/99th percentile
     - Compute rolling statistics at multiple windows (5d, 21d, 63d, 252d)

  4. Cross-sectional processing:
     - Rank-normalize within universe at each time step
     - Sector-neutralize if building sector-neutral model
     - Handle missing data: forward-fill (max 5 days), then NaN

  5. Feature selection:
     - Compute IC and ICIR for each feature
     - Remove features with VIF > 10
     - Select top features using stability-based method
     - Target: 20-50 features for most financial ML models

  6. Output:
     - Feature matrix: (N_stocks x T_periods) x K_features
     - Properly aligned with forward return targets
     - Train/validation/test split by time (never random split)
```

### Avoiding Leakage

```
Critical rules for financial feature engineering:

  1. No future information in features:
     - Features at time t use only data available at time t
     - Account for publication lag (earnings reported after market close)
     - Point-in-time fundamentals (use data as-reported, not restated)

  2. No future information in normalization:
     - Cross-sectional z-score at time t uses only time t data (OK)
     - Time-series z-score at time t must use only past data (expanding or rolling window)
     - Never standardize using full-sample statistics

  3. No future information in feature selection:
     - Feature selection must be done within training set only
     - If selecting features on full dataset, selection is biased
     - Nested cross-validation: feature selection inside each fold

  4. No future information in imputation:
     - Forward-fill missing data (not interpolation which uses future)
     - Mean imputation: use rolling mean of past data only

  5. Target alignment:
     - Forward return computed from t+1 open to t+N close (not t close to t+N close)
     - Account for execution delay: if signal is computed at t close,
       earliest execution is t+1 open
```

## Quality Gate

Before using engineered features in a financial ML model:

- [ ] No look-ahead bias: all features use only past and current data
- [ ] Corporate actions handled (splits, dividends, delistings)
- [ ] Missing data treatment documented and temporally valid
- [ ] Cross-sectional normalization applied at each time step independently
- [ ] Multicollinearity checked (VIF < 10, or PCA applied)
- [ ] Feature selection performed within training set only (not on full sample)
- [ ] Multiple time scales included (short, medium, long lookback windows)
- [ ] Feature stability tested across time periods (not just one regime)
- [ ] Outliers handled (winsorization or rank normalization)
- [ ] Feature importance is interpretable and economically sensible
