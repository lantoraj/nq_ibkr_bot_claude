"""
Economic-event calendar.

CSV columns: datetime_et (naive, US/Eastern wall clock), name, tier (1 = market-moving: FOMC/CPI/NFP, 2 = other),
and any extra columns (e.g. source) which are ignored. Keep this file current: the filter can only avoid events
it knows about. `is_stale()` lets the live runner warn when nothing upcoming is listed.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pandas as pd

from config import ContextConfig


@dataclass(frozen=True)
class Event:
    time: pd.Timestamp      # tz-aware
    name: str
    tier: int


class EventCalendar:
    def __init__(self, events: List[Event], cfg: ContextConfig, bar_seconds: int, tz: str) -> None:
        self.events = sorted(events, key=lambda e: e.time)
        self.cfg = cfg
        self.bar = pd.Timedelta(seconds=bar_seconds)
        self.tz = tz

    @classmethod
    def from_csv(cls, path: str, cfg: ContextConfig, bar_seconds: int, tz: str) -> "EventCalendar":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Event calendar not found: {path}")
        df = pd.read_csv(p)
        events = [
            Event(pd.Timestamp(r.datetime_et).tz_localize(tz), str(r.name_), int(r.tier))
            for r in df.rename(columns={"name": "name_"}).itertuples()
        ]
        return cls(events, cfg, bar_seconds, tz)

    # -- queries use the bar CLOSE time, because that is when an order would actually be placed -------------
    def _close(self, bar_start: pd.Timestamp) -> pd.Timestamp:
        t = pd.Timestamp(bar_start)
        t = t.tz_localize(self.tz) if t.tzinfo is None else t.tz_convert(self.tz)
        return t + self.bar

    def blocks_entry(self, bar_start: pd.Timestamp) -> Optional[str]:
        t = self._close(bar_start)
        c = self.cfg
        if c.skip_tier1_days:
            for e in self.events:
                if e.tier == 1 and e.time.date() == t.date():
                    return f"Tier-1 event day: {e.name}"
        for e in self.events:
            if e.time - pd.Timedelta(minutes=c.event_block_before_min) <= t <= e.time + pd.Timedelta(minutes=c.event_block_after_min):
                return f"Event window: {e.name}"
        return None

    def flatten_due(self, bar_start: pd.Timestamp) -> Optional[str]:
        """True from N min before an event until it passes (do not hold a position through the release)."""
        t = self._close(bar_start)
        for e in self.events:
            start = e.time - pd.Timedelta(minutes=self.cfg.event_flatten_before_min)
            if start <= t < e.time + pd.Timedelta(minutes=1):
                return f"Pre-event flatten: {e.name}"
        return None

    def is_stale(self, now: pd.Timestamp, horizon_days: int = 21) -> bool:
        now = pd.Timestamp(now)
        now = now.tz_localize(self.tz) if now.tzinfo is None else now.tz_convert(self.tz)
        return not any(now <= e.time <= now + pd.Timedelta(days=horizon_days) for e in self.events)

    def days(self, tier: Optional[int] = None) -> List:
        return sorted({e.time.date() for e in self.events if tier is None or e.tier == tier})


def build_calendar(cfg, bar_seconds: int) -> Optional[EventCalendar]:
    """Return a calendar if the event filter is enabled, else None."""
    if not cfg.context.use_event_filter:
        return None
    return EventCalendar.from_csv(cfg.context.event_file, cfg.context, bar_seconds, cfg.risk.timezone)
