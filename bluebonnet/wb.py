"""Weights & Biases helpers: one run per (model, target) evaluation, with the config,
the LOYO summary, and the per-row held-out predictions as a table."""

import os
from pathlib import Path

import pandas as pd

from . import DATASET_ARTIFACT, WANDB_ENTITY, WANDB_PROJECT

ROOT = Path(__file__).resolve().parent.parent


def enabled() -> bool:
    return os.environ.get("WANDB_MODE") != "disabled"


def init(name: str, job_type: str, config: dict, group: str | None = None, tags=None):
    import wandb
    run = wandb.init(entity=WANDB_ENTITY, project=WANDB_PROJECT, name=name, job_type=job_type,
                     config=config, group=group, tags=tags or [], reinit="finish_previous")
    try:
        run.use_artifact(f"{DATASET_ARTIFACT}:latest")        # lineage: which data this run read
    except Exception:
        pass
    return run


def log_loyo(run, target: str, pred: pd.DataFrame, summary: dict) -> None:
    import wandb
    for k, v in summary.items():
        run.summary[f"{target}/{k}"] = v
    cols = [c for c in ["county", "spring", "obs", "pred", "lo80", "hi80", "crps"] if c in pred]
    run.log({f"{target}/loyo_predictions": wandb.Table(dataframe=pred[cols].round(4))})
    per = pred.assign(se=(pred.pred - pred.obs) ** 2).groupby("spring").se.mean().reset_index()
    run.log({f"{target}/mse_by_spring": wandb.Table(dataframe=per.round(5))})
