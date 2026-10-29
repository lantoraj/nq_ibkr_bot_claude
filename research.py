"""
Validation harness: does the strategy hold up beyond one in-sample path?

Sections (python research.py --sections all):
  baseline     headline run under legacy vs realistic fill assumptions
  ablation     remove one component at a time
  stress       slippage / commission stress
  sensitivity  neighbourhood grids around the chosen parameters (plateau or spike?)
  split        first half vs second half with fixed parameters
  walkforward  rolling train/test: optimise on train window, trade the next window blind
  random       random-entry null with identical exits/risk (is the signal better than chance?)
  bootstrap    resampled-trade distribution of PnL and drawdown

Writes reports/research_report.md and reports/trades_default.csv.
"""
from __future__ import annotations

import argparse
import copy
import itertools
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

from backtest import Backtester
from config import BotConfig
from metrics import bootstrap, compute_metrics
from strategy import RandomEntryStrategy

KEY_COLS = ["total_trades", "win_rate_pct", "scratch_pct", "win_rate_ex_scratch_pct", "net_pnl_usd", "profit_factor", "max_drawdown_usd",
            "expectancy_r", "sharpe_daily_ann", "profitable_months"]


def md_table(rows: List[Dict], cols: Optional[Sequence[str]] = None) -> str:
    if not rows:
        return "_no rows_\n"
    cols = list(cols or rows[0].keys())
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(out) + "\n"


class Lab:
    """Holds the raw data and a cache of the enriched frame so sweeps are cheap."""

    def __init__(self, csv: str, base: Optional[BotConfig] = None) -> None:
        self.raw = pd.read_csv(csv)
        self.base = base or BotConfig()
        self._enriched: Dict[tuple, pd.DataFrame] = {}

    def enriched(self, cfg: BotConfig) -> pd.DataFrame:
        s = cfg.strategy
        key = (cfg.backtest.rth_filter_data, cfg.strategy.bar_size, s.fast_ema_period, s.slow_ema_period,
               s.trend_ema_period, s.atr_period, s.rsi_period, s.kalman_q_pos, s.kalman_q_vel,
               s.kalman_r_meas, s.hurst_lag_q, s.hurst_window)
        if key not in self._enriched:
            self._enriched[key] = Backtester(cfg).enrich(self.raw)
        return self._enriched[key]

    def cfg(self, *mods: Callable[[BotConfig], None]) -> BotConfig:
        c = copy.deepcopy(self.base)
        for m in mods:
            m(c)
        return c

    def run(self, cfg: BotConfig, start: Optional[str] = None, end: Optional[str] = None,
            strategy=None) -> Dict:
        return Backtester(cfg, strategy=strategy).run(enriched=self.enriched(cfg), start=start, end=end)

    def dates(self) -> List:
        e = self.enriched(self.base)
        return sorted(set(pd.to_datetime(e["timestamp"], utc=True).dt.tz_convert(self.base.risk.timezone).dt.date))


def _row(name: str, m: Dict) -> Dict:
    r = {"scenario": name}
    r.update({k: m[k] for k in KEY_COLS})
    return r


# ------------------------------------------------------------------ sections
def sec_baseline(lab: Lab) -> str:
    def legacy(c): c.backtest.fill_model, c.backtest.model_gaps, c.backtest.rth_filter_data = "signal_close", False, False
    def legacy_rth(c): c.backtest.fill_model, c.backtest.model_gaps = "signal_close", False
    def next_bar(c): c.backtest.model_gaps, c.backtest.rth_filter_data = False, False
    rows = [
        _row("A. legacy baseline (fill at signal close, all CSV bars)", lab.run(lab.cfg(legacy))["metrics"]),
        _row("B. + RTH-only data (VWAP/PDH/PDL exclude after-hours)", lab.run(lab.cfg(legacy_rth))["metrics"]),
        _row("C. next-bar marketable-limit fills (all CSV bars)", lab.run(lab.cfg(next_bar))["metrics"]),
        _row("D. DEFAULT: next-bar fills + gap-aware stops + RTH data", lab.run(lab.cfg())["metrics"]),
    ]
    return "## 1. Headline under different realism assumptions\n\n" + md_table(rows) + \
        "\nA is what the original README reports. D is the number to plan around.\n"


def sec_ablation(lab: Lab) -> str:
    variants: Dict[str, List[Callable]] = {
        "full default": [],
        "no confidence gate": [lambda c: setattr(c.strategy, "use_quant_meta_filter", False)],
        "no VWAP z-band": [lambda c: setattr(c.strategy, "use_vwap_z_filter", False)],
        "no PDH/PDL guard": [lambda c: setattr(c.strategy, "use_pdh_pdl_guard", False)],
        "no gate, z-band or PDH/PDL": [lambda c: setattr(c.strategy, "use_quant_meta_filter", False),
                                       lambda c: setattr(c.strategy, "use_vwap_z_filter", False),
                                       lambda c: setattr(c.strategy, "use_pdh_pdl_guard", False)],
        "entry: pullback only": [lambda c: setattr(c.strategy, "entry_mode", "pullback")],
        "entry: crossover only": [lambda c: setattr(c.strategy, "entry_mode", "crossover")],
        "entry: pullback+crossover": [lambda c: setattr(c.strategy, "entry_mode", "both")],
        "no break-even": [lambda c: setattr(c.risk, "breakeven_at_1r", False)],
        "no time-decay stop": [lambda c: setattr(c.risk, "time_decay_bars", 0)],
        "no BE and no decay": [lambda c: setattr(c.risk, "breakeven_at_1r", False),
                               lambda c: setattr(c.risk, "time_decay_bars", 0)],
        "R:R 2.0": [lambda c: setattr(c.risk, "reward_risk_ratio", 2.0)],
        "entry window to 15:00": [lambda c: setattr(c.risk, "entry_end_time", "15:00"),
                                  lambda c: setattr(c.risk, "max_daily_trades", 4)],
    }
    rows = [_row(n, lab.run(lab.cfg(*mods))["metrics"]) for n, mods in variants.items()]
    return ("## 2. Ablation (default realistic backtest, one change at a time)\n\n" + md_table(rows) +
            "\nIf removing a component does not hurt, it has not earned its complexity.\n")


def sec_stress(lab: Lab) -> str:
    sc = {
        "default (1 tick stop slip)": [],
        "stop slip 2 ticks": [lambda c: setattr(c.costs, "stop_slippage_ticks", 2)],
        "stop slip 3 ticks": [lambda c: setattr(c.costs, "stop_slippage_ticks", 3)],
        "entry +1 tick worse": [lambda c: setattr(c.costs, "extra_entry_slippage_ticks", 1)],
        "entry +2 ticks worse": [lambda c: setattr(c.costs, "extra_entry_slippage_ticks", 2)],
        "commission x2": [lambda c: setattr(c.costs, "commission_per_side_usd", 1.24)],
        "worst case: stop 3t, entry +2t, comm x2": [
            lambda c: setattr(c.costs, "stop_slippage_ticks", 3),
            lambda c: setattr(c.costs, "extra_entry_slippage_ticks", 2),
            lambda c: setattr(c.costs, "commission_per_side_usd", 1.24)],
    }
    rows = [_row(n, lab.run(lab.cfg(*m))["metrics"]) for n, m in sc.items()]
    return "## 3. Cost / slippage stress\n\n" + md_table(rows)


def sec_sensitivity(lab: Lab) -> str:
    out = "## 4. Parameter sensitivity (net PnL USD; a robust edge forms a plateau, not a single peak)\n\n"

    def grid(title, rname, rvals, cname, cvals, setr, setc):
        rows = []
        for rv in rvals:
            row = {f"{rname} \\ {cname}": rv}
            for cv in cvals:
                m = lab.run(lab.cfg(lambda c: setr(c, rv), lambda c: setc(c, cv)))["metrics"]
                row[str(cv)] = f"{m['net_pnl_usd']} ({m['total_trades']}t)"
            rows.append(row)
        return f"**{title}**\n\n" + md_table(rows) + "\n"

    out += grid("ATR stop multiplier x reward:risk", "atr_mult", [0.8, 1.0, 1.2, 1.5, 2.0], "R:R", [1.5, 2.0, 3.0, 4.0],
                lambda c, v: setattr(c.risk, "atr_stop_multiplier", v), lambda c, v: setattr(c.risk, "reward_risk_ratio", v))
    out += grid("confidence-gate threshold x min body ratio", "min_meta", [0.0, 0.50, 0.54, 0.58, 0.62, 0.66], "min_body", [0.25, 0.35, 0.45],
                lambda c, v: setattr(c.strategy, "min_meta_probability", v), lambda c, v: setattr(c.strategy, "min_body_ratio", v))
    out += grid("max daily trades x consecutive-loss limit", "max_trades", [1, 2, 3, 4], "max_consec_losses", [1, 2, 3],
                lambda c, v: setattr(c.risk, "max_daily_trades", v), lambda c, v: setattr(c.risk, "max_consecutive_losses", v))
    return out


def sec_split(lab: Lab) -> str:
    d = lab.dates()
    mid = d[len(d) // 2]
    cfg = lab.cfg()
    first = lab.run(cfg, end=str(mid))["metrics"]
    second = lab.run(cfg, start=str(mid))["metrics"]
    rows = [_row(f"first half (<{mid})", first), _row(f"second half (>={mid})", second)]
    return ("## 5. Half-split with the fixed default parameters\n\n" + md_table(rows) +
            "\nParameters were chosen looking at the whole sample, so this is a stability check, not out-of-sample proof.\n")


def sec_walkforward(lab: Lab, train_days: int = 30, test_days: int = 10) -> str:
    dates = lab.dates()
    grid = list(itertools.product([1.0, 1.2, 1.5], [2.0, 3.0], [0.50, 0.58, 0.66]))

    def score(m: Dict) -> float:
        if m["total_trades"] < 12:
            return -1e9
        return m["net_pnl_usd"] - 0.5 * m["max_drawdown_usd"]

    def with_params(p):
        return lab.cfg(lambda c: setattr(c.risk, "atr_stop_multiplier", p[0]),
                       lambda c: setattr(c.risk, "reward_risk_ratio", p[1]),
                       lambda c: setattr(c.strategy, "min_meta_probability", p[2]))

    oos_trades, fixed_trades, fold_rows = [], [], []
    a = 0
    while a + train_days + 5 <= len(dates):
        tr_s, tr_e = dates[a], dates[a + train_days]
        te_s = dates[a + train_days]
        te_end_idx = a + train_days + test_days
        te_e = dates[te_end_idx] if te_end_idx < len(dates) else dates[-1] + pd.Timedelta(days=1)
        best, best_sc = None, -1e18
        for p in grid:
            sc = score(lab.run(with_params(p), start=str(tr_s), end=str(tr_e))["metrics"])
            if sc > best_sc:
                best, best_sc = p, sc
        res = lab.run(with_params(best), start=str(te_s), end=str(te_e))
        fix = lab.run(lab.cfg(), start=str(te_s), end=str(te_e))
        oos_trades += res["trades"]
        fixed_trades += fix["trades"]
        fold_rows.append({
            "train": f"{tr_s}..{tr_e}", "test": f"{te_s}..{te_e}",
            "chosen (atr_mult, R:R, min_meta)": best,
            "train score": round(best_sc, 1),
            "test trades": res["metrics"]["total_trades"], "test net $": res["metrics"]["net_pnl_usd"],
            "fixed-default test net $": fix["metrics"]["net_pnl_usd"],
        })
        a += test_days

    agg = compute_metrics(oos_trades, None)
    aggf = compute_metrics(fixed_trades, None)
    out = "## 6. Walk-forward (optimise on train window, trade next window blind)\n\n"
    out += md_table(fold_rows)
    out += "\n" + md_table([_row("walk-forward OOS (re-optimised each fold)", agg),
                            _row("fixed default on the same test windows", aggf)])
    out += "\nOnly a few short test windows exist in a 3-month sample; indicative, not conclusive.\n"
    return out


def sec_random(lab: Lab, n: int = 100) -> str:
    cfg = lab.cfg()
    real = lab.run(cfg)["metrics"]
    nets, exps, counts = [], [], []
    for seed in range(n):
        st = RandomEntryStrategy(cfg.strategy, cfg.risk, cfg.contract, entry_prob=0.02, seed=seed)
        m = lab.run(cfg, strategy=st)["metrics"]
        nets.append(m["net_pnl_usd"]); exps.append(m["expectancy_r"]); counts.append(m["total_trades"])
    nets = np.array(nets)
    pct = float((nets < real["net_pnl_usd"]).mean() * 100)
    rows = [{
        "strategy net $": real["net_pnl_usd"], "strategy trades": real["total_trades"],
        "random mean net $": round(float(nets.mean()), 1), "random p05": round(float(np.percentile(nets, 5)), 1),
        "random p95": round(float(np.percentile(nets, 95)), 1), "random mean trades": round(float(np.mean(counts)), 1),
        "% random runs profitable": round(float((nets > 0).mean() * 100), 1),
        "strategy percentile vs random": round(pct, 1),
    }]
    return (f"## 7. Random-entry null ({n} seeds, same stops/targets/BE/decay/risk limits, random direction)\n\n"
            + md_table(rows) +
            "\nA useful signal should sit well above the random p95. Identical exits mean any gap is due to entry selection.\n")


def sec_bootstrap(lab: Lab) -> str:
    res = lab.run(lab.cfg())
    pnls = [t.net_pnl_usd for t in res["trades"]]
    b = bootstrap(pnls)
    return ("## 8. Bootstrap of the default trade list (5,000 resamples)\n\n" + md_table([b]) +
            "\nThe single-path max drawdown understates likely drawdown; use `maxdd_p95` for sizing/capital.\n")


def sec_context(lab: Lab) -> str:
    from events import EventCalendar
    out = "## 9. Market-context filters (event calendar, opening gap, overnight range)\n\n"
    base_cfg = lab.cfg()
    cal = EventCalendar.from_csv(base_cfg.context.event_file, base_cfg.context, 120, base_cfg.risk.timezone)
    sample = set(lab.dates())
    t1 = [d for d in cal.days(tier=1) if d in sample]

    def ev(**kw):
        return [lambda c: setattr(c.context, "use_event_filter", True)] + [
            (lambda k, v: (lambda c: setattr(c.context, k, v)))(k, v) for k, v in kw.items()]

    def gap(v):
        return [lambda c: setattr(c.context, "use_gap_filter", True), lambda c: setattr(c.context, "gap_min_prior_range", v)]

    variants = {
        "default (no context filters)": [],
        "event windows + flatten before event": ev(),
        "  + skip all tier-1 event days": ev(skip_tier1_days=True),
        "gap filter, gap >= 10% of prior-day range": gap(0.10),
        "gap filter, gap >= 25% of prior-day range": gap(0.25),
        "gap filter, gap >= 40% of prior-day range": gap(0.40),
        "gap filter, gap >= 60% of prior-day range": gap(0.60),
    }
    rows = [_row(n, lab.run(lab.cfg(*m))["metrics"]) for n, m in variants.items()]
    out += md_table(rows)

    res = lab.run(lab.cfg())
    tdf = res["trades_df"]
    if not tdf.empty:
        d = pd.to_datetime(tdf["entry_time"], utc=True).dt.tz_convert(base_cfg.risk.timezone).dt.date
        on_ev = d.isin(set(t1))
        desc = []
        for name, m in (("tier-1 event days", on_ev), ("all other days", ~on_ev)):
            sub = tdf[m]
            desc.append({"group": name, "sessions": len(t1) if m is on_ev else len(sample) - len(t1), "trades": len(sub),
                         "net $": round(float(sub["net_pnl_usd"].sum()), 2),
                         "avg R": round(float(sub["r_multiple"].mean()), 3) if len(sub) else 0})
        out += "\n**Default strategy on tier-1 event days vs other days**\n\n" + md_table(desc)

    e = lab.enriched(base_cfg)
    valid_on = int(e.drop_duplicates(subset=["prev_close"])["on_high"].notna().sum())
    out += (f"\n**Sample coverage.** {len(t1)} tier-1 event days fall inside this {len(sample)}-session sample. "
            f"Overnight range is available for {valid_on} sessions: the bundled CSV starts at 09:30 ET, so the overnight guard "
            "cannot be evaluated here. Download data with `--include-eth` and re-run.\n"
            "\n**Data caveat.** The CSV is an unadjusted IBKR continuous contract. The largest gaps cluster around the September roll "
            "(e.g. 2026-09-10/11/14), so some gaps include the calendar spread between contracts and are not real overnight moves. "
            "Back-adjust or use per-contract data before trusting gap statistics.\n"
            "\nWith this few event days the event filter cannot be judged statistically; its value is risk control "
            "(not holding through FOMC/CPI/NFP), not a measured edge.\n")
    return out


SECTIONS = {
    "baseline": sec_baseline, "ablation": sec_ablation, "stress": sec_stress, "sensitivity": sec_sensitivity,
    "split": sec_split, "walkforward": sec_walkforward, "random": sec_random, "bootstrap": sec_bootstrap,
    "context": sec_context,
}


def main() -> None:
    ap = argparse.ArgumentParser(description="Strategy robustness research harness")
    ap.add_argument("--csv", default="data/mnq_2m_3months.csv")
    ap.add_argument("--sections", default="all", help="comma list or 'all'")
    ap.add_argument("--out", default="reports/research_report.md")
    args = ap.parse_args()

    lab = Lab(args.csv)
    names = list(SECTIONS) if args.sections == "all" else [s.strip() for s in args.sections.split(",")]
    d = lab.dates()
    parts = [f"# Research report\n\nData: `{args.csv}` | {len(d)} sessions {d[0]} .. {d[-1]} | "
             f"symbol {lab.base.contract.symbol} | 1 contract\n"]
    for n in names:
        t0 = time.time()
        txt = SECTIONS[n](lab)
        print(f"[{n}] done in {time.time() - t0:.1f}s")
        parts.append(txt)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(parts))
    res = lab.run(lab.cfg())
    if res["trades"]:
        res["trades_df"].to_csv(Path(args.out).parent / "trades_default.csv", index=False)
    print(f"Report written to {args.out}")


if __name__ == "__main__":
    main()
