"""
Bar-by-bar backtester that reuses the live strategy, risk manager and stop manager.

Fill models
-----------
signal_close : legacy baseline - entry at signal-bar close +/- slippage (optimistic; kept for parity tests).
next_bar     : realistic - after the signal bar closes a marketable limit (signal close +/- N ticks) is
               working for `cancel_unfilled_entry_bars` bars. It fills at the bar open if the open is
               already inside the limit, otherwise at the limit if price trades through it, else it
               times out and no trade is taken.

Intrabar ambiguity is resolved pessimistically: stop before target; BE/time-decay stop changes take
effect from the NEXT bar; nothing is updated on the fill bar.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd

from config import BotConfig
from indicators import filter_rth, round_to_tick, to_session_time
from metrics import compute_metrics
from risk_manager import RiskManager
from strategy import NQIntradayStrategy, TradeSignal
from synthetic import generate_synthetic_nq_data  # noqa: F401  (re-exported)
from trade_mgmt import StopManager


@dataclass
class SimulatedTrade:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    direction: str
    reason: str
    setup: str
    contracts: int
    entry_price: float
    exit_price: float
    stop_loss: float
    take_profit: float
    exit_reason: str
    gross_points: float
    net_pnl_usd: float
    r_multiple: float
    bars_held: int


def prepare_bars(df: pd.DataFrame, cfg: BotConfig) -> pd.DataFrame:
    """tz-normalise, resample 1-min -> target bar size if needed, optionally drop non-RTH bars."""
    work = df.copy()
    work["timestamp"] = to_session_time(work["timestamp"], cfg.risk.timezone)

    if len(work) > 2:
        median_sec = work["timestamp"].diff().dt.total_seconds().median()
        rules = {"1 min": ("1min", 60), "2 mins": ("2min", 120), "5 mins": ("5min", 300)}
        rule, target_sec = rules.get(cfg.strategy.bar_size, ("1min", 60))
        if median_sec == 60 and target_sec > 60:
            work = (
                work.set_index("timestamp")
                .resample(rule, closed="left", label="left")
                .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
                .dropna()
                .reset_index()
            )
    if cfg.backtest.rth_filter_data:
        work = filter_rth(work, cfg.risk.timezone, cfg.risk.rth_open_time, cfg.risk.rth_close_time)
    return work.reset_index(drop=True)


def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


class Backtester:
    """Simulates the strategy on historical bars."""

    def __init__(self, config: BotConfig, strategy: Optional[NQIntradayStrategy] = None,
                 commission_per_side_usd: Optional[float] = None, slippage_ticks: Optional[int] = None) -> None:
        self.cfg = config
        self.strategy = strategy or NQIntradayStrategy(config.strategy, config.risk, config.contract)
        # explicit overrides kept for backward compatibility with the baseline API
        self.commission_per_side = commission_per_side_usd if commission_per_side_usd is not None \
            else config.commission_per_side
        if slippage_ticks is not None:
            config.costs.stop_slippage_ticks = slippage_ticks
            config.costs.eod_slippage_ticks = slippage_ticks
            config.costs.entry_slippage_ticks = slippage_ticks
        self.risk = RiskManager(config.risk, config.contract)

    # ------------------------------------------------------------------ helpers
    def _slip(self, ticks: int) -> float:
        return ticks * self.cfg.contract.tick_size

    def enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.strategy.prepare_dataframe(prepare_bars(df, self.cfg))

    def run(self, df: Optional[pd.DataFrame] = None, enriched: Optional[pd.DataFrame] = None,
            start: Optional[str] = None, end: Optional[str] = None) -> Dict[str, object]:
        """
        Simulate. Pass raw `df`, or a pre-computed `enriched` frame (fast path for sweeps).
        `start`/`end`: optional session-date bounds [start, end) evaluated in the session timezone.
        """
        if enriched is None:
            if df is None:
                raise ValueError("Provide df or enriched")
            enriched = self.enrich(df)

        self.risk = RiskManager(self.cfg.risk, self.cfg.contract)
        c = self.cfg
        point_val = c.contract.point_value
        tick = c.contract.tick_size
        costs, bt = c.costs, c.backtest

        local_dates = pd.to_datetime(to_session_time(enriched["timestamp"], c.risk.timezone).dt.date)
        mask = pd.Series(True, index=enriched.index)
        if start:
            mask &= local_dates >= pd.Timestamp(start)
        if end:
            mask &= local_dates < pd.Timestamp(end)
        idxs = list(enriched.index[mask.to_numpy()])
        if not idxs:
            return {"trades": [], "metrics": compute_metrics([], []), "trades_df": pd.DataFrame(), "trading_days": []}
        lo, hi = idxs[0], idxs[-1]
        trading_days = sorted(set(local_dates[mask].dt.date))

        ts_col = enriched["timestamp"]
        o_arr, h_arr = enriched["open"].to_numpy(float), enriched["high"].to_numpy(float)
        l_arr, c_arr = enriched["low"].to_numpy(float), enriched["close"].to_numpy(float)

        trades: List[SimulatedTrade] = []
        pending: Optional[TradeSignal] = None
        pending_idx = -1
        mgr: Optional[StopManager] = None
        sig: Optional[TradeSignal] = None
        contracts = 0
        fill_idx = -1
        entry_ts: Optional[pd.Timestamp] = None

        def close_trade(exit_price: float, exit_reason: str, i: int, ts: pd.Timestamp) -> None:
            nonlocal mgr, sig, contracts
            assert mgr is not None and sig is not None
            gross = (exit_price - mgr.entry_price) * mgr.sign
            net = gross * point_val * contracts - 2.0 * self.commission_per_side * contracts
            risk_usd = sig.stop_distance_points * point_val * contracts
            trades.append(SimulatedTrade(
                entry_time=entry_ts, exit_time=ts, direction=sig.direction, reason=sig.reason, setup=sig.setup,
                contracts=contracts, entry_price=round(mgr.entry_price, 2), exit_price=round(exit_price, 2),
                stop_loss=mgr.stop_price, take_profit=sig.take_profit, exit_reason=exit_reason,
                gross_points=round(gross, 2), net_pnl_usd=round(net, 2),
                r_multiple=round(net / risk_usd, 3) if risk_usd > 0 else float("nan"),
                bars_held=i - fill_idx,
            ))
            self.risk.record_trade_closed(net, exit_bar_index=i)
            mgr = None
            sig = None
            contracts = 0

        def start_position(s: TradeSignal, fill_price: float, i: int, ts: pd.Timestamp) -> None:
            nonlocal mgr, sig, contracts, fill_idx, entry_ts
            sig = s
            contracts = self.risk.calculate_contracts(s.stop_distance_points)
            mgr = StopManager(s.direction, fill_price, s.stop_loss, s.stop_distance_points, c.risk, tick)
            fill_idx = i
            entry_ts = ts if bt.fill_model == "next_bar" else s.timestamp

        def manage(i: int, ts: pd.Timestamp, fill_bar: bool) -> bool:
            """Apply exits / stop updates on bar i. Returns True if the trade closed."""
            assert mgr is not None and sig is not None
            s = mgr.sign
            o, h, l, cl = o_arr[i], h_arr[i], l_arr[i], c_arr[i]
            stop = mgr.stop_price
            if (l <= stop) if s > 0 else (h >= stop):
                ref = mgr.entry_price if fill_bar else o
                px = (min(stop, ref) if s > 0 else max(stop, ref)) if bt.model_gaps else stop
                close_trade(px - s * self._slip(costs.stop_slippage_ticks), mgr.exit_label(), i, ts)
                return True
            if (h >= sig.take_profit) if s > 0 else (l <= sig.take_profit):
                close_trade(sig.take_profit, "Take Profit", i, ts)
                return True
            if self.risk.should_flatten_eod(ts):
                close_trade(cl - s * self._slip(costs.eod_slippage_ticks), "EOD Flatten", i, ts)
                return True
            if not fill_bar:
                mgr.update(h, l, i - fill_idx)
            return False

        for i in range(lo, hi + 1):
            ts = pd.Timestamp(ts_col.iloc[i])
            self.risk.check_and_reset_session(ts)

            # 1. open position
            if mgr is not None:
                if manage(i, ts, fill_bar=False):
                    pass
                continue

            # 2. working (unfilled) entry order - next_bar model only
            if pending is not None:
                s = pending
                sgn = 1 if s.direction == "LONG" else -1
                lim = round_to_tick(s.entry_price + sgn * c.risk.entry_limit_slippage_ticks * tick, tick)
                o, h, l = o_arr[i], h_arr[i], l_arr[i]
                fill: Optional[float] = None
                if (o <= lim) if sgn > 0 else (o >= lim):
                    fill = o
                elif (l <= lim) if sgn > 0 else (h >= lim):
                    fill = lim
                if fill is not None:
                    fill += sgn * self._slip(costs.extra_entry_slippage_ticks)
                    start_position(s, fill, i, ts)
                    pending = None
                    manage(i, ts, fill_bar=True)
                    continue
                waited = i - pending_idx
                expired = c.risk.cancel_unfilled_entry_bars > 0 and waited >= c.risk.cancel_unfilled_entry_bars
                if expired or self.risk.should_flatten_eod(ts):
                    pending = None
                continue

            # 3. look for a new trade
            allowed, _ = self.risk.can_open_trade(ts, current_bar_index=i)
            if not allowed:
                continue
            signal = self.strategy.evaluate_bar(enriched, idx=i)
            if signal is None:
                continue
            if bt.fill_model == "signal_close":
                sgn = 1 if signal.direction == "LONG" else -1
                px = signal.entry_price + sgn * self._slip(costs.entry_slippage_ticks + costs.extra_entry_slippage_ticks)
                start_position(signal, px, i, ts)
            else:
                pending, pending_idx = signal, i

        # force-close at the end of the simulated window
        if mgr is not None:
            close_trade(c_arr[hi], "End of Data", hi, pd.Timestamp(ts_col.iloc[hi]))

        return {
            "trades": trades,
            "metrics": compute_metrics(trades, trading_days),
            "trades_df": pd.DataFrame([t.__dict__ for t in trades]) if trades else pd.DataFrame(),
            "trading_days": trading_days,
        }
