"""
Signal engine for NQ / MNQ intraday trading.

Pipeline per closed bar:  global filters -> regime (per direction) -> setup triggers -> confidence
score gate -> stop/target construction.  Long and short share one direction-signed implementation
(`sign = +1 / -1`) so the two sides cannot drift apart.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Tuple

import numpy as np
import pandas as pd

from config import ContractConfig, RiskConfig, StrategyConfig
from indicators import enrich_indicators, round_to_tick

SignalDirection = Literal["LONG", "SHORT"]


@dataclass
class TradeSignal:
    """Actionable signal produced on a closed bar."""
    timestamp: pd.Timestamp
    direction: SignalDirection
    reason: str
    entry_price: float
    stop_loss: float
    take_profit: float
    stop_distance_points: float
    atr: float
    rsi: float
    vwap: float
    ema_fast: float
    ema_slow: float
    meta_probability: float = 1.0
    kalman_vel_atr: float = 0.0
    hurst: float = 0.5
    setup: str = ""


def _in_band(x: float, band: Tuple[float, float]) -> bool:
    return band[0] <= x <= band[1]


class NQIntradayStrategy:
    """Hybrid EMA(9/21/50) + session-VWAP z-band + PDH/PDL + ORB strategy with a confidence gate."""

    def __init__(self, strategy_cfg: StrategyConfig, risk_cfg: RiskConfig, contract_cfg: ContractConfig) -> None:
        self.s_cfg = strategy_cfg
        self.r_cfg = risk_cfg
        self.c_cfg = contract_cfg

    # ------------------------------------------------------------------ indicators
    def prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        s = self.s_cfg
        return enrich_indicators(
            df,
            fast_ema=s.fast_ema_period,
            slow_ema=s.slow_ema_period,
            trend_ema=s.trend_ema_period,
            atr_period=s.atr_period,
            rsi_period=s.rsi_period,
            timezone=self.r_cfg.timezone,
            kalman_q_pos=s.kalman_q_pos,
            kalman_q_vel=s.kalman_q_vel,
            kalman_r_meas=s.kalman_r_meas,
            hurst_lag_q=s.hurst_lag_q,
            hurst_window=s.hurst_window,
        )

    @property
    def warmup_bars(self) -> int:
        s = self.s_cfg
        return max(s.trend_ema_period, s.slow_ema_period, s.atr_period, s.hurst_window) + 5

    # ------------------------------------------------------------------ confidence score
    @staticmethod
    def compute_meta_probability(
        direction: SignalDirection, kalman_vel_atr: float, hurst: float, body_ratio: float, vwap_z: float
    ) -> float:
        """
        Heuristic logistic confidence score in (0, 1). The weights are hand-set, not fitted, so this is
        a ranking/gating score and NOT a calibrated win probability.
        """
        signed_k = kalman_vel_atr if direction == "LONG" else -kalman_vel_atr
        signed_k = float(np.clip(signed_k, -0.5, 0.8))
        vz_opt = 1.0 - abs(abs(vwap_z) - 1.1) / 1.2
        z = 0.35 + 1.8 * signed_k + 1.5 * (hurst - 0.42) + 0.6 * (body_ratio - 0.50) + 0.4 * vz_opt
        return float(1.0 / (1.0 + np.exp(-float(np.clip(z, -15.0, 15.0)))))

    # ------------------------------------------------------------------ per-direction logic
    def _regime_ok(self, sign: int, c: pd.Series, atr: float) -> bool:
        s = self.s_cfg
        close_p, vwap = float(c["close"]), float(c["vwap"])
        if s.use_session_vwap and sign * (close_p - vwap) <= 0:
            return False
        if s.require_trend_ema_alignment and sign * (close_p - float(c["ema_trend"])) <= 0:
            return False
        if sign * (float(c["ema_fast"]) - float(c["ema_slow"])) <= 0:
            return False
        if sign * float(c["slow_slope_atr"]) <= s.min_slow_slope_atr:
            return False
        if s.use_pdh_pdl_guard:
            level = c["pdh"] if sign > 0 else c["pdl"]
            if pd.notna(level):
                dist = sign * (float(level) - close_p)  # distance to the wall in trade direction
                if 0 < dist < s.pdh_pdl_buffer_atr * atr:
                    return False
        return True

    def _candle_ok(self, sign: int, c: pd.Series) -> bool:
        wick = float(c["upper_wick_ratio"] if sign > 0 else c["lower_wick_ratio"])
        return sign * (float(c["close"]) - float(c["open"])) > 0 and wick <= self.s_cfg.max_opposing_wick_ratio

    def _find_setup(self, sign: int, c: pd.Series, p: pd.Series, atr: float, rsi: float, vol_ratio: float
                    ) -> Optional[Tuple[str, str]]:
        """Return (setup_key, reason) for the first matching trigger, or None."""
        s, mode = self.s_cfg, self.s_cfg.entry_mode
        side = "long" if sign > 0 else "short"
        word = "Bullish" if sign > 0 else "Bearish"
        arrow = ">" if sign > 0 else "<"
        close_p = float(c["close"])
        ef, es = float(c["ema_fast"]), float(c["ema_slow"])
        tol = s.pullback_ema_tolerance_atr * atr
        fp, sp = s.fast_ema_period, s.slow_ema_period

        # A) EMA pullback rejection
        if mode in ("pullback", "both", "hybrid_all") and _in_band(rsi, getattr(s, f"rsi_pullback_{side}")):
            extreme = float(c["low"] if sign > 0 else c["high"])
            touched = sign * (extreme - ef) <= tol and sign * (extreme - es) >= -tol
            reclaimed = sign * (close_p - ef) > 0
            prev_ext = float(p["high"] if sign > 0 else p["low"])
            broke = sign * (close_p - prev_ext) > 0 if s.require_prev_extreme_break else True
            if touched and reclaimed and broke:
                return "pullback", f"{word} Pullback off EMA({fp}) {arrow} VWAP & EMA50"

        # B) EMA crossover
        if mode in ("crossover", "both", "hybrid_all") and _in_band(rsi, getattr(s, f"rsi_cross_{side}")):
            crossed = sign * (float(p["ema_fast"]) - float(p["ema_slow"])) <= 0 and sign * (ef - es) > 0
            if crossed and sign * (close_p - ef) > 0:
                return "crossover", f"{word} EMA({fp}/{sp}) Crossover {arrow} VWAP"

        if mode == "hybrid_all":
            # C) 3-bar momentum continuation
            if _in_band(rsi, getattr(s, f"rsi_momentum_{side}")) and vol_ratio >= s.momentum_min_vol_ratio:
                lvl = float(c["prev_3_high"] if sign > 0 else c["prev_3_low"])
                if sign * (close_p - lvl) > 0 and sign * (close_p - ef) <= s.momentum_max_extension_atr * atr:
                    return "momentum", f"{word} 3-Bar Momentum {'Breakout' if sign > 0 else 'Breakdown'} {arrow} VWAP & EMA50"

            # D) Opening-range breakout
            orb = c["orb_high"] if sign > 0 else c["orb_low"]
            if pd.notna(orb) and _in_band(rsi, getattr(s, f"rsi_orb_{side}")):
                prev_ext = float(p["high"] if sign > 0 else p["low"])
                if sign * (prev_ext - float(orb)) <= 0 and sign * (close_p - float(orb)) > 0:
                    return "orb", f"{word} Opening Range {'Breakout (ORB High)' if sign > 0 else 'Breakdown (ORB Low)'} {arrow} VWAP"
        return None

    # ------------------------------------------------------------------ signal construction
    def build_signal(self, c: pd.Series, direction: SignalDirection, reason: str, setup: str,
                     meta_prob: float = 1.0) -> TradeSignal:
        """Construct stop / target around the closed bar's close for a given direction."""
        atr = float(c["atr"])
        raw = atr * self.r_cfg.atr_stop_multiplier if self.r_cfg.stop_mode == "atr" else self.r_cfg.fixed_stop_points
        stop_dist = max(self.r_cfg.min_stop_points, min(self.r_cfg.max_stop_points, round_to_tick(raw)))
        tp_dist = round_to_tick(stop_dist * self.r_cfg.reward_risk_ratio)
        tick = self.c_cfg.tick_size
        entry = round_to_tick(float(c["close"]), tick)
        sgn = 1 if direction == "LONG" else -1
        stop_loss = round_to_tick(entry - sgn * stop_dist, tick)
        take_profit = round_to_tick(entry + sgn * tp_dist, tick)
        return TradeSignal(
            timestamp=pd.Timestamp(c["timestamp"]),
            direction=direction,
            reason=reason,
            entry_price=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            stop_distance_points=round(abs(entry - stop_loss), 2),
            atr=round(atr, 2),
            rsi=round(float(c["rsi"]), 2),
            vwap=round(float(c["vwap"]), 2),
            ema_fast=round(float(c["ema_fast"]), 2),
            ema_slow=round(float(c["ema_slow"]), 2),
            meta_probability=round(meta_prob, 3),
            kalman_vel_atr=round(float(c["kalman_vel_atr"]), 3),
            hurst=round(float(c["hurst"]), 3),
            setup=setup,
        )

    def passes_global_filters(self, c: pd.Series) -> bool:
        s = self.s_cfg
        atr = float(c["atr"])
        if pd.isna(atr) or atr < s.min_atr_points or atr > s.max_atr_points:
            return False
        if float(c["ema_spread_atr"]) < s.min_ema_spread_atr:
            return False
        if float(c["body_ratio"]) < s.min_body_ratio:
            return False
        if float(c["vol_ratio"]) < s.min_volume_ratio:
            return False
        if s.use_vwap_z_filter and not (s.min_vwap_z_score <= abs(float(c["vwap_z"])) <= s.max_vwap_z_score):
            return False
        return True

    def evaluate_bar(self, enriched_df: pd.DataFrame, idx: int = -1) -> Optional[TradeSignal]:
        """Evaluate one bar of an enriched DataFrame. Returns a TradeSignal or None."""
        n = len(enriched_df)
        t = n + idx if idx < 0 else idx
        if t < self.warmup_bars or t >= n:
            return None

        c = enriched_df.iloc[t]
        p = enriched_df.iloc[t - 1]
        if not self.passes_global_filters(c):
            return None

        atr, rsi, vol_ratio = float(c["atr"]), float(c["rsi"]), float(c["vol_ratio"])
        for sign, direction in ((1, "LONG"), (-1, "SHORT")):
            if not (self._regime_ok(sign, c, atr) and self._candle_ok(sign, c)):
                continue
            found = self._find_setup(sign, c, p, atr, rsi, vol_ratio)
            if found is None:
                continue
            setup, reason = found
            meta = self.compute_meta_probability(
                direction, float(c["kalman_vel_atr"]), float(c["hurst"]), float(c["body_ratio"]), float(c["vwap_z"])
            )
            if self.s_cfg.use_quant_meta_filter and meta < self.s_cfg.min_meta_probability:
                # baseline semantics: first matching direction decides; a gated signal ends evaluation
                return None
            return self.build_signal(c, direction, reason, setup, meta)
        return None


class RandomEntryStrategy(NQIntradayStrategy):
    """
    Null-hypothesis benchmark: same filters-free random direction entries, identical stop/target/risk
    machinery. Used to test whether the signal logic beats chance.
    """

    def __init__(self, *args, entry_prob: float = 0.02, seed: int = 0, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.entry_prob = entry_prob
        self.rng = np.random.default_rng(seed)

    def evaluate_bar(self, enriched_df: pd.DataFrame, idx: int = -1) -> Optional[TradeSignal]:
        n = len(enriched_df)
        t = n + idx if idx < 0 else idx
        if t < self.warmup_bars or t >= n:
            return None
        c = enriched_df.iloc[t]
        atr = float(c["atr"])
        if pd.isna(atr) or atr < self.s_cfg.min_atr_points or atr > self.s_cfg.max_atr_points:
            return None
        if self.rng.random() >= self.entry_prob:
            return None
        direction: SignalDirection = "LONG" if self.rng.random() < 0.5 else "SHORT"
        return self.build_signal(c, direction, "Random entry", "random")
