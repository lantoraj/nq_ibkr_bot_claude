"""
Scalp signal lab: does ANY short-horizon signal beat transaction costs on MNQ/NQ bars?

Event study, not a strategy. For every candidate signal (an "up extreme" or "down extreme") we measure the forward
move over 1..N bars after a realistic entry (next bar open), both when FOLLOWING and when FADING the extreme, then
subtract round-trip costs. ~300 variants are tested, so we report how many pass at |t| > 2 versus the number expected by
chance, and require a Bonferroni-style bar plus consistency across both halves before calling anything a candidate.

Usage: python scalp_lab.py --csv data/mnq_2m_3months.csv --out reports/scalp_report.md
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Dict, List

import numpy as np
import pandas as pd

from backtest import Backtester
from config import BotConfig
from indicators import compute_rsi, to_session_time

HORIZONS = [1, 2, 3, 4, 6]            # bars held after the entry bar (2-min bars -> 2..12 minutes)
COOLDOWN = 5                           # bars to skip after an event (de-clustering)
WINDOW = ("09:45", "15:25")            # entry window (bar start, ET)


def cost_points(symbol: str, slip_ticks: int = 1, tick: float = 0.25) -> float:
    comm, pv = (0.62, 2.0) if symbol == "MNQ" else (2.10, 20.0)
    return 2 * comm / pv + 2 * slip_ticks * tick


def build_features(e: pd.DataFrame, tz: str) -> pd.DataFrame:
    f = e.copy()
    ts = to_session_time(f["timestamp"], tz)
    f["_date"] = ts.dt.date
    f["_hhmm"] = ts.dt.strftime("%H:%M")
    rng = (f["high"] - f["low"]).replace(0, np.nan)
    f["ibs"] = (f["close"] - f["low"]) / rng
    f["rsi2"] = compute_rsi(f["close"], 2)
    sma, sd = f["close"].rolling(20).mean(), f["close"].rolling(20).std()
    f["bb_z"] = (f["close"] - sma) / sd
    f["ema_dist"] = (f["close"] - f["ema_fast"]) / f["atr"]
    f["zret3"] = (f["close"] - f["close"].shift(3)) / f["atr"]
    f["ret1"] = f["close"].diff()
    return f


def signal_catalogue(f: pd.DataFrame) -> Dict[str, pd.Series]:
    """name -> series of +1 (up extreme), -1 (down extreme), 0 (none)."""
    def two_sided(up: pd.Series, dn: pd.Series) -> pd.Series:
        return up.astype(int) - dn.astype(int)

    sig: Dict[str, pd.Series] = {}
    for k in (1.0, 1.5, 2.0, 2.5):
        sig[f"vwap_z >= {k}"] = two_sided(f["vwap_z"] >= k, f["vwap_z"] <= -k)
    for k in (0.75, 1.25, 1.75):
        sig[f"close-EMA9 >= {k} ATR"] = two_sided(f["ema_dist"] >= k, f["ema_dist"] <= -k)
    for hi in (90, 95):
        sig[f"RSI(2) >= {hi}"] = two_sided(f["rsi2"] >= hi, f["rsi2"] <= 100 - hi)
    big = (f["high"] - f["low"]) >= f["atr"]
    sig["IBS extreme (>=0.9 / <=0.1), range >= ATR"] = two_sided((f["ibs"] >= 0.9) & big, (f["ibs"] <= 0.1) & big)
    for k in (2.0, 2.5):
        sig[f"Bollinger(20) z >= {k}"] = two_sided(f["bb_z"] >= k, f["bb_z"] <= -k)
    for k in (1.5, 2.0, 3.0):
        sig[f"3-bar return >= {k} ATR"] = two_sided(f["zret3"] >= k, f["zret3"] <= -k)
    spike = f["vol_ratio"] >= 2.0
    sig["volume spike >= 2x (bar colour)"] = two_sided(spike & (f["close"] > f["open"]), spike & (f["close"] < f["open"]))
    after_orb = f["_hhmm"] >= "10:00"
    up = after_orb & (f["close"] > f["orb_high"]) & (f["close"].shift(1) <= f["orb_high"])
    dn = after_orb & (f["close"] < f["orb_low"]) & (f["close"].shift(1) >= f["orb_low"])
    sig["opening-range break"] = two_sided(up, dn)
    return sig


def forward_pnl(f: pd.DataFrame, h: int) -> np.ndarray:
    """Gross points for a LONG entered at next bar open and exited at the close h bars later (same session only)."""
    entry = f["open"].shift(-1).to_numpy()
    exit_ = f["close"].shift(-h).to_numpy()
    same_day = (f["_date"].shift(-h) == f["_date"]).to_numpy()
    before_close = (f["_hhmm"].shift(-h) <= "15:55").to_numpy()
    out = exit_ - entry
    out[~(same_day & before_close)] = np.nan
    return out


def run_lab(e: pd.DataFrame, tz: str = "America/New_York") -> pd.DataFrame:
    f = build_features(e, tz)
    in_window = ((f["_hhmm"] >= WINDOW[0]) & (f["_hhmm"] <= WINDOW[1])).to_numpy()
    half = len(f) // 2
    mnq, nq = cost_points("MNQ"), cost_points("NQ")
    fwd = {h: forward_pnl(f, h) for h in HORIZONS}
    rows: List[Dict] = []
    for name, s in signal_catalogue(f).items():
        sv = s.to_numpy()
        idx, last = [], -10 ** 9
        for i in np.flatnonzero((sv != 0) & in_window):          # de-cluster
            if i - last >= COOLDOWN:
                idx.append(i)
                last = i
        idx = np.array(idx, dtype=int)
        for mode, mult in (("follow", 1), ("fade", -1)):
            for h in HORIZONS:
                g = fwd[h][idx] * sv[idx] * mult
                ok = ~np.isnan(g)
                g, ii = g[ok], idx[ok]
                if len(g) < 25:
                    continue
                net = g - mnq
                sd = net.std(ddof=1)
                rows.append({
                    "signal": name, "mode": mode, "hold_min": 2 * h, "n": len(g),
                    "gross_pts": g.mean(), "net_pts_MNQ": net.mean(), "net_pts_NQ": (g - nq).mean(),
                    "t_net": net.mean() / sd * np.sqrt(len(g)) if sd > 0 else 0.0,
                    "win_pct": 100 * (net > 0).mean(),
                    "net_1st_half": net[ii < half].mean() if (ii < half).any() else np.nan,
                    "net_2nd_half": net[ii >= half].mean() if (ii >= half).any() else np.nan,
                })
    return pd.DataFrame(rows)


def autocorr_table(f: pd.DataFrame) -> pd.DataFrame:
    r = f["ret1"].where(f["_date"] == f["_date"].shift(1))
    rows = [{"lag (bars)": k, "autocorrelation of 2-min returns": round(float(r.corr(r.shift(k))), 3)} for k in range(1, 6)]
    return pd.DataFrame(rows)


def tod_drift(f: pd.DataFrame) -> pd.DataFrame:
    g = f.assign(slot=f["_hhmm"].str[:2] + ":" + np.where(f["_hhmm"].str[3:].astype(int) < 30, "00", "30"))
    g = g[(g["_hhmm"] >= "09:30") & (g["_hhmm"] < "16:00")]
    t = g.groupby("slot")["ret1"].agg(["mean", "std", "count"])
    t["t-stat of mean"] = t["mean"] / (t["std"] / np.sqrt(t["count"]))
    return t.round(3).reset_index().rename(columns={"mean": "mean 2-min move (pts)"})[["slot", "mean 2-min move (pts)", "t-stat of mean"]]


def md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(f"{v:.2f}" if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(out) + "\n"


def report(res: pd.DataFrame, f: pd.DataFrame, n_days: int) -> str:
    n_tests = len(res)
    sig2 = int((res["t_net"].abs() > 2).sum())
    pos2 = int((res["t_net"] > 2).sum())
    exp_pos = n_tests * 0.025
    bonf = 3.6                                    # ~ two-sided p < 0.05/ (n_tests) for ~300 tests
    cand = res[(res["t_net"] > bonf) & (res["net_1st_half"] > 0) & (res["net_2nd_half"] > 0)]
    top = res.sort_values("t_net", ascending=False).head(12)
    out = ["# Scalp signal lab\n",
           f"{n_days} sessions, 2-minute MNQ bars. Entry = next bar open, exit = close after the hold, window {WINDOW[0]}-{WINDOW[1]} ET. "
           f"Costs per round trip: MNQ {cost_points('MNQ'):.2f} pts (${cost_points('MNQ') * 2:.2f}), NQ {cost_points('NQ'):.2f} pts "
           f"(${cost_points('NQ') * 20:.2f}).\n",
           f"## Multiple-testing check\n\n{n_tests} variants tested. Positive net edge with t > 2: **{pos2}** (about {exp_pos:.0f} expected by chance "
           f"alone). Variants with t > {bonf} AND positive in both halves: **{len(cand)}**.\n",
           "## Best 12 variants by net t-stat (MNQ costs)\n", md(top.round(2)),
           "## Candidates passing the strict bar\n",
           md(cand.round(2)) if len(cand) else "_None._\n",
           "## Short-horizon return autocorrelation\n", md(autocorr_table(f)),
           "A clearly negative lag-1 value means bid-ask bounce / mean reversion at this scale; clearly positive means momentum.\n",
           "## Average 2-minute move by half hour (pts)\n", md(tod_drift(f)),
           ]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/mnq_2m_3months.csv")
    ap.add_argument("--out", default="reports/scalp_report.md")
    a = ap.parse_args()
    cfg = BotConfig()
    bt = Backtester(cfg)
    e = bt.enrich(pd.read_csv(a.csv))
    f = build_features(e, cfg.risk.timezone)
    res = run_lab(e, cfg.risk.timezone)
    txt = report(res, f, f["_date"].nunique())
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(txt)
    res.to_csv(Path(a.out).with_suffix(".csv"), index=False)
    print(txt)


if __name__ == "__main__":
    main()
