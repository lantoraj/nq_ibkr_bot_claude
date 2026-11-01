---
name: signal-processing
description: "Signal Processing. Use when: User wants to decompose price series into trend, cycle, and noise components; Detecting dominant cycles or periodicities in financial data; Denoising financial signals while preserving important features."
---

# Signal Processing

name: signal-processing
description: Signal processing for financial data — wavelets, Fourier analysis, noise filtering. Use when extracting signals from noisy financial data.

## When to Activate

- User wants to decompose price series into trend, cycle, and noise components
- Detecting dominant cycles or periodicities in financial data
- Denoising financial signals while preserving important features
- Extracting multi-scale information (short-term noise vs long-term trend)
- Filtering price data for cleaner technical indicators
- Analyzing frequency-domain properties of returns

## First Questions

1. What are you trying to extract — trend, cycles, or high-frequency structure?
2. What is the data frequency and length of the series?
3. Is real-time (causal) filtering required, or can you use the full dataset?
4. How much phase lag is acceptable in your filtered signal?
5. Will the output be used for signal generation, risk modeling, or visualization?

## Core Concepts

### Signal vs Noise in Finance

Financial data is dominated by noise. At daily frequency, the signal-to-noise ratio of equity returns is approximately 0.05 (annualized mean / annualized std). The challenge is extracting actionable structure without overfitting to noise.

**Key principle:** Every filter involves a tradeoff between smoothness (noise reduction) and responsiveness (lag). There is no lag-free noise reduction — any claim otherwise violates causality.

### Frequency Domain Basics

Any time series can be decomposed into sinusoidal components at different frequencies:

- **Low frequency:** Long-term trends, business cycles (months to years)
- **Medium frequency:** Intermediate swings, sector rotations (weeks to months)
- **High frequency:** Daily noise, microstructure effects (hours to days)

Financial returns are approximately white noise (flat spectrum), but squared returns and volatility show strong low-frequency power (persistence).

## Detailed Methodology

### Fourier Transform for Cycle Detection

The Discrete Fourier Transform (DFT) decomposes a time series into frequency components:

```
X(f) = sum_{t=0}^{N-1} x(t) * exp(-2*pi*i*f*t/N)

Power spectrum: P(f) = |X(f)|^2

Interpretation:
- Peaks in P(f) indicate dominant cycles
- Frequency f corresponds to period T = N/f (in data units)
- For daily data: f=1 ~ 1-day cycle, f=21 ~ monthly cycle, f=252 ~ annual cycle

Practical issues:
- Spectral leakage: Apply window function (Hann, Hamming) before DFT
- Non-stationarity: Financial series change character over time — use short-window STFT
- Spurious cycles: Statistical test required (Fisher's test for periodicity)
```

**Short-Time Fourier Transform (STFT):**
- Apply DFT to sliding windows of the data
- Produces a spectrogram: time x frequency power map
- Reveals when cycles appear and disappear
- Window size trades time resolution vs frequency resolution

### Wavelet Decomposition

Wavelets decompose a signal into components at multiple scales simultaneously, with both time and frequency localization — superior to Fourier for non-stationary data.

```
Multi-Resolution Analysis (MRA):
  x(t) = A_J(t) + D_J(t) + D_{J-1}(t) + ... + D_1(t)

  A_J: approximation at scale J (smoothest trend)
  D_j: detail at scale j (oscillations at that scale)

For daily financial data with Daubechies-4 wavelet:
  D1: 2-4 day oscillations (noise)
  D2: 4-8 day oscillations (short-term)
  D3: 8-16 day oscillations (swing trading)
  D4: 16-32 day oscillations (monthly cycle)
  D5: 32-64 day oscillations (quarterly cycle)
  A5: trend component (> 64 days)

Wavelet choice:
  Haar: Simplest, step-function. Good for detecting jumps.
  Daubechies (db4-db8): Smooth, compact support. General purpose.
  Symlets: Near-symmetric Daubechies. Reduced phase distortion.
  Coiflets: Zero moments. Good for approximation.
```

**Wavelet denoising procedure:**
```
1. Decompose signal using DWT to level J
2. Apply thresholding to detail coefficients D1...DJ
   - Hard threshold: set |D_j| < lambda to zero
   - Soft threshold: shrink |D_j| by lambda toward zero (smoother)
3. Threshold selection:
   - Universal: lambda = sigma * sqrt(2 * log(N))
   - SURE (Stein Unbiased Risk Estimate): data-adaptive
   - Level-dependent: different lambda for each scale
4. Reconstruct signal from thresholded coefficients
```

### Empirical Mode Decomposition (EMD)

Data-adaptive decomposition that does not require pre-specified basis functions:

```
EMD decomposes x(t) into Intrinsic Mode Functions (IMFs):
  x(t) = sum(IMF_k(t)) + residual(t)

Sifting process:
1. Find local maxima and minima of x(t)
2. Fit upper envelope (through maxima) and lower envelope (through minima)
3. Compute mean of envelopes: m(t)
4. IMF candidate: h(t) = x(t) - m(t)
5. Repeat until h(t) satisfies IMF conditions
6. Subtract IMF from signal, repeat for next IMF

Advantages:
- Fully data-adaptive, no basis function choice
- Handles non-linear, non-stationary data naturally
- IMFs have physical meaning (instantaneous frequency)

Disadvantages:
- Mode mixing: different scales can leak into same IMF
- No mathematical framework (empirical method)
- Ensemble EMD (EEMD) reduces mode mixing but is slower
```

### Hodrick-Prescott Filter

Widely used in macroeconomics, applicable to financial trend extraction:

```
Minimize: sum(y_t - tau_t)^2 + lambda * sum((tau_{t+1} - 2*tau_t + tau_{t-1})^2)

tau_t: trend component
lambda: smoothing parameter
  lambda = 1600 for quarterly macro data (convention)
  lambda = 129600 for monthly data
  lambda = 6.25 for annual data
  For daily financial data: lambda = 10^6 to 10^8

Tradeoff: larger lambda = smoother trend (more lag)
```

**Criticism:** HP filter can produce spurious cycles at the boundary and generates artificial dynamics in random walk data. Use with awareness of these limitations.

### Practical Denoising Techniques

**Moving average variants:**
- SMA: Equal weight. Simple but introduces lag = (N-1)/2 periods.
- EMA: Exponential weight. Less lag. alpha = 2/(N+1).
- Hull MA: Reduced lag using WMA of WMA. HMA = WMA(2*WMA(N/2) - WMA(N), sqrt(N)).
- KAMA (Kaufman Adaptive): Adapts smoothing to signal-to-noise ratio.

**Savitzky-Golay filter:**
- Fits polynomial of degree d to a window of width w via least squares
- Preserves peaks and valleys better than moving averages
- Zero phase when applied non-causally (for analysis)
- Can compute smoothed derivatives (useful for momentum)

**Butterworth filter:**
- Maximally flat frequency response in the passband
- Configurable order (higher order = sharper cutoff but more ringing)
- Available as low-pass, high-pass, band-pass
- Apply with filtfilt (zero-phase) for analysis or lfilter (causal) for trading

## Templates / Examples

### Multi-Scale Analysis Report

```
Asset: [Name] | Frequency: Daily | Period: [Start]-[End]

Wavelet Decomposition (db4, 6 levels):
Scale     | Period Range | Variance Share | Dominant Feature
D1        | 2-4 days     | 42%            | Noise / microstructure
D2        | 4-8 days     | 18%            | Short-term mean reversion
D3        | 8-16 days    | 12%            | Weekly cycle
D4        | 16-32 days   | 10%            | Monthly rotation
D5        | 32-64 days   | 8%             | Quarterly earnings
A5        | >64 days     | 10%            | Trend

Key Finding: 60% of variance is at scales D1-D2 (< 8 days).
Trend component (A5) is smooth and tradable with low turnover.
Denoised signal (A5+D5+D4) Sharpe: 0.65 vs raw: 0.42.
```

### Filter Selection Guide

```
Goal                          | Recommended Filter     | Key Parameter
Smooth trend extraction       | EMA or Butterworth LP  | Period > 50 days
Cycle isolation               | Butterworth bandpass   | Band: 20-60 days
Noise removal preserving peaks| Savitzky-Golay         | Window=21, degree=3
Adaptive smoothing            | KAMA or wavelet        | ER threshold
Multi-scale decomposition     | Wavelet (db4)          | Levels: 5-7
Non-stationary cycle analysis | EMD / EEMD             | Max IMFs: 8-10
Real-time trend (low lag)     | Hull MA or KAMA        | Period: 20-50
```

### Denoising Pipeline Template

```
1. Visual inspection of raw signal
2. Compute power spectrum (FFT) — identify dominant frequencies
3. Choose denoising method based on signal characteristics:
   - Stationary cycles: Fourier filtering
   - Multi-scale, non-stationary: Wavelet denoising
   - Simple trend: Moving average or Butterworth
4. Apply filter with initial parameters
5. Evaluate:
   - Correlation between denoised signal and future returns
   - Lag measurement (cross-correlation peak)
   - Turnover of signal-based trades
   - Sharpe ratio improvement vs raw signal
6. Optimize filter parameters via walk-forward cross-validation
7. Confirm no look-ahead bias (causal filter for live trading)
```

## Quality Gate

Before using signal processing in production trading:

- [ ] Causal (real-time) filter used for trading signals — no future information
- [ ] Filter lag is measured and acceptable for the trading horizon
- [ ] Denoised signal improves IC or Sharpe ratio vs raw signal (not just smoother)
- [ ] Parameters are not overfit — validated on out-of-sample data
- [ ] Wavelet/Fourier analysis performed on sufficiently long series (>500 observations)
- [ ] Filter does not introduce spurious features (check on simulated random walk)
- [ ] Multi-scale results are robust to wavelet/filter choice (test 2-3 alternatives)
- [ ] Phase distortion is understood and documented
- [ ] Computational cost is feasible for production frequency
- [ ] Edge effects at boundaries are handled (padding, reflection, or discarded)
