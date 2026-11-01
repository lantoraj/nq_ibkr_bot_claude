"""
Selection-bias aware performance statistics (Bailey & Lopez de Prado).

All Sharpe ratios here are PER-PERIOD (per trading day) unless a name says "annual". n is the number of daily observations.

psr                       Probabilistic Sharpe Ratio: P(true Sharpe > benchmark), correcting for skew and fat tails
expected_max_sr           the Sharpe you should EXPECT from the best of N trials when no strategy has any edge
deflated_sr               PSR measured against that inflated benchmark = probability the best-found Sharpe is real
min_track_record_length   observations needed before an observed Sharpe beats a benchmark at confidence 1 - alpha
min_backtest_years        years of data needed so that the best of N trials reaching a target annual Sharpe is not luck
max_trials_supported      inverse of the above: how many independent trials a given history can support

Caveat: N is the number of INDEPENDENT trials. Variants that differ slightly are highly correlated, so counting every one of
them overstates N, while ideas tried but not recorded (prior iterations, unlogged tuning) understate it.
"""
from __future__ import annotations

import math
from statistics import NormalDist
from typing import Sequence

import numpy as np
import pandas as pd

EULER = 0.5772156649015329
_N = NormalDist()
TRADING_DAYS = 252


def daily_pnl(trades: Sequence, trading_days: Sequence) -> pd.Series:
    """Net PnL per session, zero on days without a trade."""
    s = pd.Series({d: 0.0 for d in trading_days}, dtype=float)
    for t in trades:
        d = pd.Timestamp(t.exit_time).date()
        s[d] = s.get(d, 0.0) + t.net_pnl_usd
    return s.sort_index()


def sharpe_moments(daily: Sequence[float]) -> dict:
    x = np.asarray(daily, dtype=float)
    n = len(x)
    sd = x.std(ddof=1) if n > 1 else 0.0
    if n < 3 or sd == 0:
        return {"n": n, "sr": 0.0, "skew": 0.0, "kurt": 3.0}
    z = (x - x.mean()) / sd
    return {"n": n, "sr": float(x.mean() / sd), "skew": float((z ** 3).mean()), "kurt": float((z ** 4).mean())}


def psr(sr: float, n: int, skew: float, kurt: float, sr_bench: float = 0.0) -> float:
    var = 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr ** 2
    z = (sr - sr_bench) * math.sqrt(max(n - 1, 1)) / math.sqrt(max(var, 1e-12))
    return _N.cdf(z)


def expected_max_sr(n_trials: int, var_sr: float) -> float:
    """E[max of N Sharpe estimates] under the null of zero true Sharpe; var_sr = cross-trial variance of the estimates."""
    if n_trials <= 1 or var_sr <= 0:
        return 0.0
    return math.sqrt(var_sr) * ((1 - EULER) * _N.inv_cdf(1 - 1.0 / n_trials)
                                + EULER * _N.inv_cdf(1 - 1.0 / (n_trials * math.e)))


def deflated_sr(sr: float, n: int, skew: float, kurt: float, n_trials: int, var_sr: float) -> float:
    return psr(sr, n, skew, kurt, expected_max_sr(n_trials, var_sr))


def min_track_record_length(sr: float, skew: float, kurt: float, sr_bench: float = 0.0, alpha: float = 0.05) -> float:
    """Observations needed for PSR >= 1 - alpha. inf if the observed Sharpe does not exceed the benchmark."""
    if sr <= sr_bench:
        return math.inf
    var = 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr ** 2
    return 1.0 + max(var, 1e-12) * (_N.inv_cdf(1 - alpha) / (sr - sr_bench)) ** 2


def _null_max_z(n_trials: int) -> float:
    if n_trials <= 1:
        return 0.0
    return (1 - EULER) * _N.inv_cdf(1 - 1.0 / n_trials) + EULER * _N.inv_cdf(1 - 1.0 / (n_trials * math.e))


def min_backtest_years(n_trials: int, target_sr_annual: float) -> float:
    """Years of history needed so that the best of N zero-edge trials is not expected to reach target_sr_annual by chance."""
    if target_sr_annual <= 0:
        return math.inf
    return (_null_max_z(n_trials) / target_sr_annual) ** 2


def max_trials_supported(years: float, target_sr_annual: float) -> int:
    """Largest N whose chance-level best Sharpe stays at or below the target for this much history."""
    if target_sr_annual <= 0 or years <= 0:
        return 0
    lo, hi = 1, 2
    while min_backtest_years(hi, target_sr_annual) <= years and hi < 10 ** 9:
        lo, hi = hi, hi * 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if min_backtest_years(mid, target_sr_annual) <= years:
            lo = mid
        else:
            hi = mid
    return lo if min_backtest_years(lo, target_sr_annual) <= years else 0
