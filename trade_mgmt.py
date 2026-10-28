"""
Open-trade stop management shared by the backtester and the live runner, so both apply
exactly the same break-even / time-decay rules.

Rules (evaluated once per CLOSED bar, effective from the next bar):
  1. Break-even: once the bar's extreme reaches entry +/- 1R, move the stop to
     entry +/- breakeven_offset_points.
  2. Time-decay: if +1R has not been reached after `time_decay_bars` bars since the FILL, tighten
     the stop to -time_decay_stop_r * R (only if the bar did not already trade through that level).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from config import RiskConfig
from indicators import round_to_tick


@dataclass
class StopManager:
    direction: str              # "LONG" | "SHORT"
    entry_price: float          # actual (average) fill price
    stop_price: float           # current working stop
    one_r: float                # initial risk in points
    cfg: RiskConfig
    tick_size: float = 0.25
    be_moved: bool = False
    decay_moved: bool = False

    @property
    def sign(self) -> int:
        return 1 if self.direction == "LONG" else -1

    def update(self, bar_high: float, bar_low: float, bars_held: int) -> Optional[Tuple[float, str]]:
        """Return (new_stop, kind) if the stop should be modified after this closed bar."""
        s = self.sign
        favorable = bar_high if s > 0 else bar_low

        if self.cfg.breakeven_at_1r and not self.be_moved and s * (favorable - self.entry_price) >= self.one_r:
            new_sl = round_to_tick(self.entry_price + s * self.cfg.breakeven_offset_points, self.tick_size)
            if s * (new_sl - self.stop_price) > 0:
                self.stop_price = new_sl
                self.be_moved = True
                return new_sl, "breakeven"
            return None

        if (
            self.cfg.time_decay_bars > 0
            and not self.be_moved
            and not self.decay_moved
            and bars_held >= self.cfg.time_decay_bars
        ):
            dec_sl = round_to_tick(self.entry_price - s * self.cfg.time_decay_stop_r * self.one_r, self.tick_size)
            adverse = bar_low if s > 0 else bar_high
            # tighten only if bar hasn't already traded through it and it is tighter than current stop
            if s * (adverse - dec_sl) > 0 and s * (dec_sl - self.stop_price) > 0:
                self.stop_price = dec_sl
                self.decay_moved = True
                return dec_sl, "time_decay"
        return None

    def exit_label(self) -> str:
        if self.be_moved:
            return "Break-Even Stop"
        if self.decay_moved:
            return "Time-Decay Stop (-0.5R)"
        return "Stop Loss"
