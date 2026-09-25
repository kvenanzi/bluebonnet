"""Score the point-model rungs of the ladder by leave-one-year-out (preregistration §6–7).

For each target (strength: `logit`; timing: `median_doy`) and each model, the held-out
predictions, CV+ intervals, and CRPS are saved to outputs/ladder/<target>/<model>.parquet and
logged as one W&B run (job_type "loyo", group "ladder").
Run from the repo root:
  uv run scripts/05_ladder.py                 # both targets, every model
  uv run scripts/05_ladder.py --no-wandb      # offline
  uv run scripts/05_ladder.py --only ridge
"""

import argparse
import json
from pathlib import Path

import pandas as pd

from bluebonnet import data, models, wb
from bluebonnet.eval import loyo, summarize
from bluebonnet.features import PREDICTORS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "ladder"


def ladder(target: str) -> dict:
    second = "winter_tavg" if target == "logit" else "gdd_mar1"
    return {
        "climatology": models.Climatology(),
        "persistence": models.Persistence(),
        "ols_fall_prcp": models.ols("M1a OLS fall_prcp", ["fall_prcp"]),
        f"ols_{second}": models.ols(f"M1b OLS {second}", [second]),
        "ridge": models.ridge(PREDICTORS),
        "elastic_net": models.elastic_net(PREDICTORS),
        "lightgbm": models.lightgbm(PREDICTORS),
        "per_county_fall_prcp": models.PerCounty(["fall_prcp"]),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", nargs="*", default=["logit", "median_doy"])
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--no-wandb", action="store_true")
    args = ap.parse_args()
    df = data.load()
    results = {}
    for target in args.targets:
        rows = data.training(df, target)
        (OUT / target).mkdir(parents=True, exist_ok=True)
        clim = None
        for key, proto in ladder(target).items():
            if args.only and key not in args.only and key != "climatology":
                continue
            pred = loyo(proto, rows, target)
            if key == "climatology":
                clim = pred
            s = summarize(pred, clim)
            fitted = proto.fit(rows, target)          # all ten springs: coefficients for the post
            s["full_fit"] = fitted.describe()
            pred.to_parquet(OUT / target / f"{key}.parquet", index=False)
            results[f"{target}/{key}"] = s
            print(f"{target:11s} {key:22s} rmse {s['rmse']:.4f}  crps {s['crps']:.4f}  "
                  f"cov80 {s['cov80']:.2f}  skill {s.get('crps_skill', 0):+.3f}")
            if not args.no_wandb:
                run = wb.init(f"{key}-{target}", "loyo", {"model": key, "target": target, "name": proto.name,
                              "features": getattr(proto, "features", []), "rows": len(rows)}, group="ladder")
                wb.log_loyo(run, target, pred, {k: v for k, v in s.items() if not isinstance(v, dict)})
                run.summary["full_fit"] = s["full_fit"]
                s["wandb_run"] = run.id
                run.finish()
    old = json.loads((OUT / "summary.json").read_text()) if (OUT / "summary.json").exists() else {}
    old.update(results)
    (OUT / "summary.json").write_text(json.dumps(old, indent=2, default=str))


if __name__ == "__main__":
    main()
