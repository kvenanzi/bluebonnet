"""Weather predictors for every county kept by 01_fetch_inat.py (preregistration §5).

Monthly predictors come from nClimDiv (county values back to 1895); freeze days and growing
degree days from the nearest GHCN-Daily station with >= 90% coverage in each season.
Springs 1951–2027 are computed: 1991–2020 give the normals, 2016–2026 the training rows,
El Niño springs since 1951 the forecast analogs, and 2027 whatever months are observed.

Outputs (data/interim/): weather_raw.parquet, weather_z.parquet, normals.csv, oni.csv, weather_sources.json
Run from the repo root:  uv run scripts/02_fetch_noaa.py [--refresh]
"""

import argparse
import json
from pathlib import Path

import pandas as pd

from bluebonnet import features, noaa

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "interim"
SPRINGS = list(range(1951, 2028))


def norm_name(s: str) -> str:
    return s.lower().replace(" ", "").replace(".", "")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="re-download nClimDiv and ONI (new monthly release)")
    args = ap.parse_args()

    counties = pd.read_csv(OUT / "counties.csv")
    counties = counties[counties.included | counties.forecast_county]
    gaz = noaa.counties_gazetteer()
    gaz["key"] = gaz.name.map(norm_name)
    counties = counties.assign(key=counties.name.map(norm_name)).merge(gaz[["key", "fips", "lat", "lon"]], on="key", how="left")
    missing = counties[counties.fips.isna()]
    if len(missing):
        raise SystemExit(f"no FIPS for: {missing.name.tolist()}")

    clim = {el: noaa.climdiv(el, refresh=args.refresh) for el in ["pcpn", "tmpc", "pdsi"]}
    sources = {el: df.attrs["source_file"] for el, df in clim.items()}
    for el, df in clim.items():
        last = df.dropna().sort_values(["year", "month"]).iloc[-1]
        print(f"nClimDiv {el}: {sources[el]} (last month {int(last.year)}-{int(last.month):02d})")

    monthly = features.monthly_predictors(clim, counties.fips.tolist(), SPRINGS)
    stations = noaa.ghcn_stations()
    stations = stations[stations.lat.between(25, 37.5) & stations.lon.between(-107, -93)]
    print(f"GHCN stations with TMAX+TMIN in the box: {len(stations):,}; computing station predictors ...")
    daily = features.station_predictors(counties, SPRINGS, stations)
    raw = monthly.merge(daily, on=["fips", "spring"], how="left")
    z, normals = features.standardize(raw)

    oni = noaa.oni(refresh=args.refresh)
    raw.to_parquet(OUT / "weather_raw.parquet", index=False)
    z.to_parquet(OUT / "weather_z.parquet", index=False)
    normals.to_csv(OUT / "normals.csv", index=False)
    oni.to_csv(OUT / "oni.csv", index=False)
    counties[["place_id", "name", "fips", "lat", "lon"]].to_csv(OUT / "county_fips.csv", index=False)
    cover = raw[raw.spring.between(2016, 2026)]
    sources.update({"oni": noaa.ONI, "ghcn_stations_used": int(raw.station.nunique()),
                    "station_km_median": float(cover.station_km.median()),
                    "station_missing_2016_2026": int(cover.gdd_mar1.isna().sum())})
    (OUT / "weather_sources.json").write_text(json.dumps(sources, indent=2))
    print(json.dumps(sources, indent=2))


if __name__ == "__main__":
    main()
