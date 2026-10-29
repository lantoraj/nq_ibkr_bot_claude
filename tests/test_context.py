"""Market-context features: session context (gap / overnight), event calendar, filters, flatten-before-event."""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest import Backtester
from config import BotConfig, ContextConfig
from context import attach_session_context, session_context
from events import Event, EventCalendar
from risk_manager import RiskManager
from strategy import NQIntradayStrategy
from test_bot import OneShot

NY = "America/New_York"


def bars(spec):
    """spec: list of (ts_str, o, h, l, c)."""
    return pd.DataFrame({
        "timestamp": [pd.Timestamp(t, tz=NY) for t, *_ in spec],
        "open": [x[1] for x in spec], "high": [x[2] for x in spec], "low": [x[3] for x in spec],
        "close": [x[4] for x in spec], "volume": 100.0})


ETH = bars([
    ("2026-10-22 09:30", 100, 110, 99, 105), ("2026-10-22 15:58", 105, 108, 104, 107),   # Thu RTH, last close 107
    ("2026-10-22 16:10", 107, 112, 106, 111),                                            # post-close -> Fri session
    ("2026-10-22 19:00", 111, 120, 109, 118),                                            # Globex evening -> Fri
    ("2026-10-23 03:00", 118, 119, 95, 100),                                             # pre-open
    ("2026-10-23 09:30", 102, 106, 101, 104), ("2026-10-23 15:58", 104, 105, 103, 104),  # Fri RTH, close 104
    ("2026-10-23 16:30", 104, 104, 90, 91),                                              # Fri evening -> Saturday (ignored)
    ("2026-10-25 18:00", 91, 93, 80, 92),                                                # Sunday open -> Monday
    ("2026-10-26 04:00", 92, 99, 91, 98),
    ("2026-10-26 09:30", 97, 100, 96, 99),
])


def test_gap_and_overnight_range_with_eth_data():
    ctx = session_context(ETH, NY)
    fri, mon = ctx.loc[pd.Timestamp("2026-10-23").date()], ctx.loc[pd.Timestamp("2026-10-26").date()]
    assert fri.prev_close == 107 and fri.gap_pts == 102 - 107
    assert fri.on_high == 120 and fri.on_low == 95                  # 16:10 + 19:00 + 03:00 bars
    assert mon.prev_close == 104 and mon.gap_pts == 97 - 104
    assert mon.on_high == 99 and mon.on_low == 80                   # Sunday 18:00 -> Monday; Friday evening excluded


def test_overnight_is_nan_without_preopen_coverage():
    rth_plus_postclose = ETH[~ETH["timestamp"].dt.strftime("%H:%M").isin(["03:00", "04:00", "19:00", "18:00"])]
    ctx = session_context(rth_plus_postclose, NY)
    assert ctx["on_high"].isna().all()                              # 16:xx bars alone are not an overnight range
    assert ctx.loc[pd.Timestamp("2026-10-23").date(), "gap_pts"] == -5


def test_attach_context_maps_to_rows():
    out = attach_session_context(ETH, NY)
    row = out[out["timestamp"] == pd.Timestamp("2026-10-23 09:30", tz=NY)].iloc[0]
    assert row.gap_pts == -5 and row.on_high == 120


# ----------------------------------------------------------------------------- event calendar
def cal(**kw):
    cfg = ContextConfig(use_event_filter=True, **kw)
    ev = [Event(pd.Timestamp("2026-10-28 14:00", tz=NY), "FOMC", 1), Event(pd.Timestamp("2026-10-29 10:00", tz=NY), "ISM", 2)]
    return EventCalendar(ev, cfg, 120, NY)


def test_entry_blocked_in_window_using_bar_close():
    c = cal(event_block_before_min=10, event_block_after_min=15)
    t = lambda s: pd.Timestamp(f"2026-10-29 {s}", tz=NY)
    assert c.blocks_entry(t("09:44")) is None            # closes 09:46 -> 14 min before: outside
    assert c.blocks_entry(t("09:50")) is not None        # closes 09:52 -> inside
    assert c.blocks_entry(t("10:12")) is not None        # closes 10:14 -> inside (<= +15)
    assert c.blocks_entry(t("10:16")) is None


def test_flatten_due_only_near_event():
    c = cal(event_flatten_before_min=5)
    assert c.flatten_due(pd.Timestamp("2026-10-28 13:50", tz=NY)) is None
    assert c.flatten_due(pd.Timestamp("2026-10-28 13:56", tz=NY)) is not None     # closes 13:58
    assert c.flatten_due(pd.Timestamp("2026-10-28 14:10", tz=NY)) is None


def test_skip_tier1_days_only_skips_tier1():
    c = cal(skip_tier1_days=True, event_block_before_min=0, event_block_after_min=0)
    assert c.blocks_entry(pd.Timestamp("2026-10-28 10:30", tz=NY)) is not None
    assert c.blocks_entry(pd.Timestamp("2026-10-29 11:00", tz=NY)) is None        # tier-2 day not skipped


def test_stale_calendar_detection():
    c = cal()
    assert not c.is_stale(pd.Timestamp("2026-10-20", tz=NY))
    assert c.is_stale(pd.Timestamp("2026-12-01", tz=NY))


def test_risk_manager_blocks_entries_inside_event_window():
    cfg = BotConfig()
    rm = RiskManager(cfg.risk, cfg.contract)
    rm.calendar = cal()
    ok, why = rm.can_open_trade(pd.Timestamp("2026-10-29 09:50", tz=NY), 10)
    assert not ok and "ISM" in why
    assert rm.can_open_trade(pd.Timestamp("2026-10-29 11:00", tz=NY), 20)[0]


def test_shipped_calendar_loads():
    c = EventCalendar.from_csv("data/economic_events.csv", ContextConfig(use_event_filter=True), 120, NY)
    assert len(c.days(tier=1)) >= 9 and pd.Timestamp("2026-09-16").date() in c.days()


# ----------------------------------------------------------------------------- strategy filters
def row(**kw):
    base = dict(close=100.0, open=99.0, vwap=95.0, ema_trend=95.0, ema_fast=99.0, ema_slow=97.0, slow_slope_atr=0.5,
                pdh=np.nan, pdl=np.nan, on_high=np.nan, on_low=np.nan, gap_pts=np.nan, prev_close=np.nan)
    base.update(kw)
    return pd.Series(base)


def strat(**ctx):
    cfg = BotConfig()
    return NQIntradayStrategy(cfg.strategy, cfg.risk, cfg.contract, ContextConfig(**ctx))


def test_overnight_guard_blocks_longs_below_wall_and_shorts_above_floor():
    s = strat(use_overnight_guard=True, overnight_buffer_atr=0.5)
    assert s._regime_ok(1, row(on_high=105.0), atr=20.0) is False        # 5 pts < 10 pts buffer
    assert s._regime_ok(1, row(on_high=130.0), atr=20.0) is True
    assert s._regime_ok(1, row(on_high=np.nan), atr=20.0) is True        # no ETH data -> no-op
    assert strat()._regime_ok(1, row(on_high=105.0), atr=20.0) is True   # disabled by default


def test_gap_filter_blocks_counter_gap_trades_until_filled():
    s = strat(use_gap_filter=True, gap_min_prior_range=0.25)
    rng = dict(pdh=160.0, pdl=60.0)                                       # prior-day range 100 -> threshold 25 pts
    up_gap = dict(gap_pts=30.0, prev_close=90.0, **rng)                   # gapped up, price 100 still above prev close
    assert s._regime_ok(1, row(**up_gap), atr=20.0) is True               # long with the gap
    short_row = row(close=100.0, open=101.0, vwap=105, ema_trend=105, ema_fast=101, ema_slow=103, slow_slope_atr=-0.5, **up_gap)
    assert s._regime_ok(-1, short_row, atr=20.0) is False                 # short against unfilled gap
    filled = row(close=88.0, open=89, vwap=95, ema_trend=95, ema_fast=90, ema_slow=92, slow_slope_atr=-0.5, **up_gap)
    assert s._regime_ok(-1, filled, atr=20.0) is True                     # gap filled (close < prev_close)
    small = dict(gap_pts=10.0, prev_close=90.0, **rng)
    assert s._regime_ok(-1, row(close=100.0, open=101.0, vwap=105, ema_trend=105, ema_fast=101, ema_slow=103,
                                slow_slope_atr=-0.5, **small), atr=20.0) is True   # gap below 25% of prior range


# ----------------------------------------------------------------------------- backtest: never hold through the event
def test_backtest_flattens_before_fomc():
    ts = pd.date_range("2026-10-28 13:30", periods=12, freq="2min", tz=NY)          # 13:30 .. 13:52
    f = pd.DataFrame({"timestamp": ts, "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1000.0})
    f.loc[3:, ["open", "high", "low", "close"]] = [100.5, 101.5, 99.5, 100.5]
    f = pd.concat([f, pd.DataFrame({"timestamp": pd.date_range("2026-10-28 13:54", periods=4, freq="2min", tz=NY),
                                    "open": 100.5, "high": 101.5, "low": 99.5, "close": 100.5, "volume": 1000.0})],
                  ignore_index=True)
    cfg = BotConfig()
    cfg.context.use_event_filter = True
    cfg.context.event_file = "data/economic_events.csv"       # contains 2026-10-28 14:00 FOMC
    cfg.risk.entry_end_time = "15:00"                         # let the stub signal fire in the afternoon
    cfg.costs.commission_per_side_usd = 0.01
    bt = Backtester(cfg, strategy=OneShot(0))
    res = bt.run(enriched=f)
    t = res["trades"]
    assert len(t) == 1 and t[0].exit_reason == "Event Flatten"
    assert pd.Timestamp(t[0].exit_time) <= pd.Timestamp("2026-10-28 13:58", tz=NY)
