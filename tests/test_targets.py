import numpy as np
import pandas as pd

from bluebonnet import CNC_DAYS
from bluebonnet.targets import empirical_logit, season_table, weighted_quantile_day


def synthetic_daily(peak_doy=85, spread=10, spike=True, spring=2024, place_id=431, county="Travis"):
    dates = pd.date_range(f"{spring}-02-01", f"{spring}-04-30")
    doy = dates.dayofyear.values
    plants = np.full(len(dates), 200)
    bb = np.round(40 * np.exp(-0.5 * ((doy - peak_doy) / spread) ** 2)).astype(int)
    a, b = CNC_DAYS[spring]
    cnc = (dates >= a) & (dates <= b)
    if spike:                                      # a bioblitz: 10x effort, many bluebonnets
        plants = np.where(cnc, 2000, plants)
        bb = np.where(cnc, 400, bb)
    return pd.DataFrame({"place_id": place_id, "county": county, "date": dates, "plants": plants,
                         "bb": bb, "bb_flowering": bb // 3, "spring": spring, "cnc": cnc})


def test_median_recovers_symmetric_peak():
    d = synthetic_daily(spike=False)
    days = d.date.dt.dayofyear.values
    assert abs(weighted_quantile_day(d.bb.values, d.plants.values, days, 0.5) - 85) <= 1


def test_cnc_spike_is_masked():
    t = season_table(synthetic_daily(spike=True))
    row = t[t.county == "Travis"].iloc[0]
    assert abs(row.median_doy - 85) <= 1
    assert row.n == 200 * (len(pd.date_range("2024-02-01", "2024-04-30")) - 4)   # 26-29 Apr 2024: four masked days


def test_effort_normalization_removes_weekend_effort():
    d = synthetic_daily(spike=False)
    weekend = d.date.dt.dayofweek >= 5
    d.loc[weekend, "plants"] *= 5                  # five times the observers on weekends ...
    d.loc[weekend, "bb"] *= 5                      # ... record five times the bluebonnets
    t = season_table(d)
    assert abs(t.iloc[0].median_doy - 85) <= 1


def test_empirical_logit_finite_at_zero():
    assert np.isfinite(empirical_logit(0, 10)) and np.isfinite(empirical_logit(10, 10))
