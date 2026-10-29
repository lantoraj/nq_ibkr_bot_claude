"""
Configuration for the NQ / MNQ futures IBKR bot.

Every field here is consumed by code (no dead settings). Defaults keep the baseline
strategy parameters; execution / cost / validation settings are new.
"""
from dataclasses import dataclass, field
from typing import Literal, Tuple

Band = Tuple[float, float]


@dataclass
class IBKRConfig:
    """Interactive Brokers TWS / IB Gateway connection settings."""
    host: str = "127.0.0.1"
    paper_port: int = 7497      # TWS paper (IB Gateway paper: 4002)
    live_port: int = 7496       # TWS live  (IB Gateway live: 4001)
    client_id: int = 101
    account: str = ""
    timeout: int = 20


@dataclass
class ContractConfig:
    """Futures contract specification for Nasdaq-100 E-mini (NQ) or Micro (MNQ)."""
    symbol: Literal["NQ", "MNQ"] = "MNQ"
    exchange: str = "CME"
    currency: str = "USD"
    contract_month: str = ""              # e.g. "202612"; empty = auto-resolve with roll rule
    tick_size: float = 0.25

    @property
    def point_value(self) -> float:
        return 20.0 if self.symbol == "NQ" else 2.0


@dataclass
class StrategyConfig:
    """Signal parameters. All thresholds that used to be hard-coded in strategy.py live here."""
    bar_size: Literal["1 min", "2 mins", "5 mins"] = "2 mins"
    history_duration: str = "3 D"

    # EMA & trend
    fast_ema_period: int = 9
    slow_ema_period: int = 21
    trend_ema_period: int = 50
    use_session_vwap: bool = True
    require_trend_ema_alignment: bool = True

    # Trend strength & candle quality
    min_ema_spread_atr: float = 0.10
    min_slow_slope_atr: float = 0.08
    min_body_ratio: float = 0.35
    max_opposing_wick_ratio: float = 0.40
    require_prev_extreme_break: bool = True

    # VWAP z-band and prior-day-level guard
    use_vwap_z_filter: bool = True
    min_vwap_z_score: float = 0.20
    max_vwap_z_score: float = 2.30
    use_pdh_pdl_guard: bool = True
    pdh_pdl_buffer_atr: float = 0.50

    # Heuristic confidence gate (Kalman velocity + Hurst + body + VWAP z).
    # NOTE: hand-set logistic weights, NOT a fitted/calibrated model. Treat as a score.
    use_quant_meta_filter: bool = True
    kalman_q_pos: float = 0.05
    kalman_q_vel: float = 0.01
    kalman_r_meas: float = 1.0
    hurst_lag_q: int = 4
    hurst_window: int = 24
    min_meta_probability: float = 0.58

    entry_mode: Literal["pullback", "crossover", "both", "hybrid_all"] = "hybrid_all"

    # Volatility / volume
    atr_period: int = 14
    min_atr_points: float = 4.0
    max_atr_points: float = 65.0
    rsi_period: int = 14
    min_volume_ratio: float = 0.75
    pullback_ema_tolerance_atr: float = 0.30

    # RSI acceptance bands (low, high) per setup and direction
    rsi_pullback_long: Band = (45.0, 68.0)
    rsi_pullback_short: Band = (32.0, 55.0)
    rsi_cross_long: Band = (50.0, 70.0)
    rsi_cross_short: Band = (30.0, 50.0)
    rsi_momentum_long: Band = (52.0, 70.0)
    rsi_momentum_short: Band = (30.0, 48.0)
    rsi_orb_long: Band = (52.0, 72.0)
    rsi_orb_short: Band = (28.0, 48.0)

    # Momentum-breakout setup
    momentum_min_vol_ratio: float = 1.1
    momentum_max_extension_atr: float = 1.2


@dataclass
class RiskConfig:
    """Position sizing, stops, break-even, time-decay and daily circuit breakers."""
    fixed_contracts: int = 1
    risk_per_trade_usd: float = 0.0
    max_contracts: int = 3

    entry_limit_slippage_ticks: int = 1
    cancel_unfilled_entry_bars: int = 3

    stop_mode: Literal["atr", "fixed_points", "structural"] = "atr"
    atr_stop_multiplier: float = 1.2
    fixed_stop_points: float = 15.0
    structural_lookback: int = 3          # stop_mode='structural': stop beyond the last N bars' swing extreme
    structural_buffer_ticks: int = 2
    min_stop_points: float = 8.0
    max_stop_points: float = 40.0
    reward_risk_ratio: float = 3.0
    breakeven_at_1r: bool = True
    breakeven_offset_points: float = 1.0

    time_decay_bars: int = 6
    time_decay_stop_r: float = 0.50

    max_daily_loss_usd: float = 250.0
    max_daily_trades: int = 2
    max_consecutive_losses: int = 2
    cooldown_bars_after_exit: int = 3

    timezone: str = "America/New_York"
    rth_only: bool = True
    rth_open_time: str = "09:30"
    rth_close_time: str = "16:00"
    entry_start_time: str = "09:45"
    entry_end_time: str = "12:30"
    flatten_eod_time: str = "15:55"


@dataclass
class CostConfig:
    """Transaction-cost model used by the backtester (and as live fallback estimate)."""
    commission_per_side_usd: float = 0.0   # 0 = auto by symbol (MNQ 0.62, NQ 2.10)
    stop_slippage_ticks: int = 1           # adverse slippage on stop-market exits
    eod_slippage_ticks: int = 1            # adverse slippage on forced EOD market exit
    entry_slippage_ticks: int = 1          # legacy 'signal_close' model: adverse slip on entry
    extra_entry_slippage_ticks: int = 0    # stress knob: extra adverse ticks on any entry fill


@dataclass
class BacktestConfig:
    """Simulation realism switches."""
    # 'signal_close': legacy baseline (fill at signal-bar close +/- slip).
    # 'next_bar': realistic - marketable limit is placed after the bar closes and fills on the
    #             next bar(s) only if price trades through it; otherwise it times out.
    fill_model: Literal["signal_close", "next_bar"] = "next_bar"
    model_gaps: bool = True                # stop fills at the (worse) bar open when gapping through
    rth_filter_data: bool = True           # drop bars outside RTH before computing indicators


@dataclass
class ExecutionConfig:
    """Live-execution robustness settings."""
    roll_days_before_expiry: int = 8
    state_file: str = "state/bot_state.json"
    watchdog_interval_sec: int = 15
    stale_bar_factor: float = 2.5          # resubscribe if no bar for factor * bar_size in session
    reconnect_initial_delay_sec: float = 5.0
    reconnect_max_delay_sec: float = 120.0
    cancel_wait_timeout_sec: float = 5.0
    server_side_breakeven: bool = False    # EXPERIMENTAL: IB adjusted-stop (survives bot death)


@dataclass
class ContextConfig:
    """Market-context filters. All default OFF so the baseline behaviour (and its regression tests) is unchanged."""
    # Economic-event calendar (CSV: datetime_et,name,tier). Tier 1 = FOMC / CPI / NFP class events.
    use_event_filter: bool = False
    event_file: str = "data/economic_events.csv"
    event_block_before_min: int = 10      # no new entries from N min before an event ...
    event_block_after_min: int = 15       # ... until N min after it
    event_flatten_before_min: int = 5     # flatten open positions N min before an event (never hold through it)
    skip_tier1_days: bool = False         # stand aside for the whole session on tier-1 event days

    # Opening-gap filter: block trades AGAINST an unfilled gap of at least gap_min_prior_range * (PDH - PDL)
    use_gap_filter: bool = False
    gap_min_prior_range: float = 0.25

    # Overnight (Globex) high/low as walls, like PDH/PDL. Needs ETH bars (download with --include-eth).
    use_overnight_guard: bool = False
    overnight_buffer_atr: float = 0.5

    @property
    def needs_eth_data(self) -> bool:
        return self.use_overnight_guard


@dataclass
class EntryConfig:
    """Entry-quality options. All default OFF (baseline behaviour)."""
    execution_style: Literal["marketable", "retrace"] = "marketable"
    retrace_atr: float = 0.25             # 'retrace': rest a limit this many ATR better than the signal close
    confirm_bars: int = 0                 # 1 = require the next bar to confirm before entering
    confirm_min_move_atr: float = 0.0     # confirmation bar must close this far beyond the signal close
    max_extension_atr: float = 0.0        # >0: skip signals whose close is further than this from the fast EMA


@dataclass
class BotConfig:
    """Master configuration container."""
    ibkr: IBKRConfig = field(default_factory=IBKRConfig)
    contract: ContractConfig = field(default_factory=ContractConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    costs: CostConfig = field(default_factory=CostConfig)
    backtest: BacktestConfig = field(default_factory=BacktestConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    context: ContextConfig = field(default_factory=ContextConfig)
    entry: EntryConfig = field(default_factory=EntryConfig)

    @property
    def commission_per_side(self) -> float:
        if self.costs.commission_per_side_usd > 0:
            return self.costs.commission_per_side_usd
        return 0.62 if self.contract.symbol == "MNQ" else 2.10
