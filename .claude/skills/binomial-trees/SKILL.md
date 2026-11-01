---
name: binomial-trees
description: "CRR model, multi-step trees, American options, early exercise boundary, calibration, and convergence to BSM. Use when: User pricing American options where closed-form solutions do not exist; Teaching or explaining option pricing intuition through discrete models; Pricing options with discrete dividends or complex exercise features."
---

# Binomial Option Pricing

> CRR model, multi-step trees, American options, early exercise boundary, calibration, and convergence to BSM.

## When to Activate

- User pricing American options where closed-form solutions do not exist
- Teaching or explaining option pricing intuition through discrete models
- Pricing options with discrete dividends or complex exercise features
- Calibrating tree parameters to match market prices
- Understanding early exercise boundaries for American puts and calls on dividend-paying stocks
- Validating other pricing methods (Monte Carlo, finite differences) against tree results

## Core Concepts

### Binomial Model Intuition

At each time step, the stock price can move to one of two states:
- Up state: S_u = S * u (up factor)
- Down state: S_d = S * d (down factor)
- Risk-neutral probability of up move: p = (exp(r*dt) - d) / (u - d)
- Option value at each node: discounted expected value under risk-neutral probabilities
- At expiry: option value = intrinsic value (max(S-K, 0) for call, max(K-S, 0) for put)
- Work backward from expiry to today, computing option value at each node

### Cox-Ross-Rubinstein (CRR) Parameterization

The standard parameterization ensuring the tree converges to GBM:
- u = exp(sigma * sqrt(dt))
- d = 1/u = exp(-sigma * sqrt(dt))
- p = (exp(r*dt) - d) / (u - d)
- dt = T/N where N = number of time steps

Properties:
- u * d = 1 (recombining tree — the tree reconnects, keeping the number of nodes manageable)
- After N steps: 2^N paths but only N+1 distinct terminal prices (due to recombination)
- Terminal stock prices: S * u^j * d^(N-j) for j = 0, 1, ..., N
- Risk-neutral probability of reaching node (j ups out of N steps): C(N,j) * p^j * (1-p)^(N-j)

### Alternative Parameterizations

**Jarrow-Rudd (Equal Probability)**
- p = 0.5
- u = exp((r - sigma^2/2)*dt + sigma*sqrt(dt))
- d = exp((r - sigma^2/2)*dt - sigma*sqrt(dt))
- Better for some convergence properties but less commonly used

**Tian (Moment-Matching)**
- Matches the first three moments of the log-normal distribution
- u = 0.5 * exp(r*dt) * M2 * (M2 + 1 + sqrt(M2^2 + 2*M2 - 3))
- d = 0.5 * exp(r*dt) * M2 * (M2 + 1 - sqrt(M2^2 + 2*M2 - 3))
- M2 = exp(sigma^2 * dt)
- Faster convergence than CRR for some option types

**Leisen-Reimer**
- Designed to minimize oscillation in convergence
- Uses the Peizer-Pratt inversion for d1 and d2 from BSM
- Very smooth convergence even with moderate N (50-100 steps)

## Methodology

### European Option Pricing on a Binomial Tree

1. **Build the stock tree**: compute stock price at each node (i, j) where i = time step, j = up moves
   - S(i, j) = S_0 * u^j * d^(i-j) for j = 0, 1, ..., i
2. **Compute terminal payoffs**: at step N, payoff(N, j) = max(S(N,j) - K, 0) for calls
3. **Backward induction**: for i = N-1, N-2, ..., 0:
   - V(i, j) = exp(-r*dt) * [p * V(i+1, j+1) + (1-p) * V(i+1, j)]
4. **Option price**: V(0, 0) at the root node

### American Option Pricing

The key addition: at each node, compare holding value to exercise value.

1. Build stock tree (same as European)
2. Terminal payoffs (same as European)
3. Backward induction with early exercise check:
   - Continuation value: C(i, j) = exp(-r*dt) * [p * V(i+1, j+1) + (1-p) * V(i+1, j)]
   - Exercise value: E(i, j) = max(K - S(i,j), 0) for put; max(S(i,j) - K, 0) for call
   - V(i, j) = max(C(i, j), E(i, j))
4. If E(i, j) > C(i, j), early exercise is optimal at that node
5. The set of nodes where early exercise is optimal defines the early exercise boundary

### Early Exercise Boundary

**American Put**
- Always optimal to exercise sufficiently deep ITM (where time value is negative)
- Critical stock price S*(t): exercise if S < S*(t)
- S*(t) decreases as t -> T (boundary converges to K at expiry)
- For r > 0: S*(T) = K (exercise ATM puts at expiry)
- The boundary is smooth and monotonically increasing toward K

**American Call on Dividend-Paying Stock**
- Early exercise may be optimal just before ex-dividend dates
- Exercise if the dividend exceeds the time value of the option
- Rule of thumb: exercise is optimal if dividend > K * (1 - exp(-r*dt_remaining))
- For continuous dividend yield q: early exercise boundary exists for all t if q > 0

**American Call on Non-Dividend Stock**
- Never optimal to exercise early (no boundary exists)
- American call = European call (no early exercise premium)
- Proof: call value >= S - K*exp(-rT) > S - K (intrinsic value) when r > 0

### Discrete Dividends on Trees

**Method 1: Reduce stock price at ex-dividend node**
- At the ex-dividend step, subtract the known dividend D from all stock prices
- Problem: tree no longer recombines after the dividend (branches split)
- Fix: use the "Black approximation" — reduce S_0 by PV of dividends, build tree on adjusted S

**Method 2: Dividend yield approach**
- Model dividend as a proportional reduction: S -> S * (1 - delta) at ex-date
- Tree remains recombining
- Less accurate for stocks with fixed dollar dividends

**Method 3: Interpolation method**
- Build recombining tree, at dividend date interpolate between nodes after dividend adjustment
- More accurate but computationally more complex

### Convergence to BSM

- As N -> infinity, CRR binomial price converges to BSM price for European options
- Rate of convergence: O(1/N) — error decreases proportionally with number of steps
- Oscillation: CRR oscillates around the true value (even/odd N give systematically different prices)
- Practical: N = 200-500 steps gives accuracy within 1 cent for most options
- Richardson extrapolation: average prices from N and N+1 steps to cancel oscillation
- Leisen-Reimer: smooth convergence with N = 50-100

## Examples

### 3-Step CRR Tree for European Call
```
Parameters: S=100, K=100, r=5%, sigma=30%, T=0.75 (3 quarters)
dt = 0.25, u = exp(0.30*sqrt(0.25)) = 1.1618, d = 1/u = 0.8607
p = (exp(0.05*0.25) - 0.8607) / (1.1618 - 0.8607) = 0.5073

Stock tree:
  t=0:     100.00
  t=0.25:  116.18 / 86.07
  t=0.50:  135.00 / 100.00 / 74.08
  t=0.75:  156.83 / 116.18 / 86.07 / 63.76

Call payoffs at T:
  156.83-100=56.83, 116.18-100=16.18, max(86.07-100,0)=0, max(63.76-100,0)=0

Backward induction:
  t=0.50: (0.5073*56.83 + 0.4927*16.18)*exp(-0.0125) = 36.74
          (0.5073*16.18 + 0.4927*0)*exp(-0.0125) = 8.11
          (0.5073*0 + 0.4927*0)*exp(-0.0125) = 0
  t=0.25: (0.5073*36.74 + 0.4927*8.11)*exp(-0.0125) = 22.35
          (0.5073*8.11 + 0.4927*0)*exp(-0.0125) = 4.06
  t=0:    (0.5073*22.35 + 0.4927*4.06)*exp(-0.0125) = 13.18

Tree price: $13.18
BSM price: $13.15 (close even with just 3 steps)
```

### American Put Early Exercise
```
Same parameters but pricing a put (K=100):

Put payoffs at T: 0, 0, max(100-86.07,0)=13.93, max(100-63.76,0)=36.24

Backward induction with early exercise check:
  t=0.50 (S=74.08):
    Continuation: (0.5073*13.93 + 0.4927*36.24)*exp(-0.0125) = 24.60
    Exercise: 100-74.08 = 25.92
    Value = max(24.60, 25.92) = 25.92 ***EARLY EXERCISE***

  t=0.50 (S=100): Continuation=6.99, Exercise=0, Value=6.99
  t=0.50 (S=135): Continuation=0, Exercise=0, Value=0

American put premium over European: $0.35 (from early exercise value)
```

### Convergence Analysis
```
European call (S=100, K=100, r=5%, sigma=30%, T=1):
BSM exact = $14.23

N=10:   $14.35 (error = +$0.12)
N=50:   $14.25 (error = +$0.02)
N=100:  $14.24 (error = +$0.01)
N=200:  $14.23 (error < $0.005)
N=500:  $14.23 (error < $0.002)

Richardson extrapolation (N=100, N=101): $14.231 (error < $0.001)
Leisen-Reimer (N=51): $14.231 (error < $0.001)
```

## Quality Gate

- CRR parameters must satisfy: 0 < p < 1 (verify risk-neutral probability is valid)
- Tree must recombine: verify u*d = 1 within numerical precision
- American option price must be >= European option price (verify early exercise premium is non-negative)
- American call on non-dividend stock must equal European call (verify no early exercise)
- Convergence must be verified: increase N until price changes by less than $0.01 between successive N
- Use at least N=200 steps for production pricing; N=500+ for precise benchmark values
- Early exercise boundary must be smooth and monotonic (irregular boundary suggests implementation error)
- Discrete dividend handling must correctly adjust stock prices at ex-dividend nodes
- Validate against BSM for European options: tree price must converge to BSM within 0.1%
- Richardson extrapolation or Leisen-Reimer should be used when computational time is limited
