---
name: monte-carlo-pricing
description: "Random number generation, GBM simulation, path-dependent options, variance reduction, Longstaff-Schwartz for Americans, and convergence analysis. Use when: User pricing path-dependent or exotic derivatives (Asian, barrier, lookback); Pricing options on multiple underlyings (basket, rainbow, worst-of); American option pricing via Longstaff-Schwartz regression."
---

# Monte Carlo Methods for Derivatives Pricing

> Random number generation, GBM simulation, path-dependent options, variance reduction, Longstaff-Schwartz for Americans, and convergence analysis.

## When to Activate

- User pricing path-dependent or exotic derivatives (Asian, barrier, lookback)
- Pricing options on multiple underlyings (basket, rainbow, worst-of)
- American option pricing via Longstaff-Schwartz regression
- Evaluating variance reduction techniques for pricing efficiency
- Multi-factor model simulation (stochastic vol, rates, credit)
- Convergence analysis and error estimation for MC prices

## Core Concepts

### Monte Carlo Pricing Framework

The price of a derivative under risk-neutral pricing:

V_0 = exp(-rT) * E^Q[payoff(S_T)]

Monte Carlo estimates this expectation by:
1. Simulating N paths of the underlying under the risk-neutral measure
2. Computing the payoff for each path
3. Averaging the payoffs and discounting

V_MC = exp(-rT) * (1/N) * sum_{i=1}^{N} payoff_i

Standard error = sigma_payoff / sqrt(N), where sigma_payoff is the std dev of simulated payoffs.

### GBM Path Simulation

Under risk-neutral GBM: dS = r*S*dt + sigma*S*dW

**Exact Simulation** (log-normal):
S(t+dt) = S(t) * exp((r - sigma^2/2)*dt + sigma*sqrt(dt)*Z)
where Z ~ N(0,1)

- Exact: no discretization error regardless of dt
- Use for simple GBM dynamics (constant vol, no barriers)

**Euler Discretization**:
S(t+dt) = S(t) + r*S(t)*dt + sigma*S(t)*sqrt(dt)*Z

- Introduces discretization bias of order O(dt)
- Required for more complex SDEs (stochastic vol, local vol) where exact simulation is unavailable
- Can produce negative stock prices; use log-Euler: ln(S(t+dt)) = ln(S(t)) + (r - sigma^2/2)*dt + sigma*sqrt(dt)*Z

**Milstein Scheme**:
S(t+dt) = S(t) + r*S(t)*dt + sigma*S(t)*sqrt(dt)*Z + 0.5*sigma^2*S(t)*(Z^2 - 1)*dt

- Higher-order accuracy: O(dt) vs. O(sqrt(dt)) for Euler
- For GBM, Milstein = exact simulation (coincidence of the specific SDE)
- Useful for general SDEs where exact simulation is unavailable

### Random Number Generation

- Use high-quality pseudo-random generators: Mersenne Twister (MT19937) is standard
- Box-Muller or inverse CDF to transform uniform to normal variates
- Quasi-random sequences (Sobol, Halton) for faster convergence:
  - QMC convergence: O(1/N) vs. O(1/sqrt(N)) for pseudo-random MC
  - Sobol sequences preferred for high dimensions (up to 1000+ dimensions)
  - Scrambled Sobol: adds randomization for error estimation while preserving QMC convergence
- Seed management: fix seeds for reproducibility; vary seeds for independence testing

### Multi-Asset Simulation

For correlated assets with covariance matrix Sigma:
1. Cholesky decomposition: Sigma = L * L' where L is lower triangular
2. Generate independent Z = [Z_1, ..., Z_d] ~ N(0, I)
3. Correlated normals: W = L * Z
4. Simulate each asset using its correlated Brownian increment W_i
5. For d assets and N time steps: need d*N normal variates per path

## Methodology

### Variance Reduction Techniques

**Antithetic Variates**
- For each path using Z, also simulate the path using -Z
- Average the two payoffs: reduces variance when payoff is monotonic in Z
- Variance reduction factor: up to 2x for simple payoffs
- Free to implement (no additional random numbers needed)
- Works poorly for payoffs that are symmetric in Z (e.g., straddles)

**Control Variates**
- Use a correlated quantity with known expected value as a control
- Adjusted estimate: V_CV = V_MC + beta * (E[C] - C_MC)
- beta = -cov(payoff, C) / var(C) (optimal beta)
- Common controls: stock price itself (E[S_T] = S_0*exp(rT)), geometric Asian option (closed-form), BSM European option
- Can reduce variance by 10-100x for well-chosen controls
- Multiple controls: use regression to find optimal combination

**Importance Sampling**
- Change the probability measure to sample more from the region that matters
- V = E^P[payoff] = E^Q[payoff * dP/dQ] where Q is the importance sampling distribution
- Shift the mean of the GBM drift to make ITM paths more likely for OTM options
- Optimal importance distribution minimizes the variance of the weighted estimator
- Risk: poor choice of Q can increase variance; requires care

**Stratified Sampling**
- Divide the probability space into strata; sample uniformly within each stratum
- Ensures tails are sampled proportionally
- Latin hypercube sampling: generalization to multiple dimensions
- Typically combined with other techniques for maximum benefit

### Path-Dependent Option Pricing

**Asian Options**
- Payoff depends on the average price: max(avg(S) - K, 0) for fixed-strike Asian call
- Simulate full price path, compute the average at each monitoring date
- Arithmetic average: no closed-form, MC is the standard method
- Geometric average: closed-form exists, use as control variate for arithmetic
- Variance reduction: geometric Asian control variate reduces variance by 50-90%

**Barrier Options**
- Payoff depends on whether the path crosses a barrier
- Naive MC with discrete monitoring misses barrier crossings between time steps
- Brownian bridge correction: compute probability of crossing barrier between observed points
- Continuity correction (Broadie-Glasserman-Kou): adjust barrier by 0.5826*sigma*sqrt(dt) for discrete monitoring approximation of continuous barrier
- Importance sampling: shift drift toward the barrier to increase the frequency of barrier hits

**Lookback Options**
- Payoff depends on the maximum or minimum price over the path
- Simulate path and track running max/min
- Discretization bias: discrete monitoring underestimates continuous max/min
- Correction: apply Brownian bridge to estimate continuous extremum between discrete points

### Longstaff-Schwartz for American Options

The LSM algorithm uses regression to estimate continuation value:

1. Simulate N paths of the underlying to maturity
2. At the final time step: exercise value = intrinsic value
3. Work backward from T-dt to dt:
   a. At time step t, identify in-the-money paths
   b. Regress discounted future cashflows on basis functions of current stock price (e.g., 1, S, S^2, or Laguerre polynomials)
   c. Fitted regression = estimated continuation value C(S)
   d. Exercise if intrinsic value > C(S); otherwise continue
4. Option price = average of discounted cashflows along optimal exercise paths

Key implementation details:
- Basis functions: polynomials of S (degree 3-5 usually sufficient), Laguerre or Hermite polynomials
- Only use ITM paths for regression (reduces noise)
- Forward pass after backward exercise decisions to get unbiased estimate
- Bias: LSM gives a lower bound (suboptimal exercise policy); use dual method for upper bound
- N = 50,000-200,000 paths typically needed for stable estimates

## Examples

### European Call via MC
```
S=100, K=100, r=5%, sigma=30%, T=1.0
Exact BSM price: $14.23

Standard MC (N=10,000): $14.35, SE=$0.28, 95% CI: [$13.80, $14.90]
Standard MC (N=100,000): $14.21, SE=$0.09, 95% CI: [$14.03, $14.39]
Antithetic (N=50,000 pairs): $14.24, SE=$0.06, 95% CI: [$14.12, $14.36]
Control variate + antithetic: $14.23, SE=$0.02, 95% CI: [$14.19, $14.27]

Variance reduction: 196x improvement from SE=$0.28 to SE=$0.02
```

### Arithmetic Asian Option with Control Variate
```
S=100, K=100, r=5%, sigma=30%, T=1.0, monthly averaging (12 dates)

Geometric Asian (closed-form): $8.42
Arithmetic Asian (MC, N=100,000): $8.89, SE=$0.07
With geometric Asian control variate: $8.91, SE=$0.01

Control variate reduced SE by 7x (variance by 49x).
The correlation between arithmetic and geometric Asian payoffs is 0.998.
```

### Longstaff-Schwartz American Put
```
S=100, K=100, r=5%, sigma=30%, T=1.0, monthly exercise (12 dates)
N=100,000 paths, basis functions: 1, S, S^2, S^3

European put (MC): $10.08
American put (LSM): $10.85
Early exercise premium: $0.77

Regression at t=0.5 (example):
  Continuation value = 2.31 + 0.15*S - 0.002*S^2 (fitted)
  At S=85: continuation = 2.31 + 12.75 - 14.45 = $0.61
  Intrinsic = 100 - 85 = $15.00
  Decision: exercise (intrinsic >> continuation)

Binomial tree (N=500) benchmark: $10.87 — LSM within $0.02.
```

## Quality Gate

- Standard error must be reported with every MC price — a price without error bounds is meaningless
- SE target: less than 1% of option price, or less than $0.05, whichever is tighter
- Convergence check: verify that price stabilizes as N increases (no systematic drift)
- At least one variance reduction technique should be applied (antithetic is minimum)
- For barrier options: Brownian bridge correction must be applied; verify with analytical formula where available
- For American options (LSM): validate against binomial tree for simple cases; difference should be <$0.05
- Random number generator must pass standard tests (Mersenne Twister or better)
- For QMC (Sobol): use scrambled sequences and randomize for error estimation
- Discretization: use exact simulation for GBM; for other SDEs, verify convergence by halving dt
- Multi-asset: verify Cholesky decomposition reproduces target correlation matrix (simulate and measure)
- Seed must be documented for reproducibility
