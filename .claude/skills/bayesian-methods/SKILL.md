---
name: bayesian-methods
description: "Bayesian Methods. Use when: User wants to incorporate prior beliefs into parameter estimation; Estimating Sharpe ratios or expected returns with uncertainty quantification; Building Black-Litterman portfolios with investor views."
---

# Bayesian Methods

name: bayesian-methods
description: Bayesian inference for trading — prior selection, posterior updating, Bayesian portfolio optimization. Use for probabilistic trading analysis.

## When to Activate

- User wants to incorporate prior beliefs into parameter estimation
- Estimating Sharpe ratios or expected returns with uncertainty quantification
- Building Black-Litterman portfolios with investor views
- Working with small sample sizes where frequentist methods are unreliable
- Combining multiple data sources or expert opinions with market data
- Performing robust parameter estimation under uncertainty

## First Questions

1. What parameter or quantity are you trying to estimate (Sharpe ratio, expected return, volatility, correlation)?
2. Do you have prior beliefs or external information to incorporate?
3. How much data is available (small sample = Bayesian advantage is largest)?
4. Do you need point estimates or full posterior distributions?
5. Is computational cost a constraint (closed-form vs MCMC)?

## Core Concepts

### Bayes' Theorem in Finance

```
P(theta | data) = P(data | theta) * P(theta) / P(data)

posterior = likelihood * prior / normalizing constant

theta: parameter of interest (expected return, Sharpe ratio, volatility)
data: observed returns
P(theta): prior distribution — encodes beliefs before seeing data
P(data | theta): likelihood — probability of observed data given parameter
P(theta | data): posterior — updated belief after seeing data
```

The Bayesian framework naturally handles uncertainty: instead of a single point estimate, you get a full distribution over plausible parameter values.

### Prior Selection

**Uninformative (diffuse) priors:**
- Let the data speak. Use when you have no strong prior knowledge.
- Normal with large variance, Jeffreys prior, flat prior
- Result will be close to maximum likelihood estimate

**Informative priors:**
- Encode domain knowledge or external data
- Example: Prior on equity risk premium centered at 5% with std of 2%
- Shrinks estimates toward the prior, reducing estimation error

**Empirical Bayes:**
- Estimate prior parameters from data (e.g., cross-sectional distribution of stock returns)
- James-Stein shrinkage is an empirical Bayes estimator
- Practical compromise between subjective and uninformative

**Conjugate priors (closed-form posteriors):**

| Likelihood | Conjugate Prior | Posterior |
|------------|----------------|-----------|
| Normal (known var) | Normal | Normal |
| Normal (unknown var) | Inverse-Gamma | Inverse-Gamma |
| Normal (both unknown) | Normal-Inverse-Gamma | Normal-Inverse-Gamma |
| Bernoulli | Beta | Beta |

## Detailed Methodology

### Bayesian Sharpe Ratio Estimation

The frequentist Sharpe ratio SR = mean(r) / std(r) is a noisy estimator. With 5 years of monthly data (60 observations), the standard error of the Sharpe ratio is approximately sqrt((1 + SR^2/2) / T) which is about 0.13 even for SR = 0.

**Bayesian approach:**
```
Prior: SR ~ N(SR_prior, sigma_prior^2)
  SR_prior = 0 (skeptical) or 0.4 (typical equity premium)
  sigma_prior = 0.3 (allows reasonable range)

Likelihood: observed returns ~ N(mu, sigma^2)
  Implies observed SR_hat ~ N(true_SR, (1 + SR^2/2)/T)

Posterior: SR | data ~ N(SR_posterior, sigma_posterior^2)
  SR_posterior = (SR_prior/sigma_prior^2 + SR_hat/sigma_hat^2) / (1/sigma_prior^2 + 1/sigma_hat^2)

Interpretation: Posterior SR is shrunk toward prior
  - With strong prior (small sigma_prior): heavy shrinkage
  - With weak prior (large sigma_prior): close to sample SR
  - With lots of data (small sigma_hat): close to sample SR
```

### Black-Litterman as Bayesian Framework

Black-Litterman combines market equilibrium returns (prior) with investor views (likelihood):

```
Prior: mu_prior = delta * Sigma * w_mkt  (implied equilibrium returns)
  delta: risk aversion coefficient
  Sigma: covariance matrix
  w_mkt: market capitalization weights

Views: P * mu = q + epsilon,  epsilon ~ N(0, Omega)
  P: pick matrix (which assets the view is about)
  q: expected returns from views
  Omega: uncertainty in views (critical parameter)

Posterior: mu_BL = mu_prior + tau*Sigma*P'*(P*tau*Sigma*P' + Omega)^{-1} * (q - P*mu_prior)

tau: scaling parameter (typically 0.025 to 0.05)
  Controls how much weight the prior gets vs views
```

**Omega calibration:**
- Proportional to variance: Omega = diag(P * tau * Sigma * P') — views have uncertainty proportional to asset volatility
- Confidence-based: Set diagonal elements inversely proportional to confidence in each view
- He-Litterman: Omega_ii = (P * tau * Sigma * P')_ii — makes results invariant to tau

### MCMC Methods for Complex Models

When conjugate priors are not available, use Markov Chain Monte Carlo:

**Metropolis-Hastings:**
```
1. Start with initial theta_0
2. Propose theta* from proposal distribution q(theta* | theta_t)
3. Accept with probability min(1, [p(theta*|data) * q(theta_t|theta*)] / [p(theta_t|data) * q(theta*|theta_t)])
4. If accepted: theta_{t+1} = theta*; else theta_{t+1} = theta_t
5. After burn-in, samples approximate the posterior
```

**Hamiltonian Monte Carlo (HMC) / NUTS:**
- More efficient than Metropolis-Hastings for high dimensions
- Uses gradient information to propose better moves
- NUTS (No-U-Turn Sampler) auto-tunes step size
- Available in Stan, PyMC, NumPyro

**Practical MCMC guidance:**
- Run multiple chains (at least 4) and check convergence (Gelman-Rubin R-hat < 1.01)
- Discard burn-in period (first 25-50% of samples)
- Check effective sample size (ESS > 400 for reliable inference)
- Examine trace plots for stationarity

### Bayesian Regression for Return Prediction

```
Model: r_t = X_t * beta + epsilon_t

Frequentist OLS: beta_hat = (X'X)^{-1} X'r
  Problem: unstable when features are correlated or sample is small

Bayesian regression with prior beta ~ N(0, lambda^{-1} * I):
  Posterior mean: beta_post = (X'X + lambda*I)^{-1} X'r
  This IS ridge regression — Bayesian shrinkage

Bayesian advantage:
  - Full posterior on beta: uncertainty quantification
  - Posterior predictive distribution: P(r_new | data) includes parameter uncertainty
  - Automatic regularization through prior
  - Can use informative priors from economic theory
```

### Bayesian Portfolio Optimization

Traditional mean-variance optimization is notoriously sensitive to expected return estimates. Bayesian methods help:

```
1. Specify prior on mu and Sigma (e.g., from equilibrium model)
2. Update with observed data to get posterior P(mu, Sigma | data)
3. For each posterior sample (mu_s, Sigma_s):
   Solve: w_s = argmax w' * mu_s - (lambda/2) * w' * Sigma_s * w
4. Average across samples: w_Bayes = mean(w_s)

Result: Portfolio weights that account for estimation uncertainty
  - More diversified than plug-in MVO
  - Naturally shrinks toward prior (e.g., equal weight or market cap)
  - Robust to outliers in return estimates
```

## Templates / Examples

### Bayesian Strategy Evaluation Template

```
Strategy: [Name]
Sample: [Period], N = [observations]

Frequentist Estimates:
  Sharpe Ratio:    0.85
  Annual Return:   12.3%
  Annual Vol:      14.5%

Bayesian Estimates (prior: SR ~ N(0, 0.3)):
  Posterior SR:    0.62  [95% CI: 0.18, 1.05]
  P(SR > 0):      99.2%
  P(SR > 0.5):    65.8%
  P(SR > 1.0):    8.3%

Interpretation: After accounting for estimation uncertainty and
applying a skeptical prior, there is strong evidence the strategy
is profitable (P(SR>0) = 99%) but less certainty it exceeds
institutional thresholds (P(SR>0.5) = 66%).
```

### Black-Litterman Implementation Checklist

```
[ ] Market cap weights obtained for the universe
[ ] Covariance matrix estimated (shrinkage recommended)
[ ] Risk aversion delta calibrated (from market portfolio Sharpe)
[ ] Equilibrium returns computed: mu_eq = delta * Sigma * w_mkt
[ ] Views specified: P matrix, q vector
[ ] View uncertainty Omega calibrated (not arbitrary)
[ ] tau parameter set (0.025 default, sensitivity tested)
[ ] Posterior returns mu_BL computed
[ ] Portfolio optimized with mu_BL (confirm it is more stable than raw MVO)
[ ] Sensitivity analysis: vary view confidence and check weight stability
```

### Prior Sensitivity Analysis Template

```
Prior Specification Tests for [Parameter]:

Prior            | Prior Mean | Prior Std | Posterior Mean | 95% CI
Uninformative    | 0          | 100       | 0.82          | [0.35, 1.29]
Weakly inform.   | 0          | 0.50      | 0.65          | [0.28, 1.02]
Moderately inform| 0.40       | 0.30      | 0.58          | [0.25, 0.91]
Strongly inform. | 0.40       | 0.15      | 0.48          | [0.22, 0.74]

Assessment: Results are [robust / sensitive] to prior specification.
The posterior is [dominated by data / influenced by prior].
```

## Quality Gate

Before deploying Bayesian models in production:

- [ ] Prior is documented and justified (economic rationale or reference study)
- [ ] Prior sensitivity analysis performed — results should not hinge entirely on prior choice
- [ ] MCMC diagnostics pass if applicable (R-hat < 1.01, ESS > 400, trace plots stable)
- [ ] Posterior predictive checks: simulated data from the model resembles actual data
- [ ] Comparison with frequentist methods: Bayesian approach should improve, not degrade, OOS performance
- [ ] Computational cost is acceptable for production frequency
- [ ] Uncertainty in parameter estimates is communicated (credible intervals, not just point estimates)
- [ ] Model updating procedure defined (how often to re-estimate posterior)
- [ ] Edge cases handled: what happens with extreme observations or prior-data conflict?
- [ ] Black-Litterman: views are based on defensible analysis, not arbitrary numbers
