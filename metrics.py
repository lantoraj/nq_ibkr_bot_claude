"""
Performance metrics and statistical-robustness helpers.

* Sharpe is computed on DAILY PnL (zero-filled over all trading days) and annualised with sqrt(252).
* `trade_t_stat` is the old per-trade statistic (mean/std*sqrt(N)) kept for reference only.
* `bootstrap` resamples the trade list to give a distribution of outcomes instead of one path.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd


# |net PnL| below this (per trade) is treated as a scratch: break-even stops net ~+/- a few dollars after
# costs, so a raw win rate flips with a single tick of slippage and says little about edge.
SCRATCH_USD = 5.0


def max_drawdown(pnls: Sequence[float]) -> float:
    if len(pnls) == 0:
        return 0.0
    eq = np.concatenate([[0.0], np.cumsum(pnls)])
    return float(np.max(np.maximum.accumulate(eq) - eq))


def longest_losing_streak(pnls: Sequence[float]) -> int:
    best = cur = 0
    for p in pnls:
        cur = cur + 1 if p < 0 else 0
        best = max(best, cur)
    return best


def compute_metrics(trades: List, trading_days: Optional[Sequence] = None) -> Dict[str, float]:
    """`trades`: SimulatedTrade-like objects. `trading_days`: all session dates in the sample."""
    empty = {
        "total_trades": 0, "win_rate_pct": 0.0, "net_pnl_usd": 0.0, "profit_factor": 0.0,
        "max_drawdown_usd": 0.0, "avg_trade_usd": 0.0, "expectancy_r": 0.0, "avg_win_usd": 0.0,
        "avg_loss_usd": 0.0, "scratch_pct": 0.0, "win_rate_ex_scratch_pct": 0.0, "sharpe_daily_ann": 0.0, "trade_t_stat": 0.0, "longest_losing_streak": 0,
        "profitable_months": "0/0", "trades_per_day": 0.0,
    }
    if not trades:
        return empty

    pnls = np.array([t.net_pnl_usd for t in trades], dtype=float)
    wins, losses = pnls[pnls > 0], pnls[pnls <= 0]
    gp, gl = float(wins.sum()), float(abs(losses.sum()))
    pf = gp / gl if gl > 0 else float("inf")

    scratch = np.abs(pnls) < SCRATCH_USD
    decisive = pnls[~scratch]
    wr_ex = 100.0 * float((decisive > 0).sum()) / len(decisive) if len(decisive) else 0.0

    r_mult = np.array([t.r_multiple for t in trades if t.r_multiple == t.r_multiple], dtype=float)

    exit_days = pd.Series([pd.Timestamp(t.exit_time).date() for t in trades])
    daily = pd.Series(pnls).groupby(exit_days.values).sum()
    if trading_days is not None and len(trading_days) > 0:
        daily = daily.reindex(sorted(set(trading_days) | set(daily.index)), fill_value=0.0)
    d_std = float(daily.std(ddof=1)) if len(daily) > 1 else 0.0
    sharpe = float(daily.mean() / d_std * np.sqrt(252)) if d_std > 0 else 0.0

    months = pd.Series(pnls).groupby([pd.Timestamp(t.exit_time).strftime("%Y-%m") for t in trades]).sum()
    n_days = len(daily) if len(daily) else 1

    std = float(np.std(pnls, ddof=1)) if len(pnls) > 1 else 0.0
    return {
        "total_trades": len(trades),
        "win_rate_pct": round(100.0 * len(wins) / len(trades), 2),
        "net_pnl_usd": round(float(pnls.sum()), 2),
        "profit_factor": round(pf, 2),
        "max_drawdown_usd": round(max_drawdown(pnls), 2),
        "avg_trade_usd": round(float(pnls.mean()), 2),
        "expectancy_r": round(float(r_mult.mean()), 3) if len(r_mult) else 0.0,
        "avg_win_usd": round(float(wins.mean()), 2) if len(wins) else 0.0,
        "avg_loss_usd": round(float(losses.mean()), 2) if len(losses) else 0.0,
        "scratch_pct": round(100.0 * float(scratch.mean()), 1),
        "win_rate_ex_scratch_pct": round(wr_ex, 2),
        "sharpe_daily_ann": round(sharpe, 2),
        "trade_t_stat": round(float(pnls.mean() / std * np.sqrt(len(pnls))), 2) if std > 0 else 0.0,
        "longest_losing_streak": longest_losing_streak(pnls),
        "profitable_months": f"{int((months > 0).sum())}/{len(months)}",
        "trades_per_day": round(len(trades) / n_days, 3),
    }


def bootstrap(pnls: Sequence[float], n_iter: int = 5000, seed: int = 7) -> Dict[str, float]:
    """Resample trades with replacement; report the spread of total PnL and max drawdown."""
    arr = np.asarray(pnls, dtype=float)
    if len(arr) < 5:
        return {}
    rng = np.random.default_rng(seed)
    n = len(arr)
    idx = rng.integers(0, n, size=(n_iter, n))
    paths = arr[idx]
    totals = paths.sum(axis=1)
    eq = np.concatenate([np.zeros((n_iter, 1)), np.cumsum(paths, axis=1)], axis=1)
    dd = (np.maximum.accumulate(eq, axis=1) - eq).max(axis=1)
    return {
        "pnl_p05": round(float(np.percentile(totals, 5)), 2),
        "pnl_p50": round(float(np.percentile(totals, 50)), 2),
        "pnl_p95": round(float(np.percentile(totals, 95)), 2),
        "prob_net_loss_pct": round(float((totals <= 0).mean() * 100), 1),
        "maxdd_p50": round(float(np.percentile(dd, 50)), 2),
        "maxdd_p95": round(float(np.percentile(dd, 95)), 2),
    }
