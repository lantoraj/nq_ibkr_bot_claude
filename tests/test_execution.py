"""Execution-layer tests against a fake IB (no network). They pin the behaviours that were broken in the baseline."""
from __future__ import annotations

import asyncio
from datetime import date

import pandas as pd
import pytest
from ib_async import Contract, Execution, Fill, CommissionReport, LimitOrder, Order, OrderStatus, Position, StopOrder, Trade

from config import BotConfig
from ibkr_execution import IBKRNQBotRunner, pick_contract
from strategy import TradeSignal

NY = "America/New_York"
CON = Contract(conId=777, symbol="MNQ", localSymbol="MNQZ6")


class FakeClient:
    def __init__(self) -> None:
        self.n = 100

    def getReqId(self) -> int:
        self.n += 1
        return self.n


class FakeIB:
    """Just enough of ib_async.IB for the runner."""

    def __init__(self) -> None:
        self.client = FakeClient()
        self.trades: list[Trade] = []
        self.pos = 0
        self.avg_cost = 0.0
        self.placed: list[Order] = []
        self.on_cancel = None

    def positions(self):
        return [Position("DU1", CON, self.pos, self.avg_cost)] if self.pos else []

    async def reqPositionsAsync(self):
        return self.positions()

    def openTrades(self):
        return [t for t in self.trades if not t.isDone()]

    def placeOrder(self, contract, order):
        self.placed.append(order)
        for t in self.trades:
            if t.order.orderId == order.orderId and order.orderId:
                return t                                # modification of a working order
        t = Trade(contract, order, OrderStatus(orderId=order.orderId, status="Submitted"), [], [], None)
        self.trades.append(t)
        return t

    def cancelOrder(self, order):
        for t in self.trades:
            if t.order.orderId == order.orderId:
                t.orderStatus.status = "Cancelled"
        if self.on_cancel:
            self.on_cancel(order)

    def isConnected(self):
        return True


def make(tmp_path, **cfg_kw):
    cfg = BotConfig()
    cfg.execution.state_file = str(tmp_path / "state.json")
    cfg.execution.cancel_wait_timeout_sec = 0.5
    cfg.costs.commission_per_side_usd = 0.5
    r = IBKRNQBotRunner(cfg, mode="paper", ib=FakeIB())
    r.contract = CON
    return r


def signal(direction="LONG", entry=29000.0, stop=28960.0, tp=29120.0):
    return TradeSignal(timestamp=pd.Timestamp("2026-10-27 10:00", tz=NY), direction=direction, reason="t",
                       entry_price=entry, stop_loss=stop, take_profit=tp, stop_distance_points=abs(entry - stop),
                       atr=30.0, rsi=55.0, vwap=entry, ema_fast=entry, ema_slow=entry, setup="stub")


def fill(trade: Trade, side: str, qty: float, price: float, t="2026-10-27 14:02:30", commission=0.5):
    ex = Execution(execId=f"e{len(trade.fills)}{trade.order.orderId}", side=side, shares=qty, price=price,
                   orderId=trade.order.orderId)
    f = Fill(CON, ex, CommissionReport(commission=commission, realizedPNL=0.0), pd.Timestamp(t, tz="UTC").to_pydatetime())
    trade.fills.append(f)
    trade.orderStatus.filled = sum(x.execution.shares for x in trade.fills)
    trade.orderStatus.avgFillPrice = price
    trade.orderStatus.status = "Filled"
    return f


def bar_df(ts, high, low, close=None):
    close = close if close is not None else (high + low) / 2
    return pd.DataFrame({"timestamp": [pd.Timestamp(ts, tz=NY)], "open": [close], "high": [high], "low": [low],
                         "close": [close], "volume": [1000]})


# ------------------------------------------------------------------ bracket construction
def test_bracket_is_oca_with_correct_prices(tmp_path):
    r = make(tmp_path)
    br = r.place_bracket_order(signal(), 1, bar_ts=pd.Timestamp("2026-10-27 10:00", tz=NY))
    parent, tp, sl = (t.order for t in br.trades)
    assert isinstance(parent, LimitOrder) and parent.lmtPrice == 29000.25 and parent.transmit is False
    assert tp.ocaGroup == sl.ocaGroup != "" and tp.ocaType == sl.ocaType == 1
    assert sl.orderType == "STP" and sl.auxPrice == 28960.0 and sl.transmit is True
    assert tp.parentId == sl.parentId == parent.orderId


def test_server_side_breakeven_fields_are_optional(tmp_path):
    r = make(tmp_path)
    r.cfg.execution.server_side_breakeven = True
    sl = r.place_bracket_order(signal(), 1).trades[2].order
    assert sl.triggerPrice == 29040.0 and sl.adjustedOrderType == "STP" and sl.adjustedStopPrice == 29001.0


# ------------------------------------------------------------------ stop modification (baseline bug: .stopPrice)
def test_breakeven_modifies_auxprice_and_replaces_order(tmp_path):
    r = make(tmp_path)
    br = r.place_bracket_order(signal(), 1, bar_ts=pd.Timestamp("2026-10-27 10:00", tz=NY))
    parent = br.trades[0]
    fill(parent, "BOT", 1, 29000.0, t="2026-10-27 14:00:30")          # 10:00:30 ET -> fill bar 10:00
    r._on_parent_filled(parent)
    assert br.mgr is not None and br.fill_price == 29000.0
    sl_trade = br.trades[2]

    r._manage_active(br, bar_df("2026-10-27 10:00", 29050, 28990), pd.Timestamp("2026-10-27 10:00", tz=NY))
    assert sl_trade.order.auxPrice == 28960.0                           # fill bar: no update
    r._manage_active(br, bar_df("2026-10-27 10:02", 29045, 29000), pd.Timestamp("2026-10-27 10:02", tz=NY))
    assert sl_trade.order.auxPrice == 29001.0                           # +1R reached -> BE+1pt
    assert r.ib.placed[-1].orderId == sl_trade.order.orderId            # same order id => modification
    assert not hasattr(sl_trade.order, "stopPrice")


def test_time_decay_counts_bars_from_fill(tmp_path):
    r = make(tmp_path)
    br = r.place_bracket_order(signal(), 1, bar_ts=pd.Timestamp("2026-10-27 10:00", tz=NY))
    fill(br.trades[0], "BOT", 1, 29000.0, t="2026-10-27 14:06:10")     # fills during the 10:06 bar
    r._on_parent_filled(br.trades[0])
    sl = br.trades[2].order
    for k in range(1, 6):                                               # bars 10:08 .. 10:16 (held 1..5)
        r._manage_active(br, bar_df(f"2026-10-27 10:{6 + 2 * k:02d}", 29010, 28995), pd.Timestamp(f"2026-10-27 10:{6 + 2 * k:02d}", tz=NY))
    assert sl.auxPrice == 28960.0
    r._manage_active(br, bar_df("2026-10-27 10:18", 29010, 28995), pd.Timestamp("2026-10-27 10:18", tz=NY))   # held 6
    assert sl.auxPrice == 28980.0                                       # -0.5R


def test_unfilled_entry_cancelled_after_n_bars(tmp_path):
    r = make(tmp_path)
    br = r.place_bracket_order(signal(), 1, bar_ts=pd.Timestamp("2026-10-27 10:00", tz=NY))
    parent = br.trades[0]
    r._manage_active(br, bar_df("2026-10-27 10:04", 29005, 28995), pd.Timestamp("2026-10-27 10:04", tz=NY))
    assert not parent.isDone()
    r._manage_active(br, bar_df("2026-10-27 10:06", 29005, 28995), pd.Timestamp("2026-10-27 10:06", tz=NY))   # 3 bars
    assert parent.orderStatus.status == "Cancelled"
    r._manage_active(br, bar_df("2026-10-27 10:08", 29005, 28995), pd.Timestamp("2026-10-27 10:08", tz=NY))
    assert r.active is None


# ------------------------------------------------------------------ closed-trade accounting
def _open_position(r, qty=2):
    br = r.place_bracket_order(signal(), qty, bar_ts=pd.Timestamp("2026-10-27 10:00", tz=NY))
    fill(br.trades[0], "BOT", qty, 29000.0, t="2026-10-27 14:00:30")
    r._on_parent_filled(br.trades[0])
    r.ib.pos = qty
    return br


def test_pnl_is_computed_from_bracket_fills_with_commissions(tmp_path):
    r = make(tmp_path)
    br = _open_position(r, 2)
    fill(br.trades[1], "SLD", 2, 29120.0, t="2026-10-27 14:30:00")
    r.ib.pos = 0
    r._check_closed(force=True)
    # gross = 120pt * $2 * 2 = 480 ; commissions = 4 fills-lines * 0.5 = 1.0 (entry + exit reports)
    assert r.risk.state.trades_taken == 1 and r.risk.state.realized_pnl_usd == pytest.approx(479.0)
    assert r.active is None


def test_scratch_trade_is_still_counted(tmp_path):
    r = make(tmp_path)
    br = _open_position(r, 1)
    fill(br.trades[2], "SLD", 1, 29000.0, t="2026-10-27 14:30:00", commission=0.0)
    r.ib.pos = 0
    br.trades[0].fills[0] = br.trades[0].fills[0]._replace(commissionReport=CommissionReport(commission=0.0))
    r._check_closed(force=True)
    assert r.risk.state.trades_taken == 1                                # baseline skipped realizedPNL == 0
    assert r.risk.state.realized_pnl_usd == pytest.approx(-1.0)          # est. 2 * 0.5 commission


def test_daily_loss_halt_persists_across_restart(tmp_path):
    r = make(tmp_path)
    br = _open_position(r, 1)
    fill(br.trades[2], "SLD", 1, 28960.0, t="2026-10-27 14:20:00")
    r.ib.pos = 0
    r.risk.check_and_reset_session(pd.Timestamp.now(tz="UTC"))
    r._check_closed(force=True)
    r.risk.state.session_date = date.today()                              # persisted record for "today"
    r.persist()
    r2 = make(tmp_path)
    r2.risk.load_state(r2.store.load()["risk"], today=date.today())
    assert r2.risk.state.trades_taken == 1


# ------------------------------------------------------------------ flatten race
def test_flatten_does_not_reverse_when_stop_fills_during_cancel(tmp_path):
    r = make(tmp_path)
    br = _open_position(r, 1)
    sl = br.trades[2]

    def stop_fills_first(order):                    # exchange fills the stop while we are cancelling
        if order.orderId == br.tp_id:
            fill(sl, "SLD", 1, 28960.0)
            r.ib.pos = 0
    r.ib.on_cancel = stop_fills_first
    n_before = len(r.ib.placed)
    asyncio.run(r.flatten_async("test"))
    assert not any(isinstance(o, Order) and o.orderType == "MKT" for o in r.ib.placed[n_before:])


def test_flatten_sends_opposite_market_order_when_still_in_position(tmp_path):
    r = make(tmp_path)
    _open_position(r, 2)
    asyncio.run(r.flatten_async("test"))
    mkt = [o for o in r.ib.placed if o.orderType == "MKT"]
    assert len(mkt) == 1 and mkt[0].action == "SELL" and mkt[0].totalQuantity == 2
    assert all(t.isDone() for t in r.ib.trades[:3])                       # bracket orders cancelled first


# ------------------------------------------------------------------ recovery
def test_unmanaged_position_without_stop_is_flattened(tmp_path):
    r = make(tmp_path)
    r.ib.pos, r.ib.avg_cost = 1, 29000.0 * 2
    asyncio.run(r.recover_async())
    assert [o.action for o in r.ib.placed if o.orderType == "MKT"] == ["SELL"]


def test_orphan_position_with_stop_is_adopted_and_managed(tmp_path):
    r = make(tmp_path)
    r.ib.pos, r.ib.avg_cost = 1, 29000.0 * 2
    stop = StopOrder("SELL", 1, 28960.0, orderId=55)
    r.ib.placeOrder(CON, stop)
    asyncio.run(r.recover_async())
    a = r.active
    assert a is not None and a.recovered and a.mgr.entry_price == 29000.0 and a.mgr.one_r == 40.0
    assert not any(o.orderType == "MKT" for o in r.ib.placed)


def test_saved_bracket_is_reattached_after_restart(tmp_path):
    r = make(tmp_path)
    br = _open_position(r, 1)
    r.persist()
    r2 = make(tmp_path)
    r2.ib = r.ib                                   # same broker state, new process
    asyncio.run(r2.recover_async())
    assert r2.active is not None and r2.active.mgr.entry_price == 29000.0 and r2.active.parent_id == br.parent_id


# ------------------------------------------------------------------ contract roll & CLI guard
class _D:
    def __init__(self, exp):
        self.contract = Contract(lastTradeDateOrContractMonth=exp, symbol="MNQ")


def test_contract_rolls_before_expiry():
    d = [_D("20260918"), _D("20261218"), _D("20260619")]
    assert pick_contract(d, date(2026, 8, 20), 8).lastTradeDateOrContractMonth == "20260918"
    assert pick_contract(d, date(2026, 9, 10), 8).lastTradeDateOrContractMonth == "20260918"   # exactly 8 days left
    assert pick_contract(d, date(2026, 9, 11), 8).lastTradeDateOrContractMonth == "20261218"   # 7 days left -> rolled


def test_live_mode_requires_explicit_confirmation(capsys):
    import main
    assert main.main(["--mode", "live"]) == 2


# ------------------------------------------------------------------ event flatten in the live loop
def test_live_loop_flattens_before_event_and_blocks_entries(tmp_path):
    from events import Event, EventCalendar
    r = make(tmp_path)
    r.cfg.context.use_event_filter = True
    r.risk.calendar = EventCalendar([Event(pd.Timestamp("2026-10-28 14:00", tz=NY), "FOMC", 1)], r.cfg.context, 120, NY)
    calls = []
    r.flatten_all = lambda reason="": calls.append(reason)
    _open_position(r, 1)
    df = bar_df("2026-10-28 13:56", 29010, 28995)
    r.process_closed_bar(df)
    assert calls == ["Pre-event flatten"]
