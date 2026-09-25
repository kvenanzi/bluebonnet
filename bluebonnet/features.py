"""Weather predictors per county and spring (preregistration §5).

For spring t, "fall" is September–November of year t-1 and "winter" is December of t-1
through February of t. Every predictor is returned raw and as a z-score against the
county's normal: the mean and standard deviation over springs 1991–2020.
"""

import numpy as np
import pandas as pd

from . import noaa

PREDICTORS = ["fall_prcp", "sepoct_prcp", "octdec_prcp", "winter_prcp", "winter_tavg",
              "freeze_days", "gdd_mar1", "summer_pdsi"]
MODEL_PREDICTORS = ["fall_prcp", "winter_prcp", "winter_tavg", "freeze_days", "gdd_mar1", "summer_pdsi"]
NORMAL_SPRINGS = (1991, 2020)
FREEZE_C = -2.0
GDD_BASE_C = 5.0
MIN_COVERAGE = 0.90
MAX_STATION_KM = 150.0

# (predictor, months as (year offset from spring, month), aggregate)
MONTHLY = {
    "fall_prcp": ("pcpn", [(-1, 9), (-1, 10), (-1, 11)], "sum"),
    "sepoct_prcp": ("pcpn", [(-1, 9), (-1, 10)], "sum"),
    "octdec_prcp": ("pcpn", [(-1, 10), (-1, 11), (-1, 12)], "sum"),
    "winter_prcp": ("pcpn", [(-1, 12), (0, 1), (0, 2)], "sum"),
    "winter_tavg": ("tmpc", [(-1, 12), (0, 1), (0, 2)], "mean"),
    "summer_pdsi": ("pdsi", [(-1, 6), (-1, 7), (-1, 8)], "mean"),
}


def monthly_predictors(climdiv: dict[str, pd.DataFrame], fips: list[str], springs: list[int]) -> pd.DataFrame:
    """Predictors from nClimDiv monthly values. A spring whose months are not all present
    gets NaN (this is how unobserved months are marked in the forecast)."""
    rows = []
    lookup = {el: df.set_index(["fips", "year", "month"])["value"] for el, df in climdiv.items()}
    for f in fips:
        for t in springs:
            row = {"fips": f, "spring": t}
            for name, (el, months, agg) in MONTHLY.items():
                vals = [lookup[el].get((f, t + dy, m), np.nan) for dy, m in months]
                if any(pd.isna(v) for v in vals):
                    row[name] = np.nan
                    continue
                if el == "pcpn":
                    vals = [v * 25.4 for v in vals]            # inches -> mm
                if el == "tmpc":
                    vals = [(v - 32) / 1.8 for v in vals]      # °F -> °C
                row[name] = float(np.sum(vals) if agg == "sum" else np.mean(vals))
            rows.append(row)
    return pd.DataFrame(rows)


def season_days(spring: int) -> tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp]:
    return pd.Timestamp(f"{spring - 1}-12-01"), pd.Timestamp(f"{spring}-01-01"), pd.Timestamp(f"{spring}-03-01")


def station_season(daily: pd.DataFrame, spring: int) -> dict | None:
    """freeze_days (Dec–Feb) and gdd_mar1 (Jan–Feb) from one station's daily data, or None
    if fewer than 90% of the season's days have both TMAX and TMIN. Counts are scaled up
    by the share of days present."""
    dec1, jan1, mar1 = season_days(spring)
    days = pd.date_range(dec1, mar1 - pd.Timedelta(days=1))
    s = daily.reindex(days).dropna(subset=["TMAX", "TMIN"]) if {"TMAX", "TMIN"} <= set(daily.columns) else None
    if s is None or len(s) < MIN_COVERAGE * len(days):
        return None
    freeze = (s.TMIN <= FREEZE_C).sum() * len(days) / len(s)
    jf = s[s.index >= jan1]
    n_jf = (mar1 - jan1).days
    if len(jf) < MIN_COVERAGE * n_jf:
        return None
    gdd = (((jf.TMAX + jf.TMIN) / 2 - GDD_BASE_C).clip(lower=0)).sum() * n_jf / len(jf)
    return {"freeze_days": float(freeze), "gdd_mar1": float(gdd)}


def station_predictors(counties: pd.DataFrame, springs: list[int], stations: pd.DataFrame,
                       log=print) -> pd.DataFrame:
    """For each county and spring, the nearest station (to the county's interior point)
    with >= 90% daily coverage in that season; stations are downloaded only when reached."""
    cache: dict[str, pd.DataFrame] = {}
    rows = []
    for _, c in counties.iterrows():
        d = noaa.haversine_km(c.lat, c.lon, stations.lat.values, stations.lon.values)
        near = stations.assign(km=d)
        near = near[near.km <= MAX_STATION_KM].sort_values("km")
        for t in springs:
            found = None
            for _, st in near[(near["first"] <= t - 1) & (near["last"] >= t)].iterrows():
                if st.id not in cache:
                    try:
                        cache[st.id] = noaa.station_daily(st.id)
                    except Exception as e:                       # a missing file: try the next station
                        log(f"  station {st.id}: {e}")
                        cache[st.id] = pd.DataFrame()
                v = station_season(cache[st.id], t) if len(cache[st.id]) else None
                if v:
                    found = {**v, "station": st.id, "station_km": round(float(st.km), 1)}
                    break
            rows.append({"fips": c.fips, "spring": t,
                         **(found or {"freeze_days": np.nan, "gdd_mar1": np.nan, "station": None, "station_km": np.nan})})
    return pd.DataFrame(rows)


def standardize(raw: pd.DataFrame, cols: list[str] = PREDICTORS) -> tuple[pd.DataFrame, pd.DataFrame]:
    """z-scores against each county's 1991–2020 springs. Returns (z, normals)."""
    base = raw[raw.spring.between(*NORMAL_SPRINGS)]
    normals = base.groupby("fips")[cols].agg(["mean", "std"])
    z = raw[["fips", "spring"]].copy()
    for col in cols:
        mu = raw.fips.map(normals[(col, "mean")])
        sd = raw.fips.map(normals[(col, "std")])
        z[col] = (raw[col] - mu) / sd
    normals.columns = [f"{a}_{b}" for a, b in normals.columns]
    return z, normals.reset_index()
