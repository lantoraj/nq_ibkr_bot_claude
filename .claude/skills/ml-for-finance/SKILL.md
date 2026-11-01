---
name: ml-for-finance
description: "Machine Learning for Finance. Use when: User wants to apply supervised ML models to predict returns, classify regimes, or rank assets; Designing cross-validation schemes for financial time series; Evaluating feature importance for trading signals."
---

# Machine Learning for Finance

name: ml-for-finance
description: Machine learning for trading — supervised models, feature importance, cross-validation for time series. Use when applying ML to trading problems.

## When to Activate

- User wants to apply supervised ML models to predict returns, classify regimes, or rank assets
- Designing cross-validation schemes for financial time series
- Evaluating feature importance for trading signals
- Building ensemble models from multiple alpha signals
- Diagnosing model overfitting or decay in production ML trading systems

## First Questions

1. What is the prediction target (next-day return, sign, quintile rank, volatility)?
2. What features/signals are available and at what frequency?
3. How large is the training dataset (observations and time span)?
4. Is the goal cross-sectional ranking or time-series forecasting?
5. What are the constraints (latency, interpretability, turnover)?

## Core Concepts

### Why ML is Hard in Finance

Finance presents unique challenges that make naive ML application dangerous:

- **Low signal-to-noise ratio:** Daily return prediction R-squared is typically 0.01-0.02 at best. A "good" model explains 1-2% of variance.
- **Non-stationarity:** Relationships between features and returns change over time. Models trained on 2010-2015 may fail in 2020.
- **Small effective sample size:** Even with 20 years of daily data, you may only have 4-5 independent business cycles.
- **Look-ahead bias:** Extremely easy to leak future information through features, labels, or data processing.
- **Adversarial environment:** Markets adapt to predictable patterns. Profitable signals decay.
- **Transaction costs:** High-turnover ML predictions may be unprofitable after costs.

### The Overfitting Hierarchy

From most to least dangerous:
1. **Data snooping:** Testing many models, reporting only the best
2. **Feature engineering on full dataset:** Computing features using future data
3. **Hyperparameter tuning on test set:** Optimizing parameters to maximize test performance
4. **Information leakage through cross-validation:** Standard k-fold allows future data to inform past predictions
5. **Survivorship bias:** Training only on currently listed securities

## Detailed Methodology

### Tree-Based Models

Tree-based models are the workhorse of ML in finance due to their ability to capture non-linear interactions without explicit specification.

**Random Forest:**
- Ensemble of decorrelated decision trees (bagging + feature subsampling)
- Robust to outliers, handles mixed feature types, no scaling required
- Key parameters: n_estimators (500-1000), max_depth (3-6 for finance), min_samples_leaf (50+)
- Low variance but can still overfit on noisy financial data

**XGBoost / LightGBM:**
- Gradient boosting: sequentially fit trees to residuals
- More powerful than RF but higher overfitting risk
- Key parameters: learning_rate (0.01-0.05), max_depth (3-5), n_estimators (100-500), subsample (0.7-0.8)
- LightGBM is faster for large datasets (histogram-based splitting)
- Early stopping on validation set is essential

**Practical guidance:**
- Start with Random Forest as baseline (less overfit risk)
- Move to XGBoost/LightGBM only if RF shows signal
- Use shallow trees (max_depth 3-5) — deep trees memorize noise
- Large min_samples_leaf (50-200) for regularization

### Feature Importance

Understanding which features drive predictions is critical for trust and debugging.

**Permutation importance:**
- Shuffle each feature and measure performance drop
- Model-agnostic, accounts for feature interactions
- Compute on out-of-sample data to avoid bias
- Slow for many features but most reliable

**SHAP (SHapley Additive exPlanations):**
- Game-theoretic approach to feature attribution
- TreeSHAP is efficient for tree models
- Provides per-prediction explanations (not just global)
- SHAP dependence plots reveal non-linear relationships
- Preferred for production model monitoring

**MDI (Mean Decrease in Impurity):**
- Built into sklearn Random Forest
- Fast but biased toward high-cardinality and correlated features
- Use only as a quick screening tool, not for final importance ranking

### Purged and Embargo Cross-Validation

Standard k-fold CV is invalid for financial time series because:
1. Autocorrelation in features/labels leaks information across folds
2. Overlapping labels (e.g., 5-day forward return) create direct leakage

**Purged k-fold CV (Lopez de Prado):**
```
1. Split data into k time-ordered folds
2. For each fold used as test:
   - Remove (purge) training samples whose labels overlap with test samples
   - Add embargo period after each test fold before allowing training data
   - Embargo length >= label horizon (e.g., if predicting 5-day return, embargo 5+ days)
3. Train on purged training set, evaluate on test fold
4. Average performance across folds
```

**Combinatorial Purged CV (CPCV):**
- Tests all combinations of train/test fold splits
- Produces a distribution of backtest paths, not a single path
- Enables estimation of strategy Sharpe ratio distribution
- More robust but computationally expensive

**Walk-forward validation (expanding or rolling window):**
```
For t = T_start to T_end:
  Train on data [0, t-embargo]
  Predict on data [t, t+step]
  Advance t by step

Pros: Most realistic simulation of live trading
Cons: Early predictions use less training data
Preferred for final production evaluation
```

### Avoiding Look-Ahead Bias

Checklist of common sources:

```
[ ] Features computed using only past data (no future prices, volumes, fundamentals)
[ ] Labels do not overlap between train and test (purged CV)
[ ] Data preprocessing (scaling, imputation) fit ONLY on training data
[ ] Point-in-time data used for fundamentals (not restated data)
[ ] Universe selection does not use future information (no survivorship bias)
[ ] Feature engineering code verified: no accidental .shift(-1) errors
[ ] Target variable properly lagged (predict NEXT period return, not current)
```

### Ensemble Methods

Combining multiple models reduces variance and improves robustness:

- **Bagging:** Train same model on bootstrap samples, average. RF is bagging.
- **Boosting:** Sequentially fit residuals. XGBoost, LightGBM.
- **Stacking:** Train a meta-model on predictions from base models.
- **Simple averaging:** Average predictions from diverse models. Often competitive with stacking and more robust.
- **Rank averaging:** Convert predictions to ranks, average ranks. Non-parametric, robust to scale differences.

### Model Decay Monitoring

ML models in production decay as market conditions change:

```
Monitor weekly/monthly:
- Rolling IC of predictions vs realized returns
- Rolling hit rate (directional accuracy)
- Feature importance stability (top features changing = drift)
- Prediction distribution shift (mean, std of predictions over time)
- Strategy Sharpe on rolling 6-month window

Alert thresholds:
- IC drops below 50% of training IC for 2+ months
- Hit rate drops below 51% for 3+ months
- Feature importance ranking changes by >3 positions for top features

Response:
- Retrain on recent data (expanding or rolling window)
- Re-evaluate feature set (some features may have lost predictive power)
- Check for regime change (model may need regime conditioning)
```

## Templates / Examples

### ML Model Evaluation Report

```
Model: LightGBM Classifier (return sign prediction)
Universe: S&P 500 | Frequency: Daily | Features: 45

Training: 2010-01-01 to 2019-12-31
Validation: 2020-01-01 to 2021-12-31
Test: 2022-01-01 to 2024-12-31

--- Purged CV Results (5-fold, 5-day embargo) ---
AUC:           0.528 +/- 0.008
Accuracy:      52.1% +/- 0.5%
IC (rank):     0.024 +/- 0.012

--- Walk-Forward Test (2022-2024) ---
AUC:           0.521
Accuracy:      51.8%
IC (rank):     0.019
Long-short Sharpe: 0.65 (gross), 0.32 (net of costs)
Turnover: 85% monthly

--- Top Features (SHAP) ---
1. 20-day momentum residual     (importance: 0.15)
2. Earnings revision breadth    (importance: 0.12)
3. 5-day realized vol ratio     (importance: 0.09)
4. Sector-relative RSI          (importance: 0.08)
5. Short interest change        (importance: 0.07)

Verdict: Marginal signal. Net Sharpe < 0.5. Explore feature engineering
or combination with existing alpha before production deployment.
```

### ML Pipeline Checklist

```
[ ] Target variable defined with proper lag (no look-ahead)
[ ] Features use point-in-time data only
[ ] Universe is survivorship-bias-free
[ ] Train/validation/test split respects time ordering
[ ] Purged CV with embargo applied (embargo >= label horizon)
[ ] Multiple model types compared (RF, XGBoost, LightGBM, linear)
[ ] Hyperparameters tuned on validation set only (never on test)
[ ] Feature importance computed on OOS data (SHAP or permutation)
[ ] Transaction costs modeled (turnover * cost deducted from returns)
[ ] Comparison vs simple baselines (linear model, equal-weight signals)
[ ] Model decay monitoring plan established
[ ] Retraining schedule defined
```

## Quality Gate

Before deploying an ML model for live trading:

- [ ] Out-of-sample IC is positive and economically meaningful (> 0.01)
- [ ] Walk-forward Sharpe ratio exceeds hurdle (> 0.5 net of costs)
- [ ] No look-ahead bias (verified by code review and sanity checks)
- [ ] Purged CV performance is consistent across folds (low variance)
- [ ] Feature importance is stable and interpretable
- [ ] Model performance survives transaction cost deduction
- [ ] Comparison with simpler models shows ML adds value
- [ ] Retraining and monitoring infrastructure in place
- [ ] Model behavior under extreme conditions documented (tail analysis)
- [ ] Decay detection alerts configured for production monitoring
