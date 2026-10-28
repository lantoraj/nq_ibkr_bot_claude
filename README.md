# nq_ibkr_bot_claude

Hardened rework of [`lantoraj/nq_ibkr_bot`](https://github.com/lantoraj/nq_ibkr_bot): same intraday MNQ/NQ strategy,
but with a realistic backtester, a statistical validation harness, and a live engine whose failure modes were fixed.

> **Status: research / paper-trading only.** 111 trades over 66 sessions in one market regime cannot establish an edge.
> Run it on a paper account for weeks and extend the data set (see "Next steps") before risking money.

## What changed vs the baseline

| Area | Baseline | Now |
|---|---|---|
| Backtest fills | fill at signal-bar close | next-bar marketable limit (open-or-limit fill, 3-bar timeout), gap-aware stops |
| Session data | CSV includes 16:00-17:00 ET bars in VWAP / PDH / PDL | RTH-only (configurable) |
| Metrics | "Sharpe" = per-trade t-stat | daily-PnL Sharpe, expectancy in R, scratch-aware win rate, bootstrap drawdown |
| Validation | none (all tuning in-sample) | `research.py`: ablation, stress, sensitivity grids, walk-forward, random-entry null, bootstrap |
| Config | 9 dead fields; RSI bands & other thresholds hard-coded | every field consumed; thresholds in `StrategyConfig` |
| `strategy.py` | 8 copy-pasted long/short blocks | one direction-signed implementation (verified identical to baseline: 109 trades, +$2,926.84) |
| Live stop moves | set `order.stopPrice` (not a field of `StopOrder`; raises `AttributeError`) so **break-even / time-decay never worked live** | `order.auxPrice`; same `StopManager` as the backtester |
| Bracket exits | TP and SL not OCA-linked | explicit OCA group |
| Flatten | cancel then immediately market-close (can reverse the position if the stop fills meanwhile) | cancel -> wait -> re-read position -> close remainder |
| Restart | in-memory state lost, daily limits reset | state file; recover/adopt/flatten orphan positions |
| PnL accounting | `realizedPNL != 0` filter (scratch trades uncounted) | PnL from the bracket's own fills + commissions |
| Connectivity | none | auto-reconnect with back-off, stale-data watchdog, resubscribe |
| Contract | nearest unexpired contract | rolls 8 days before expiry |
| Time zones | naive timestamps silently treated as UTC | naive timestamps rejected; IB bars requested as UTC |
| Live safety | warning log only | `--confirm-live I-ACCEPT-REAL-MONEY-RISK` required |
| Tests | 4 | 34 (baseline-parity golden test, lookahead audit, backtest mechanics, fake-IB execution tests) |

## Layout

```
config.py          all settings (strategy / risk / costs / backtest / execution)
indicators.py      EMA, ATR, RSI, VWAP+z, Kalman velocity, variance-ratio Hurst, PDH/PDL, ORB, RTH filter
strategy.py        signal engine (+ RandomEntryStrategy null benchmark)
trade_mgmt.py      StopManager: break-even + time-decay, shared by backtest and live
risk_manager.py    daily limits, session window, sizing, serialisable state
backtest.py        bar-by-bar simulator (signal_close legacy model | next_bar realistic model)
metrics.py         metrics + bootstrap
research.py        robustness harness -> reports/research_report.md
ibkr_execution.py  live/paper runner (ib_async)
state_store.py     atomic JSON persistence
main.py            CLI
tests/             pytest suite
reports/           generated research report + trade list
docs/legacy/       the baseline READMEs
```

## Usage

```bash
pip install -r requirements.txt
python -m pytest -q

python main.py --mode backtest --csv data/mnq_2m_3months.csv                     # realistic fills (default)
python main.py --mode backtest --csv data/mnq_2m_3months.csv --fill-model signal_close   # baseline's optimistic model
python research.py --sections all                                                # full validation report (~3 min)

python main.py --mode download-history --duration "1 Y" --csv data/mnq_2m_1y.csv  # needs TWS/Gateway
python main.py --mode paper --symbol MNQ                                          # paper port 7497
python main.py --mode live  --symbol MNQ --confirm-live I-ACCEPT-REAL-MONEY-RISK
```

## What the validation says (3-month MNQ sample, 1 contract)

Full tables: [`reports/research_report.md`](reports/research_report.md).

* The baseline headline (+$2,927, PF 1.97) shrinks to **+$1,789, PF 1.52, max DD $704** once fills are next-bar,
  stops are gap-aware and VWAP/PDH/PDL use RTH bars only. After-hours bars alone are worth ~$870 of the baseline number.
* **Break-even is a risk-smoothing tool, not a profit source** (no-BE: +$1,970 but DD $983). The baseline credited it with
  most of the edge, and it never executed live.
* The **confidence gate (Kalman/Hurst "meta-labeling") adds nothing** at the default threshold (identical results with it
  off). Its weights are hand-set, not fitted. Candidate for removal.
* The **VWAP z-band is the component that earns its keep** (removing it: $1,171, DD $1,001).
* Defaults sit on a **local peak** of the ATR-multiplier x R:R grid, and a 1-tick change to entry price moves net PnL by ~$200:
  the result is noisy at this sample size.
* Walk-forward re-optimisation did **worse** out of sample (+$256) than the fixed defaults (+$1,041): more tuning = more overfit.
* Random entries with the same exits are profitable in ~35% of seeds; the strategy ranks at the ~98th percentile.
  Encouraging but not conclusive, given the strategy was selected after many variants were tried.
* Edge is concentrated in the last ~5 weeks (first half +$455, second half +$1,334).
* Bootstrap: ~6% chance a 111-trade sample is net negative; p95 max drawdown ~$1,300 per MNQ.

## Next steps before trusting it

1. Pull 1-2 years of 2-min data (`download-history`) and re-run `research.py`; judge the strategy on that, not on these 66 days.
2. Paper trade 4-6 weeks; compare actual fills against `next_bar` assumptions.
3. Decide on removing the confidence gate / simplifying parameters based on the longer sample.
4. `server_side_breakeven` (IB adjusted stop, survives bot death) is implemented but **untested against a live IB**; try on paper first.

## Known limits

* The execution layer is tested against a fake IB, not a real TWS/Gateway. Expect to shake out issues on paper.
* Fills assume a marketable limit that trades through; real NQ queue effects are not modelled.
* One instrument, one regime, 3 months.
