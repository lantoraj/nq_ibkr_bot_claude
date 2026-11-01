---
name: time-series-analysis
description: "Time Series Analysis. Use when: User needs to model or forecast financial time series (prices, returns, volatility); Testing for stationarity before applying statistical models; Modeling conditional volatility (GARCH family)."
---

# Time Series Analysis

name: time-series-analysis
description: Time series analysis for financial data — ARIMA, GARCH, cointegration, stationarity. Use when modeling financial time series.

## When to Activate

- User needs to model or forecast financial time series (prices, returns, volatility)
- Testing for stationarity before applying statistical models
- Modeling conditional volatility (GARCH family)
- Testing for cointegration between two or more assets
- Diagnosing autocorrelation, seasonality, or structural breaks in data
- Building econometric models for trading signals

## First Questions

1. What is the data frequency (tick, minute, daily, weekly, monthly)?
2. Are you modeling returns, prices, spreads, or volatility?
3. What is the purpose — forecasting, signal generation, risk modeling, or hypothesis testing?
4. How much historical data is available (observations and time span)?
5. Is this univariate (single series) or multivariate (multiple related series)?

## Core Concepts

### Stationarity

Most statistical models require stationarity. Financial prices are non-stationary (unit root); returns are generally stationary.

**Augmented Dickey-Fuller (ADF) test:**
- H0: Unit root exists (non-stationary)
- Reject H0 at p < 0.05 to confirm stationarity
- Choose appropriate lag length (AIC/BIC criteria)
- Include trend/intercept terms based on visual inspection

**KPSS test:**
- H0: Series is stationary (opposite of ADF)
- Use ADF and KPSS together for robustness
- If ADF rejects but KPSS does not: stationary
- If both reject: trend-stationary (difference to remove trend)
- If neither rejects: inconclusive, need more data

**Achieving stationarity:**
- First-differencing: y_t = price_t - price_{t-1} (returns)
- Log-differencing: y_t = ln(price_t / price_{t-1}) (log returns, preferred)
- Seasonal differencing for periodic data
- Fractional differencing for long-memory processes (preserves more information)

### Autocorrelation

- **ACF (Autocorrelation Function):** Correlation between y_t and y_{t-k} at various lags k
- **PACF (Partial ACF):** Direct correlation at lag k, removing intermediate lag effects
- ACF decaying slowly suggests AR process; ACF cutting off suggests MA process
- PACF cutting off at lag p suggests AR(p); ACF cutting off at lag q suggests MA(q)
- Financial returns typically show weak autocorrelation, but squared returns show strong persistence (volatility clustering)

## Detailed Methodology

### ARIMA Modeling

ARIMA(p, d, q): AutoRegressive Integrated Moving Average

```
Step 1: Plot the series. Visual inspection for trends, seasonality, breaks.
Step 2: Test stationarity (ADF, KPSS). Difference if needed (d = 0 or 1).
Step 3: Examine ACF/PACF of stationary series to identify p (AR order) and q (MA order).
Step 4: Fit candidate models. Use AIC/BIC for model selection.
Step 5: Diagnostic checks:
        - Ljung-Box test on residuals (H0: no autocorrelation, want p > 0.05)
        - Normality test on residuals (Jarque-Bera)
        - Plot residual ACF — should be white noise
Step 6: Forecast with confidence intervals.
```

**Practical note:** ARIMA rarely produces profitable trading signals on raw returns due to low signal-to-noise ratio. More useful for modeling spreads, basis, or macro variables.

### GARCH Family for Volatility Modeling

Volatility clustering is the dominant stylized fact of financial returns: large moves follow large moves.

**GARCH(1,1):**
```
sigma_t^2 = omega + alpha * epsilon_{t-1}^2 + beta * sigma_{t-1}^2

alpha: reaction to recent shock (typically 0.05-0.15)
beta: persistence of volatility (typically 0.80-0.95)
alpha + beta < 1: covariance stationarity required
alpha + beta close to 1: high persistence (near-IGARCH)
```

**EGARCH (Exponential GARCH):**
- Models log(sigma^2), so variance is always positive without parameter constraints
- Captures leverage effect: negative returns increase volatility more than positive returns
- Preferred for equity markets where leverage effect is strong

**GJR-GARCH (Glosten-Jagannathan-Runkle):**
- Adds asymmetric term: gamma * I(epsilon < 0) * epsilon^2
- gamma > 0 indicates negative shocks increase volatility more
- Simpler than EGARCH, often sufficient for practical applications

**Model selection guidance:**
- Start with GARCH(1,1) — it captures 90% of volatility dynamics
- Use GJR-GARCH for equity indices (leverage effect)
- Use EGARCH when you need guaranteed positive variance
- Higher-order GARCH(p,q) rarely improves fit meaningfully

### Cointegration

Two non-stationary series are cointegrated if a linear combination is stationary. Critical for pairs trading and spread modeling.

**Engle-Granger two-step method:**
```
Step 1: Regress y1_t = alpha + beta * y2_t + epsilon_t (OLS)
Step 2: Test residuals epsilon_t for stationarity (ADF test)
        Use Engle-Granger critical values (NOT standard ADF critical values)
Step 3: If residuals are stationary, series are cointegrated
Step 4: Beta is the hedge ratio; epsilon_t is the spread
```

**Johansen method (preferred for multiple series):**
- Tests for number of cointegrating vectors simultaneously
- Provides trace statistic and max-eigenvalue statistic
- Returns cointegrating vectors and adjustment speeds
- Handles more than two series naturally
- Use for baskets, sector relationships, term structure

### Structural Breaks

Financial time series often contain regime changes that invalidate models estimated on full samples.

**Chow test:** Tests for a break at a known date. Compare unrestricted model (separate regressions before/after) vs restricted (single regression).

**Bai-Perron test:** Detects multiple unknown break dates. Estimates break locations and confidence intervals. Essential for understanding when relationships change.

**CUSUM test:** Monitors cumulative sum of recursive residuals. Detects gradual structural change.

### Seasonality

- **Intraday:** U-shaped volume/volatility pattern (high at open/close, low midday)
- **Day-of-week:** Monday effect (negative returns), Friday effect
- **Month-of-year:** January effect (small caps), Halloween effect (sell in May)
- **Turn-of-month:** Positive returns in last/first days of month
- Use dummy variables or seasonal differencing to account for these patterns

## Templates / Examples

### Time Series Diagnostic Report

```
Series: [Asset/Spread Name]
Frequency: Daily | Period: 2010-01-01 to 2024-12-31 | N = 3,780

--- Stationarity ---
ADF Statistic:    -2.85 (p = 0.051)    [Borderline]
KPSS Statistic:   0.42 (p = 0.08)      [Borderline]
Action: First-difference (log returns)
Post-diff ADF:    -42.1 (p < 0.001)     [Stationary]

--- Autocorrelation (Returns) ---
Lag 1 ACF:        -0.03 (not significant)
Ljung-Box(10):    p = 0.32 (no serial correlation)

--- Autocorrelation (Squared Returns) ---
Lag 1 ACF:        0.18 (significant)
Ljung-Box(10):    p < 0.001 (volatility clustering present)

--- GARCH(1,1) Fit ---
omega:  0.000003    alpha: 0.08    beta: 0.90
Persistence (a+b): 0.98
Half-life of vol shock: 34 days
AIC: -18,452

--- Residual Diagnostics ---
Ljung-Box(10) on std residuals:    p = 0.45 (adequate)
Jarque-Bera on std residuals:      p < 0.001 (fat tails remain)
Recommendation: Use Student-t innovations for better tail fit
```

### Cointegration Test Template

```
Pair: [Asset A] vs [Asset B]
Period: [Start] to [End]

Engle-Granger:
  Hedge ratio (beta):    1.32
  ADF on residuals:      -3.85 (p = 0.003) [Cointegrated]
  Half-life of spread:   14 days

Johansen (Trace):
  r=0: stat=22.4, cv(5%)=15.5  [Reject: at least 1 cointegrating vector]
  r=1: stat=3.1,  cv(5%)=3.8   [Fail to reject: exactly 1 vector]

Spread stationarity confirmed. Proceed with mean-reversion strategy.
```

## Quality Gate

Before deploying a time series model in production:

- [ ] Stationarity confirmed (or appropriate differencing applied)
- [ ] Model order selected by information criteria (AIC/BIC), not overfitting
- [ ] Residual diagnostics pass: no autocorrelation, homoscedastic (or GARCH captures heteroscedasticity)
- [ ] Out-of-sample forecast evaluation performed (RMSE, MAE, directional accuracy)
- [ ] Structural break analysis confirms model stability over intended period
- [ ] Cointegration tests use correct critical values (Engle-Granger, not standard ADF)
- [ ] GARCH parameters satisfy stationarity condition (alpha + beta < 1)
- [ ] Model re-estimation schedule defined (rolling window vs expanding window)
- [ ] Fat tails addressed (Student-t or skewed-t innovations for GARCH)
- [ ] Economic interpretation of model parameters is documented
