"""Apply the pre-registered decision rules (preregistration §6) to the saved predictions.

Reads outputs/ladder/, outputs/bayes/, docs/bloom-year-codes.md; writes outputs/hypotheses.json
and logs one W&B run (job_type "analysis"). Sensitivity analyses are reported alongside and
never change a verdict.
Run from the repo root:  uv run scripts/06_hypotheses.py [--no-wandb]
"""

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from bluebonnet import POOLED, TRAIN_SPRINGS, data, models, wb
from bluebonnet.eval import loyo, per_spring_loss, summarize
from bluebonnet.features import PREDICTORS
from bluebonnet.stats import bootstrap_mean_ci

ROOT = Path(__file__).resolve().parent.parent
LADDER, BAYES = ROOT / "outputs" / "ladder", ROOT / "outputs" / "bayes"
CODE = {"poor": 0, "moderate": 1, "good": 2}


def codes() -> dict[int, int]:
    text = (ROOT / "docs" / "bloom-year-codes.md").read_text()
    return {int(y): CODE[c] for y, c in re.findall(r"^\| (\d{4}) \| (poor|moderate|good) \(", text, re.M)}


def paired(a: pd.DataFrame, b: pd.DataFrame, kind: str) -> dict:
    """Mean over springs of loss(b) - loss(a): positive means a is better."""
    la, lb = per_spring_loss(a, kind), per_spring_loss(b, kind)
    diff = (lb - la).dropna()
    m, lo, hi = bootstrap_mean_ci(diff.values)
    return {"mean_diff": m, "ci95": [lo, hi], "springs_a_better": int((diff > 0).sum()), "n_springs": int(len(diff)),
            "per_spring": diff.round(5).to_dict(), "loss_a": float(la.mean()), "loss_b": float(lb.mean())}


def verdict(p: dict, a: str, b: str) -> str:
    lo, hi = p["ci95"]
    if lo > 0:
        return f"supported ({a} better)"
    if hi < 0:
        return f"reversed ({b} better)"
    return "not distinguishable at n = 10 springs"


def rd(name, target):
    return pd.read_parquet(LADDER / target / f"{name}.parquet")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-wandb", action="store_true")
    args = ap.parse_args()
    df = data.load()
    out = {}

    # H1: pooled Central Texas index against the independent codes.
    c = codes()
    pooled = df[(df.county == POOLED)].set_index("spring")
    for label, springs in [("primary_2017_2026", TRAIN_SPRINGS), ("with_2016", [2016] + TRAIN_SPRINGS)]:
        s = [t for t in springs if t in c and t in pooled.index]
        rho = spearmanr(pooled.loc[s, "logit"], [c[t] for t in s]).statistic
        lowest = pooled.loc[s, "logit"].nsmallest(2).index.tolist()
        ok = bool(rho > 0.5 and all(c[t] <= 1 for t in lowest))
        out[f"H1_{label}"] = {"spearman_rho": float(rho), "lowest_two": lowest,
                              "codes_of_lowest": [c[t] for t in lowest], "supported": ok,
                              "per_spring": {int(t): {"logit": round(float(pooled.loc[t, "logit"]), 4),
                                                      "per_1000": round(float(pooled.loc[t, "per_1000"]), 2),
                                                      "code": c[t]} for t in s}}
    # Sensitivity: the same with only Flowering-annotated records in the numerator.
    from bluebonnet.targets import empirical_logit
    fl = empirical_logit(pooled.loc[TRAIN_SPRINGS, "y_flowering"], pooled.loc[TRAIN_SPRINGS, "n"])
    out["H1_sensitivity_flowering_annotation"] = {
        "spearman_rho": float(spearmanr(fl, [c[t] for t in TRAIN_SPRINGS]).statistic),
        "rho_with_all_records_index": float(spearmanr(fl, pooled.loc[TRAIN_SPRINGS, "logit"]).statistic)}

    # H2: fall precipitation vs winter temperature, strength, squared error.
    h2 = paired(rd("ols_fall_prcp", "logit"), rd("ols_winter_tavg", "logit"), "se")
    h2["verdict"] = verdict(h2, "fall_prcp", "winter_tavg")
    bsum = json.loads((BAYES / "summary.json").read_text()) if (BAYES / "summary.json").exists() else {}
    if "logit" in bsum:
        h2["hierarchical_p_abs_fall_gt_abs_winter_tavg"] = bsum["logit"]["full"]["p_abs_fall_gt_abs_winter_tavg"]
        h2["hierarchical_beta"] = {k: bsum["logit"]["full"][k] for k in ["beta_mean", "beta_q05", "beta_q95", "p_beta_positive"]}
    # Each single predictor against climatology (is either one useful at all?).
    clim = rd("climatology", "logit")
    h2["fall_vs_climatology"] = paired(rd("ols_fall_prcp", "logit"), clim, "se")
    h2["winter_vs_climatology"] = paired(rd("ols_winter_tavg", "logit"), clim, "se")
    out["H2"] = h2

    # H3: growing degree days vs fall precipitation, timing, absolute error.
    h3 = paired(rd("ols_gdd_mar1", "median_doy"), rd("ols_fall_prcp", "median_doy"), "ae")
    h3["verdict"] = verdict(h3, "gdd_mar1", "fall_prcp")
    h3["gdd_vs_climatology"] = paired(rd("ols_gdd_mar1", "median_doy"), rd("climatology", "median_doy"), "ae")
    if "median_doy" in bsum:
        h3["hierarchical_p_abs_fall_gt_abs_gdd"] = bsum["median_doy"]["full"]["p_abs_fall_gt_abs_gdd_mar1"]
        h3["hierarchical_beta"] = {k: bsum["median_doy"]["full"][k] for k in ["beta_mean", "beta_q05", "beta_q95", "p_beta_positive"]}
    out["H3"] = h3

    # H4 and H6: the ladder.
    summ = json.loads((LADDER / "summary.json").read_text())
    for target in ["logit", "median_doy"]:
        lg = "lightgbm_best" if f"{target}/lightgbm_best" in summ else "lightgbm"
        rid, lgb = summ[f"{target}/ridge"], summ[f"{target}/{lg}"]
        h4 = {"ridge_rmse": rid["rmse"], "lightgbm_rmse": lgb["rmse"], "lightgbm_variant": lg,
              "lightgbm_not_better": lgb["rmse"] >= rid["rmse"]}
        if target in bsum:
            m4 = bsum[target]["rmse"]
            h4.update({"hierarchical_rmse": m4, "hierarchical_within_5pct": m4 <= 1.05 * min(rid["rmse"], lgb["rmse"])})
            h4["supported"] = bool(h4["lightgbm_not_better"] and h4["hierarchical_within_5pct"])
        out[f"H4_{target}"] = h4
        cov = {"ridge": rid["cov80"], lg: lgb["cov80"]}
        if target in bsum:
            cov["hierarchical"] = bsum[target]["cov80"]
        out[f"H6_{target}"] = {"cov80": cov, "all_within_70_90": all(0.7 <= v <= 0.9 for v in cov.values())}

    # H5: thin counties, hierarchical vs per-county OLS.
    rows = data.training(df, "logit")
    med = df[df.included.fillna(False).astype(bool) & df.spring.isin(TRAIN_SPRINGS)].groupby("place_id").y.median()
    thin = set(med[med < 50].index)
    pc = rd("per_county_fall_prcp", "logit")
    h5 = {"thin_counties": sorted(df[df.place_id.isin(thin)].county.unique().tolist())}
    if (BAYES / "loyo_logit.parquet").exists():
        m4 = pd.read_parquet(BAYES / "loyo_logit.parquet")
        rm = lambda p: float(np.sqrt(np.mean((p.pred - p.obs) ** 2)))
        h5.update({"hierarchical_rmse_thin": rm(m4[m4.place_id.isin(thin)]), "per_county_rmse_thin": rm(pc[pc.place_id.isin(thin)]),
                   "n_rows_thin": int(pc.place_id.isin(thin).sum())})
        h5["supported"] = h5["hierarchical_rmse_thin"] < h5["per_county_rmse_thin"]
    out["H5"] = h5

    # Sensitivity: every fall window, and 2016 added (eleven springs), for H2.
    sens = {}
    for w in ["sepoct_prcp", "octdec_prcp", "winter_prcp", "summer_pdsi", "freeze_days", "gdd_mar1"]:
        p = loyo(models.ols(w, [w]), rows, "logit", intervals=False)
        sens[f"ols_{w}_mse"] = float(per_spring_loss(p).mean())
    sens["ols_fall_prcp_mse"] = h2["loss_a"]
    sens["ols_winter_tavg_mse"] = h2["loss_b"]
    sens["climatology_mse"] = float(per_spring_loss(clim).mean())
    springs11 = [2016] + TRAIN_SPRINGS
    d11 = df[df.included.fillna(False).astype(bool) & df.spring.isin(springs11) & df.point_ok]
    a = loyo(models.ols("fall", ["fall_prcp"]), d11, "logit", springs=springs11, intervals=False)
    b = loyo(models.ols("winter", ["winter_tavg"]), d11, "logit", springs=springs11, intervals=False)
    sens["H2_with_2016"] = {k: v for k, v in paired(a, b, "se").items() if k != "per_spring"}
    out["sensitivity"] = sens

    (ROOT / "outputs" / "hypotheses.json").write_text(json.dumps(out, indent=2, default=str))
    print(json.dumps(out, indent=2, default=str))
    if not args.no_wandb:
        run = wb.init("hypotheses", "analysis", {"bootstrap": 10_000}, group="analysis")
        flat = pd.json_normalize(out, sep="/").iloc[0].to_dict()
        for k, v in flat.items():
            if isinstance(v, (int, float, bool, str)):
                run.summary[k] = v
        run.finish()


if __name__ == "__main__":
    main()
