"""One LightGBM sweep trial: read the hyper-parameters W&B assigned, score them by LOYO on
both targets, log the summaries. Shared by scripts/07_sweep.py and the Colab notebook."""

import wandb

from . import WANDB_ENTITY, WANDB_PROJECT, data, models
from .eval import loyo, summarize
from .features import PREDICTORS

KEYS = ["num_leaves", "learning_rate", "n_estimators", "min_child_samples"]


def run_one(from_artifact: bool = False, tags=("sweep",)) -> None:
    run = wandb.init(entity=WANDB_ENTITY, project=WANDB_PROJECT, job_type="sweep", tags=list(tags))
    params = {k: run.config[k] for k in KEYS if k in run.config}
    df = data.load(from_artifact=from_artifact)
    for target in ["logit", "median_doy"]:
        rows = data.training(df, target)
        clim = loyo(models.Climatology(), rows, target)
        pred = loyo(models.lightgbm(PREDICTORS, params), rows, target)
        for k, v in summarize(pred, clim).items():
            run.summary[f"{target}/{k}"] = v
    run.finish()
