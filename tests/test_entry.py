"""Entry-quality options: retrace limit, confirmation bar, structural stop, no-chase filter."""
from __future__ import annotations

import pandas as pd

from backtest import Backtester
from config import BotConfig
from entry import confirm_ok, plan_entry
from strategy import NQIntradayStrategy
from test_bot import OneShot, _frame
from test_execution import bar_df, make, signal as live_signal

NY = "America/New_York"


def cfg_with(**entry):
    c = BotConfig()
    c.costs.commission_per_side_usd = 0.01
    for k, v in entry.items():
        setattr(c.entry, k, v)
    return c


def sig(direction="LONG"):
    stub = OneShot(0, direction) if direction == "LONG" else OneShot(0, direction, entry=100.0, stop=110.0, tp=70.0)
    return stub.evaluate_bar(_frame([(100, 101, 99, 100)]), 0)


def test_plan_entry_marketable_is_unchanged():
    lim, s = plan_entry(sig(), cfg_with())
    assert lim == 100.25 and s.entry_price == 100.0 and s.stop_loss == 90.0


def test_plan_entry_retrace_rebases_levels_keeping_distances():
    lim, s = plan_entry(sig(), cfg_with(execution_style="retrace", retrace_atr=0.25))
    assert lim == 97.5 and s.entry_price == 97.5 and s.stop_loss == 87.5 and s.take_profit == 127.5
    assert s.stop_distance_points == 10.0
    lim, s = plan_entry(sig("SHORT"), cfg_with(execution_style="retrace", retrace_atr=0.5))
    assert lim == 105.0


def test_confirm_ok_rules():
    c = cfg_with(confirm_min_move_atr=0.1)
    s = sig()
    assert confirm_ok(s, 101.5, 99.0, 102.0, c) is True
    assert confirm_ok(s, 100.5, 99.0, 101.0, c) is False          # moved < 0.1 ATR (1 pt)
    assert confirm_ok(s, 101.5, 89.0, 102.0, c) is False          # touched the stop
    assert confirm_ok(sig("SHORT"), 98.0, 98.0, 100.0, c) is True


def test_backtest_retrace_waits_for_dip_and_rebases_exits():
    f = _frame([(100, 101, 99, 100), (99, 100, 98, 99.5), (99, 99.5, 97, 98), (98, 128, 98, 127)])
    bt = Backtester(cfg_with(execution_style="retrace", retrace_atr=0.25), strategy=OneShot(0))
    t = bt.run(enriched=f)["trades"]
    assert len(t) == 1 and t[0].entry_price == 97.5 and t[0].take_profit == 127.5 and t[0].exit_reason == "Take Profit"


def test_backtest_retrace_skips_trade_when_price_runs_away():
    f = _frame([(100, 101, 99, 100)] + [(105, 110, 104, 108)] * 6)
    assert Backtester(cfg_with(execution_style="retrace"), strategy=OneShot(0)).run(enriched=f)["trades"] == []


def test_backtest_confirmation_bar_enters_after_confirm_with_rebased_levels():
    f = _frame([(100, 101, 99, 100), (100, 102, 99.5, 101), (101, 102, 100.5, 101.5), (101.5, 140, 101, 139)])
    t = Backtester(cfg_with(confirm_bars=1), strategy=OneShot(0)).run(enriched=f)["trades"]
    assert len(t) == 1 and t[0].entry_price == 101.0 and t[0].take_profit == 131.0 and t[0].exit_reason == "Take Profit"


def test_backtest_confirmation_failure_means_no_trade():
    f = _frame([(100, 101, 99, 100), (100, 100.5, 98, 99), (99, 100, 98, 99.5), (99, 140, 98, 139)])
    assert Backtester(cfg_with(confirm_bars=1), strategy=OneShot(0)).run(enriched=f)["trades"] == []


# ------------------------------------------------------------------ structural stop & no-chase filter
def row(**kw):
    base = dict(timestamp=pd.Timestamp("2026-10-27 10:00", tz=NY), close=100.0, atr=10.0, rsi=55.0, vwap=99.0,
                ema_fast=99.5, ema_slow=98.0, kalman_vel_atr=0.1, hurst=0.5, swing_low=95.0, swing_high=105.0)
    base.update(kw)
    return pd.Series(base)


def strat(**risk):
    c = BotConfig()
    for k, v in risk.items():
        setattr(c.risk, k, v)
    return NQIntradayStrategy(c.strategy, c.risk, c.contract)


def test_structural_stop_uses_swing_extreme_within_bounds():
    s = strat(stop_mode="structural", structural_buffer_ticks=2)
    far = s.build_signal(row(swing_low=80.0), "LONG", "t", "x")
    assert far.stop_loss == 79.5 and far.stop_distance_points == 20.5 and far.take_profit == 100 + 3 * 20.5
    tight = s.build_signal(row(swing_low=99.0), "LONG", "t", "x")          # raw 1.5 -> floored at min_stop_points (8)
    assert tight.stop_distance_points == 8.0
    short = s.build_signal(row(swing_high=115.0), "SHORT", "t", "x")
    assert short.stop_loss == 115.5


def test_atr_stop_default_unchanged():
    assert strat().build_signal(row(), "LONG", "t", "x").stop_distance_points == 12.0


def test_max_extension_filter_reduces_signals():
    from backtest import prepare_bars
    raw = pd.read_csv("data/mnq_2m_3months.csv")
    c = BotConfig()
    bars = prepare_bars(raw, c)
    d = pd.to_datetime(bars["timestamp"], utc=True).dt.tz_convert(NY).dt.strftime("%Y-%m")
    sl = bars[d == "2026-09"].reset_index(drop=True)
    base = NQIntradayStrategy(c.strategy, c.risk, c.contract, c.context, c.entry)
    c2 = BotConfig()
    c2.entry.max_extension_atr = 0.05
    tight = NQIntradayStrategy(c2.strategy, c2.risk, c2.contract, c2.context, c2.entry)
    en = base.prepare_dataframe(sl)
    n_base = sum(base.evaluate_bar(en, i) is not None for i in range(len(en)))
    n_tight = sum(tight.evaluate_bar(en, i) is not None for i in range(len(en)))
    assert n_base > 0 and n_tight < n_base


# ------------------------------------------------------------------ live runner
def test_live_retrace_limit_and_rebased_exits(tmp_path):
    r = make(tmp_path)
    r.cfg.entry.execution_style = "retrace"
    r.cfg.entry.retrace_atr = 0.25
    br = r.place_bracket_order(live_signal(), 1, bar_ts=pd.Timestamp("2026-10-27 10:00", tz=NY))
    parent, tp, sl = (t.order for t in br.trades)
    assert parent.lmtPrice == 28992.5 and sl.auxPrice == 28952.5 and tp.lmtPrice == 29112.5       # atr=30 -> 7.5 pts


def test_live_confirmation_flow(tmp_path):
    r = make(tmp_path)
    r.cfg.entry.confirm_bars = 1
    s = live_signal()

    class Stub:
        def prepare_dataframe(self, df): return df
        def evaluate_bar(self, df, idx=-1): return s if not getattr(self, "used", False) and setattr(self, "used", True) is None else None
    r.strategy = Stub()
    t0 = pd.Timestamp("2026-10-27 10:00", tz=NY)
    r.process_closed_bar(bar_df("2026-10-27 10:00", 29005, 28995, 29000))
    assert r._confirm is s and r.active is None                               # waiting
    r.process_closed_bar(bar_df("2026-10-27 10:02", 29020, 28998, 29015))      # closes beyond signal close
    assert r.active is not None and r.active.signal.entry_price == 29015.0     # re-based onto confirmation close
    assert r.active.signal.stop_loss == 28975.0 and t0 is not None


def test_live_confirmation_failure_places_nothing(tmp_path):
    r = make(tmp_path)
    r.cfg.entry.confirm_bars = 1
    s = live_signal()

    class Stub:
        used = False
        def prepare_dataframe(self, df): return df
        def evaluate_bar(self, df, idx=-1):
            if not self.used:
                self.used = True
                return s
    r.strategy = Stub()
    r.process_closed_bar(bar_df("2026-10-27 10:00", 29005, 28995, 29000))
    r.process_closed_bar(bar_df("2026-10-27 10:02", 29004, 28990, 28992))      # closes below signal close
    assert r.active is None and r._confirm is None
