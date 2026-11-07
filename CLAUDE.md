# nq_ibkr_bot_claude: handoff notes for Claude Code

Intraday MNQ/NQ futures bot for Interactive Brokers (`ib_async`), plus a validation harness. Owner works on **Windows
(PowerShell)**, project at `C:\Users\lanto\AI_Trading\nq_ibkr_bot_claude`, paper account on TWS port 7497.

## Where things stand (read this first)
* The strategy is **not validated for live trading**. On two years of data (517 sessions, Oct 2024 to Oct 2026) the default
  nets +$1,538 on 1 MNQ: profit factor 1.05, Sharpe 0.36, deflated Sharpe 0.20. The early +$2.9k/3-month numbers were a lucky
  window plus optimistic fills plus tuning on the same 66 days.
* Almost all two-year profit arrived in October 2026 (+$1,334 of +$1,538). The curve spent 434 days without a new high.
* Full results: `reports/research_2y.md` and `reports/research_2y.html`; trade list `reports/trades_2y.csv`.
* No scalping edge exists at the 2-minute bar level (`scalp_lab.py`). Tick-level work needs data recorded with
  `python main.py --mode record-ticks` first.

## Pending experiment: "let winners run" (report section 13)
Hold-out design, rules fixed in advance (see README). Run on the two-year bars:
```powershell
git pull origin main
python research.py --csv data\mnq_2m_2y.csv --sections winners --out reports\research_winners.md
```
`data\mnq_2m_2y.csv` exists only on the owner's machine (not in git). If it FAILS the criteria, drop the idea; do not re-tune
it on the same data.

## Commands
```powershell
python -m pytest -q                       # 83 tests, no broker needed
python main.py --mode backtest --csv data\mnq_2m_2y.csv
python research.py --csv data\mnq_2m_2y.csv --out reports\research_2y.md      # full report (~10+ minutes on 2 years)
python main.py --mode download-history --years 2 --include-eth --csv data\mnq_2m_2y.csv   # needs TWS/Gateway running
python main.py --mode paper --symbol MNQ                                      # paper trading
```
Live mode additionally requires `--confirm-live I-ACCEPT-REAL-MONEY-RISK`. Never enable it without the owner asking.

## Layout
`config.py` settings | `strategy.py` signals | `trade_mgmt.py` stop manager (BE, time-decay, trailing; shared by backtest and live) |
`backtest.py` simulator (next-bar fills default; `signal_close` is the legacy optimistic model) | `risk_manager.py` |
`ibkr_execution.py` live runner | `research.py` validation harness (sections 1-13) | `stats_tests.py` PSR/DSR/MinBTL |
`history.py` back-adjusted long-history download | `events.py` + `data/economic_events.csv` | `context.py` gap/overnight |
`entry.py` entry options | `scalp_lab.py`, `microstructure.py`, `tick_recorder.py`, `tick_lab.py` | `tests/`.

## Conventions and cautions
* Research discipline matters more than new features: every variant tried raises the bar (see deflated Sharpe, section 12).
  Prefer hold-out or forward tests; do not tune on the full sample and then report it.
* `data/economic_events.csv` covers only Jul to Dec 2026 and some CPI dates are marked UNVERIFIED. Event results are unreliable
  until it covers the whole sample.
* The live execution layer has been tested against a fake IB only. Expect first-run issues on paper; the downloader worked on
  the owner's machine for the two-year pull.
* `.claude/` holds 29 trading skills, 9 agents and 9 commands from everything-claude-trading (see
  `.claude/THIRD_PARTY_everything-claude-trading.md`).
* Commit messages end with a `Co-Authored-By` line; push to `origin main` (repo `lantoraj/nq_ibkr_bot_claude`).
