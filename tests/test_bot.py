"""Core tests: indicators, risk, strategy parity with the baseline, backtester mechanics."""
from __future__ import annotations

import pandas as pd
import pytest

from backtest import Backtester, generate_synthetic_nq_data
from config import BotConfig, RiskConfig
from indicators import compute_session_vwap, enrich_indicators, filter_rth, round_to_tick, to_session_time
from metrics import bootstrap, compute_metrics, max_drawdown
from risk_manager import RiskManager
from strategy import NQIntradayStrategy, TradeSignal
from trade_mgmt import StopManager

NY = "America/New_York"
CSV = "data/mnq_2m_3months.csv"


def test_round_to_tick() -> None:
    assert round_to_tick(20123.11, 0.25) == 20123.00
    assert round_to_tick(20123.14, 0.25) == 20123.25
    assert round_to_tick(20123.89, 0.25) == 20124.00


def test_session_vwap_resets_each_day() -> None:
    df = pd.DataFrame({
        "timestamp": [pd.Timestamp("2026-10-26 09:30", tz=NY), pd.Timestamp("2026-10-26 09:31", tz=NY),
                      pd.Timestamp("2026-10-27 09:30", tz=NY)],
        "high": [20010.0, 20030.0, 20510.0], "low": [19990.0, 20010.0, 20490.0],
        "close": [20000.0, 20020.0, 20500.0], "volume": [1000, 1000, 500],
    })
    v = compute_session_vwap(df)
    assert v.iloc[0] == 20000.0 and v.iloc[1] == 20010.0 and v.iloc[2] == 20500.0


def test_naive_timestamps_are_rejected() -> None:
    s = pd.Series(pd.to_datetime(["2026-10-27 09:30:00"]))
    with pytest.raises(ValueError):
        to_session_time(s, NY)


def test_filter_rth_drops_after_hours() -> None:
    ts = [pd.Timestamp(f"2026-10-27 {t}", tz=NY) for t in ("09:28", "09:30", "15:58", "16:00", "16:30")]
    df = pd.DataFrame({"timestamp": ts, "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1})
    kept = filter_rth(df, NY)
    assert list(pd.to_datetime(kept["timestamp"]).dt.strftime("%H:%M")) == ["09:30", "15:58"]


def test_risk_manager_guardrails_and_eod_flatten() -> None:
    cfg = BotConfig()
    cfg.risk.max_daily_loss_usd, cfg.risk.max_consecutive_losses, cfg.risk.cooldown_bars_after_exit = 200.0, 2, 2
    rm = RiskManager(cfg.risk, cfg.contract)
    ok, reason = rm.can_open_trade(pd.Timestamp("2026-10-27 09:31", tz=NY), 1)
    assert not ok and "Outside allowed RTH" in reason
    ts = pd.Timestamp("2026-10-27 10:15", tz=NY)
    assert rm.can_open_trade(ts, 10)[0]
    rm.record_trade_closed(-100.0, exit_bar_index=10)
    ok, reason = rm.can_open_trade(ts, 11)
    assert not ok and "Cooldown" in reason
    rm.record_trade_closed(-50.0, exit_bar_index=15)
    ok, reason = rm.can_open_trade(ts, 20)
    assert not ok and "halted" in reason.lower()
    assert rm.can_open_trade(pd.Timestamp("2026-10-28 10:15", tz=NY), 25)[0]   # next day resets
    assert rm.should_flatten_eod(pd.Timestamp("2026-10-28 15:55", tz=NY))


def test_risk_state_roundtrip_and_other_day_ignored() -> None:
    cfg = BotConfig()
    rm = RiskManager(cfg.risk, cfg.contract)
    rm.check_and_reset_session(pd.Timestamp("2026-10-27 10:00", tz=NY))
    rm.record_trade_closed(-300.0, exit_bar_index=5)
    assert rm.state.halted
    saved = rm.state_to_dict()
    rm2 = RiskManager(cfg.risk, cfg.contract)
    assert rm2.load_state(saved, today=pd.Timestamp("2026-10-27").date())
    assert rm2.state.halted and rm2.state.realized_pnl_usd == -300.0 and rm2.state.trades_taken == 1
    rm3 = RiskManager(cfg.risk, cfg.contract)
    assert not rm3.load_state(saved, today=pd.Timestamp("2026-10-28").date())
    assert not rm3.state.halted


# ----------------------------------------------------------------------------- stop manager
def _mgr(direction: str, entry=100.0, stop=90.0, one_r=10.0, **kw) -> StopManager:
    return StopManager(direction, entry, stop, one_r, RiskConfig(**kw))


def test_stop_manager_breakeven_long_and_short() -> None:
    m = _mgr("LONG")
    assert m.update(109.0, 99.0, 1) is None
    assert m.update(110.0, 99.0, 2) == (101.0, "breakeven") and m.be_moved
    assert m.update(130.0, 99.0, 3) is None                    # only once
    s = _mgr("SHORT", stop=110.0)
    assert s.update(101.0, 90.0, 1) == (99.0, "breakeven")


def test_stop_manager_time_decay_only_when_not_traded_through() -> None:
    m = _mgr("LONG")
    assert m.update(104.0, 98.0, 5) is None                    # not yet 6 bars
    assert m.update(104.0, 94.0, 6) is None                    # bar already traded through -5.0 level
    assert m.update(104.0, 98.0, 7) == (95.0, "time_decay")
    assert m.exit_label().startswith("Time-Decay")
    # decay works even when break-even is disabled (baseline live code nested it inside the BE block)
    n = _mgr("LONG", breakeven_at_1r=False)
    assert n.update(104.0, 98.0, 6) == (95.0, "time_decay")


# ----------------------------------------------------------------------------- strategy / baseline parity
def test_strategy_end_to_end_synthetic() -> None:
    df = generate_synthetic_nq_data(num_days=5, seed=42)
    assert {"vwap", "ema_fast", "atr"} <= set(enrich_indicators(df).columns)
    res = Backtester(BotConfig()).run(df)
    assert res["metrics"]["total_trades"] > 0
    for t in res["trades"]:
        assert round(t.stop_loss % 0.25, 5) == 0.0 and round(t.take_profit % 0.25, 5) == 0.0
        assert (t.take_profit > t.entry_price) == (t.direction == "LONG")


@pytest.fixture(scope="module")
def raw() -> pd.DataFrame:
    return pd.read_csv(CSV)


def test_refactor_reproduces_baseline_exactly(raw) -> None:
    """With legacy assumptions the refactored engine must equal the original repo's published result."""
    cfg = BotConfig()
    cfg.backtest.fill_model, cfg.backtest.model_gaps, cfg.backtest.rth_filter_data = "signal_close", False, False
    m = Backtester(cfg).run(raw)["metrics"]
    assert (m["total_trades"], m["net_pnl_usd"], m["profit_factor"], m["max_drawdown_usd"]) == (109, 2926.84, 1.97, 790.52)


def test_default_realistic_regression(raw) -> None:
    m = Backtester(BotConfig()).run(raw)["metrics"]
    assert m["total_trades"] == 111 and m["net_pnl_usd"] == 1789.37


def test_window_runs_are_independent(raw) -> None:
    bt = Backtester(BotConfig())
    enriched = bt.enrich(raw)
    a = bt.run(enriched=enriched, start="2026-08-01", end="2026-09-01")
    b = bt.run(enriched=enriched, start="2026-08-01", end="2026-09-01")
    assert a["metrics"] == b["metrics"]
    assert all(pd.Timestamp("2026-08-01") <= pd.Timestamp(t.exit_time).tz_localize(None).normalize() < pd.Timestamp("2026-09-01")
               for t in a["trades"])


# ----------------------------------------------------------------------------- backtester mechanics (stub strategy)
class OneShot:
    """Emits one signal at a given row index of a hand-built frame."""
    warmup_bars = 0

    def __init__(self, at: int, direction: str = "LONG", entry=100.0, stop=90.0, tp=130.0) -> None:
        self.at, self.direction, self.entry, self.stop, self.tp = at, direction, entry, stop, tp
        self.s_cfg = BotConfig().strategy

    def evaluate_bar(self, df, idx=-1):
        if idx != self.at:
            return None
        return TradeSignal(timestamp=pd.Timestamp(df.iloc[idx]["timestamp"]), direction=self.direction, reason="t",
                           entry_price=self.entry, stop_loss=self.stop, take_profit=self.tp, stop_distance_points=10.0,
                           atr=10.0, rsi=50.0, vwap=100.0, ema_fast=100.0, ema_slow=100.0, setup="stub")


def _frame(bars):
    ts = pd.date_range("2026-10-27 10:00", periods=len(bars), freq="2min", tz=NY)
    return pd.DataFrame({"timestamp": ts, "open": [b[0] for b in bars], "high": [b[1] for b in bars],
                         "low": [b[2] for b in bars], "close": [b[3] for b in bars], "volume": 1000.0})


def _bt(stub, **cost):
    cfg = BotConfig()
    cfg.costs.commission_per_side_usd = 0.01
    for k, v in cost.items():
        setattr(cfg.costs, k, v)
    return Backtester(cfg, strategy=stub), cfg


def test_next_bar_fill_at_open_and_take_profit() -> None:
    f = _frame([(100, 101, 99, 100), (99.5, 100.0, 99, 99.8), (100, 131, 99, 130)])
    bt, _ = _bt(OneShot(0))
    t = bt.run(enriched=f)["trades"]
    assert len(t) == 1 and t[0].entry_price == 99.5 and t[0].exit_reason == "Take Profit" and t[0].exit_price == 130.0


def test_unfilled_marketable_limit_times_out() -> None:
    f = _frame([(100, 101, 99, 100)] + [(105, 110, 104, 108)] * 5)          # price runs away above the limit
    bt, _ = _bt(OneShot(0))
    assert bt.run(enriched=f)["trades"] == []


def test_gap_through_stop_fills_at_open_not_at_stop() -> None:
    f = _frame([(100, 101, 99, 100), (100, 100.5, 99, 100), (80, 82, 78, 81)])   # gaps 10 pts below the stop
    bt, _ = _bt(OneShot(0))
    t = bt.run(enriched=f)["trades"][0]
    assert t.exit_price == 80 - 0.25 and t.exit_reason == "Stop Loss"
    bt2, cfg2 = _bt(OneShot(0))
    cfg2.backtest.model_gaps = False
    assert bt2.run(enriched=f)["trades"][0].exit_price == 90 - 0.25


def test_breakeven_moves_after_one_r_and_stops_next_bar() -> None:
    f = _frame([(100, 101, 99, 100), (100, 100.5, 99.5, 100), (100, 111, 99.5, 110), (105, 106, 100.0, 104)])
    bt, _ = _bt(OneShot(0))
    t = bt.run(enriched=f)["trades"][0]
    assert t.exit_reason == "Break-Even Stop" and t.exit_price == 101.0 - 0.25


def test_fill_bar_never_updates_stop() -> None:
    """Even if the fill bar's range spans +1R, BE only becomes active for subsequent bars."""
    f = _frame([(100, 101, 99, 100), (99.5, 112, 99, 111), (111, 112, 100, 101)])
    bt, _ = _bt(OneShot(0))
    t = bt.run(enriched=f)["trades"][0]
    assert t.exit_reason == "End of Data"       # a BE stop (100.5) would have been hit by the last bar low (100)


def test_metrics_helpers() -> None:
    assert max_drawdown([10, -5, -5, 3]) == 10
    assert bootstrap([1, 2, 3]) == {}
    assert compute_metrics([])["total_trades"] == 0


def test_indicators_and_signals_have_no_lookahead(raw) -> None:
    """Signals computed on truncated history must equal those from the full-history frame, bar by bar."""
    cfg = BotConfig()
    bt = Backtester(cfg)
    from backtest import prepare_bars
    bars = prepare_bars(raw, cfg)
    d = pd.to_datetime(bars["timestamp"], utc=True).dt.tz_convert(NY).dt.strftime("%Y-%m-%d")
    sl = bars[(d >= "2026-10-19") & (d <= "2026-10-22")].reset_index(drop=True)
    strat = NQIntradayStrategy(cfg.strategy, cfg.risk, cfg.contract)
    full = strat.prepare_dataframe(sl)
    hhmm = pd.to_datetime(sl["timestamp"], utc=True).dt.tz_convert(NY).dt.strftime("%H:%M")
    n_signals = 0
    for i in range(len(sl)):
        if not ("09:45" <= hhmm[i] <= "12:30"):
            continue
        a = strat.evaluate_bar(full, idx=i)
        b = strat.evaluate_bar(strat.prepare_dataframe(sl.iloc[: i + 1]), idx=-1)
        key = lambda s: None if s is None else (s.direction, s.entry_price, s.stop_loss, s.take_profit, s.meta_probability)
        assert key(a) == key(b), f"look-ahead at row {i}"
        n_signals += a is not None
    assert n_signals >= 1
