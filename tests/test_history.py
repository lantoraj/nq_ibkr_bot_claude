"""Offline tests for the long-history pipeline (roll rule, chunked download, back-adjusted stitching)."""
from __future__ import annotations

from datetime import date
from types import SimpleNamespace

import numpy as np
import pandas as pd

from history import COLS, download_chunked, segments_from_details, stitch


def det(conid, expiry):
    return SimpleNamespace(contract=SimpleNamespace(conId=conid, lastTradeDateOrContractMonth=expiry, localSymbol=f"C{conid}"))


DETAILS = [det(3, "20260320"), det(1, "20250919"), det(2, "20251219"), det(4, "20260618")]


def test_segments_follow_the_live_roll_rule():
    segs = segments_from_details(DETAILS, date(2025, 8, 1), date(2026, 3, 1), roll_days=8)
    ids = [s.contract.conId for s in segs]
    assert ids == [1, 2, 3]
    assert segs[0].end == pd.Timestamp("2025-09-11", tz="UTC") and segs[1].start == segs[0].end    # 19 Sep - 8 days
    assert segs[1].end == pd.Timestamp("2025-12-11", tz="UTC")
    assert segs[0].start == pd.Timestamp("2025-08-01", tz="UTC") and segs[2].end == pd.Timestamp("2026-03-01", tz="UTC")


def bars(start, n, base, freq="2min"):
    ts = pd.date_range(start, periods=n, freq=freq, tz="UTC")
    px = base + np.arange(n, dtype=float)
    return pd.DataFrame({"timestamp": ts, "open": px, "high": px + 1, "low": px - 1, "close": px, "volume": 10.0})


def test_stitch_removes_the_roll_gap_and_keeps_latest_prices():
    # contract A trades 100..; contract B trades the same moves with a +50 spread; roll at bar 5
    a = bars("2026-01-05 15:00", 10, 100)
    b = bars("2026-01-05 15:00", 10, 150)
    roll = pd.Timestamp("2026-01-05 15:10", tz="UTC")                       # == timestamp of bar index 5
    out = stitch([a, b], [roll])
    assert len(out) == 10 and out["timestamp"].is_monotonic_increasing
    assert out["close"].diff().dropna().eq(1.0).all()                      # no jump at the roll
    assert out["close"].iloc[-1] == 159.0                                   # newest segment unadjusted
    assert out["close"].iloc[0] == 150.0                                    # older segment shifted up by the spread


def test_stitch_three_contracts_accumulates_spreads():
    a = bars("2026-01-05 15:00", 10, 100)
    b = bars("2026-01-05 15:00", 10, 130)       # +30 over A
    c = bars("2026-01-05 15:00", 10, 135)       # +5 over B
    out = stitch([a, b, c], [pd.Timestamp("2026-01-05 15:06", tz="UTC"), pd.Timestamp("2026-01-05 15:12", tz="UTC")])
    assert out["close"].diff().dropna().eq(1.0).all()
    assert out["close"].iloc[-1] == 144.0 and out["close"].iloc[0] == 135.0


def test_download_chunked_walks_backwards_and_dedups():
    full = bars("2026-01-05 14:00", 60, 100)
    calls = []

    def fetch(contract, end):
        calls.append(end)
        d = full[full["timestamp"] <= end].tail(20)           # each call returns up to 20 bars ending at 'end'
        return d

    out = download_chunked(fetch, object(), full["timestamp"].min(), full["timestamp"].max() + pd.Timedelta(minutes=2))
    assert len(out) == 60 and out["timestamp"].is_unique and len(calls) >= 3
    assert list(out.columns) == COLS


def test_download_chunked_stops_on_empty():
    out = download_chunked(lambda c, e: pd.DataFrame(columns=COLS), object(), pd.Timestamp("2026-01-01", tz="UTC"),
                           pd.Timestamp("2026-02-01", tz="UTC"))
    assert out.empty
