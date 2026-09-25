"""Pull the iNaturalist data behind the bloom targets (preregistration §2–3).

1. Every verifiable Lupinus texensis observation in Texas, 1 Feb–30 Apr of each spring,
   uploaded by 15 May of the same year.
2. The Texas county of each record, from the county place id iNaturalist attaches.
3. The county inclusion rule: >= 20 records (City Nature Challenge days removed) in
   >= 6 of the 10 training springs; the seven forecast counties are always kept.
4. For every kept county and spring, daily counts of all verifiable Plantae (the effort
   denominator) and of bluebonnet records carrying the Flowering annotation (sensitivity).

Outputs (data/interim/): observations.parquet, counties.csv, daily.parquet
Run from the repo root:
  uv run scripts/01_fetch_inat.py                 # all springs 2016-2026 (~20 min cold, seconds cached)
  uv run scripts/01_fetch_inat.py --springs 2027  # the grading pull (on or after 15 May 2027);
                                                  # writes *_2027.parquet, keeps counties.csv
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from bluebonnet import (CNC_DAYS, FORECAST_COUNTIES, MIN_RECORDS, MIN_SPRINGS, SENSITIVITY_SPRINGS,
                        TAXON_BLUEBONNET, TAXON_PLANTAE, TRAIN_SPRINGS)
from bluebonnet import inat

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "interim"


def cnc_mask(dates: pd.Series, years: pd.Series) -> pd.Series:
    out = pd.Series(False, index=dates.index)
    for y, (a, b) in CNC_DAYS.items():
        out |= (years == y) & (dates >= a) & (dates <= b)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--springs", type=int, nargs="*", default=SENSITIVITY_SPRINGS + TRAIN_SPRINGS)
    ap.add_argument("--refresh", action="store_true", help="ignore the cache")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    # A pull of springs after the training period (the May 2027 grading pull) keeps the county
    # table fixed and writes to separate files, so the training data are never replaced.
    grading = min(args.springs) > max(TRAIN_SPRINGS)
    suffix = f"_{'_'.join(map(str, args.springs))}" if grading else ""
    missing_cnc = [y for y in args.springs if y not in CNC_DAYS]
    if missing_cnc:
        raise SystemExit(f"add the City Nature Challenge dates for {missing_cnc} to CNC_DAYS first")

    obs = pd.concat([inat.bluebonnet_observations(y, args.refresh) for y in args.springs], ignore_index=True)
    print(f"bluebonnet observations: {len(obs):,}")
    print(obs.groupby("spring").size().to_string())

    if grading:
        counties = pd.read_csv(OUT / "counties.csv")
    else:
        counties = inat.texas_counties([p for ids in obs.place_ids for p in ids])
    cset = set(counties.place_id)
    obs["county_place_id"] = obs.place_ids.apply(lambda ids: next((p for p in ids if p in cset), None))
    obs["cnc"] = cnc_mask(obs.observed_on, obs.spring)
    print(f"no county: {obs.county_place_id.isna().sum():,}; City Nature Challenge days: {obs.cnc.sum():,}")
    obs.drop(columns=["place_ids"]).to_parquet(OUT / f"observations{suffix}.parquet", index=False)

    # Inclusion rule on the training springs only.
    if grading:
        use = counties[counties.forecast_county]
    if not grading:
        kept = obs[~obs.cnc & obs.county_place_id.notna() & obs.spring.isin(TRAIN_SPRINGS)]
        per = kept.groupby(["county_place_id", "spring"]).size().unstack(fill_value=0)
        n_ok = (per >= MIN_RECORDS).sum(axis=1)
        counties["springs_ge_20"] = counties.place_id.map(n_ok).fillna(0).astype(int)
        counties["forecast_county"] = counties.place_id.isin(FORECAST_COUNTIES.values())
        counties["included"] = counties.springs_ge_20 >= MIN_SPRINGS
        use = counties[counties.included | counties.forecast_county]
        print(f"Texas counties with records: {len(counties)}; included by rule: {counties.included.sum()}; "
              f"fetched (included or forecast): {len(use)}")
        counties.to_csv(OUT / "counties.csv", index=False)

    def one(job):
        pid, name, y = job
        plants = inat.daily_histogram(pid, y, TAXON_PLANTAE, refresh=args.refresh)
        flower = inat.daily_histogram(pid, y, TAXON_BLUEBONNET, {"term_id": 12, "term_value_id": 13},
                                      refresh=args.refresh)
        return pd.DataFrame({"place_id": pid, "county": name, "date": plants.index,
                             "plants": plants.values, "bb_flowering": flower.values})

    jobs = [(int(c.place_id), c["name"], y) for _, c in use.iterrows() for y in args.springs]
    # The API's latency (several seconds) dominates, so four requests are kept in flight while
    # the shared limiter in inat.get still starts at most one per second.
    with ThreadPoolExecutor(4) as pool:
        frames = list(pool.map(one, jobs))
    print(f"histograms: {len(jobs)} county-springs", flush=True)
    daily = pd.concat(frames, ignore_index=True)
    bb = (obs.dropna(subset=["county_place_id"]).assign(date=lambda d: pd.to_datetime(d.observed_on))
          .groupby(["county_place_id", "date"]).size().rename("bb").reset_index()
          .rename(columns={"county_place_id": "place_id"}))
    daily = daily.merge(bb, on=["place_id", "date"], how="left").fillna({"bb": 0})
    daily["bb"] = daily.bb.astype(int)
    daily["spring"] = daily.date.dt.year
    daily["cnc"] = cnc_mask(daily.date.dt.strftime("%Y-%m-%d"), daily.spring)
    daily.to_parquet(OUT / f"daily{suffix}.parquet", index=False)
    print(f"daily rows: {len(daily):,} -> {OUT / f'daily{suffix}.parquet'}")


if __name__ == "__main__":
    main()
