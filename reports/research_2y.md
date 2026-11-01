# Research report

Data: `data\mnq_2m_2y.csv` | 517 sessions 2024-10-29 .. 2026-10-30 | symbol MNQ | 1 contract

## 1. Headline under different realism assumptions

| scenario | total_trades | win_rate_pct | scratch_pct | win_rate_ex_scratch_pct | net_pnl_usd | profit_factor | max_drawdown_usd | expectancy_r | sharpe_daily_ann | profitable_months |
|---|---|---|---|---|---|---|---|---|---|---|
| A. legacy baseline (fill at signal close, all CSV bars) | 934 | 47.75 | 31.0 | 24.22 | 181.34 | 1.01 | 2485.6 | -0.006 | 0.04 | 11/25 |
| B. + RTH-only data (VWAP/PDH/PDL exclude after-hours) | 921 | 48.21 | 31.6 | 24.29 | 965.46 | 1.03 | 1872.78 | 0.002 | 0.23 | 15/25 |
| C. next-bar marketable-limit fills (all CSV bars) | 932 | 48.07 | 30.4 | 25.42 | 1851.32 | 1.06 | 2039.06 | 0.027 | 0.41 | 14/25 |
| D. DEFAULT: next-bar fills + gap-aware stops + RTH data | 916 | 46.62 | 29.4 | 24.57 | 1538.16 | 1.05 | 1869.56 | 0.007 | 0.36 | 13/25 |

A is what the original README reports. D is the number to plan around.

## 2. Ablation (default realistic backtest, one change at a time)

| scenario | total_trades | win_rate_pct | scratch_pct | win_rate_ex_scratch_pct | net_pnl_usd | profit_factor | max_drawdown_usd | expectancy_r | sharpe_daily_ann | profitable_months |
|---|---|---|---|---|---|---|---|---|---|---|
| full default | 916 | 46.62 | 29.4 | 24.57 | 1538.16 | 1.05 | 1869.56 | 0.007 | 0.36 | 13/25 |
| no confidence gate | 921 | 46.8 | 29.4 | 24.77 | 1931.96 | 1.07 | 1802.3 | 0.013 | 0.45 | 13/25 |
| no VWAP z-band | 946 | 45.88 | 29.1 | 23.99 | 524.96 | 1.02 | 1921.46 | -0.005 | 0.12 | 13/25 |
| no PDH/PDL guard | 919 | 46.79 | 29.3 | 24.92 | 2072.44 | 1.07 | 1946.7 | 0.016 | 0.49 | 12/25 |
| no gate, z-band or PDH/PDL | 951 | 46.37 | 29.1 | 24.63 | 1264.26 | 1.04 | 1851.82 | 0.011 | 0.29 | 14/25 |
| entry: pullback only | 893 | 48.04 | 30.1 | 25.8 | 3499.68 | 1.13 | 1384.08 | 0.044 | 0.86 | 15/25 |
| entry: crossover only | 115 | 41.74 | 21.7 | 25.56 | 785.9 | 1.22 | 612.1 | 0.045 | 0.51 | 12/25 |
| entry: pullback+crossover | 899 | 47.16 | 29.7 | 25.0 | 2290.24 | 1.08 | 1419.32 | 0.022 | 0.55 | 15/25 |
| no break-even | 904 | 22.79 | 0.0 | 22.79 | 1933.04 | 1.05 | 2563.76 | 0.012 | 0.4 | 12/25 |
| no time-decay stop | 911 | 48.85 | 30.7 | 26.31 | 1864.36 | 1.06 | 1408.9 | 0.018 | 0.43 | 14/25 |
| no BE and no decay | 884 | 27.15 | 0.0 | 27.15 | 3165.34 | 1.08 | 2124.14 | 0.037 | 0.62 | 13/25 |
| R:R 2.0 | 939 | 46.01 | 21.4 | 31.44 | -421.86 | 0.99 | 2350.74 | -0.02 | -0.12 | 13/25 |
| entry window to 15:00 | 1536 | 46.88 | 30.5 | 24.16 | 153.86 | 1.0 | 3045.96 | -0.038 | 0.03 | 12/25 |

If removing a component does not hurt, it has not earned its complexity.

## 3. Cost / slippage stress

| scenario | total_trades | win_rate_pct | scratch_pct | win_rate_ex_scratch_pct | net_pnl_usd | profit_factor | max_drawdown_usd | expectancy_r | sharpe_daily_ann | profitable_months |
|---|---|---|---|---|---|---|---|---|---|---|
| default (1 tick stop slip) | 916 | 46.62 | 29.4 | 24.57 | 1538.16 | 1.05 | 1869.56 | 0.007 | 0.36 | 13/25 |
| stop slip 2 ticks | 916 | 17.36 | 29.4 | 24.57 | 1159.66 | 1.04 | 2057.04 | 0.0 | 0.27 | 13/25 |
| stop slip 3 ticks | 916 | 17.36 | 29.4 | 24.57 | 781.16 | 1.03 | 2245.04 | -0.007 | 0.18 | 13/25 |
| entry +1 tick worse | 916 | 46.29 | 28.9 | 24.58 | 1408.16 | 1.05 | 2032.56 | 0.003 | 0.33 | 13/25 |
| entry +2 ticks worse | 916 | 46.18 | 28.9 | 24.42 | 838.16 | 1.03 | 2176.56 | -0.007 | 0.2 | 13/25 |
| commission x2 | 916 | 17.36 | 29.4 | 24.57 | 402.32 | 1.01 | 2422.08 | -0.014 | 0.1 | 12/25 |
| worst case: stop 3t, entry +2t, comm x2 | 916 | 17.36 | 28.9 | 24.42 | -1054.68 | 0.97 | 3355.84 | -0.044 | -0.25 | 12/25 |

## 4. Parameter sensitivity (net PnL USD; a robust edge forms a plateau, not a single peak)

**ATR stop multiplier x reward:risk**

| atr_mult \ R:R | 1.5 | 2.0 | 3.0 | 4.0 |
|---|---|---|---|---|
| 0.8 | 10.1 (960t) | -735.2 (955t) | -256.78 (947t) | 3141.4 (940t) |
| 1.0 | -983.96 (954t) | -33.02 (948t) | 1561.34 (934t) | 3170.16 (916t) |
| 1.2 | -841.56 (944t) | -421.86 (939t) | 1538.16 (916t) | 2226.3 (905t) |
| 1.5 | -2067.68 (932t) | -1754.74 (926t) | 695.0 (900t) | 2437.12 (887t) |
| 2.0 | -593.54 (921t) | 604.8 (905t) | 3519.08 (883t) | 3775.16 (866t) |

**confidence-gate threshold x min body ratio**

| min_meta \ min_body | 0.25 | 0.35 | 0.45 |
|---|---|---|---|
| 0.0 | 1336.76 (926t) | 1931.96 (921t) | 2558.06 (906t) |
| 0.5 | 1336.76 (926t) | 1931.96 (921t) | 2558.06 (906t) |
| 0.54 | 1175.5 (925t) | 1692.2 (920t) | 2318.3 (905t) |
| 0.58 | 1124.2 (920t) | 1538.16 (916t) | 2278.24 (899t) |
| 0.62 | 400.26 (901t) | 825.48 (898t) | 1788.08 (883t) |
| 0.66 | -892.0 (850t) | -658.28 (847t) | 315.82 (832t) |

**max daily trades x consecutive-loss limit**

| max_trades \ max_consec_losses | 1 | 2 | 3 |
|---|---|---|---|
| 1 | -454.22 (503t) | -454.22 (503t) | -454.22 (503t) |
| 2 | 757.7 (670t) | 1538.16 (916t) | 1538.16 (916t) |
| 3 | 1695.62 (712t) | 1090.56 (1081t) | 51.36 (1186t) |
| 4 | 1830.44 (719t) | 2106.26 (1126t) | 896.3 (1280t) |


## 5. Half-split with the fixed default parameters

| scenario | total_trades | win_rate_pct | scratch_pct | win_rate_ex_scratch_pct | net_pnl_usd | profit_factor | max_drawdown_usd | expectancy_r | sharpe_daily_ann | profitable_months |
|---|---|---|---|---|---|---|---|---|---|---|
| first half (<2025-10-30) | 461 | 45.34 | 29.5 | 22.77 | -672.64 | 0.95 | 1360.2 | -0.03 | -0.37 | 6/13 |
| second half (>=2025-10-30) | 455 | 47.91 | 29.2 | 26.4 | 2210.8 | 1.14 | 1268.08 | 0.046 | 0.94 | 8/13 |

Parameters were chosen looking at the whole sample, so this is a stability check, not out-of-sample proof.

## 6. Walk-forward (optimise on train window, trade next window blind)

| train | test | chosen (atr_mult, R:R, min_meta) | train score | test trades | test net $ | fixed-default test net $ |
|---|---|---|---|---|---|---|
| 2024-10-29..2025-04-21 | 2025-04-21..2025-06-02 | (1.0, 3.0, 0.5) | -208.8 | 55 | -202.7 | -96.96 |
| 2024-12-10..2025-06-02 | 2025-06-02..2025-07-14 | (1.0, 3.0, 0.5) | 281.6 | 51 | -108.24 | 176.0 |
| 2025-01-24..2025-07-14 | 2025-07-14..2025-08-25 | (1.2, 3.0, 0.5) | -58.5 | 58 | -8.92 | -9.18 |
| 2025-03-07..2025-08-25 | 2025-08-25..2025-10-06 | (1.2, 3.0, 0.5) | 811.6 | 57 | -754.68 | -740.18 |
| 2025-04-21..2025-10-06 | 2025-10-06..2025-11-17 | (1.2, 2.0, 0.66) | -887.9 | 50 | -180.5 | 474.3 |
| 2025-06-02..2025-11-17 | 2025-11-17..2025-12-30 | (1.2, 2.0, 0.5) | 34.4 | 53 | -234.72 | -222.48 |
| 2025-07-14..2025-12-30 | 2025-12-30..2026-02-11 | (1.2, 2.0, 0.5) | -247.6 | 54 | 139.04 | 214.02 |
| 2025-08-25..2026-02-11 | 2026-02-11..2026-03-25 | (1.0, 3.0, 0.5) | -230.7 | 57 | -425.68 | -999.18 |
| 2025-10-06..2026-03-25 | 2026-03-25..2026-05-07 | (1.0, 3.0, 0.5) | 83.5 | 54 | 321.54 | 275.28 |
| 2025-11-17..2026-05-07 | 2026-05-07..2026-06-18 | (1.0, 3.0, 0.5) | -187.2 | 50 | 1008.5 | 1294.24 |
| 2025-12-30..2026-06-18 | 2026-06-18..2026-07-30 | (1.0, 3.0, 0.5) | 924.2 | 55 | -90.7 | -148.72 |
| 2026-02-11..2026-07-30 | 2026-07-30..2026-09-10 | (1.0, 3.0, 0.5) | 379.0 | 58 | 153.08 | 169.56 |
| 2026-03-25..2026-09-10 | 2026-09-10..2026-10-22 | (1.2, 3.0, 0.5) | 1321.4 | 48 | 757.98 | 757.98 |
| 2026-05-07..2026-10-22 | 2026-10-22..2026-10-31 | (1.2, 3.0, 0.5) | 1804.1 | 12 | 479.62 | 479.62 |

| scenario | total_trades | win_rate_pct | scratch_pct | win_rate_ex_scratch_pct | net_pnl_usd | profit_factor | max_drawdown_usd | expectancy_r | sharpe_daily_ann | profitable_months |
|---|---|---|---|---|---|---|---|---|---|---|
| walk-forward OOS (re-optimised each fold) | 712 | 46.07 | 26.8 | 26.3 | 853.62 | 1.04 | 2601.44 | 0.003 | 0.29 | 9/19 |
| fixed default on the same test windows | 705 | 46.24 | 28.2 | 25.1 | 1624.3 | 1.07 | 1869.56 | 0.016 | 0.5 | 10/19 |

Only a few short test windows exist in a 3-month sample; indicative, not conclusive.

## 7. Random-entry null (100 seeds, same stops/targets/BE/decay/risk limits, random direction)

| strategy net $ | strategy trades | random mean net $ | random p05 | random p95 | random mean trades | % random runs profitable | strategy percentile vs random |
|---|---|---|---|---|---|---|---|
| 1538.16 | 916 | -2653.9 | -5828.9 | 730.5 | 622.2 | 17.0 | 97.0 |

A useful signal should sit well above the random p95. Identical exits mean any gap is due to entry selection.

## 8. Bootstrap of the default trade list (5,000 resamples)

| pnl_p05 | pnl_p50 | pnl_p95 | prob_net_loss_pct | maxdd_p50 | maxdd_p95 |
|---|---|---|---|---|---|
| -3169.37 | 1535.16 | 6392.43 | 29.9 | 2658.52 | 5133.85 |

The single-path max drawdown understates likely drawdown; use `maxdd_p95` for sizing/capital.

## 9. Market-context filters (event calendar, opening gap, overnight range)

| scenario | total_trades | win_rate_pct | scratch_pct | win_rate_ex_scratch_pct | net_pnl_usd | profit_factor | max_drawdown_usd | expectancy_r | sharpe_daily_ann | profitable_months |
|---|---|---|---|---|---|---|---|---|---|---|
| default (no context filters) | 916 | 46.62 | 29.4 | 24.57 | 1538.16 | 1.05 | 1869.56 | 0.007 | 0.36 | 13/25 |
| event windows + flatten before event | 916 | 46.62 | 29.4 | 24.57 | 1538.16 | 1.05 | 1869.56 | 0.007 | 0.36 | 13/25 |
|   + skip all tier-1 event days | 899 | 46.38 | 29.6 | 24.01 | 529.24 | 1.02 | 1869.56 | -0.008 | 0.13 | 12/25 |
| gap filter, gap >= 10% of prior-day range | 798 | 47.99 | 30.8 | 25.0 | 2471.48 | 1.1 | 1742.14 | 0.028 | 0.64 | 12/25 |
| gap filter, gap >= 25% of prior-day range | 817 | 47.98 | 30.6 | 25.22 | 2854.92 | 1.11 | 1814.82 | 0.034 | 0.73 | 14/25 |
| gap filter, gap >= 40% of prior-day range | 829 | 47.53 | 30.5 | 24.65 | 2307.54 | 1.09 | 2122.26 | 0.021 | 0.58 | 14/25 |
| gap filter, gap >= 60% of prior-day range | 850 | 46.47 | 29.8 | 23.95 | 1026.0 | 1.04 | 2716.02 | 0.001 | 0.26 | 14/25 |

**Default strategy on tier-1 event days vs other days**

| group | sessions | trades | net $ | avg R |
|---|---|---|---|---|
| tier-1 event days | 9 | 17 | 1008.92 | 0.836 |
| all other days | 508 | 899 | 529.24 | -0.008 |

> **Calendar coverage warning:** `data/economic_events.csv` lists tier-1 events in only 4 of 25 months of this sample. Event results are meaningless until the file covers the whole period.

**Sample coverage.** 9 tier-1 event days fall inside this 517-session sample. Overnight range is available for 510 sessions: the bundled CSV starts at 09:30 ET, so the overnight guard cannot be evaluated here. Download data with `--include-eth` and re-run.

**Data caveat.** The CSV is an unadjusted IBKR continuous contract. The largest gaps cluster around the September roll (e.g. 2026-09-10/11/14), so some gaps include the calendar spread between contracts and are not real overnight moves. Back-adjust or use per-contract data before trusting gap statistics.

With this few event days the event filter cannot be judged statistically; its value is risk control (not holding through FOMC/CPI/NFP), not a measured edge.

## 10. Entry-quality options (next-bar fill model, one change at a time)

| variant | trades | net $ | PF | max DD $ | avg R | fast fails (<=3 bars) | fast-fail net $ | 1st half $ | 2nd half $ |
|---|---|---|---|---|---|---|---|---|---|
| baseline (marketable limit, ATR stop) | 916 | 1538.16 | 1.05 | 1869.56 | 0.007 | 372 | -17456.0 | -672.64 | 2210.8 |
| retrace limit 0.10 ATR | 893 | 3630.18 | 1.13 | 1988.82 | 0.05 | 365 | -15875.0 | -35.98 | 3666.16 |
| retrace limit 0.25 ATR | 831 | -515.44 | 0.98 | 3586.98 | -0.02 | 320 | -15133.0 | -1308.36 | 792.92 |
| retrace limit 0.50 ATR | 724 | -2017.26 | 0.91 | 2548.04 | -0.049 | 241 | -11936.0 | -1347.84 | -669.42 |
| retrace limit 0.75 ATR | 607 | 164.82 | 1.01 | 2690.34 | -0.023 | 194 | -9590.0 | -1906.36 | 2071.18 |
| confirmation bar | 701 | -2308.74 | 0.89 | 3692.24 | -0.054 | 262 | -12558.0 | -1915.3 | -393.44 |
| confirmation bar, move >= 0.1 ATR | 629 | -3535.46 | 0.83 | 4314.82 | -0.089 | 236 | -12145.0 | -1815.24 | -1720.22 |
| structural stop, 2-bar swing | 907 | 1455.32 | 1.05 | 2199.52 | 0.008 | 366 | -16768.0 | -954.22 | 2409.54 |
| structural stop, 3-bar swing | 897 | 1578.72 | 1.05 | 2209.6 | 0.014 | 325 | -15915.0 | -870.54 | 2449.26 |
| structural stop, 5-bar swing | 891 | 2205.66 | 1.07 | 1738.9 | 0.032 | 295 | -15590.0 | 700.42 | 1505.24 |
| structural stop, 8-bar swing | 884 | 3129.34 | 1.1 | 1783.16 | 0.047 | 274 | -14766.0 | 1416.88 | 1712.46 |
| no-chase: close within 0.3 ATR of EMA9 | 58 | 524.08 | 1.34 | 275.94 | 0.103 | 20 | -878.0 | 298.02 | 226.06 |
| no-chase: within 0.6 ATR | 377 | 90.02 | 1.01 | 1423.54 | 0.027 | 142 | -6666.0 | -423.38 | 513.4 |
| no-chase: within 1.0 ATR | 808 | 2356.08 | 1.1 | 1788.5 | 0.041 | 305 | -14826.0 | 601.72 | 1754.36 |
| combo: structural 3 + confirmation | 689 | -1761.36 | 0.92 | 3757.62 | -0.021 | 230 | -11326.0 | -914.9 | -846.46 |
| combo: structural 3 + retrace 0.25 | 817 | -699.08 | 0.97 | 3418.7 | -0.021 | 278 | -14066.0 | -1278.44 | 579.36 |
| combo: confirmation + within 0.6 ATR | 200 | 1584.0 | 1.28 | 1383.96 | 0.155 | 64 | -3209.0 | 1092.2 | 491.8 |

A variant is only interesting if it helps in BOTH halves and its neighbours (other retrace sizes, swing lengths) behave similarly. Each row is a hypothesis tested on the same 111-trade sample, so some will look good by chance.

## 11. Macro-event day concentration

**A. The tier-1 event days**

| date | event | trades | net $ | day range pts | range rank (of 517) | trend efficiency |
|---|---|---|---|---|---|---|
| 2026-07-29 | FOMC rate decision | 2 | 477.0 | 782.0 | 16 | 0.74 |
| 2026-08-07 | Employment Situation (NFP) | 2 | -82.0 | 296.0 | 256 | 0.4 |
| 2026-08-12 | CPI | 2 | -163.0 | 183.0 | 436 | 0.76 |
| 2026-09-04 | Employment Situation (NFP) | 2 | 193.0 | 224.0 | 378 | 0.09 |
| 2026-09-11 | CPI | 2 | -82.0 | 166.0 | 462 | 0.16 |
| 2026-09-16 | FOMC rate decision | 2 | 110.0 | 500.0 | 76 | 0.27 |
| 2026-10-02 | Employment Situation (NFP) | 1 | 235.0 | 295.0 | 260 | 0.27 |
| 2026-10-14 | CPI | 2 | 479.0 | 582.0 | 45 | 0.63 |
| 2026-10-28 | FOMC rate decision | 2 | -156.0 | 239.0 | 352 | 0.26 |

**B. Profit concentration across all days** (total net $1538; 204 of 517 days positive, 14 flat)

| top days | their net $ | % of total net | net WITHOUT them $ |
|---|---|---|---|
| 1 | 479.0 | 31.0 | 1060.0 |
| 3 | 1434.0 | 93.0 | 105.0 |
| 5 | 2383.0 | 155.0 | -845.0 |
| 8 | 3441.0 | 224.0 | -1902.0 |

Of the 8 best days, 2 are tier-1 event days.

**C. Are event days just wider, more trending days?**

| group | days | mean range pts | mean range % | mean trend efficiency | net $ / day | trades / day |
|---|---|---|---|---|---|---|
| tier-1 event days | 9 | 363.0 | 1.22 | 0.4 | 112.1 | 1.89 |
| other days | 508 | 344.0 | 1.36 | 0.48 | 1.0 | 1.77 |

**D. Rank correlation with daily net PnL:** day range +0.14, trend efficiency +0.11, is-event-day +0.03

**E. Placebo tests: could any 8 days (or any 8 volatile days) have produced the event days' PnL?**

| placebo: pick 9 days at random from | event days' net $ | placebo median $ | placebo p95 $ | event days beat % of placebos |
|---|---|---|---|---|
| all 517 days | 1009.0 | 5.0 | 701.0 | 99.0 |
| the 27 widest-range days | 1009.0 | 506.0 | 1263.0 | 86.5 |
| the 24 most one-directional non-event days | 1009.0 | 135.0 | 540.0 | 100.0 |

**F. By event type**

| event type | days | trades | net $ |
|---|---|---|---|
| CPI | 3 | 6 | 233.0 |
| FOMC | 3 | 6 | 430.0 |
| NFP | 3 | 5 | 346.0 |

**G. Can anything known before the entry window predict the profitable days?**

| feature known before 09:45 | rank corr with day net | days | low third net $ | mid third net $ | high third net $ |
|---|---|---|---|---|---|
| prior-day range (PDH-PDL) | -0.05 | 516 | 316.0 | 5.0 | 1299.0 |
| opening 15-min range | -0.0 | 517 | -1577.0 | -2718.0 | 5833.0 |
| abs(opening gap) | -0.04 | 516 | 1114.0 | 221.0 | 284.0 |
| ATR at 09:45 | -0.03 | 517 | -944.0 | 1608.0 | 875.0 |

Four features tested on 66 days: a correlation near 0.2 is within chance here, so only a strong, monotonic pattern (low < mid < high) would be worth following up.

8 days and 14 trades are a very small sample. Read this as a map of where the risk of being wrong is, not as a verdict.

## 12. Deflated Sharpe ratio and minimum backtest length

Sharpe ratios on **daily PnL** over 517 sessions (2.05 years). A Sharpe found after trying many variants is inflated by selection; these statistics measure by how much.

**A. The default configuration**

| annualised Sharpe | daily skew | daily kurtosis | PSR vs 0 (P true Sharpe > 0) | days needed for 95% confidence (MinTRL) | days available |
|---|---|---|---|---|---|
| 0.36 | 1.02 | 3.6 | 0.701 | 5038 | 517 |

**B. How many variants have been tried?** This report evaluated **90 distinct full-sample configurations** (ablations, cost stress, sensitivity grids, context filters, entry options). Their daily Sharpe ratios have a cross-trial standard deviation of 0.024 per day (0.38 annualised); the best of them reaches an annualised Sharpe of 0.86.

**C. Deflated Sharpe ratio by number of trials** (above 0.95 = statistically convincing)

| assumed independent trials N | expected best Sharpe by luck (annualised) | DSR of default (P its Sharpe is real) | DSR of best-found variant |
|---|---|---|---|
| 1 | 0.0 | 0.701 | 0.898 |
| 5 | 0.45 | 0.449 | 0.726 |
| 10 | 0.6 | 0.368 | 0.651 |
| 25 | 0.76 | 0.284 | 0.561 |
| 50 | 0.86 | 0.235 | 0.499 |
| 90 | 0.95 | 0.2 | 0.451 |
| 250 | 1.08 | 0.151 | 0.376 |
| 500 | 1.16 | 0.125 | 0.331 |
| 1000 | 1.24 | 0.104 | 0.291 |

**D. Minimum backtest length** (years of data before the best of N zero-edge trials is not expected to reach the target Sharpe by chance)

| target annualised Sharpe | N=1: years needed | N=10: years needed | N=50: years needed | N=90: years needed | N=500: years needed | max N this history supports |
|---|---|---|---|---|---|---|
| 0.36 | n/a (no selection) | 19.13 | 39.98 | 47.97 | 71.9 | 1 |
| 1.0 | n/a (no selection) | 2.48 | 5.18 | 6.22 | 9.32 | 7 |
| 1.5 | n/a (no selection) | 1.1 | 2.3 | 2.76 | 4.14 | 36 |
| 2.0 | n/a (no selection) | 0.62 | 1.3 | 1.55 | 2.33 | 272 |

**Reading this.** With 90 variants tried, luck alone is expected to produce an annualised Sharpe of about 0.95; the default's is 0.36, so its deflated Sharpe is 0.20 (not convincing). At this Sharpe the luck threshold is never beaten. The count N is a lower bound on the real number of decisions behind the defaults (the original author's v0-v4 tuning is not counted), and variants that differ slightly are correlated, which pulls the effective N down; treat the DSR as a guide, not a p-value.
