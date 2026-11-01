"""Trailing stop ("let winners run"): stop manager, backtest exit, live persistence."""
from __future__ import annotations

import pandas as pd

from backtest import Backtester
from config import BotConfig, RiskConfig
from test_bot import OneShot, _frame
from test_execution import make, signal as live_signal
from trade_mgmt import StopManager

NY = "America/New_York"


def mgr(direction="LONG", entry=100.0, stop=90.0, **kw):
    return StopManager(direction, entry, stop, 10.0, RiskConfig(trail_r=1.0, trail_start_r=1.5, **kw))


def test_trail_off_by_default_leaves_baseline_untouched():
    m = StopManager("LONG", 100.0, 90.0, 10.0, RiskConfig())
    m.update(112, 99, 1)                                   # break-even as before
    assert m.update(140, 130, 2) is None and not m.trail_moved


def test_trailing_starts_after_threshold_and_only_tightens_long():
    m = mgr()
    assert m.update(112.0, 99.0, 1) == (101.0, "breakeven")           # +1.2R -> break-even first
    assert m.update(114.0, 105.0, 2) is None                          # best 114 = +1.4R, below +1.5R start
    assert m.update(125.0, 110.0, 3) == (115.0, "trail")              # best 125 -> stop 125 - 10
    assert m.update(122.0, 118.0, 4) is None                          # pullback: stop never loosened
    assert m.update(135.0, 120.0, 5) == (125.0, "trail") and m.exit_label() == "Trailing Stop"


def test_trailing_short_mirrors_long():
    m = StopManager("SHORT", 100.0, 110.0, 10.0, RiskConfig(trail_r=1.0, trail_start_r=1.5))
    assert m.update(101.0, 88.0, 1) == (99.0, "breakeven")
    assert m.update(95.0, 75.0, 2) == (85.0, "trail")                 # best 75 -> stop 75 + 10
    assert m.update(80.0, 78.0, 3) is None


def test_backtest_exits_on_the_trailing_stop_not_the_target():
    f = _frame([(100, 101, 99, 100), (100, 100.5, 99.5, 100), (100, 112, 99.5, 111), (111, 125, 108, 124),
                (120, 121, 114, 115)])
    cfg = BotConfig()
    cfg.costs.commission_per_side_usd = 0.01
    cfg.risk.trail_r, cfg.risk.trail_start_r = 1.0, 1.5
    t = Backtester(cfg, strategy=OneShot(0, tp=200.0)).run(enriched=f)["trades"]
    assert len(t) == 1 and t[0].exit_reason == "Trailing Stop" and t[0].exit_price == 115.0 - 0.25
    assert t[0].gross_points > 10                                        # kept well over 1R of the move


def test_live_bracket_persists_trailing_state(tmp_path):
    r = make(tmp_path)
    r.cfg.risk.trail_r = 1.0
    br = r.place_bracket_order(live_signal(), 1, bar_ts=pd.Timestamp("2026-10-27 10:00", tz=NY))
    from test_execution import fill
    fill(br.trades[0], "BOT", 1, 29000.0, t="2026-10-27 14:00:30")
    r._on_parent_filled(br.trades[0])
    br.mgr.best, br.mgr.trail_moved = 29075.0, True
    d = br.to_dict()
    assert d["trail_moved"] is True and d["best"] == 29075.0
