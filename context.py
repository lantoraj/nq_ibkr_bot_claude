"""
Session context features attached to every bar:

  prev_close   last RTH close of the previous session
  gap_pts      RTH open minus prev_close
  on_high/low  overnight (post-close + Globex) high/low that precedes the session; NaN unless the data really
               contains pre-open bars for that session (a CSV that only has 09:30+ bars yields NaN, never a
               misleading partial range)

Compute on the FULL (ETH) frame, then drop non-RTH bars.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from indicators import to_session_time

CONTEXT_COLS = ["prev_close", "gap_pts", "on_high", "on_low"]


def session_context(df: pd.DataFrame, tz: str, rth_open: str = "09:30", rth_close: str = "16:00") -> pd.DataFrame:
    """Return one row per RTH session date with CONTEXT_COLS."""
    ts = to_session_time(df["timestamp"], tz)
    hhmm = ts.dt.strftime("%H:%M")
    date = ts.dt.date
    is_rth = (hhmm >= rth_open) & (hhmm < rth_close)

    rth = df[is_rth].assign(_d=date[is_rth])
    g = rth.groupby("_d")
    day = pd.DataFrame({"rth_open_px": g["open"].first(), "rth_last_close": g["close"].last()}).sort_index()
    day["prev_close"] = day["rth_last_close"].shift(1)
    day["gap_pts"] = day["rth_open_px"] - day["prev_close"]

    # assign non-RTH bars to the session they precede: evening bars -> next calendar day, early bars -> same day
    eth = ~is_rth
    sess = pd.Series(pd.NaT, index=df.index, dtype="object")
    evening = eth & (hhmm >= rth_close)
    morning = eth & (hhmm < rth_open)
    sess[evening] = (pd.to_datetime(date[evening]) + pd.Timedelta(days=1)).dt.date
    sess[morning] = date[morning]
    e = df[evening | morning].assign(_s=sess[evening | morning], _pre=(morning[evening | morning]))
    if e.empty:
        day["on_high"] = np.nan
        day["on_low"] = np.nan
    else:
        ge = e.groupby("_s")
        on = pd.DataFrame({"on_high": ge["high"].max(), "on_low": ge["low"].min(), "has_pre": ge["_pre"].any()})
        on.loc[~on["has_pre"], ["on_high", "on_low"]] = np.nan      # require real pre-open coverage
        day = day.join(on[["on_high", "on_low"]], how="left")
    for c in ("on_high", "on_low"):
        if c not in day:
            day[c] = np.nan
    return day[CONTEXT_COLS]


def attach_session_context(df: pd.DataFrame, tz: str, rth_open: str = "09:30", rth_close: str = "16:00") -> pd.DataFrame:
    """Merge per-session context onto every row of df by session date."""
    ctx = session_context(df, tz, rth_open, rth_close)
    dates = to_session_time(df["timestamp"], tz).dt.date
    out = df.copy()
    for c in CONTEXT_COLS:
        out[c] = dates.map(ctx[c])
    return out
