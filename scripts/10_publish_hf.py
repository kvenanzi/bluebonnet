"""Stage and upload the Hugging Face dataset and model repositories.

Dataset `<ns>/texas-bluebonnet-seasons`: the county-spring table (aggregate counts and weather
z-scores; no individual observations), the pre-registration, the independent year codes, and
every registered forecast with its samples.
Model `<ns>/bluebonnet-bloom-forecast`: the hierarchical model's posterior draws (NetCDF), ridge
coefficients (JSON), the LightGBM model (text), and a model card. No pickles.

Repositories are created private; making them public is a manual step on huggingface.co.
  uv run scripts/10_publish_hf.py --dry-run      # stage under outputs/hf/ only
  uv run scripts/10_publish_hf.py                # stage and upload
"""

import argparse
import json
import shutil
from pathlib import Path

import pandas as pd

from bluebonnet import data, models
from bluebonnet.features import PREDICTORS

ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "outputs" / "hf"

DATASET_CARD = """---
license: cc-by-4.0
pretty_name: Texas bluebonnet county-springs, 2016–2026
tags: [phenology, citizen-science, inaturalist, climate, texas, forecasting]
size_categories: [n<1K]
---

# Texas bluebonnet county-springs, 2016–2026

One row per Texas county and spring: the number of verifiable iNaturalist observations of the
Texas bluebonnet (*Lupinus texensis*, taxon 49564) and of all plants, 1 February–30 April, uploaded
by 15 May of the same year, with City Nature Challenge days removed; the effort-weighted median
observation date; and NOAA weather predictors for the preceding fall and winter as county z-scores.

- `seasons.parquet`: the table (`y`, `n`, `logit`, `per_1000`, `median_doy`, predictors, `raw_*` in physical units).
- `preregistration.md`: hypotheses, targets, predictors, and grading rules, committed before any model was fit.
- `bloom-year-codes.md`: independent good/moderate/poor codes from published statements.
- `forecasts/`: every registered forecast for spring 2027 (`<issue>.csv`, `<issue>-samples.parquet`, `<issue>.json`).

Sources: iNaturalist (observation counts via the public API; the research-grade export is archived
at GBIF, doi:10.15468/ab3s5x); NOAA NCEI nClimDiv and GHCN-Daily (public domain). The table holds
aggregate counts only, so no observation, photograph, or observer is redistributed.

Write-up: https://withinnoise.dev/blog/posts/bluebonnet-bloom-forecast/
Code, pre-registration history, and the forecast tag: https://github.com/kvenanzi/bluebonnet
"""

MODEL_CARD = """---
license: mit
tags: [phenology, bayesian, pymc, forecasting, tabular-regression]
datasets: [__NS__/texas-bluebonnet-seasons]
---

# Bluebonnet bloom forecast (Central Texas)

Hierarchical Bayesian models (PyMC) of the Texas bluebonnet bloom per county, from fall and winter
weather, fit on ten springs (2017–2026) and 15 Texas counties.

- `full_logit.nc`: strength model, `y ~ BetaBinomial(n, mu*phi, (1-mu)*phi)`, `logit mu = alpha + a[county] + b[spring] + X beta`.
- `full_median_doy.nc`: timing model, Student-t on the effort-weighted median day of year.
- `ridge.json`, `lightgbm.txt`: the point models of the ladder, fit on the same rows.
- `metrics.json`: leave-one-year-out scores for every rung.

Load a posterior with `arviz.from_netcdf("full_logit.nc")`. Predictors are county z-scores against
1991–2020 (see the dataset card). With ten springs, the between-year evidence is thin; read the
leave-one-year-out skill in `metrics.json` before using any forecast.

Write-up: https://withinnoise.dev/blog/posts/bluebonnet-bloom-forecast/
Code: https://github.com/kvenanzi/bluebonnet
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--namespace")
    args = ap.parse_args()
    from huggingface_hub import HfApi
    api = HfApi()
    ns = args.namespace or api.whoami()["name"]

    ds, md = STAGE / "dataset", STAGE / "model"
    shutil.rmtree(STAGE, ignore_errors=True)
    (ds / "forecasts").mkdir(parents=True)
    md.mkdir(parents=True)
    shutil.copy(ROOT / "data" / "processed" / "seasons.parquet", ds)
    shutil.copy(ROOT / "data" / "processed" / "manifest.json", ds)
    for f in ["preregistration.md", "bloom-year-codes.md"]:
        shutil.copy(ROOT / "docs" / f, ds)
    for f in (ROOT / "forecasts").glob("*"):
        shutil.copy(f, ds / "forecasts")
    (ds / "README.md").write_text(DATASET_CARD)

    for t in ["logit", "median_doy"]:
        shutil.copy(ROOT / "outputs" / "bayes" / f"full_{t}.nc", md)
    df = data.load()
    rows = data.training(df, "logit")
    r = models.ridge(PREDICTORS).fit(rows, "logit")
    (md / "ridge.json").write_text(json.dumps({"target": "logit anomaly from the county mean", **r.describe(),
                                               "county_means": {int(k): float(v) for k, v in r.means.items()}}, indent=2))
    best = ROOT / "outputs" / "sweep_best.json"
    params = json.loads(best.read_text())["params"] if best.exists() else None
    lg = models.lightgbm(PREDICTORS, params).fit(rows, "logit")
    lg.estimator.booster_.save_model(str(md / "lightgbm.txt"))
    metrics = {"ladder": json.loads((ROOT / "outputs" / "ladder" / "summary.json").read_text()),
               "hierarchical": json.loads((ROOT / "outputs" / "bayes" / "summary.json").read_text())}
    (md / "metrics.json").write_text(json.dumps(metrics, indent=2, default=str))
    (md / "README.md").write_text(MODEL_CARD.replace("__NS__", ns))
    print(f"staged {ds} and {md}")
    if args.dry_run:
        return
    for kind, folder, name in [("dataset", ds, "texas-bluebonnet-seasons"), ("model", md, "bluebonnet-bloom-forecast")]:
        repo = f"{ns}/{name}"
        api.create_repo(repo, repo_type=kind, private=True, exist_ok=True)
        info = api.upload_folder(folder_path=str(folder), repo_id=repo, repo_type=kind,
                                 commit_message="Publish data and models for the October 2026 forecast")
        print(f"{kind}: https://huggingface.co/{'datasets/' if kind == 'dataset' else ''}{repo}  commit {info.oid}")


if __name__ == "__main__":
    main()
