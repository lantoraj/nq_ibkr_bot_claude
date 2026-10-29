"""
Entry planning shared by the backtester and the live runner (so they cannot drift apart).

plan_entry   : where the resting limit goes, and the signal re-based to that price (stop/target keep their distances)
confirm_ok   : did the bar after the signal confirm the move?
"""
from __future__ import annotations

from typing import Tuple

from config import BotConfig
from indicators import round_to_tick
from strategy import TradeSignal


def plan_entry(signal: TradeSignal, cfg: BotConfig) -> Tuple[float, TradeSignal]:
    """Return (limit_price, signal). 'retrace' re-bases the signal onto the limit price."""
    tick = cfg.contract.tick_size
    sgn = 1 if signal.direction == "LONG" else -1
    if cfg.entry.execution_style == "retrace":
        lim = round_to_tick(signal.entry_price - sgn * cfg.entry.retrace_atr * signal.atr, tick)
        return lim, signal.rebased(lim)
    slip = cfg.risk.entry_limit_slippage_ticks * tick
    return round_to_tick(signal.entry_price + sgn * slip, tick), signal


def confirm_ok(signal: TradeSignal, bar_close: float, bar_low: float, bar_high: float, cfg: BotConfig) -> bool:
    """Confirmation bar: closes beyond the signal close (by a margin) without touching the stop."""
    sgn = 1 if signal.direction == "LONG" else -1
    moved = sgn * (bar_close - signal.entry_price) > cfg.entry.confirm_min_move_atr * signal.atr
    alive = bar_low > signal.stop_loss if sgn > 0 else bar_high < signal.stop_loss
    return bool(moved and alive)
