# Scalp signal lab

66 sessions, 2-minute MNQ bars. Entry = next bar open, exit = close after the hold, window 09:45-15:25 ET. Costs per round trip: MNQ 1.12 pts ($2.24), NQ 0.71 pts ($14.20).

## Multiple-testing check

170 variants tested. Positive net edge with t > 2: **1** (about 4 expected by chance alone). Variants with t > 3.6 AND positive in both halves: **0**.

## Best 12 variants by net t-stat (MNQ costs)

| signal | mode | hold_min | n | gross_pts | net_pts_MNQ | net_pts_NQ | t_net | win_pct | net_1st_half | net_2nd_half |
|---|---|---|---|---|---|---|---|---|---|---|
| RSI(2) >= 95 | follow | 12 | 730 | 4.17 | 3.05 | 3.46 | 2.20 | 50.27 | 5.49 | 0.88 |
| close-EMA9 >= 1.75 ATR | follow | 12 | 156 | 6.50 | 5.38 | 5.79 | 1.46 | 45.51 | 11.41 | 1.92 |
| volume spike >= 2x (bar colour) | follow | 12 | 144 | 5.15 | 4.03 | 4.44 | 1.34 | 51.39 | 11.03 | 0.07 |
| 3-bar return >= 1.5 ATR | follow | 12 | 728 | 2.84 | 1.72 | 2.13 | 1.18 | 49.04 | 2.82 | 0.66 |
| RSI(2) >= 95 | follow | 8 | 730 | 2.40 | 1.28 | 1.69 | 1.13 | 49.59 | 3.60 | -0.78 |
| RSI(2) >= 95 | follow | 6 | 730 | 2.15 | 1.03 | 1.44 | 1.09 | 49.86 | 2.53 | -0.30 |
| 3-bar return >= 2.0 ATR | follow | 12 | 307 | 3.48 | 2.36 | 2.77 | 1.02 | 47.23 | 6.71 | -1.05 |
| vwap_z >= 2.5 | follow | 4 | 90 | 3.97 | 2.85 | 3.26 | 0.95 | 56.67 | -4.04 | 9.16 |
| 3-bar return >= 3.0 ATR | follow | 12 | 37 | 8.98 | 7.86 | 8.27 | 0.91 | 45.95 | 7.37 | 8.06 |
| 3-bar return >= 1.5 ATR | follow | 8 | 728 | 2.10 | 0.98 | 1.39 | 0.77 | 48.35 | 1.54 | 0.44 |
| close-EMA9 >= 1.75 ATR | follow | 4 | 156 | 2.80 | 1.68 | 2.09 | 0.75 | 47.44 | 5.43 | -0.47 |
| IBS extreme (>=0.9 / <=0.1), range >= ATR | fade | 8 | 797 | 1.93 | 0.81 | 1.22 | 0.70 | 48.81 | 0.87 | 0.74 |

## Candidates passing the strict bar

_None._

## Short-horizon return autocorrelation

| lag (bars) | autocorrelation of 2-min returns |
|---|---|
| 1.00 | 0.01 |
| 2.00 | -0.02 |
| 3.00 | 0.01 |
| 4.00 | -0.00 |
| 5.00 | 0.04 |

A clearly negative lag-1 value means bid-ask bounce / mean reversion at this scale; clearly positive means momentum.

## Average 2-minute move by half hour (pts)

| slot | mean 2-min move (pts) | t-stat of mean |
|---|---|---|
| 09:30 | 0.77 | 0.36 |
| 10:00 | -0.09 | -0.12 |
| 10:30 | 1.00 | 1.67 |
| 11:00 | -0.27 | -0.51 |
| 11:30 | 0.38 | 0.79 |
| 12:00 | 0.00 | 0.00 |
| 12:30 | -0.12 | -0.29 |
| 13:00 | -0.58 | -1.43 |
| 13:30 | 0.47 | 1.38 |
| 14:00 | -0.18 | -0.48 |
| 14:30 | 0.11 | 0.30 |
| 15:00 | 0.42 | 1.09 |
| 15:30 | -0.94 | -2.11 |
