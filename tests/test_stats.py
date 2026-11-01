"""Deflated Sharpe / minimum backtest length: formulas, internal consistency, and a null-calibration simulation."""
from __future__ import annotations

import math

import numpy as np
import pytest

from stats_tests import (daily_pnl, deflated_sr, expected_max_sr, max_trials_supported, min_backtest_years,
                         min_track_record_length, psr, sharpe_moments)


def test_expected_max_of_100_standard_normals_is_about_2_5():
    assert abs(expected_max_sr(100, 1.0) - 2.53) < 0.05          # known value for E[max] of 100 N(0,1) draws (~2.51)
    assert expected_max_sr(1, 1.0) == 0.0
    assert expected_max_sr(10, 1.0) < expected_max_sr(100, 1.0) < expected_max_sr(1000, 1.0)


def test_psr_basics():
    assert psr(0.1, 250, 0.0, 3.0, sr_bench=0.1) == pytest.approx(0.5)
    assert psr(0.1, 1000, 0.0, 3.0) > psr(0.1, 100, 0.0, 3.0) > 0.5
    assert psr(0.1, 250, -1.0, 8.0) < psr(0.1, 250, 0.0, 3.0)    # negative skew and fat tails reduce confidence


def test_deflated_sr_falls_as_trials_grow_and_equals_psr_for_one_trial():
    base = psr(0.15, 300, 0.0, 3.0)
    assert deflated_sr(0.15, 300, 0.0, 3.0, 1, 0.001) == pytest.approx(base)
    d = [deflated_sr(0.15, 300, 0.0, 3.0, n, 0.002) for n in (2, 10, 100, 1000)]
    assert d == sorted(d, reverse=True) and d[-1] < base


def test_min_track_record_length_is_the_inverse_of_psr():
    sr, sk, ku = 0.08, -0.5, 5.0
    n = min_track_record_length(sr, sk, ku, alpha=0.05)
    assert psr(sr, int(math.ceil(n)), sk, ku) == pytest.approx(0.95, abs=0.01)
    assert min_track_record_length(0.0, 0, 3) == math.inf and min_track_record_length(0.2, 0, 3) < n


def test_min_backtest_years_and_max_trials_are_consistent():
    assert min_backtest_years(10, 1.5) < min_backtest_years(100, 1.5) < min_backtest_years(1000, 1.5)
    assert min_backtest_years(100, 3.0) < min_backtest_years(100, 1.5)                      # higher Sharpe needs less
    for n in (5, 20, 200):
        yrs = min_backtest_years(n, 2.0)
        assert max_trials_supported(yrs * 1.0001, 2.0) == n or abs(max_trials_supported(yrs * 1.0001, 2.0) - n) <= 1
    assert max_trials_supported(0.26, 2.7) < 15                                              # ~66 days supports only a handful


def test_sharpe_moments_and_daily_pnl():
    m = sharpe_moments([1.0, 2.0, 3.0, 4.0, 10.0])
    assert m["n"] == 5 and m["sr"] > 0 and m["skew"] > 0
    assert sharpe_moments([0.0] * 10)["sr"] == 0.0

    class T:
        def __init__(self, d, p): self.exit_time, self.net_pnl_usd = d, p
    s = daily_pnl([T("2026-01-05 10:00", 10.0), T("2026-01-05 11:00", -4.0), T("2026-01-07 10:00", 3.0)],
                  [__import__("datetime").date(2026, 1, d) for d in (5, 6, 7)])
    assert list(s.values) == [6.0, 0.0, 3.0]


def test_null_calibration_best_of_many_random_strategies_is_not_significant_after_deflation():
    """200 zero-edge strategies: the best one looks 'significant' by PSR almost always, but rarely after deflation."""
    rng = np.random.default_rng(5)
    reps, trials, days = 60, 200, 250
    raw_hits = defl_hits = 0
    for _ in range(reps):
        x = rng.normal(0, 1, (trials, days))
        srs = x.mean(axis=1) / x.std(axis=1, ddof=1)
        best = srs.argmax()
        m = sharpe_moments(x[best])
        raw_hits += psr(m["sr"], days, m["skew"], m["kurt"]) > 0.95
        defl_hits += deflated_sr(m["sr"], days, m["skew"], m["kurt"], trials, float(np.var(srs, ddof=1))) > 0.95
    assert raw_hits / reps > 0.8          # without deflation, picking the best of 200 nearly always "wins"
    assert defl_hits / reps < 0.15        # with deflation the false-positive rate is controlled (nominal 5%)
