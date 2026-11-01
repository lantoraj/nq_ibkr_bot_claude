"""
Tick event study: python tick_lab.py --quotes data/ticks/MNQ_quotes_20261102.csv --trades data/ticks/MNQ_trades_20261102.csv
Accepts several files via glob patterns. Prints a net-of-cost table; see microstructure.py for the cost model.
"""
from __future__ import annotations

import argparse
import glob

import pandas as pd

from microstructure import build_grid, evaluate


def load(pattern: str, cols) -> pd.DataFrame:
    files = sorted(glob.glob(pattern))
    if not files:
        raise SystemExit(f"no files match {pattern}")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quotes", required=True)
    ap.add_argument("--trades", required=True)
    ap.add_argument("--symbol", default="MNQ", choices=["MNQ", "NQ"])
    ap.add_argument("--top-frac", type=float, default=0.10)
    a = ap.parse_args()
    comm = 2 * (0.62 if a.symbol == "MNQ" else 2.10) / (2.0 if a.symbol == "MNQ" else 20.0)
    grid = build_grid(load(a.quotes, None), load(a.trades, None))
    feats = [c for c in grid.columns if c in ("qi", "micro_dev") or c.startswith(("ofi_", "tfi_"))]
    res = evaluate(grid, feats, top_frac=a.top_frac, commission_pts=comm)
    pd.set_option("display.width", 200)
    print(res.sort_values("t_net", ascending=False).round(3).head(20).to_string(index=False))
    print(f"\n{len(res)} variants; positive net with t>2: {(res['t_net'] > 2).sum()} (about {len(res) * 0.025:.0f} expected by chance)")


if __name__ == "__main__":
    main()
