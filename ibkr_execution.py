"""
Interactive Brokers live / paper execution engine (`ib_async`).

Robustness features (vs. the original baseline):
  * Stop modifications use `Order.auxPrice` (the field a StopOrder actually uses).
  * Bracket children are an explicit OCA group, so a filled TP can never leave a live stop behind.
  * Flatten is a cancel -> wait-for-confirmation -> re-read position -> close sequence (no race that
    could reverse the position).
  * Risk state and the active bracket are persisted and recovered after a restart; orphan positions
    are adopted if protected by a stop, otherwise flattened.
  * Realised PnL is computed per bracket from its own fills (+ commissions), so scratch trades and
    multi-fill exits are counted correctly.
  * Auto-reconnect with back-off, stale-data watchdog and resubscribe.
  * Contract roll happens `roll_days_before_expiry` days before expiry.
  * Break-even / time-decay use the same StopManager as the backtester and count bars from the FILL.
  * Timestamps are requested as UTC (formatDate=2); naive timestamps are rejected.
"""
from __future__ import annotations

import asyncio
import logging
import time as _time
from dataclasses import asdict
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import pandas as pd
from ib_async import IB, BarDataList, Contract, Future, LimitOrder, MarketOrder, StopOrder, Trade, util

from config import BotConfig
from context import attach_session_context
from entry import confirm_ok, plan_entry
from events import build_calendar
from indicators import filter_rth, round_to_tick, to_session_time
from risk_manager import RiskManager
from state_store import StateStore
from strategy import NQIntradayStrategy, TradeSignal
from trade_mgmt import StopManager

logger = logging.getLogger("nq_ibkr_bot")

UNSET = 1.7976931348623157e308
BAR_SECONDS = {"1 min": 60, "2 mins": 120, "5 mins": 300}


# ---------------------------------------------------------------------------- pure helpers
def pick_contract(details: List[Any], today: date, roll_days: int) -> Contract:
    """Nearest expiry that is at least `roll_days` away (so we roll before liquidity leaves)."""
    cutoff = (datetime.combine(today, datetime.min.time()) + timedelta(days=roll_days)).strftime("%Y%m%d")
    valid = sorted(
        (d.contract for d in details if d.contract.lastTradeDateOrContractMonth[:8] >= cutoff),
        key=lambda c: c.lastTradeDateOrContractMonth,
    )
    if not valid:
        raise RuntimeError("No contract with enough time to expiry found")
    return valid[0]


class Bracket:
    """Everything we track about one entry + TP + SL group."""

    def __init__(self, signal: TradeSignal, qty: int, parent_id: int, tp_id: int, sl_id: int,
                 submit_bar_ts: pd.Timestamp) -> None:
        self.signal = signal
        self.qty = qty
        self.parent_id, self.tp_id, self.sl_id = parent_id, tp_id, sl_id
        self.submit_bar_ts = pd.Timestamp(submit_bar_ts)
        self.fill_price: Optional[float] = None
        self.fill_bar_ts: Optional[pd.Timestamp] = None
        self.mgr: Optional[StopManager] = None
        self.trades: List[Trade] = []          # parent, tp, sl, + any flatten market order
        self.recovered = False
        self.realized_accum = 0.0              # only used for recovered brackets (no local fills)
        self.finalized = False

    @property
    def direction(self) -> str:
        return self.signal.direction

    def to_dict(self) -> Dict[str, Any]:
        sig = asdict(self.signal)
        sig["timestamp"] = str(self.signal.timestamp)
        return {
            "signal": sig, "qty": self.qty, "parent_id": self.parent_id, "tp_id": self.tp_id, "sl_id": self.sl_id,
            "submit_bar_ts": str(self.submit_bar_ts),
            "fill_price": self.fill_price, "fill_bar_ts": str(self.fill_bar_ts) if self.fill_bar_ts is not None else None,
            "stop_price": self.mgr.stop_price if self.mgr else self.signal.stop_loss,
            "be_moved": self.mgr.be_moved if self.mgr else False,
            "decay_moved": self.mgr.decay_moved if self.mgr else False,
            "recovered": self.recovered, "realized_accum": self.realized_accum,
        }


# ---------------------------------------------------------------------------- runner
class IBKRNQBotRunner:
    """Live / paper execution engine for NQ & MNQ futures on Interactive Brokers."""

    def __init__(self, config: BotConfig, mode: str = "paper", ib: Optional[IB] = None) -> None:
        self.cfg = config
        self.mode = mode.lower()
        self.ib = ib or IB()
        self.strategy = NQIntradayStrategy(config.strategy, config.risk, config.contract, config.context, config.entry)
        self.risk = RiskManager(config.risk, config.contract)
        self.bar_sec = BAR_SECONDS[config.strategy.bar_size]
        self.risk.calendar = build_calendar(config, self.bar_sec)
        if self.risk.calendar is not None and self.risk.calendar.is_stale(pd.Timestamp.now(tz=config.risk.timezone)):
            logger.warning("Event calendar %s lists no events in the next 21 days - update it", config.context.event_file)
        self.store = StateStore(config.execution.state_file)

        self.contract: Optional[Contract] = None
        self.bars: Optional[BarDataList] = None
        self.bar_count = 0
        self._last_processed_bar_time: Optional[pd.Timestamp] = None
        self._last_bar_ts: Optional[pd.Timestamp] = None
        self.active: Optional[Bracket] = None

        self._flattening = False
        self._flatten_reason = ""
        self._flatten_retries = 0
        self._last_update_mono = _time.monotonic()
        self._needs_resubscribe = False
        self._events_wired = False
        self._stop = False
        self._last_orphan_check = 0.0
        self._confirm: Optional[TradeSignal] = None      # signal waiting for its confirmation bar

    # ------------------------------------------------------------------ small utilities
    def _now_et_date(self) -> date:
        return datetime.now(timezone.utc).astimezone(self.risk.tz).date()

    def _bars_between(self, a: pd.Timestamp, b: pd.Timestamp) -> int:
        return int(round((pd.Timestamp(b) - pd.Timestamp(a)).total_seconds() / self.bar_sec))

    def _floor_to_bar(self, ts: pd.Timestamp) -> pd.Timestamp:
        ts = pd.Timestamp(ts)
        return ts.floor(f"{self.bar_sec}s")

    def net_position(self) -> int:
        if self.contract is None:
            return 0
        return int(sum(p.position for p in self.ib.positions() if p.contract.conId == self.contract.conId))

    def _contract_open_trades(self) -> List[Trade]:
        if self.contract is None:
            return []
        return [t for t in self.ib.openTrades() if t.contract.conId == self.contract.conId]

    def has_open_position_or_orders(self) -> bool:
        return self.net_position() != 0 or bool(self._contract_open_trades())

    # ------------------------------------------------------------------ persistence
    def persist(self) -> None:
        try:
            self.store.save({
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "risk": self.risk.state_to_dict(),
                "active": self.active.to_dict() if self.active and not self.active.finalized else None,
            })
        except OSError:
            logger.exception("Could not persist bot state")

    # ------------------------------------------------------------------ connection / contract
    async def connect_async(self) -> None:
        port = self.cfg.ibkr.paper_port if self.mode == "paper" else self.cfg.ibkr.live_port
        logger.info("Connecting to IBKR (%s) at %s:%d clientId=%d", self.mode.upper(), self.cfg.ibkr.host, port,
                    self.cfg.ibkr.client_id)
        await self.ib.connectAsync(self.cfg.ibkr.host, port, clientId=self.cfg.ibkr.client_id,
                                   timeout=self.cfg.ibkr.timeout, account=self.cfg.ibkr.account or "")
        logger.info("Connected. Accounts: %s", self.ib.managedAccounts())

    async def resolve_contract_async(self) -> Contract:
        c = self.cfg.contract
        if c.contract_month:
            fut = Future(symbol=c.symbol, lastTradeDateOrContractMonth=c.contract_month,
                         exchange=c.exchange, currency=c.currency)
            q = await self.ib.qualifyContractsAsync(fut)
            if not q:
                raise RuntimeError(f"Could not qualify {c.symbol} {c.contract_month}")
            self.contract = q[0]
        else:
            details = await self.ib.reqContractDetailsAsync(Future(symbol=c.symbol, exchange=c.exchange, currency=c.currency))
            if not details:
                raise RuntimeError(f"No contract details for {c.symbol}")
            self.contract = pick_contract(details, self._now_et_date(), self.cfg.execution.roll_days_before_expiry)
        logger.info("Active contract: %s expiry=%s conId=%s", self.contract.localSymbol,
                    self.contract.lastTradeDateOrContractMonth, self.contract.conId)
        return self.contract

    # ------------------------------------------------------------------ orders
    def place_bracket_order(self, signal: TradeSignal, quantity: int, bar_ts: Optional[pd.Timestamp] = None) -> Bracket:
        if self.contract is None:
            raise RuntimeError("Contract is not resolved.")
        r, tick = self.cfg.risk, self.cfg.contract.tick_size
        action = "BUY" if signal.direction == "LONG" else "SELL"
        rev = "SELL" if action == "BUY" else "BUY"
        outside = not r.rth_only

        lmt, signal = plan_entry(signal, self.cfg)          # marketable limit, or a retrace limit with re-based exits
        parent_id = self.ib.client.getReqId()
        parent = LimitOrder(action, quantity, lmt, orderId=parent_id, transmit=False, outsideRth=outside, tif="DAY")

        oca = f"OCA_{parent_id}"
        tp = LimitOrder(rev, quantity, signal.take_profit, parentId=parent_id, transmit=False, outsideRth=outside,
                        tif="DAY", ocaGroup=oca, ocaType=1)
        tp.orderId = self.ib.client.getReqId()
        sl = StopOrder(rev, quantity, signal.stop_loss, parentId=parent_id, transmit=True, outsideRth=outside,
                       tif="DAY", ocaGroup=oca, ocaType=1)
        sl.orderId = self.ib.client.getReqId()

        if self.cfg.execution.server_side_breakeven and r.breakeven_at_1r:
            sgn = 1 if action == "BUY" else -1
            sl.triggerPrice = round_to_tick(signal.entry_price + sgn * signal.stop_distance_points, tick)
            sl.adjustedOrderType = "STP"
            sl.adjustedStopPrice = round_to_tick(signal.entry_price + sgn * r.breakeven_offset_points, tick)

        br = Bracket(signal, quantity, parent_id, tp.orderId, sl.orderId,
                     bar_ts if bar_ts is not None else pd.Timestamp(signal.timestamp))
        for o in (parent, tp, sl):
            br.trades.append(self.ib.placeOrder(self.contract, o))
        br.trades[0].filledEvent += lambda trade: self._on_parent_filled(trade)
        self.active = br
        self.persist()
        logger.info("BRACKET SUBMITTED [%s] %s %d %s lmt=%.2f SL=%.2f TP=%.2f | %s", signal.direction, action, quantity,
                    self.contract.localSymbol, lmt, signal.stop_loss, signal.take_profit, signal.reason)
        return br

    def _modify_stop(self, br: Bracket, new_price: float, why: str) -> None:
        sl_trade = next((t for t in br.trades if t.order.orderId == br.sl_id), None)
        if sl_trade is None or sl_trade.isDone():
            logger.error("Cannot modify stop (%s): stop order missing or done", why)
            return
        sl_trade.order.auxPrice = new_price      # StopOrder price lives in auxPrice
        self.ib.placeOrder(self.contract, sl_trade.order)
        logger.info("Stop moved (%s) -> %.2f", why, new_price)
        self.persist()

    def _on_parent_filled(self, trade: Trade) -> None:
        br = self.active
        if br is None or br.mgr is not None:
            return
        px = float(trade.orderStatus.avgFillPrice or trade.order.lmtPrice)
        fills = trade.fills
        fill_time = pd.Timestamp(fills[-1].time) if fills else pd.Timestamp.now(tz="UTC")
        self._init_manager(br, px, self._floor_to_bar(fill_time))

    def _init_manager(self, br: Bracket, fill_price: float, fill_bar_ts: pd.Timestamp) -> None:
        br.fill_price, br.fill_bar_ts = fill_price, fill_bar_ts
        br.mgr = StopManager(br.direction, fill_price, br.signal.stop_loss, br.signal.stop_distance_points,
                             self.cfg.risk, self.cfg.contract.tick_size)
        logger.info("ENTRY FILLED %s @ %.2f (fill bar %s)", br.direction, fill_price, fill_bar_ts)
        self.persist()

    # ------------------------------------------------------------------ flatten (race-free)
    def flatten_all(self, reason: str = "Manual/EOD Flatten") -> None:
        """Schedule the async flatten sequence (safe to call from sync callbacks)."""
        if self._flattening:
            return
        self._flatten_reason = reason
        try:
            asyncio.get_event_loop().create_task(self.flatten_async(reason))
        except RuntimeError:
            asyncio.run(self.flatten_async(reason))

    async def flatten_async(self, reason: str) -> None:
        if self._flattening or self.contract is None:
            return
        self._flattening = True
        try:
            logger.warning("FLATTEN requested: %s", reason)
            cancelling = self._contract_open_trades()
            for t in cancelling:
                self.ib.cancelOrder(t.order)
            deadline = _time.monotonic() + self.cfg.execution.cancel_wait_timeout_sec
            while any(not t.isDone() for t in cancelling) and _time.monotonic() < deadline:
                await asyncio.sleep(0.1)
            if any(not t.isDone() for t in cancelling):
                logger.error("Some orders not confirmed cancelled within timeout; continuing with position check")

            # a stop/TP may have filled while we were cancelling - trust a fresh position read, not our cache
            await self.ib.reqPositionsAsync()
            pos = self.net_position()
            if pos == 0:
                logger.info("Flatten: already flat after cancel (%s)", reason)
                self._flatten_retries = 0
                self._check_closed(force=True)
                return
            action = "SELL" if pos > 0 else "BUY"
            order = MarketOrder(action, abs(pos), tif="DAY")
            trade = self.ib.placeOrder(self.contract, order)
            if self.active is not None:
                self.active.trades.append(trade)
            logger.warning("Flatten: submitted %s %d MKT (%s)", action, abs(pos), reason)
        finally:
            self._flattening = False

    # ------------------------------------------------------------------ closed-trade accounting
    def _bracket_fill_summary(self, br: Bracket) -> Dict[str, float]:
        """Net shares, gross PnL ($) and commissions from the bracket's own fills."""
        net_sh, cash, comm, missing_comm = 0.0, 0.0, 0.0, False
        mult = self.cfg.contract.point_value
        for t in br.trades:
            for f in t.fills:
                sgn = 1 if f.execution.side.upper().startswith("B") else -1
                net_sh += sgn * f.execution.shares
                cash += -sgn * f.execution.shares * f.execution.price * mult
                cr = getattr(f, "commissionReport", None)
                if cr is not None and cr.commission not in (None, 0.0) and cr.commission < UNSET / 2:
                    comm += float(cr.commission)
                else:
                    missing_comm = True
        return {"net_shares": net_sh, "gross": cash, "commission": comm, "missing_comm": float(missing_comm)}

    def _check_closed(self, force: bool = False) -> None:
        br = self.active
        if br is None or br.finalized:
            return
        if br.recovered:
            if self.net_position() == 0 and br.fill_price is not None and (force or br.realized_accum != 0.0):
                self._finalize(br, br.realized_accum)
            return
        s = self._bracket_fill_summary(br)
        entered = any(f for f in br.trades[0].fills)
        if not entered or abs(s["net_shares"]) > 1e-9:
            return
        if s["missing_comm"] and not force:
            return                                  # wait for commission reports (or the next bar)
        comm = s["commission"] if not s["missing_comm"] else 2.0 * br.qty * self.cfg.commission_per_side
        self._finalize(br, s["gross"] - comm)

    def _finalize(self, br: Bracket, net_pnl: float) -> None:
        br.finalized = True
        self.risk.check_and_reset_session(pd.Timestamp.now(tz="UTC"))
        self.risk.record_trade_closed(net_pnl, exit_bar_index=self.bar_count)
        logger.info("TRADE CLOSED %s | PnL $%.2f | session PnL $%.2f | trades today %d", br.direction, net_pnl,
                    self.risk.state.realized_pnl_usd, self.risk.state.trades_taken)
        self.active = None
        self.persist()
        if self.risk.state.halted:
            logger.warning("Risk halt: %s", self.risk.state.halt_reason)
            self.flatten_all(self.risk.state.halt_reason)

    def _on_exec_details(self, trade: Trade, fill: Any) -> None:
        try:
            self._check_closed(force=False)
        except Exception:
            logger.exception("error in exec handler")

    def _on_commission_report(self, trade: Trade, fill: Any, report: Any) -> None:
        try:
            br = self.active
            if br is not None and br.recovered and report.realizedPNL not in (None, 0.0) and abs(report.realizedPNL) < UNSET / 2:
                br.realized_accum += float(report.realizedPNL)
            self._check_closed(force=False)
        except Exception:
            logger.exception("error in commission handler")

    def _on_error(self, reqId: int, code: int, msg: str, contract: Any = None) -> None:
        if code in (1100,):
            logger.error("IB connectivity LOST (1100): %s", msg)
        elif code in (1101,):
            logger.error("IB connectivity restored but data lost (1101) -> will resubscribe")
            self._needs_resubscribe = True
        elif code in (1102,):
            logger.warning("IB connectivity restored, data maintained (1102)")
        elif code in (201, 202, 10147, 10148) or code >= 10000:
            logger.error("IB order/data error %s (reqId=%s): %s", code, reqId, msg)

    # ------------------------------------------------------------------ bar handling
    def _bars_to_dataframe(self, bars: BarDataList) -> pd.DataFrame:
        df = util.df(bars)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.rename(columns={"date": "timestamp"})
        if len(df) > 1:
            df = df.iloc[:-1]                         # drop the still-forming bar
        df = df[["timestamp", "open", "high", "low", "close", "volume"]].reset_index(drop=True)
        df["timestamp"] = to_session_time(df["timestamp"], self.cfg.risk.timezone)   # rejects naive stamps
        df = attach_session_context(df, self.cfg.risk.timezone, self.cfg.risk.rth_open_time, self.cfg.risk.rth_close_time)
        return filter_rth(df, self.cfg.risk.timezone, self.cfg.risk.rth_open_time, self.cfg.risk.rth_close_time)

    def _on_bar_update(self, bars: BarDataList, has_new_bar: bool) -> None:
        self._last_update_mono = _time.monotonic()
        if not has_new_bar:
            return
        try:
            df = self._bars_to_dataframe(bars)
            if not df.empty:
                self.process_closed_bar(df)
        except Exception:
            logger.exception("Unhandled error while processing bar")

    def process_closed_bar(self, df: pd.DataFrame) -> None:
        """Core per-bar logic. Pure w.r.t. IB subscriptions so it can be driven by tests."""
        ts = pd.Timestamp(df.iloc[-1]["timestamp"])
        if self._last_processed_bar_time == ts:
            return
        self._last_processed_bar_time = ts
        self._last_bar_ts = ts
        self.bar_count += 1
        self.risk.check_and_reset_session(ts)
        self._check_closed(force=True)

        # 1. mandatory end-of-day flatten
        if self.risk.should_flatten_eod(ts):
            if self.has_open_position_or_orders():
                self.flatten_all("End of Day Auto-Flatten")
            return

        if self.risk.should_flatten_event(ts):
            if self.has_open_position_or_orders():
                self.flatten_all("Pre-event flatten")
            return

        br = self.active
        if br is not None:
            self._manage_active(br, df, ts)
            return

        # position / orders we do not manage (manual trade, failed recovery): do not stack more risk
        if self.has_open_position_or_orders():
            logger.debug("Unmanaged position/orders present; skipping new entries")
            return

        allowed, why = self.risk.can_open_trade(ts, self.bar_count)
        if not allowed:
            logger.debug("Skip %s: %s", ts, why)
            return

        if self._confirm is not None:
            pend, self._confirm = self._confirm, None
            last = df.iloc[-1]
            if confirm_ok(pend, float(last["close"]), float(last["low"]), float(last["high"]), self.cfg):
                rebased = pend.rebased(round_to_tick(float(last["close"]), self.cfg.contract.tick_size))
                self.place_bracket_order(rebased, self.risk.calculate_contracts(rebased.stop_distance_points), bar_ts=ts)
            return

        enriched = self.strategy.prepare_dataframe(df)
        signal = self.strategy.evaluate_bar(enriched, idx=-1)
        if signal is not None:
            if self.cfg.entry.confirm_bars > 0:
                self._confirm = signal
                logger.info("Signal %s %s awaiting confirmation bar", signal.direction, signal.setup)
                return
            qty = self.risk.calculate_contracts(signal.stop_distance_points)
            self.place_bracket_order(signal, qty, bar_ts=ts)

    def _manage_active(self, br: Bracket, df: pd.DataFrame, ts: pd.Timestamp) -> None:
        parent = br.trades[0]
        # entry fill may have happened without our filledEvent (e.g. partial fills): fall back to status
        if br.mgr is None and parent.orderStatus.filled and parent.orderStatus.filled >= br.qty:
            self._init_manager(br, float(parent.orderStatus.avgFillPrice), self._floor_to_bar(ts))

        if br.mgr is None:                                    # still working
            if parent.isDone():
                filled = int(parent.orderStatus.filled or 0)
                if filled <= 0:                               # cancelled / rejected without fill
                    logger.info("Entry order ended without fill (%s)", parent.orderStatus.status)
                    self.active = None
                    self.persist()
                    return
                # partial fill, remainder cancelled: manage what we got and shrink the exits to match
                logger.warning("Partial entry fill %d/%d - resizing exits", filled, br.qty)
                br.qty = filled
                for t in br.trades[1:3]:
                    if not t.isDone():
                        t.order.totalQuantity = filled
                        self.ib.placeOrder(self.contract, t.order)
                self._init_manager(br, float(parent.orderStatus.avgFillPrice), self._floor_to_bar(ts))
                return
            limit = self.cfg.risk.cancel_unfilled_entry_bars
            if limit > 0 and self._bars_between(br.submit_bar_ts, ts) >= limit:
                logger.info("Entry unfilled after %d bars -> cancelling", limit)
                self.ib.cancelOrder(parent.order)             # children are cancelled with the parent
            return

        bars_held = self._bars_between(br.fill_bar_ts, ts)
        if bars_held < 1:                                     # no stop updates on the fill bar (matches backtest)
            return
        last = df.iloc[-1]
        upd = br.mgr.update(float(last["high"]), float(last["low"]), bars_held)
        if upd is not None:
            self._modify_stop(br, upd[0], upd[1])

    # ------------------------------------------------------------------ recovery
    async def recover_async(self) -> None:
        """Rebuild risk + active-trade state from the state file and IB's live view."""
        await self.ib.reqPositionsAsync()
        saved = self.store.load()
        if saved.get("risk"):
            if self.risk.load_state(saved["risk"], today=self._now_et_date()):
                self.risk.state.last_exit_bar_index = -999
                logger.info("Restored risk state: pnl=%.2f trades=%d halted=%s", self.risk.state.realized_pnl_usd,
                            self.risk.state.trades_taken, self.risk.state.halted)
        pos = self.net_position()
        working = self._contract_open_trades()

        if self.active is not None and not self.active.finalized:
            return                                            # reconnect within the same process: state is live

        sv = saved.get("active")
        if sv and (pos != 0 or working):
            self._reattach(sv, pos, working)
        elif pos != 0 or working:
            await self._adopt_or_flatten(pos, working)
        elif sv:
            logger.warning("Saved bracket has no live position/orders - it closed while the bot was down; "
                           "counting it as a trade with unknown PnL (0)")
            self.risk.check_and_reset_session(pd.Timestamp.now(tz="UTC"))
            self.risk.record_trade_closed(0.0, exit_bar_index=self.bar_count)
        self.persist()

    def _reattach(self, sv: Dict[str, Any], pos: int, working: List[Trade]) -> None:
        d = dict(sv["signal"])
        d["timestamp"] = pd.Timestamp(d["timestamp"])
        sig = TradeSignal(**d)
        br = Bracket(sig, sv["qty"], sv["parent_id"], sv["tp_id"], sv["sl_id"], pd.Timestamp(sv["submit_bar_ts"]))
        br.trades = [t for t in working if t.order.orderId in (br.parent_id, br.tp_id, br.sl_id)]
        br.recovered = True
        br.realized_accum = float(sv.get("realized_accum", 0.0))
        if sv.get("fill_price") is not None:
            br.fill_price = float(sv["fill_price"])
            br.fill_bar_ts = pd.Timestamp(sv["fill_bar_ts"])
            sl_live = next((t.order.auxPrice for t in br.trades if t.order.orderId == br.sl_id), sv["stop_price"])
            br.mgr = StopManager(sig.direction, br.fill_price, float(sl_live), sig.stop_distance_points,
                                 self.cfg.risk, self.cfg.contract.tick_size,
                                 be_moved=bool(sv.get("be_moved")), decay_moved=bool(sv.get("decay_moved")))
        self.active = br
        logger.warning("Recovered active bracket (%s, pos=%d, working=%d)", sig.direction, pos, len(working))

    async def _adopt_or_flatten(self, pos: int, working: List[Trade]) -> None:
        """Position/orders with no saved state: adopt only if a protective stop exists."""
        sgn = 1 if pos > 0 else -1
        stop = next((t for t in working if t.order.orderType == "STP" and
                     ((t.order.action == "SELL") == (sgn > 0))), None)
        if pos == 0 or stop is None:
            logger.critical("UNMANAGED exposure (pos=%d, working=%d, no protective stop) -> flattening", pos, len(working))
            await self.flatten_async("Unmanaged exposure at startup")
            return
        pc = next((p for p in self.ib.positions() if p.contract.conId == self.contract.conId), None)
        entry = round_to_tick(float(pc.avgCost) / self.cfg.contract.point_value, self.cfg.contract.tick_size)
        stop_px = float(stop.order.auxPrice)
        one_r = abs(entry - stop_px)
        tp = next((t for t in working if t.order.orderType == "LMT"), None)
        sig = TradeSignal(
            timestamp=pd.Timestamp.now(tz="UTC"), direction="LONG" if sgn > 0 else "SHORT", reason="Adopted orphan",
            entry_price=entry, stop_loss=stop_px,
            take_profit=float(tp.order.lmtPrice) if tp else entry + sgn * 3 * one_r,
            stop_distance_points=round(one_r, 2), atr=0.0, rsi=0.0, vwap=0.0, ema_fast=0.0, ema_slow=0.0, setup="adopted")
        br = Bracket(sig, abs(pos), 0, tp.order.orderId if tp else 0, stop.order.orderId, pd.Timestamp.now(tz="UTC"))
        br.trades = list(working)
        br.recovered = True
        be_done = sgn * (stop_px - entry) >= 0
        br.fill_price, br.fill_bar_ts = entry, self._floor_to_bar(pd.Timestamp.now(tz="UTC"))
        br.mgr = StopManager(sig.direction, entry, stop_px, one_r, self.cfg.risk, self.cfg.contract.tick_size,
                             be_moved=be_done, decay_moved=True)   # no time-decay for adopted trades
        self.active = br
        logger.warning("ADOPTED orphan %s position %d @ %.2f with stop %.2f", sig.direction, abs(pos), entry, stop_px)

    # ------------------------------------------------------------------ subscription + watchdog
    async def subscribe_async(self) -> None:
        if self.bars is not None:
            try:
                self.ib.cancelHistoricalData(self.bars)
            except Exception:
                pass
            self.bars.updateEvent.clear()
        logger.info("Subscribing to %s %s bars (RTH=%s)", self.contract.localSymbol, self.cfg.strategy.bar_size,
                    self.cfg.risk.rth_only)
        self.bars = await self.ib.reqHistoricalDataAsync(
            self.contract, endDateTime="", durationStr=self.cfg.strategy.history_duration,
            barSizeSetting=self.cfg.strategy.bar_size, whatToShow="TRADES",
            useRTH=self.cfg.risk.rth_only and not self.cfg.context.needs_eth_data, formatDate=2, keepUpToDate=True)
        self.bars.updateEvent += self._on_bar_update
        self._last_update_mono = _time.monotonic()
        self._needs_resubscribe = False

    def _wire_events(self) -> None:
        if self._events_wired:
            return
        self.ib.execDetailsEvent += self._on_exec_details
        self.ib.commissionReportEvent += self._on_commission_report
        self.ib.errorEvent += self._on_error
        self._events_wired = True

    def _in_session(self) -> bool:
        now = datetime.now(timezone.utc).astimezone(self.risk.tz)
        if now.weekday() >= 5:
            return False
        hhmm = now.strftime("%H:%M")
        return self.cfg.risk.rth_open_time <= hhmm < self.cfg.risk.rth_close_time

    async def watchdog_async(self) -> None:
        stale_after = self.cfg.execution.stale_bar_factor * self.bar_sec
        if self._needs_resubscribe or (self._in_session() and _time.monotonic() - self._last_update_mono > stale_after):
            logger.error("Market-data stream stale/lost -> resubscribing")
            await self.subscribe_async()
        # exposure we are not managing (e.g. manual order, lost state)
        if self.active is None and not self._flattening and _time.monotonic() - self._last_orphan_check > 60:
            self._last_orphan_check = _time.monotonic()
            await self.ib.reqPositionsAsync()
            if self.net_position() != 0:
                logger.critical("Position without managed bracket detected by watchdog")
                await self._adopt_or_flatten(self.net_position(), self._contract_open_trades())
        # flatten that did not complete
        if self._flatten_reason and self.net_position() != 0 and not self._flattening and self.risk.should_flatten_eod(
                pd.Timestamp.now(tz="UTC")):
            if self._flatten_retries < 3:
                self._flatten_retries += 1
                logger.error("EOD position still open - retrying flatten (%d/3)", self._flatten_retries)
                await self.flatten_async("EOD retry")
            elif self._flatten_retries == 3:
                self._flatten_retries += 1
                logger.critical("EOD flatten failed 3 times - MANUAL INTERVENTION REQUIRED")
        self.persist()

    async def _session_async(self) -> None:
        await self.connect_async()
        self._wire_events()
        await self.resolve_contract_async()
        await self.recover_async()
        await self.subscribe_async()
        logger.info("Bot live. Ctrl+C to stop.")
        while not self._stop and self.ib.isConnected():
            await asyncio.sleep(self.cfg.execution.watchdog_interval_sec)
            await self.watchdog_async()

    async def main_async(self) -> None:
        delay = self.cfg.execution.reconnect_initial_delay_sec
        while not self._stop:
            try:
                await self._session_async()
                delay = self.cfg.execution.reconnect_initial_delay_sec
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Session error")
            finally:
                if self.ib.isConnected():
                    self.ib.disconnect()
            if self._stop:
                break
            logger.warning("Disconnected - reconnecting in %.0fs", delay)
            await asyncio.sleep(delay)
            delay = min(delay * 2, self.cfg.execution.reconnect_max_delay_sec)

    def run_streaming(self) -> None:
        try:
            util.run(self.main_async())
        except KeyboardInterrupt:
            logger.info("Shutdown requested (Ctrl+C). Protective bracket orders remain on the exchange.")
        finally:
            self._stop = True
            self.persist()
            if self.ib.isConnected():
                self.ib.disconnect()

    # ------------------------------------------------------------------ history download
    def download_historical_csv(self, output_path: str, duration: str = "5 D", include_eth: bool = False) -> pd.DataFrame:
        from ib_async import ContFuture
        port = self.cfg.ibkr.paper_port if self.mode == "paper" else self.cfg.ibkr.live_port
        self.ib.connect(self.cfg.ibkr.host, port, clientId=self.cfg.ibkr.client_id, timeout=self.cfg.ibkr.timeout)
        try:
            long_span = any(u in duration.upper() for u in ("M", "W", "Y")) or (
                "D" in duration.upper() and int(duration.split()[0]) > 15)
            c = self.cfg.contract
            if long_span:
                q = self.ib.qualifyContracts(ContFuture(symbol=c.symbol, exchange=c.exchange, currency=c.currency))
                target = q[0]
            else:
                details = self.ib.reqContractDetails(Future(symbol=c.symbol, exchange=c.exchange, currency=c.currency))
                target = pick_contract(details, self._now_et_date(), self.cfg.execution.roll_days_before_expiry)
            bars = self.ib.reqHistoricalData(target, endDateTime="", durationStr=duration,
                                             barSizeSetting=self.cfg.strategy.bar_size, whatToShow="TRADES",
                                             useRTH=self.cfg.risk.rth_only and not include_eth, formatDate=2, keepUpToDate=False,
                                             timeout=120)
            df = util.df(bars)
            if df is None or df.empty:
                raise RuntimeError("No historical bars returned from IBKR.")
            df = df.rename(columns={"date": "timestamp"})[["timestamp", "open", "high", "low", "close", "volume"]]
            df.to_csv(output_path, index=False)
            logger.info("Saved %d bars to %s", len(df), output_path)
            return df
        finally:
            if self.ib.isConnected():
                self.ib.disconnect()
