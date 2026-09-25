"""M4, the hierarchical Bayesian models: leave-one-year-out and the full ten-spring fit.

Strength is fit on every included county-spring (the Beta-Binomial weights each by its
counts) and scored on the same rows as the point models (>= 5 records). Timing is fit and
scored on county-springs with >= 50 records.

Outputs (outputs/bayes/): loyo_<target>.parquet, full_<target>.nc (posterior), summary.json
Run from the repo root:  uv run scripts/08_bayes.py [--targets logit median_doy] [--no-wandb] [--quick]
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from bluebonnet import TRAIN_SPRINGS, bayes, data, wb
from bluebonnet.eval import summarize
from bluebonnet.features import MODEL_PREDICTORS
from bluebonnet.stats import crps_ensemble

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "bayes"


def fit_rows(df: pd.DataFrame, target: str) -> pd.DataFrame:
    d = df[df.included.fillna(False).astype(bool) & df.spring.isin(TRAIN_SPRINGS)]
    return d[d.n > 0] if target == "logit" else d[d.timing_ok & d.median_doy.notna()]


def model_target(target: str) -> str:
    return "strength" if target == "logit" else "median_doy"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", nargs="*", default=["logit", "median_doy"])
    ap.add_argument("--no-wandb", action="store_true")
    ap.add_argument("--quick", action="store_true", help="2 chains x 300 draws, for plumbing checks")
    args = ap.parse_args()
    sampler = dict(draws=300, tune=300, chains=2) if args.quick else {}
    OUT.mkdir(parents=True, exist_ok=True)
    df = data.load()
    summary = json.loads((OUT / "summary.json").read_text()) if (OUT / "summary.json").exists() else {}
    for target in args.targets:
        rows = fit_rows(df, target)
        score_rows = data.training(df, target)
        preds, diags = [], []
        for k in TRAIN_SPRINGS:
            fitted = bayes.fit(rows[rows.spring != k], model_target(target), MODEL_PREDICTORS, seed=k, **sampler)
            d = bayes.diagnostics(fitted)
            diags.append({"spring": k, **{x: d[x] for x in ["rhat_max", "ess_bulk_min", "divergences"]}})
            test = score_rows[score_rows.spring == k]
            samples, _, _ = bayes.predict_new_spring(fitted, test, seed=k)
            res = test[["place_id", "county", "spring", target]].rename(columns={target: "obs"}).copy()
            res["pred"] = np.median(samples, axis=1)
            res["lo80"], res["hi80"] = np.quantile(samples, 0.1, axis=1), np.quantile(samples, 0.9, axis=1)
            res["crps"] = [crps_ensemble(s, o) for s, o in zip(samples, res.obs)]
            preds.append(res)
            print(f"{target} held-out {k}: rhat {d['rhat_max']:.3f}  ess {d['ess_bulk_min']:.0f}  div {d['divergences']}")
        pred = pd.concat(preds, ignore_index=True)
        pred.to_parquet(OUT / f"loyo_{target}.parquet", index=False)
        clim_path = ROOT / "outputs" / "ladder" / target / "climatology.parquet"
        clim = pd.read_parquet(clim_path) if clim_path.exists() else None
        s = summarize(pred, clim)
        s["loyo_diagnostics"] = diags

        full = bayes.fit(rows, model_target(target), MODEL_PREDICTORS, seed=0, **sampler)
        d = bayes.diagnostics(full)
        full["idata"].to_netcdf(OUT / f"full_{target}.nc")
        post = bayes.posterior(full)
        beta = pd.DataFrame(post["beta"], columns=MODEL_PREDICTORS)
        s["full"] = {"rhat_max": d["rhat_max"], "ess_bulk_min": d["ess_bulk_min"], "divergences": d["divergences"],
                     "rows": len(rows), "counties": rows.place_id.nunique(),
                     "beta_mean": beta.mean().round(4).to_dict(),
                     "beta_q05": beta.quantile(0.05).round(4).to_dict(),
                     "beta_q95": beta.quantile(0.95).round(4).to_dict(),
                     "p_beta_positive": (beta > 0).mean().round(4).to_dict(),
                     "sigma_c": float(np.mean(post["sigma_c"])), "sigma_y": float(np.mean(post["sigma_y"]))}
        second = "winter_tavg" if target == "logit" else "gdd_mar1"
        ratio = beta.fall_prcp.abs() / beta[second].abs()
        s["full"][f"p_abs_fall_gt_abs_{second}"] = float((beta.fall_prcp.abs() > beta[second].abs()).mean())
        s["full"][f"ratio_median_fall_over_{second}"] = float(ratio.median())
        # Posterior predictive check on the training rows: the share of observed values inside
        # the 80% interval of replicated data (the model's own springs, so year effects are known).
        import pymc as pm
        with full["model"]:
            ppc = pm.sample_posterior_predictive(full["idata"], random_seed=0, progressbar=False)
        var = "y" if target == "logit" else "obs"
        rep = ppc.posterior_predictive[var].stack(s=("chain", "draw")).values          # rows x draws
        observed = rows.y.values if target == "logit" else rows[target].values
        lo, hi = np.quantile(rep, 0.1, axis=1), np.quantile(rep, 0.9, axis=1)
        s["full"]["ppc_cov80"] = float(((observed >= lo) & (observed <= hi)).mean())
        summary[target] = s
        print(json.dumps({k: v for k, v in s.items() if k != "loyo_diagnostics"}, indent=2, default=str))
        if not args.no_wandb:
            run = wb.init(f"hierarchical-{target}", "loyo", {"model": "hierarchical", "target": target,
                          "features": MODEL_PREDICTORS, "rows_fit": len(rows), **bayes.SAMPLER, **sampler}, group="ladder")
            wb.log_loyo(run, target, pred, {k: v for k, v in s.items() if not isinstance(v, (dict, list))})
            run.summary["full"] = s["full"]
            import wandb
            art = wandb.Artifact(f"hierarchical-{target}", type="model", metadata=s["full"])
            art.add_file(str(OUT / f"full_{target}.nc"))
            run.log_artifact(art)
            summary[target]["wandb_run"] = run.id
            run.finish()
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
