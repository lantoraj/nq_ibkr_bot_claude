"""Synthetic trending NQ-like bars for smoke tests only (NOT for performance claims)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from indicators import round_to_tick


def generate_synthetic_nq_data(
    num_days: int = 5,
    seed: int = 42,
    start_price: float = 20250.0,
) -> pd.DataFrame:
    """
    Generate realistic 1-minute RTH (09:30 - 16:00 ET) NQ futures bars with
    intraday trend regimes, pullbacks, and volume profiles for offline verification.
    """
    rng = np.random.default_rng(seed)
    rows = []
    base_dates = pd.bdate_range("2026-10-19", periods=num_days)
    price = start_price

    for day_idx, bdate in enumerate(base_dates):
        day_timestamps = pd.date_range(
            f"{bdate.strftime('%Y-%m-%d')} 09:30:00",
            f"{bdate.strftime('%Y-%m-%d')} 15:59:00",
            freq="1min",
            tz="America/New_York",
        )
        # Alternate bullish and bearish intraday trend regimes with periodic 5-8 bar pullbacks
        regime_dir = 1.0 if day_idx % 2 == 0 else -1.0

        for m_idx, ts in enumerate(day_timestamps):
            # Create structured trend + periodic pullback waves every ~25 minutes
            cycle_pos = m_idx % 28
            if cycle_pos < 20:
                drift = regime_dir * 0.85
            elif cycle_pos < 25:
                # Controlled pullback toward fast/slow EMA
                drift = -regime_dir * 1.15
            else:
                # Strong resumption bar reclaiming Fast EMA
                drift = regime_dir * 2.10

            noise = rng.normal(0, 2.2)
            delta = drift + noise

            open_p = round_to_tick(price)
            close_p = round_to_tick(open_p + delta)
            wick_up = abs(rng.normal(2.5, 1.2))
            wick_dn = abs(rng.normal(2.5, 1.2))

            high_p = round_to_tick(max(open_p, close_p) + wick_up)
            low_p = round_to_tick(min(open_p, close_p) - wick_dn)

            # Higher volume at open, close, and trend resumption bars
            u_shape = 1.6 if (m_idx < 30 or m_idx > 350) else 1.0
            resumption_boost = 1.35 if cycle_pos >= 25 else 1.0
            volume = int(max(150, rng.normal(950, 220) * u_shape * resumption_boost))

            rows.append(
                {
                    "timestamp": ts,
                    "open": open_p,
                    "high": high_p,
                    "low": low_p,
                    "close": close_p,
                    "volume": volume,
                }
            )
            price = close_p

    return pd.DataFrame(rows)
