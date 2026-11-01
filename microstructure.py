"""
Tick-level microstructure features and a net-of-cost event study.

Inputs
  quotes: ts (UTC datetime), bid, ask, bid_size, ask_size        (one row per top-of-book change)
  trades: ts (UTC datetime), price, size

Features on a 1-second grid
  qi        queue imbalance   (bid_size - ask_size) / (bid_size + ask_size)
  micro_dev microprice - mid, in ticks  (microprice = size-weighted price, leans toward the thinner side)
  ofi_N     order-flow imbalance over N seconds (Cont-Kukanov-Stoikov): signed change in top-of-book depth
  tfi_N     trade-flow imbalance over N seconds: (buy - sell volume) / total, trades signed vs the prevailing mid

Evaluation: enter at the mid when the feature is in its top-|decile| and trade WITH its sign; exit h seconds later.
Cost is crossing the spread at both ends (market orders) plus commission, so a feature must beat roughly 2 half-spreads
before it is worth anything. Passive (limit) execution is NOT modelled: fills are adverse-selected and need a queue model.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Sequence

import numpy as np
import pandas as pd

TICK = 0.25


def _ofi_events(q: pd.DataFrame) -> pd.Series:
    """Per-update order-flow imbalance e_n (CKS 2014)."""
    bp, ap = q["bid"].to_numpy(), q["ask"].to_numpy()
    bs, as_ = q["bid_size"].to_numpy(float), q["ask_size"].to_numpy(float)
    e = np.zeros(len(q))
    for i in range(1, len(q)):
        eb = bs[i] if bp[i] > bp[i - 1] else (bs[i] - bs[i - 1] if bp[i] == bp[i - 1] else -bs[i - 1])
        ea = -as_[i] if ap[i] < ap[i - 1] else (-(as_[i] - as_[i - 1]) if ap[i] == ap[i - 1] else as_[i - 1])
        e[i] = eb + ea
    return pd.Series(e, index=q["ts"])


def build_grid(quotes: pd.DataFrame, trades: pd.DataFrame, windows: Sequence[int] = (5, 15), tick: float = TICK) -> pd.DataFrame:
    q = quotes.sort_values("ts").reset_index(drop=True)
    q = q[(q["ask"] > q["bid"]) & (q["bid_size"] + q["ask_size"] > 0)]
    ofi = _ofi_events(q).resample("1s").sum()
    g = q.set_index("ts")[["bid", "ask", "bid_size", "ask_size"]].resample("1s").last().ffill(limit=30)
    g["mid"] = (g["bid"] + g["ask"]) / 2
    g["spread"] = g["ask"] - g["bid"]
    g["qi"] = (g["bid_size"] - g["ask_size"]) / (g["bid_size"] + g["ask_size"])
    micro = (g["ask"] * g["bid_size"] + g["bid"] * g["ask_size"]) / (g["bid_size"] + g["ask_size"])
    g["micro_dev"] = (micro - g["mid"]) / tick
    ofi = ofi.reindex(g.index).fillna(0.0)
    if len(trades):
        t = trades.sort_values("ts")
        mid_at = pd.merge_asof(t, g[["mid"]].reset_index().rename(columns={"index": "ts"}), on="ts", direction="backward")
        sign = np.sign(mid_at["price"] - mid_at["mid"]).fillna(0.0)
        t = t.assign(buy=np.where(sign > 0, t["size"], 0.0), sell=np.where(sign < 0, t["size"], 0.0)).set_index("ts")
        buy = t["buy"].resample("1s").sum().reindex(g.index).fillna(0.0)
        sell = t["sell"].resample("1s").sum().reindex(g.index).fillna(0.0)
    else:
        buy = sell = pd.Series(0.0, index=g.index)
    for w in windows:
        g[f"ofi_{w}"] = ofi.rolling(w, min_periods=1).sum()
        b, s = buy.rolling(w, min_periods=1).sum(), sell.rolling(w, min_periods=1).sum()
        g[f"tfi_{w}"] = ((b - s) / (b + s).replace(0, np.nan)).fillna(0.0)
    return g.dropna(subset=["mid", "qi"])


def evaluate(grid: pd.DataFrame, features: Iterable[str], horizons: Sequence[int] = (1, 2, 5, 10, 30),
             top_frac: float = 0.10, commission_pts: float = 0.31) -> pd.DataFrame:
    """commission_pts: round-trip commission in points (MNQ 1.24 USD / 2 = 0.62; NQ 4.2 / 20 = 0.21; per side halves it)."""
    rows: List[Dict] = []
    mid, spread = grid["mid"].to_numpy(), grid["spread"].to_numpy()
    half = len(grid) // 2
    for f in features:
        x = grid[f].to_numpy()
        thr = np.nanquantile(np.abs(x), 1 - top_frac)
        cand = np.flatnonzero((np.abs(x) >= thr) & (np.abs(x) > 0))
        for h in horizons:
            idx, last = [], -10 ** 9
            for i in cand:                                    # de-cluster: events at least h seconds apart
                if i + h < len(grid) and i - last >= max(h, 1):
                    idx.append(i)
                    last = i
            idx = np.array(idx, dtype=int)
            if len(idx) < 30:
                continue
            gross = np.sign(x[idx]) * (mid[idx + h] - mid[idx])
            cost = (spread[idx] + spread[idx + h]) / 2 + commission_pts
            net = gross - cost
            sd = net.std(ddof=1)
            rows.append({"feature": f, "hold_sec": h, "n": len(idx), "gross_pts": gross.mean(), "cost_pts": cost.mean(),
                         "net_pts": net.mean(), "t_net": net.mean() / sd * np.sqrt(len(idx)) if sd > 0 else 0.0,
                         "gross_t": gross.mean() / gross.std(ddof=1) * np.sqrt(len(idx)) if gross.std(ddof=1) > 0 else 0.0,
                         "net_1st_half": net[idx < half].mean() if (idx < half).any() else np.nan,
                         "net_2nd_half": net[idx >= half].mean() if (idx >= half).any() else np.nan})
    return pd.DataFrame(rows)
