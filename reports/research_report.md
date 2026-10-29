# Research report

Data: `data/mnq_2m_3months.csv` | 66 sessions 2026-07-27 .. 2026-10-27 | symbol MNQ | 1 contract

## 1. Headline under different realism assumptions

| scenario | total_trades | win_rate_pct | scratch_pct | win_rate_ex_scratch_pct | net_pnl_usd | profit_factor | max_drawdown_usd | expectancy_r | sharpe_daily_ann | profitable_months |
|---|---|---|---|---|---|---|---|---|---|---|
| A. legacy baseline (fill at signal close, all CSV bars) | 109 | 56.88 | 30.3 | 38.16 | 2926.84 | 1.97 | 790.52 | 0.393 | 4.36 | 4/4 |
| B. + RTH-only data (VWAP/PDH/PDL exclude after-hours) | 111 | 53.15 | 29.7 | 33.33 | 2057.86 | 1.61 | 629.3 | 0.259 | 3.1 | 4/4 |
| C. next-bar marketable-limit fills (all CSV bars) | 109 | 56.88 | 31.2 | 37.33 | 2706.21 | 1.9 | 825.22 | 0.367 | 4.07 | 4/4 |
| D. DEFAULT: next-bar fills + gap-aware stops + RTH data | 111 | 52.25 | 29.7 | 32.05 | 1789.37 | 1.52 | 703.63 | 0.231 | 2.72 | 4/4 |

A is what the original README reports. D is the number to plan around.

## 2. Ablation (default realistic backtest, one change at a time)

| scenario | total_trades | win_rate_pct | scratch_pct | win_rate_ex_scratch_pct | net_pnl_usd | profit_factor | max_drawdown_usd | expectancy_r | sharpe_daily_ann | profitable_months |
|---|---|---|---|---|---|---|---|---|---|---|
| full default | 111 | 52.25 | 29.7 | 32.05 | 1789.37 | 1.52 | 703.63 | 0.231 | 2.72 | 4/4 |
| no confidence gate | 112 | 51.79 | 29.5 | 31.65 | 1788.0 | 1.52 | 704.97 | 0.225 | 2.74 | 4/4 |
| no VWAP z-band | 116 | 50.0 | 29.3 | 29.27 | 1170.87 | 1.31 | 1001.38 | 0.16 | 1.74 | 2/4 |
| no PDH/PDL guard | 112 | 52.68 | 30.4 | 32.05 | 1777.41 | 1.52 | 777.59 | 0.228 | 2.73 | 3/4 |
| no gate, z-band or PDH/PDL | 117 | 50.43 | 29.9 | 29.27 | 1178.92 | 1.31 | 1075.33 | 0.159 | 1.77 | 2/4 |
| entry: pullback only | 109 | 51.38 | 31.2 | 29.33 | 1108.22 | 1.33 | 819.09 | 0.158 | 1.9 | 2/4 |
| entry: crossover only | 13 | 69.23 | 38.5 | 50.0 | 539.25 | 2.75 | 149.35 | 0.602 | 2.33 | 3/3 |
| entry: pullback+crossover | 108 | 50.93 | 30.6 | 29.33 | 1136.98 | 1.34 | 610.38 | 0.159 | 1.92 | 3/4 |
| no break-even | 110 | 29.09 | 0.0 | 29.09 | 1969.88 | 1.43 | 982.63 | 0.282 | 2.72 | 3/4 |
| no time-decay stop | 110 | 53.64 | 30.9 | 32.89 | 1594.85 | 1.44 | 773.13 | 0.211 | 2.4 | 3/4 |
| no BE and no decay | 109 | 31.19 | 0.0 | 31.19 | 1484.81 | 1.28 | 1337.44 | 0.212 | 1.96 | 2/4 |
| R:R 2.0 | 115 | 50.43 | 19.1 | 38.71 | 1345.42 | 1.37 | 659.9 | 0.163 | 2.72 | 4/4 |
| entry window to 15:00 | 199 | 48.24 | 28.6 | 28.17 | 1660.84 | 1.3 | 1083.68 | 0.128 | 2.06 | 1/4 |

If removing a component does not hurt, it has not earned its complexity.

## 3. Cost / slippage stress

| scenario | total_trades | win_rate_pct | scratch_pct | win_rate_ex_scratch_pct | net_pnl_usd | profit_factor | max_drawdown_usd | expectancy_r | sharpe_daily_ann | profitable_months |
|---|---|---|---|---|---|---|---|---|---|---|
| default (1 tick stop slip) | 111 | 52.25 | 29.7 | 32.05 | 1789.37 | 1.52 | 703.63 | 0.231 | 2.72 | 4/4 |
| stop slip 2 ticks | 111 | 22.52 | 29.7 | 32.05 | 1746.37 | 1.5 | 713.13 | 0.225 | 2.65 | 4/4 |
| stop slip 3 ticks | 111 | 22.52 | 29.7 | 32.05 | 1703.37 | 1.49 | 722.63 | 0.22 | 2.58 | 4/4 |
| entry +1 tick worse | 111 | 52.25 | 28.8 | 32.91 | 1993.37 | 1.58 | 709.63 | 0.253 | 2.99 | 4/4 |
| entry +2 ticks worse | 111 | 52.25 | 28.8 | 32.91 | 1957.87 | 1.56 | 715.63 | 0.248 | 2.94 | 4/4 |
| commission x2 | 111 | 22.52 | 29.7 | 32.05 | 1651.73 | 1.47 | 728.43 | 0.213 | 2.51 | 3/4 |
| worst case: stop 3t, entry +2t, comm x2 | 111 | 23.42 | 28.8 | 32.91 | 1735.23 | 1.48 | 759.43 | 0.219 | 2.6 | 3/4 |

## 4. Parameter sensitivity (net PnL USD; a robust edge forms a plateau, not a single peak)

**ATR stop multiplier x reward:risk**

| atr_mult \ R:R | 1.5 | 2.0 | 3.0 | 4.0 |
|---|---|---|---|---|
| 0.8 | 768.63 (117t) | 920.13 (117t) | 930.37 (116t) | 1635.35 (114t) |
| 1.0 | 1051.82 (116t) | 1163.56 (115t) | 1548.04 (113t) | 1537.51 (111t) |
| 1.2 | 1339.56 (115t) | 1345.42 (115t) | 1789.37 (111t) | 1178.64 (110t) |
| 1.5 | 1432.06 (115t) | 1471.9 (113t) | 1234.61 (110t) | 865.2 (108t) |
| 2.0 | 1881.06 (115t) | 1982.88 (111t) | 1484.35 (109t) | 1003.94 (107t) |

**confidence-gate threshold x min body ratio**

| min_meta \ min_body | 0.25 | 0.35 | 0.45 |
|---|---|---|---|
| 0.0 | 1624.48 (113t) | 1788.0 (112t) | 1407.44 (109t) |
| 0.5 | 1624.48 (113t) | 1788.0 (112t) | 1407.44 (109t) |
| 0.54 | 1624.48 (113t) | 1788.0 (112t) | 1407.44 (109t) |
| 0.58 | 1625.85 (112t) | 1789.37 (111t) | 1436.86 (108t) |
| 0.62 | 1184.18 (110t) | 1347.7 (109t) | 1148.58 (107t) |
| 0.66 | 591.18 (102t) | 754.7 (101t) | 713.06 (100t) |

**max daily trades x consecutive-loss limit**

| max_trades \ max_consec_losses | 1 | 2 | 3 |
|---|---|---|---|
| 1 | 370.94 (63t) | 370.94 (63t) | 370.94 (63t) |
| 2 | 1918.47 (86t) | 1789.37 (111t) | 1789.37 (111t) |
| 3 | 2126.08 (94t) | 1769.35 (132t) | 1984.28 (140t) |
| 4 | 2126.38 (95t) | 1651.17 (135t) | 1673.68 (148t) |


## 5. Half-split with the fixed default parameters

| scenario | total_trades | win_rate_pct | scratch_pct | win_rate_ex_scratch_pct | net_pnl_usd | profit_factor | max_drawdown_usd | expectancy_r | sharpe_daily_ann | profitable_months |
|---|---|---|---|---|---|---|---|---|---|---|
| first half (<2026-09-11) | 59 | 49.15 | 28.8 | 28.57 | 455.35 | 1.22 | 703.63 | 0.134 | 1.4 | 3/3 |
| second half (>=2026-09-11) | 52 | 55.77 | 30.8 | 36.11 | 1334.02 | 1.96 | 289.94 | 0.341 | 3.97 | 1/2 |

Parameters were chosen looking at the whole sample, so this is a stability check, not out-of-sample proof.

## 6. Walk-forward (optimise on train window, trade next window blind)

| train | test | chosen (atr_mult, R:R, min_meta) | train score | test trades | test net $ | fixed-default test net $ |
|---|---|---|---|---|---|---|
| 2026-07-27..2026-09-08 | 2026-09-08..2026-09-22 | (1.5, 2.0, 0.58) | 512.0 | 15 | -236.34 | -272.34 |
| 2026-08-10..2026-09-22 | 2026-09-22..2026-10-06 | (1.2, 3.0, 0.66) | 361.8 | 17 | 92.42 | 332.68 |
| 2026-08-24..2026-10-06 | 2026-10-06..2026-10-20 | (1.5, 2.0, 0.66) | 730.5 | 16 | 5.16 | 582.16 |
| 2026-09-08..2026-10-20 | 2026-10-20..2026-10-28 | (1.5, 3.0, 0.5) | 506.4 | 9 | 394.34 | 398.34 |

| scenario | total_trades | win_rate_pct | scratch_pct | win_rate_ex_scratch_pct | net_pnl_usd | profit_factor | max_drawdown_usd | expectancy_r | sharpe_daily_ann | profitable_months |
|---|---|---|---|---|---|---|---|---|---|---|
| walk-forward OOS (re-optimised each fold) | 57 | 49.12 | 28.1 | 29.27 | 255.58 | 1.13 | 737.97 | 0.038 | 0.89 | 1/2 |
| fixed default on the same test windows | 58 | 53.45 | 31.0 | 32.5 | 1040.84 | 1.62 | 561.79 | 0.235 | 2.94 | 1/2 |

Only a few short test windows exist in a 3-month sample; indicative, not conclusive.

## 7. Random-entry null (100 seeds, same stops/targets/BE/decay/risk limits, random direction)

| strategy net $ | strategy trades | random mean net $ | random p05 | random p95 | random mean trades | % random runs profitable | strategy percentile vs random |
|---|---|---|---|---|---|---|---|
| 1789.37 | 111 | -250.6 | -1431.3 | 1142.5 | 80.2 | 35.0 | 98.0 |

A useful signal should sit well above the random p95. Identical exits mean any gap is due to entry selection.

## 8. Bootstrap of the default trade list (5,000 resamples)

| pnl_p05 | pnl_p50 | pnl_p95 | prob_net_loss_pct | maxdd_p50 | maxdd_p95 |
|---|---|---|---|---|---|
| -78.95 | 1747.23 | 3739.94 | 5.9 | 671.13 | 1296.89 |

The single-path max drawdown understates likely drawdown; use `maxdd_p95` for sizing/capital.

## 9. Market-context filters (event calendar, opening gap, overnight range)

| scenario | total_trades | win_rate_pct | scratch_pct | win_rate_ex_scratch_pct | net_pnl_usd | profit_factor | max_drawdown_usd | expectancy_r | sharpe_daily_ann | profitable_months |
|---|---|---|---|---|---|---|---|---|---|---|
| default (no context filters) | 111 | 52.25 | 29.7 | 32.05 | 1789.37 | 1.52 | 703.63 | 0.231 | 2.72 | 4/4 |
| event windows + flatten before event | 111 | 52.25 | 29.7 | 32.05 | 1789.37 | 1.52 | 703.63 | 0.231 | 2.72 | 4/4 |
|   + skip all tier-1 event days | 97 | 50.52 | 32.0 | 27.27 | 581.87 | 1.19 | 628.57 | 0.097 | 1.09 | 2/4 |
| gap filter, gap >= 10% of prior-day range | 97 | 55.67 | 36.1 | 30.65 | 1265.44 | 1.45 | 778.15 | 0.178 | 2.08 | 3/4 |
| gap filter, gap >= 25% of prior-day range | 97 | 56.7 | 35.1 | 33.33 | 1782.23 | 1.65 | 574.37 | 0.25 | 2.86 | 4/4 |
| gap filter, gap >= 40% of prior-day range | 97 | 56.7 | 35.1 | 33.33 | 1782.23 | 1.65 | 574.37 | 0.25 | 2.86 | 4/4 |
| gap filter, gap >= 60% of prior-day range | 99 | 55.56 | 33.3 | 33.33 | 1797.62 | 1.62 | 656.61 | 0.255 | 2.83 | 4/4 |

**Default strategy on tier-1 event days vs other days**

| group | sessions | trades | net $ | avg R |
|---|---|---|---|---|
| tier-1 event days | 8 | 14 | 1207.5 | 1.159 |
| all other days | 58 | 97 | 581.87 | 0.097 |

**Sample coverage.** 8 tier-1 event days fall inside this 66-session sample. Overnight range is available for 0 sessions: the bundled CSV starts at 09:30 ET, so the overnight guard cannot be evaluated here. Download data with `--include-eth` and re-run.

**Data caveat.** The CSV is an unadjusted IBKR continuous contract. The largest gaps cluster around the September roll (e.g. 2026-09-10/11/14), so some gaps include the calendar spread between contracts and are not real overnight moves. Back-adjust or use per-contract data before trusting gap statistics.

With this few event days the event filter cannot be judged statistically; its value is risk control (not holding through FOMC/CPI/NFP), not a measured edge.
