---
name: black-scholes
description: "BSM derivation intuition, formula, put-call parity, Greeks, limitations, and extensions for dividends, American options, and implied volatility. Use when: User pricing European options or computing implied volatility; Deriving or interpreting BSM Greeks for hedging; Understanding BSM assumptions and when they break down."
---

# Black-Scholes-Merton Model and Extensions

> BSM derivation intuition, formula, put-call parity, Greeks, limitations, and extensions for dividends, American options, and implied volatility.

## When to Activate

- User pricing European options or computing implied volatility
- Deriving or interpreting BSM Greeks for hedging
- Understanding BSM assumptions and when they break down
- Extending BSM for dividends, discrete hedging, or jumps
- Computing put-call parity relationships or identifying arbitrage
- Teaching or explaining option pricing fundamentals

## Core Concepts

### BSM Derivation Intuition

The Black-Scholes-Merton model rests on three pillars:

1. **Geometric Brownian Motion (GBM)**: stock price follows dS = mu*S*dt + sigma*S*dW
   - Log returns are normally distributed: ln(S_T/S_0) ~ N((mu - sigma^2/2)*T, sigma^2*T)
   - Continuous paths, no jumps — a key limitation

2. **No-arbitrage / risk-neutral pricing**: construct a riskless portfolio of option + delta shares
   - The portfolio earns the risk-free rate by no-arbitrage
   - Under the risk-neutral measure, the drift of S becomes r (risk-free rate), not mu
   - Option price = discounted expected payoff under risk-neutral measure

3. **Continuous hedging**: delta hedge is rebalanced continuously (no transaction costs)
   - In practice, discrete hedging introduces hedging error proportional to gamma * (dS)^2

### BSM Formula

**European Call**:
C = S * N(d1) - K * exp(-rT) * N(d2)

**European Put**:
P = K * exp(-rT) * N(-d2) - S * N(-d1)

Where:
- d1 = [ln(S/K) + (r + sigma^2/2)*T] / (sigma * sqrt(T))
- d2 = d1 - sigma * sqrt(T)
- N(x) = cumulative standard normal distribution
- S = spot price, K = strike, r = risk-free rate, T = time to expiry, sigma = volatility

**Interpretation**:
- N(d2) = risk-neutral probability that the option expires in-the-money
- S * N(d1) = present value of receiving the stock conditional on exercise
- K * exp(-rT) * N(d2) = present value of paying the strike conditional on exercise
- Delta of call = N(d1); Delta of put = N(d1) - 1

### Put-Call Parity

For European options with same strike and expiry:
- C - P = S - K * exp(-rT)
- Holds by no-arbitrage regardless of model
- If violated, construct an arbitrage: buy the cheap side, sell the expensive side
- With dividends: C - P = S - PV(dividends) - K * exp(-rT)
- Put-call parity does NOT hold for American options (early exercise creates inequality)

### BSM Greeks (Analytical)

**Delta**: dC/dS = N(d1) for calls; N(d1) - 1 for puts
**Gamma**: d^2C/dS^2 = phi(d1) / (S * sigma * sqrt(T)) — same for calls and puts
**Theta**: dC/dt = -(S * phi(d1) * sigma) / (2*sqrt(T)) - r * K * exp(-rT) * N(d2) for calls
**Vega**: dC/d(sigma) = S * phi(d1) * sqrt(T) — same for calls and puts
**Rho**: dC/dr = K * T * exp(-rT) * N(d2) for calls

Where phi(x) = standard normal density function.

### BSM Assumptions and Limitations

1. **Constant volatility**: real markets show volatility smile/skew — OTM puts have higher implied vol
2. **Log-normal returns**: real returns have fat tails and negative skewness
3. **No jumps**: real prices jump (earnings, macro events) — jump-diffusion models address this
4. **Continuous trading**: discrete hedging introduces P&L noise
5. **No transaction costs**: in practice, hedging costs make BSM prices underestimates
6. **Constant interest rates**: relevant for long-dated options on bonds/rates
7. **No dividends**: base BSM assumes no dividends (correctable)
8. **European exercise**: BSM does not price American options directly

## Methodology

### Implied Volatility Computation

Implied volatility is the sigma that makes BSM price equal to the observed market price.

**Newton-Raphson Method**:
1. Start with initial guess sigma_0 (e.g., 20%)
2. Compute BSM price C(sigma_n) and vega V(sigma_n)
3. Update: sigma_{n+1} = sigma_n - (C(sigma_n) - C_market) / V(sigma_n)
4. Converge when |C(sigma_n) - C_market| < tolerance (e.g., 0.01)
5. Typically converges in 3-5 iterations
6. Edge cases: deep ITM/OTM options have low vega — may not converge; use bisection as fallback

**Brenner-Subrahmanyam Approximation** (quick initial guess for ATM):
- sigma_approx = C * sqrt(2*pi) / (S * sqrt(T))
- Accurate to within 1-2 vol points for near-ATM options

### BSM Extensions

**Dividends (Merton's Model)**
- Continuous dividend yield q: replace S with S * exp(-qT) in BSM formula
- d1 = [ln(S/K) + (r - q + sigma^2/2)*T] / (sigma * sqrt(T))
- Discrete dividends: reduce S by PV of expected dividends before expiry
- For index options, continuous yield approximation works well

**American Options**
- American calls on non-dividend stocks = European calls (early exercise never optimal)
- American puts and calls on dividend stocks may be exercised early
- No closed-form BSM solution for Americans
- Approximations: Barone-Adesi and Whaley, Bjerksund-Stensland
- Exact methods: binomial trees, finite differences

**Merton's Jump-Diffusion**
- dS/S = (mu - lambda*k)*dt + sigma*dW + J*dN
- J = jump size (log-normal), dN = Poisson process with intensity lambda, k = E[e^J - 1]
- Produces fat tails and short-dated volatility smile
- Option price = weighted sum of BSM prices with adjusted variance: sum over n of (exp(-lambda'*T) * (lambda'*T)^n / n!) * BSM(sigma_n)
- sigma_n^2 = sigma^2 + n * delta^2 / T

**Stochastic Volatility (Heston)**
- dS = mu*S*dt + sqrt(v)*S*dW_1
- dv = kappa*(theta - v)*dt + xi*sqrt(v)*dW_2, corr(dW_1, dW_2) = rho
- Produces volatility smile and term structure
- Semi-analytical solution via characteristic function and FFT
- Parameters: kappa (mean reversion speed), theta (long-run vol), xi (vol of vol), rho (spot-vol correlation), v_0 (initial vol)

### Volatility Surface from BSM

- Compute implied vol for each traded strike and expiry
- Plot implied vol vs. moneyness (K/S or delta) and maturity
- Smile: implied vol is U-shaped across strikes (equity index: skew — puts higher than calls)
- Term structure: implied vol varies by maturity (typically upward-sloping in calm markets)
- The vol surface is the market's correction to BSM's constant-vol assumption

## Examples

### BSM Pricing
```
S = $100, K = $105, r = 5%, T = 0.5 years, sigma = 25%

d1 = [ln(100/105) + (0.05 + 0.0625/2)*0.5] / (0.25 * sqrt(0.5))
   = [-0.04879 + 0.04063] / 0.17678
   = -0.00816 / 0.17678 = -0.04615

d2 = -0.04615 - 0.17678 = -0.22293

N(d1) = 0.4816, N(d2) = 0.4118

Call = 100 * 0.4816 - 105 * exp(-0.025) * 0.4118
     = 48.16 - 105 * 0.9753 * 0.4118
     = 48.16 - 42.16 = $6.00

Put (via put-call parity) = 6.00 - 100 + 105 * 0.9753 = $8.41
```

### Implied Volatility via Newton-Raphson
```
Market call price: $7.50 (same parameters as above except sigma unknown)

Iteration 1: sigma_0 = 0.20
  BSM price = $4.85, vega = 27.5
  sigma_1 = 0.20 - (4.85 - 7.50) / 27.5 = 0.20 + 0.0964 = 0.2964

Iteration 2: sigma_1 = 0.2964
  BSM price = $7.35, vega = 28.1
  sigma_2 = 0.2964 - (7.35 - 7.50) / 28.1 = 0.2964 + 0.0053 = 0.3017

Iteration 3: sigma_2 = 0.3017
  BSM price = $7.49, vega = 28.1
  sigma_3 = 0.3017 + 0.0004 = 0.3021

Converged: implied vol = 30.2%
```

### Delta Hedging P&L Attribution
```
Long 100 calls, delta = 0.50, gamma = 0.03, theta = -$150/day, vega = $200/vol point
Hedge: short 50 shares

Day 1: Stock moves +$2
  Delta P&L: 100 * 0.50 * $2 - 50 * $2 = $0 (hedged)
  Gamma P&L: 0.5 * 100 * 0.03 * $4 = $6
  Theta P&L: -$150
  Net P&L: -$144

The gamma P&L ($6) is small because the $2 move is within normal range.
For gamma scalping to profit, need realized vol > implied vol.
```

## Quality Gate

- BSM should only be used as a benchmark; always acknowledge smile/skew effects for real pricing
- Implied volatility must converge within 0.01% accuracy; verify with independent pricer
- Put-call parity must hold to within bid-ask spread; violations indicate data errors or arbitrage
- Greeks must be computed analytically from BSM for European options (not finite differences unless validating)
- For American options, do not use BSM — use binomial trees or finite difference methods
- Dividend treatment must match the actual dividend schedule (discrete dividends for single stocks, continuous yield for indices)
- When BSM implied vol varies significantly across strikes (>5 vol points), note that BSM is failing and a stochastic vol or local vol model is needed
- Validate BSM implementation against known test cases (e.g., ATM call approximately = S * sigma * sqrt(T) * 0.4)
- Document all input assumptions (rate curve, dividend yield, borrow cost) used in BSM calculation
