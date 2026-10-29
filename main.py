"""
CLI entry point.

  python main.py --mode backtest --csv data/mnq_2m_3months.csv
  python main.py --mode backtest --csv data/mnq_2m_3months.csv --fill-model signal_close   # legacy optimistic model
  python main.py --mode download-history --duration "6 M" --csv data/mnq_2m_6m.csv
  python main.py --mode paper --symbol MNQ
  python main.py --mode live  --symbol MNQ --confirm-live I-ACCEPT-REAL-MONEY-RISK
Robustness research:  python research.py --sections all
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

from backtest import Backtester, generate_synthetic_nq_data
from config import BotConfig

LIVE_CONFIRMATION = "I-ACCEPT-REAL-MONEY-RISK"


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="NQ / MNQ intraday futures bot (IBKR)")
    p.add_argument("--mode", choices=["backtest", "paper", "live", "download-history"], default="backtest")
    p.add_argument("--symbol", choices=["NQ", "MNQ"], default="MNQ")
    p.add_argument("--contract-month", default="", help="e.g. 202612; empty = auto-select with roll rule")
    p.add_argument("--bar-size", choices=["1 min", "2 mins", "5 mins"], default="2 mins")
    p.add_argument("--entry-mode", choices=["pullback", "crossover", "both", "hybrid_all"], default="hybrid_all")
    p.add_argument("--contracts", type=int, default=1)
    p.add_argument("--max-daily-loss", type=float, default=250.0)
    p.add_argument("--csv", default="")
    p.add_argument("--duration", default="5 D")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=0)
    p.add_argument("--client-id", type=int, default=101)
    p.add_argument("--fill-model", choices=["next_bar", "signal_close"], default="next_bar")
    p.add_argument("--include-eth", action="store_true", help="download-history: include overnight bars (needed for the overnight guard)")
    p.add_argument("--event-filter", action="store_true", help="enable economic-event calendar filter")
    p.add_argument("--gap-filter", action="store_true", help="block trades against an unfilled opening gap")
    p.add_argument("--overnight-guard", action="store_true", help="treat overnight high/low as walls (needs ETH data)")
    p.add_argument("--state-file", default="state/bot_state.json")
    p.add_argument("--confirm-live", default="", help=f"must equal {LIVE_CONFIRMATION} to trade a live account")
    return p.parse_args(argv)


def build_config(args: argparse.Namespace) -> BotConfig:
    cfg = BotConfig()
    cfg.contract.symbol = args.symbol
    cfg.contract.contract_month = args.contract_month
    cfg.strategy.bar_size = args.bar_size
    cfg.strategy.entry_mode = args.entry_mode
    cfg.risk.fixed_contracts = args.contracts
    cfg.risk.max_daily_loss_usd = args.max_daily_loss
    cfg.ibkr.host = args.host
    cfg.ibkr.client_id = args.client_id
    cfg.backtest.fill_model = args.fill_model
    cfg.execution.state_file = args.state_file
    cfg.context.use_event_filter = args.event_filter
    cfg.context.use_gap_filter = args.gap_filter
    cfg.context.use_overnight_guard = args.overnight_guard
    if args.port > 0:
        if args.mode == "live":
            cfg.ibkr.live_port = args.port
        else:
            cfg.ibkr.paper_port = args.port
    return cfg


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")
    args = parse_args(argv)
    log = logging.getLogger("nq_ibkr_bot")
    cfg = build_config(args)

    if args.mode == "backtest":
        if args.csv and Path(args.csv).exists():
            df = pd.read_csv(args.csv)
        else:
            log.warning("No CSV given: using SYNTHETIC data (smoke test only, results are meaningless)")
            df = generate_synthetic_nq_data(num_days=5)
        res = Backtester(cfg).run(df)
        print("\n" + "=" * 68)
        print(f"  BACKTEST ({cfg.contract.symbol} | {cfg.strategy.bar_size} | fills={cfg.backtest.fill_model})")
        print("=" * 68)
        for k, v in res["metrics"].items():
            print(f"  {k:<24}: {v}")
        print("=" * 68)
        tdf = res["trades_df"]
        if not tdf.empty:
            cols = ["entry_time", "exit_time", "direction", "setup", "entry_price", "exit_price", "exit_reason",
                    "net_pnl_usd", "r_multiple"]
            print("\nLast trades:\n" + tdf[cols].tail(10).to_string(index=False))
        return 0

    from ibkr_execution import IBKRNQBotRunner

    if args.mode == "download-history":
        out = args.csv or f"data/{cfg.contract.symbol.lower()}_history.csv"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        IBKRNQBotRunner(cfg, mode="paper").download_historical_csv(out, duration=args.duration, include_eth=args.include_eth)
        return 0

    if args.mode == "live":
        if args.confirm_live != LIVE_CONFIRMATION:
            log.error("Refusing to start LIVE trading. Re-run with --confirm-live %s", LIVE_CONFIRMATION)
            return 2
        log.warning("LIVE TRADING on port %d", cfg.ibkr.live_port)

    IBKRNQBotRunner(cfg, mode=args.mode).run_streaming()
    return 0


if __name__ == "__main__":
    sys.exit(main())
