"""
Long-history download for backtesting.

Why not IB's ContFuture? It is stitched without price adjustment, so every quarterly roll injects the calendar
spread (often 100-300 NQ points) as a fake overnight gap. Here each quarterly contract is downloaded in paced
chunks, contracts are switched on the SAME rule the live bot uses (`roll_days_before_expiry`), and earlier
segments are shifted by the spread at each roll (difference / "Panama" back-adjustment), so the most recent
prices are real and point moves are preserved.

Pure functions (testable offline): segments_from_details, stitch, download_chunked.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable, List, Optional

import pandas as pd

logger = logging.getLogger("nq_ibkr_bot")
COLS = ["timestamp", "open", "high", "low", "close", "volume"]
PRICE_COLS = ["open", "high", "low", "close"]


@dataclass
class Segment:
    contract: Any
    start: pd.Timestamp     # inclusive (UTC)
    end: pd.Timestamp       # exclusive (UTC)


def _expiry(c: Any) -> date:
    s = c.lastTradeDateOrContractMonth
    return datetime.strptime(s[:8], "%Y%m%d").date()


def segments_from_details(details: List[Any], start: date, end: date, roll_days: int) -> List[Segment]:
    """Which contract is 'front' when: contract i is used from roll(i-1) until roll(i), roll(i) = expiry - roll_days."""
    contracts = sorted({d.contract.conId: d.contract for d in details}.values(), key=_expiry)
    segs: List[Segment] = []
    prev_roll: Optional[date] = None
    for c in contracts:
        roll = _expiry(c) - timedelta(days=roll_days)
        seg_start = prev_roll if prev_roll is not None else date(1990, 1, 1)
        if roll > start and seg_start < end:
            s = max(seg_start, start)
            e = min(roll, end)
            if s < e:
                segs.append(Segment(c, pd.Timestamp(s, tz="UTC"), pd.Timestamp(e, tz="UTC")))
        prev_roll = roll
    return segs


def download_chunked(fetch: Callable[[Any, pd.Timestamp], pd.DataFrame], contract: Any, start: pd.Timestamp,
                     end: pd.Timestamp, pace_sec: float = 0.0, sleep: Callable[[float], None] = time.sleep) -> pd.DataFrame:
    """Walk backwards from `end`, one chunk per call, until `start` or no more data."""
    parts: List[pd.DataFrame] = []
    cursor = end
    while cursor > start:
        df = fetch(contract, cursor)
        if df is None or df.empty:
            break
        df = df[COLS]
        parts.append(df)
        earliest = pd.to_datetime(df["timestamp"], utc=True).min()
        if earliest >= cursor:                      # no progress -> stop (avoid infinite loop)
            break
        cursor = earliest
        if pace_sec:
            sleep(pace_sec)
    if not parts:
        return pd.DataFrame(columns=COLS)
    out = pd.concat(parts, ignore_index=True)
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out = out.drop_duplicates("timestamp").sort_values("timestamp")
    return out[(out["timestamp"] >= start) & (out["timestamp"] < end)].reset_index(drop=True)


def stitch(parts: List[pd.DataFrame], roll_times: List[pd.Timestamp]) -> pd.DataFrame:
    """
    parts[i] covers contract i over its own segment PLUS some overlap beyond it; roll_times[i] is the switch from
    part i to part i+1. Earlier parts are shifted so there is no jump at the switch (spread = next.close - this.close
    at the last timestamp both contracts traded at or before the roll); most recent prices stay unadjusted.
    """
    assert len(parts) == len(roll_times) + 1
    parts = [p.assign(timestamp=pd.to_datetime(p["timestamp"], utc=True)).sort_values("timestamp").reset_index(drop=True)
             for p in parts]
    shifts = [0.0] * len(parts)
    cumulative = 0.0
    for i in range(len(parts) - 2, -1, -1):
        a, b = parts[i], parts[i + 1]
        rt = roll_times[i]
        common = pd.Index(a["timestamp"]).intersection(pd.Index(b["timestamp"]))
        common = common[common <= rt]
        if len(common) == 0:                                   # no overlap: fall back to nearest closes around the roll
            ca = a[a["timestamp"] <= rt]["close"]
            cb = b[b["timestamp"] >= rt]["close"]
            spread = float(cb.iloc[0] - ca.iloc[-1]) if len(ca) and len(cb) else 0.0
            logger.warning("No overlapping bars at roll %s - spread estimated from nearest bars", rt)
        else:
            t = common.max()
            spread = float(b.loc[b["timestamp"] == t, "close"].iloc[0] - a.loc[a["timestamp"] == t, "close"].iloc[0])
        cumulative += spread
        shifts[i] = cumulative
    pieces = []
    for i, p in enumerate(parts):
        lo = roll_times[i - 1] if i > 0 else p["timestamp"].min()
        hi = roll_times[i] if i < len(roll_times) else p["timestamp"].max() + pd.Timedelta(seconds=1)
        seg = p[(p["timestamp"] >= lo) & (p["timestamp"] < hi)].copy()
        seg[PRICE_COLS] = seg[PRICE_COLS] + shifts[i]
        pieces.append(seg)
    return pd.concat(pieces, ignore_index=True)[COLS]


def download_stitched(ib: Any, cfg: Any, years: float, include_eth: bool, out_csv: str,
                      cache_dir: str = "data/cache", pace_sec: float = 10.5, chunk: str = "5 D") -> pd.DataFrame:
    """Download + roll + back-adjust. Resumable: each contract's raw bars are cached as CSV."""
    from ib_async import Future, util
    c = cfg.contract
    details = ib.reqContractDetails(Future(symbol=c.symbol, exchange=c.exchange, currency=c.currency, includeExpired=True))
    today = datetime.utcnow().date()
    start = today - timedelta(days=int(365 * years))
    segs = segments_from_details(details, start, today + timedelta(days=1), cfg.execution.roll_days_before_expiry)
    if not segs:
        raise RuntimeError("No contract segments for the requested period")
    overlap = pd.Timedelta(days=3)
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    use_rth = cfg.risk.rth_only and not include_eth

    def fetch(contract: Any, end_dt: pd.Timestamp) -> pd.DataFrame:
        bars = ib.reqHistoricalData(contract, endDateTime=end_dt.to_pydatetime(), durationStr=chunk,
                                    barSizeSetting=cfg.strategy.bar_size, whatToShow="TRADES", useRTH=use_rth,
                                    formatDate=2, keepUpToDate=False, timeout=120)
        d = util.df(bars)
        return pd.DataFrame(columns=COLS) if d is None or d.empty else d.rename(columns={"date": "timestamp"})

    parts: List[pd.DataFrame] = []
    for k, s in enumerate(segs):
        tag = f"{c.symbol}_{s.contract.lastTradeDateOrContractMonth[:8]}_{cfg.strategy.bar_size.replace(' ', '')}_{'eth' if include_eth else 'rth'}.csv"
        cache = Path(cache_dir) / tag
        if cache.exists():
            df = pd.read_csv(cache, parse_dates=["timestamp"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
            logger.info("[%d/%d] %s from cache (%d bars)", k + 1, len(segs), tag, len(df))
        else:
            logger.info("[%d/%d] downloading %s %s .. %s", k + 1, len(segs), s.contract.localSymbol, s.start.date(), s.end.date())
            df = download_chunked(fetch, s.contract, s.start - overlap, s.end + overlap, pace_sec=pace_sec, sleep=ib.sleep)
            df.to_csv(cache, index=False)
        parts.append(df)
    out = stitch(parts, [s.end for s in segs[:-1]]) if len(parts) > 1 else parts[0][COLS]
    out.to_csv(out_csv, index=False)
    logger.info("Saved %d stitched bars (%d contracts) to %s", len(out), len(parts), out_csv)
    return out
