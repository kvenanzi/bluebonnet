"""Join targets and predictors into the county-spring table every model reads.

Output: data/processed/seasons.parquet (one row per county-spring, 2016–2026, plus the pooled
Central Texas row per spring) and data/processed/manifest.json (sources, counts, hash).
Run from the repo root:  uv run scripts/03_build_dataset.py
"""

import hashlib
import json
from pathlib import Path

import pandas as pd

from bluebonnet import FORECAST_COUNTIES, POOLED, SENSITIVITY_SPRINGS, TRAIN_SPRINGS
from bluebonnet.features import PREDICTORS
from bluebonnet.targets import season_table

ROOT = Path(__file__).resolve().parent.parent
INTERIM, OUT = ROOT / "data" / "interim", ROOT / "data" / "processed"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    daily = pd.read_parquet(INTERIM / "daily.parquet")
    counties = pd.read_csv(INTERIM / "counties.csv")
    fips = pd.read_csv(INTERIM / "county_fips.csv", dtype={"fips": str})
    z = pd.read_parquet(INTERIM / "weather_z.parquet")
    raw = pd.read_parquet(INTERIM / "weather_raw.parquet")

    t = season_table(daily)
    t = t[t.spring.isin(SENSITIVITY_SPRINGS + TRAIN_SPRINGS)]
    t = t.merge(counties[["place_id", "included", "forecast_county"]], on="place_id", how="left")
    t.loc[t.county == POOLED, ["included", "forecast_county"]] = [False, True]
    t = t.merge(fips[["place_id", "fips"]], on="place_id", how="left")

    # The pooled region's predictors are the mean of its counties' z-scores.
    zc = z.merge(fips[["fips", "place_id"]], on="fips")
    pooled_z = (zc[zc.place_id.isin(FORECAST_COUNTIES.values())].groupby("spring")[PREDICTORS].mean()
                .reset_index().assign(place_id=0))
    zc = pd.concat([zc.drop(columns="fips"), pooled_z], ignore_index=True)
    t = t.merge(zc, on=["place_id", "spring"], how="left")
    rawc = raw.merge(fips[["fips", "place_id"]], on="fips").drop(columns="fips")
    rawc = rawc.rename(columns={c: f"raw_{c}" for c in PREDICTORS})
    t = t.merge(rawc, on=["place_id", "spring"], how="left")

    t = t.sort_values(["place_id", "spring"]).reset_index(drop=True)
    for col in ["logit", "median_doy"]:
        prev = t[["place_id", "spring", col]].assign(spring=lambda d: d.spring + 1)
        t = t.merge(prev.rename(columns={col: f"prev_{col}"}), on=["place_id", "spring"], how="left")
    t = t.sort_values(["place_id", "spring"]).reset_index(drop=True)

    path = OUT / "seasons.parquet"
    t.to_parquet(path, index=False)
    digest = hashlib.sha256(pd.util.hash_pandas_object(t, index=False).values.tobytes()).hexdigest()
    train = t[t.included & t.spring.isin(TRAIN_SPRINGS)]
    manifest = {
        "rows": len(t), "included_counties": int(t[t.included].place_id.nunique()),
        "training_rows": len(train), "training_point_rows": int(train.point_ok.sum()),
        "training_timing_rows": int(train.timing_ok.sum()),
        "bluebonnet_records_training": int(train.y.sum()), "plant_records_training": int(train.n.sum()),
        "content_sha256": digest,
        "weather_sources": json.loads((INTERIM / "weather_sources.json").read_text()),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
