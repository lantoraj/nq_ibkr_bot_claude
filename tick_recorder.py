"""
Record top-of-book quotes and trades (tick-by-tick) for MNQ/NQ to CSV so microstructure ideas can be tested on YOUR data.

  python main.py --mode record-ticks --minutes 390          # one regular session
Output: data/ticks/<SYMBOL>_quotes_YYYYMMDD.csv and <SYMBOL>_trades_YYYYMMDD.csv (UTC timestamps), rotated by ET date.
Notes: IB limits concurrent tick-by-tick subscriptions (about 1 per 100 market-data lines); this uses two.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, TextIO

import pytz

logger = logging.getLogger("nq_ibkr_bot")
QUOTE_HDR = "ts,bid,ask,bid_size,ask_size\n"
TRADE_HDR = "ts,price,size\n"


class TickWriter:
    def __init__(self, out_dir: str, symbol: str, tz: str = "America/New_York") -> None:
        self.dir, self.symbol, self.tz = Path(out_dir), symbol, pytz.timezone(tz)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._files: Dict[str, TextIO] = {}
        self.counts = {"quotes": 0, "trades": 0}

    def _file(self, kind: str, ts: datetime) -> TextIO:
        day = ts.astimezone(self.tz).strftime("%Y%m%d")
        key = f"{kind}_{day}"
        if key not in self._files:
            path = self.dir / f"{self.symbol}_{key}.csv"
            new = not path.exists()
            fh = open(path, "a", buffering=1)
            if new:
                fh.write(QUOTE_HDR if kind == "quotes" else TRADE_HDR)
            self._files[key] = fh
        return self._files[key]

    def write(self, tick: Any) -> None:
        """Accepts ib_async TickByTickBidAsk / TickByTickAllLast objects."""
        name = type(tick).__name__
        ts = tick.time
        if name == "TickByTickBidAsk":
            self._file("quotes", ts).write(f"{ts.isoformat()},{tick.bidPrice},{tick.askPrice},{tick.bidSize},{tick.askSize}\n")
            self.counts["quotes"] += 1
        elif name == "TickByTickAllLast":
            self._file("trades", ts).write(f"{ts.isoformat()},{tick.price},{tick.size}\n")
            self.counts["trades"] += 1

    def close(self) -> None:
        for fh in self._files.values():
            fh.close()
        self._files.clear()


async def record_ticks(runner: Any, out_dir: str = "data/ticks", minutes: float = 0) -> None:
    """Uses an IBKRNQBotRunner for connection + contract resolution."""
    await runner.connect_async()
    await runner.resolve_contract_async()
    ib, contract = runner.ib, runner.contract
    writer = TickWriter(out_dir, runner.cfg.contract.symbol, runner.cfg.risk.timezone)

    def on_pending(tickers: Any) -> None:
        for t in tickers:
            for tk in t.tickByTicks:
                writer.write(tk)
            t.tickByTicks.clear()

    ib.pendingTickersEvent += on_pending
    ib.reqTickByTickData(contract, "BidAsk", 0, False)
    ib.reqTickByTickData(contract, "AllLast", 0, False)
    logger.info("Recording ticks for %s to %s%s", contract.localSymbol, out_dir, f" for {minutes} min" if minutes else " (Ctrl+C to stop)")
    try:
        end = asyncio.get_event_loop().time() + minutes * 60 if minutes else None
        while ib.isConnected() and (end is None or asyncio.get_event_loop().time() < end):
            await asyncio.sleep(5)
            logger.info("recorded quotes=%d trades=%d", writer.counts["quotes"], writer.counts["trades"])
    finally:
        ib.pendingTickersEvent -= on_pending
        writer.close()
        if ib.isConnected():
            ib.disconnect()
