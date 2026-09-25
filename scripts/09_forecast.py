"""Issue a registered forecast for spring 2027 (preregistration §8).

  uv run scripts/09_forecast.py --issue forecast-2026-10 --observed-through 2026-08
  uv run scripts/09_forecast.py --issue forecast-2026-12 --observed-through 2026-11
  uv run scripts/09_forecast.py --issue forecast-2027-03 --observed-through 2027-02

A predictor counts as observed only if every month it needs is on or before
--observed-through and present in the weather table; everything else comes from the
El Niño analog seasons. Writes forecasts/<issue>.csv (the registered numbers) and
forecasts/<issue>.json (data cut, analogs, extrapolation, point-model comparison, SHA-256).
Refuses to overwrite an existing issue.
"""

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

import arviz as az
import numpy as np
import pandas as pd

from bluebonnet import FORECAST_COUNTIES, POOLED, TRAIN_SPRINGS, bayes, data, forecast, models
from bluebonnet.features import MODEL_PREDICTORS, PREDICTORS
from bluebonnet.targets import empirical_logit

ROOT = Path(__file__).resolve().parent.parent
INTERIM, BAYES, OUT = ROOT / "data" / "interim", ROOT / "outputs" / "bayes", ROOT / "forecasts"
SPRING = 2027
LAST_MONTH = {"fall_prcp": (2026, 11), "sepoct_prcp": (2026, 10), "octdec_prcp": (2026, 12),
              "winter_prcp": (2027, 2), "winter_tavg": (2027, 2), "freeze_days": (2027, 2),
              "gdd_mar1": (2027, 2), "summer_pdsi": (2026, 8)}


def doy_to_date(d: float) -> str:
    return (pd.Timestamp(f"{SPRING}-01-01") + pd.Timedelta(days=round(d) - 1)).strftime("%d %b")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True)
    ap.add_argument("--observed-through", required=True, help="YYYY-MM")
    ap.add_argument("--force", action="store_true", help="overwrite (only before the issue is published)")
    args = ap.parse_args()
    csv, meta_path = OUT / f"{args.issue}.csv", OUT / f"{args.issue}.json"
    if csv.exists() and not args.force:
        raise SystemExit(f"{csv} exists; a registered forecast is never overwritten")
    OUT.mkdir(exist_ok=True)
    cut = tuple(int(x) for x in args.observed_through.split("-"))

    df = data.load()
    z = pd.read_parquet(INTERIM / "weather_z.parquet")
    fips = pd.read_csv(INTERIM / "county_fips.csv", dtype={"fips": str})
    fips_of = dict(zip(fips.place_id, fips.fips))
    oni = pd.read_csv(INTERIM / "oni.csv")
    analogs = forecast.analog_springs(oni)
    pids = list(FORECAST_COUNTIES.values())

    z27 = z[z.spring == SPRING].set_index("fips")
    observed = {}
    for pid in pids:
        obs = {}
        for p in PREDICTORS:
            if LAST_MONTH[p] <= cut and fips_of[pid] in z27.index and not pd.isna(z27.loc[fips_of[pid], p]):
                obs[p] = float(z27.loc[fips_of[pid], p])
        observed[pid] = obs
    observed_names = sorted({k for o in observed.values() for k in o})
    print(f"observed predictors for {SPRING}: {observed_names or 'none'}; analog springs: {len(analogs)}")
    scen = forecast.scenarios(z, pids, observed, PREDICTORS, analogs, fips_of)

    train_rows = df[df.included.fillna(False).astype(bool) & df.spring.isin(TRAIN_SPRINGS)]
    n2026 = df[df.spring == 2026].set_index("place_id").n.to_dict()
    names = {v: k for k, v in FORECAST_COUNTIES.items()}
    samples = []   # every predictive draw, committed with the CSV so the May grading can compute CRPS
    rows, meta = [], {"issue": args.issue, "issued_on": date.today().isoformat(), "observed_through": args.observed_through,
                      "observed_predictors": {names[p]: o for p, o in observed.items()},
                      "analog_springs": analogs, "model": "M4 hierarchical (preregistration §7)",
                      "n_assumed": "each county's 2026 count of plant records"}

    for target, mt in [("logit", "strength"), ("median_doy", "median_doy")]:
        idata = az.from_netcdf(BAYES / f"full_{target}.nc")
        post = bayes.posterior({"idata": idata})
        fitted_counties = [int(c) for c in idata.posterior.coords["county"].values]
        sims, pick = forecast.simulate(post, fitted_counties, MODEL_PREDICTORS, scen, mt, n2026)
        if target == "logit":
            pooled_y = sum(sims[p][0] for p in pids)
            pooled_n = sum(sims[p][1] for p in pids)
            series = {p: (empirical_logit(y, n), 1000 * y / n) for p, (y, n) in sims.items()}
            series[0] = (empirical_logit(pooled_y, pooled_n), 1000 * pooled_y / pooled_n)
            for pid, (lg, per) in series.items():
                samples += [(POOLED if pid == 0 else names[pid], "strength_logit", lg), (POOLED if pid == 0 else names[pid], "strength_per_1000", per)]
                hist = df[(df.place_id == pid) & df.spring.isin(TRAIN_SPRINGS)]
                name = POOLED if pid == 0 else names[pid]
                rows.append({"county": name, "target": "strength_logit", **forecast.summarize_samples(lg, forecast.terciles(hist.logit))})
                rows.append({"county": name, "target": "strength_per_1000", **forecast.summarize_samples(per, forecast.terciles(hist.per_1000))})
        else:
            w = np.array([n2026.get(p, 0) for p in pids], float)
            ys = {p: df[(df.place_id == p) & (df.spring == 2026)].y.iloc[0] for p in pids}
            wy = np.array([ys[p] for p in pids], float)
            series = dict(sims)
            series[0] = sum(sims[p] * wy[i] for i, p in enumerate(pids)) / wy.sum()
            pooled_hist = df[(df.place_id == 0) & df.spring.isin(TRAIN_SPRINGS)].median_doy
            for pid, s in series.items():
                samples.append((POOLED if pid == 0 else names[pid], "median_doy", s))
                hist = df[(df.place_id == pid) & df.spring.isin(TRAIN_SPRINGS)].median_doy.dropna()
                name = POOLED if pid == 0 else names[pid]
                ter = forecast.terciles(hist if len(hist) >= 5 else pooled_hist)
                r = {"county": name, "target": "median_doy", **forecast.summarize_samples(s, ter),
                     "tercile_source": "county" if len(hist) >= 5 else POOLED}
                rows.append(r)
        meta[f"draws_{target}"] = int(len(post["alpha"]))

    fc = pd.DataFrame(rows)
    fc.insert(0, "issue", args.issue)
    fc["included_in_training"] = fc.county.map(lambda c: c == POOLED or bool(train_rows.county.eq(c).any()))
    for q in forecast.QUANTILES:
        fc.loc[fc.target == "median_doy", f"{q}_date"] = fc.loc[fc.target == "median_doy", q].map(doy_to_date)
    fc = fc.round(4)
    fc.to_csv(csv, index=False)
    sm = pd.DataFrame([{"county": c, "target": t, "draw": i, "value": float(v)} for c, t, arr in samples for i, v in enumerate(arr)])
    sm.to_parquet(OUT / f"{args.issue}-samples.parquet", index=False)
    sha = hashlib.sha256(csv.read_bytes()).hexdigest()
    meta["samples_sha256"] = hashlib.sha256((OUT / f"{args.issue}-samples.parquet").read_bytes()).hexdigest()

    # Extrapolation: share of scenario values outside the training range of each predictor.
    allscen = pd.concat(scen.values())
    rng = train_rows[PREDICTORS].agg(["min", "max"])
    meta["extrapolation_share"] = {p: float(((allscen[p] < rng.loc["min", p]) | (allscen[p] > rng.loc["max", p])).mean())
                                   for p in PREDICTORS if p not in observed_names}
    meta["training_range"] = rng.round(3).to_dict()
    # Point-model comparison under the same scenarios (not registered; for the discussion).
    rows_pt = data.training(df, "logit")
    cmp = {}
    for key, m in [("ridge", models.ridge(PREDICTORS)), ("lightgbm", models.lightgbm(PREDICTORS))]:
        m.fit(rows_pt, "logit")
        preds = np.stack([m.predict(scen[a].merge(df[df.spring == 2026][["place_id"]], on="place_id")) for a in analogs])
        cmp[key] = {names[p]: {"median": float(np.median(preds[:, i])), "q10": float(np.quantile(preds[:, i], 0.1)),
                               "q90": float(np.quantile(preds[:, i], 0.9))} for i, p in enumerate(pids)}
    meta["point_models_under_scenarios_logit"] = cmp
    meta["csv_sha256"] = sha
    meta_path.write_text(json.dumps(meta, indent=2, default=str))
    print(fc[["county", "target", "q10", "q50", "q90", "p_below", "p_near", "p_above"]].to_string())
    print(f"\nwrote {csv}\nsha256 {sha}")


if __name__ == "__main__":
    main()
