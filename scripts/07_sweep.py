"""Register the LightGBM W&B Sweep and, optionally, run an agent for it locally.

A sweep is a search over settings that W&B coordinates: the grid is registered once, then
any number of agents (the Colab notebook, this machine) ask W&B for the next untried cell,
score it, and report back.
  uv run scripts/07_sweep.py --create              # prints the sweep id
  uv run scripts/07_sweep.py --create --smoke      # a one-cell sweep to test the plumbing
  uv run scripts/07_sweep.py --agent <sweep id> [--count N] [--from-artifact]
  uv run scripts/07_sweep.py --best <sweep id>     # pick the cell with the lowest logit/rmse, score it
                                                   # on the ladder as `lightgbm_best`
"""

import argparse
import copy
import json
from pathlib import Path

import wandb
import yaml

from bluebonnet import WANDB_ENTITY, WANDB_PROJECT
from bluebonnet.sweep import KEYS, run_one

ROOT = Path(__file__).resolve().parent.parent


def smoke_config(config: dict) -> dict:
    out = copy.deepcopy(config)
    for name, spec in out["parameters"].items():
        if "values" in spec:
            out["parameters"][name] = {"value": spec["values"][0]}
    out["name"] = f"smoke-{config.get('name', 'sweep')}"
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--create", action="store_true")
    ap.add_argument("--config", type=Path, default=ROOT / "sweeps" / "lgbm.yaml")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--agent", metavar="SWEEP_ID")
    ap.add_argument("--count", type=int)
    ap.add_argument("--from-artifact", action="store_true")
    ap.add_argument("--best", metavar="SWEEP_ID")
    args = ap.parse_args()
    if args.best:
        best(args.best)
        return
    if args.create:
        config = yaml.safe_load(args.config.read_text())
        if args.smoke:
            config = smoke_config(config)
        sweep_id = wandb.sweep(config, entity=WANDB_ENTITY, project=WANDB_PROJECT)
        print(f"\nsweep id: {sweep_id}\nrun an agent: uv run scripts/07_sweep.py --agent {sweep_id}")
    if args.agent:
        wandb.agent(args.agent, function=lambda: run_one(args.from_artifact, ("sweep", "local")),
                    count=args.count, entity=WANDB_ENTITY, project=WANDB_PROJECT)


def best(sweep_id: str) -> None:
    """Choose the sweep cell by its LOYO strength RMSE, then score it like every other rung."""
    from bluebonnet import data, models, wb
    from bluebonnet.eval import loyo, summarize
    from bluebonnet.features import PREDICTORS
    import pandas as pd
    runs = wandb.Api().sweep(f"{WANDB_ENTITY}/{WANDB_PROJECT}/{sweep_id}").runs
    done = [r for r in runs if r.state == "finished" and "logit/rmse" in r.summary]
    top = min(done, key=lambda r: r.summary["logit/rmse"])
    params = {k: top.config[k] for k in KEYS}
    table = sorted(({**{k: r.config[k] for k in KEYS}, "logit_rmse": r.summary["logit/rmse"],
                     "median_doy_rmse": r.summary.get("median_doy/rmse")} for r in done), key=lambda d: d["logit_rmse"])
    out = {"sweep_id": sweep_id, "cells": len(done), "best_run": top.id, "params": params, "cells_sorted": table}
    (ROOT / "outputs" / "sweep_best.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({k: v for k, v in out.items() if k != "cells_sorted"}, indent=2))
    df = data.load()
    ladder = ROOT / "outputs" / "ladder"
    summary = json.loads((ladder / "summary.json").read_text())
    for target in ["logit", "median_doy"]:
        rows = data.training(df, target)
        clim = pd.read_parquet(ladder / target / "climatology.parquet")
        pred = loyo(models.lightgbm(PREDICTORS, params), rows, target)
        s = summarize(pred, clim)
        pred.to_parquet(ladder / target / "lightgbm_best.parquet", index=False)
        run = wb.init(f"lightgbm_best-{target}", "loyo", {"model": "lightgbm_best", "target": target,
                      "sweep": sweep_id, **params}, group="ladder")
        wb.log_loyo(run, target, pred, s)
        s["wandb_run"] = run.id
        run.finish()
        summary[f"{target}/lightgbm_best"] = {**s, "params": params}
        print(target, {k: round(v, 4) for k, v in s.items() if isinstance(v, float)})
    (ladder / "summary.json").write_text(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
