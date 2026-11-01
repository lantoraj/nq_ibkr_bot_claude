"""Validate the research labs themselves: null data must give (almost) no findings, planted effects must be found."""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest import Backtester
from config import BotConfig
from microstructure import build_grid, evaluate
from scalp_lab import cost_points, run_lab
from tick_recorder import TickWriter

NY = "America/New_York"


def bars(days: int, phi: float, seed: int) -> pd.DataFrame:
    """2-minute RTH bars from an AR(1) return process (phi=0 -> random walk, phi<0 -> mean reverting)."""
    rng = np.random.default_rng(seed)
    rows, price = [], 20000.0
    for d in pd.bdate_range("2026-03-02", periods=days):
        ts = pd.date_range(f"{d.date()} 09:30", f"{d.date()} 15:58", freq="2min", tz=NY)
        r_prev = 0.0
        for t in ts:
            r = phi * r_prev + rng.normal(0, 3.0)
            o, c = price, price + r
            rows.append((t, o, max(o, c) + abs(rng.normal(0, 1)), min(o, c) - abs(rng.normal(0, 1)), c, 1000 + rng.integers(0, 500)))
            price, r_prev = c, r
    return pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume"])


def lab(df: pd.DataFrame) -> pd.DataFrame:
    return run_lab(Backtester(BotConfig()).enrich(df), NY)


def test_scalp_lab_finds_nothing_in_a_random_walk():
    res = lab(bars(40, 0.0, seed=1))
    assert len(res) > 50
    assert (res["t_net"] > 3.6).sum() == 0                       # costs make a random walk a loser everywhere
    assert (res["net_pts_MNQ"] > 0).mean() < 0.15


def test_scalp_lab_detects_a_planted_reversal_effect():
    res = lab(bars(40, -0.5, seed=2))
    hit = res[(res["mode"] == "fade") & (res["t_net"] > 3.6)]
    assert len(hit) > 0 and (hit["net_1st_half"] > 0).any()


def test_cost_model_nq_is_cheaper_per_point_than_mnq():
    assert abs(cost_points("MNQ") - 1.12) < 1e-9 and abs(cost_points("NQ") - 0.71) < 1e-9


# ----------------------------------------------------------------------------- tick lab
def ticks(seconds: int, planted: bool, seed: int):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2026-11-02 14:30", periods=seconds, freq="1s", tz="UTC")
    bid_t = np.zeros(seconds, dtype=int)
    bsz, asz = rng.integers(5, 60, seconds).astype(float), rng.integers(5, 60, seconds).astype(float)
    qi = (bsz - asz) / (bsz + asz)
    bid_t[0] = 80000
    for t in range(1, seconds):
        drift = 4.0 * qi[t - 1] if planted else 0.0
        bid_t[t] = bid_t[t - 1] + int(round(drift + rng.normal(0, 0.6)))
    bid = bid_t * 0.25
    q = pd.DataFrame({"ts": idx, "bid": bid, "ask": bid + 0.25, "bid_size": bsz, "ask_size": asz})
    tr = pd.DataFrame({"ts": idx[::3], "price": bid[::3] + 0.25 * rng.integers(0, 2, len(idx[::3])), "size": 1.0})
    return q, tr


def test_tick_lab_null_has_no_gross_edge():
    q, tr = ticks(20000, planted=False, seed=3)
    res = evaluate(build_grid(q, tr), ["qi", "micro_dev", "ofi_5", "tfi_5"])
    assert len(res) > 0 and res["gross_t"].abs().max() < 4.0


def test_tick_lab_detects_planted_queue_imbalance_effect():
    q, tr = ticks(20000, planted=True, seed=4)
    res = evaluate(build_grid(q, tr), ["qi", "micro_dev"], horizons=(1, 2, 5))
    best = res[res["feature"] == "qi"].sort_values("gross_t", ascending=False).iloc[0]
    assert best["gross_t"] > 6 and best["gross_pts"] > 0
    # crossing the spread twice + commission is a real hurdle: cost is at least one spread plus commission
    assert (res["cost_pts"] >= 0.25 + 0.31 - 1e-9).all()


def test_tick_writer_writes_rotated_csvs(tmp_path):
    class TickByTickBidAsk:
        def __init__(self, t): self.time, self.bidPrice, self.askPrice, self.bidSize, self.askSize = t, 100.0, 100.25, 10, 12

    class TickByTickAllLast:
        def __init__(self, t): self.time, self.price, self.size = t, 100.25, 2

    w = TickWriter(str(tmp_path), "MNQ")
    t1 = pd.Timestamp("2026-11-02 14:30:00", tz="UTC").to_pydatetime()
    t2 = pd.Timestamp("2026-11-03 14:30:00", tz="UTC").to_pydatetime()
    for t in (t1, t2):
        w.write(TickByTickBidAsk(t))
        w.write(TickByTickAllLast(t))
    w.close()
    names = sorted(p.name for p in tmp_path.iterdir())
    assert names == ["MNQ_quotes_20261102.csv", "MNQ_quotes_20261103.csv", "MNQ_trades_20261102.csv", "MNQ_trades_20261103.csv"]
    q = pd.read_csv(tmp_path / "MNQ_quotes_20261102.csv")
    assert list(q.columns) == ["ts", "bid", "ask", "bid_size", "ask_size"] and len(q) == 1
