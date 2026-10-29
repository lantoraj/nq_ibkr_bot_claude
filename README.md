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
| Tests | 4 | 60 (baseline-parity golden test, lookahead audit, backtest mechanics, fake-IB execution tests, market-context and entry-option tests) |

## Layout

```
config.py          all settings (strategy / risk / costs / backtest / execution)
indicators.py      EMA, ATR, RSI, VWAP+z, Kalman velocity, variance-ratio Hurst, PDH/PDL, ORB, RTH filter
strategy.py        signal engine (+ RandomEntryStrategy null benchmark)
trade_mgmt.py      StopManager: break-even + time-decay, shared by backtest and live
context.py         opening gap + overnight (Globex) range per session
events.py          economic-event calendar: entry blackout, flatten-before-event, skip tier-1 days
entry.py           entry planning shared by backtest and live: retrace limit, confirmation bar
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

* **Correction after the deeper analysis (report section 11):** the 8 tier-1 event days did earn +$1,208, but that is
  two days: the 2026-07-29 FOMC day (+$477, the widest-range day in the sample) and the 2026-10-14 CPI day (+$479).
  The other six event days net +$252. Event days are not wider or more trending than other days on average, and only 2 of
  the 8 best days are event days. So this is a **profit-concentration** problem, not an event effect (see below).
  `skip_tier1_days` still hurts (net falls to +$582), but only because it removes those two days; do not enable it.
* The event blackout + pre-event flatten changed nothing in the backtest (no trade was open into an event), so it is pure
  risk control. Keep it on for live trading.
* The gap filter at 25-40% of the prior range keeps net PnL (+$1,782) with 14 fewer trades and lower drawdown ($574 vs $704),
  but 10% is worse and this is in-sample on roll-contaminated gaps. Not enough to enable by default.
* The overnight guard **could not be evaluated**: the bundled CSV starts at 09:30 ET. It is implemented and unit-tested.
* `data/economic_events.csv` was assembled from web search because bls.gov and federalreserve.gov were unreachable from the
  build environment. FOMC dates matched across sources; CPI dates are from secondary sites and marked UNVERIFIED. Confirm them
  and extend the file (it only protects against events it lists; the live runner warns when it is stale).
* The CSV is an unadjusted continuous contract; gaps near the September roll include calendar spread.

## Profit concentration (report section 11)

* The top 3 days earn 80% of net profit and the top 5 earn 107%; **without the 5 best days the strategy loses $117.**
  Only 29 of 66 days are positive. This is a classic trend-following fat tail, not a smooth edge.
* Day range is the best explanation of a day's PnL (rank correlation +0.31); event status explains less (+0.17).
  Against 8 random days from the 24 widest-range days, the event days beat only 81% of placebos, so volatility explains
  most of it. Against any 8 random days they beat 98.5%.
* Nothing known before 09:45 predicted the big days (prior-day range, opening 15-minute range, opening gap, ATR: all
  rank correlations within +/-0.12). So a simple "trade only on volatile days" filter is not supported by this data.
* Practical meaning: expect long flat or losing stretches punctuated by a few large winners, and size/psychology accordingly.
  Whether those big days recur is the main thing a longer data set must answer.

## Entry-quality experiments (all default OFF; result: nothing beat the baseline)

Motivated by the 35 trades that fail within 3 bars (-$1,829). Flags: `--entry-style retrace --retrace-atr X`, `--confirm-bar`,
`--structural-stop`, `--max-extension-atr X`. Results are in `reports/research_report.md`, section 10.

| Idea | Result vs baseline (+$1,789, 111 trades) |
|---|---|
| Retrace limit (wait for a dip) | 0.10 ATR: +$2,163 but worse in the first half; 0.25: +$969; 0.50: -$426. Non-monotonic and degrading. No robust gain |
| Confirmation bar | +$86. **Waiting for confirmation destroys the edge**, the edge is in the early momentum entry |
| No-chase filter (close near EMA9) | -$619 to +$485. Most winning signals are extended bars, so filtering them out hurts |
| Structural (swing) stop | 2-bar swing: +$2,053 (better in both halves); 3-bar: +$1,420; 5-bar: +$1,082. Gets worse as the swing lengthens, within noise of the +/-$200 sensitivity seen earlier |

Takeaway: the data do not support changing the entry. The only candidates worth re-testing on a longer data set are the 2-bar
structural stop and a 0.10 ATR retrace, and both gains are inside the sample's noise.

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
