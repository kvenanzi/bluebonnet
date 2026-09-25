"""Bloom targets per county and spring (preregistration §4).

Strength: y = bluebonnet records and n = all Plantae records over 1 Feb–30 Apr with the
City Nature Challenge days removed; point models use the empirical logit of y/n.
Timing: the effort-weighted median day of year. Each day's bluebonnet count is divided by
that day's Plantae count, the ratios are smoothed by a 7-day centred moving sum, and the
day on which the cumulative share first reaches one half is the median (0.1: onset).
"""

import numpy as np
import pandas as pd

from . import FORECAST_COUNTIES, MIN_POINT_RECORDS, MIN_TIMING_RECORDS, POOLED


def empirical_logit(y, n):
    y, n = np.asarray(y, float), np.asarray(n, float)
    return np.log((y + 0.5) / (n - y + 0.5))


def weighted_quantile_day(bb: np.ndarray, plants: np.ndarray, days: np.ndarray, q: float) -> float:
    """Day of year at which the smoothed effort-normalized distribution reaches quantile q."""
    ratio = np.divide(bb, plants, out=np.zeros(len(bb), float), where=plants > 0)
    smooth = np.convolve(ratio, np.ones(7), mode="same")
    total = smooth.sum()
    if total <= 0:
        return np.nan
    cum = np.cumsum(smooth) / total
    return float(days[np.searchsorted(cum, q)])


def season_table(daily: pd.DataFrame) -> pd.DataFrame:
    """One row per county-spring (and a pooled row per spring) from data/interim/daily.parquet.
    CNC days are zeroed in both series before the sums and the timing distribution."""
    d = daily.copy()
    d.loc[d.cnc, ["bb", "plants", "bb_flowering"]] = 0
    d["doy"] = d.date.dt.dayofyear
    pooled = (d[d.place_id.isin(FORECAST_COUNTIES.values())]
              .groupby(["spring", "date", "doy"], as_index=False)[["bb", "plants", "bb_flowering"]].sum()
              .assign(place_id=0, county=POOLED))
    rows = []
    for (pid, county, spring), g in pd.concat([d, pooled]).groupby(["place_id", "county", "spring"]):
        g = g.sort_values("date")
        bb, pl, days = g.bb.values, g.plants.values, g.doy.values
        rows.append({
            "place_id": int(pid), "county": county, "spring": int(spring),
            "y": int(bb.sum()), "n": int(pl.sum()), "y_flowering": int(g.bb_flowering.sum()),
            "median_doy": weighted_quantile_day(bb, pl, days, 0.5),
            "onset_doy": weighted_quantile_day(bb, pl, days, 0.1),
        })
    t = pd.DataFrame(rows)
    t["logit"] = empirical_logit(t.y, t.n)
    t["per_1000"] = 1000 * t.y / t.n.where(t.n > 0)
    t["point_ok"] = t.y >= MIN_POINT_RECORDS
    t["timing_ok"] = t.y >= MIN_TIMING_RECORDS
    t.loc[~t.timing_ok, ["median_doy", "onset_doy"]] = np.nan
    return t
