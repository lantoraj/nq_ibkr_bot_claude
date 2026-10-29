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
| Tests | 4 | 47 (baseline-parity golden test, lookahead audit, backtest mechanics, fake-IB execution tests, market-context tests) |

## Layout

```
config.py          all settings (strategy / risk / costs / backtest / execution)
indicators.py      EMA, ATR, RSI, VWAP+z, Kalman velocity, variance-ratio Hurst, PDH/PDL, ORB, RTH filter
strategy.py        signal engine (+ RandomEntryStrategy null benchmark)
trade_mgmt.py      StopManager: break-even + time-decay, shared by backtest and live
context.py         opening gap + overnight (Globex) range per session
events.py          economic-event calendar: entry blackout, flatten-before-event, skip tier-1 days
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

## Market-context filters (all default OFF)

| Flag | What it does |
|---|---|
| `--event-filter` | no entries from 10 min before to 15 min after an event in `data/economic_events.csv`; flattens any open position 5 min before an event (never hold through FOMC/CPI/NFP); optional `skip_tier1_days` |
| `--gap-filter` | blocks trades against an unfilled opening gap larger than 25% of the prior day's range |
| `--overnight-guard` | treats the overnight high/low as walls (like PDH/PDL); needs ETH bars: `download-history --include-eth` |

Findings on the 3-month sample (`reports/research_report.md`, section 9):

* **Most of the profit comes from 8 tier-1 event days:** +$1,208 on 14 trades (1.16 R/trade), versus +$582 on 97 trades
  (0.10 R/trade) on the other 58 days. Skipping event days cuts net from $1,789 to $582, so do **not** enable `skip_tier1_days`
  on this evidence. Away from macro events the strategy is roughly break-even. This is the most important caveat so far.
* The event blackout + pre-event flatten changed nothing in the backtest (no trade was open into an event), so it is pure
  risk control. Keep it on for live trading.
* The gap filter at 25-40% of the prior range keeps net PnL (+$1,782) with 14 fewer trades and lower drawdown ($574 vs $704),
  but 10% is worse and this is in-sample on roll-contaminated gaps. Not enough to enable by default.
* The overnight guard **could not be evaluated**: the bundled CSV starts at 09:30 ET. It is implemented and unit-tested.
* `data/economic_events.csv` was assembled from web search because bls.gov and federalreserve.gov were unreachable from the
  build environment. FOMC dates matched across sources; CPI dates are from secondary sites and marked UNVERIFIED. Confirm them
  and extend the file (it only protects against events it lists; the live runner warns when it is stale).
* The CSV is an unadjusted continuous contract; gaps near the September roll include calendar spread.

## Next steps before trusting it

1. Pull 1-2 years of 2-min data (`download-history`) and re-run `research.py`; judge the strategy on that, not on these 66 days.
2. Download with `--include-eth`, back-adjust or use per-contract data, then re-test the gap and overnight filters.
3. Paper trade 4-6 weeks; compare actual fills against `next_bar` assumptions.
4. Decide on removing the confidence gate / simplifying parameters based on the longer sample.
5. `server_side_breakeven` (IB adjusted stop, survives bot death) is implemented but **untested against a live IB**; try on paper first.

## Known limits

* The execution layer is tested against a fake IB, not a real TWS/Gateway. Expect to shake out issues on paper.
* Fills assume a marketable limit that trades through; real NQ queue effects are not modelled.
* One instrument, one regime, 3 months.
