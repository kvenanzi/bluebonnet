"""Load the county-spring table, from disk or from the W&B dataset artifact (Colab)."""

from pathlib import Path

import pandas as pd

from . import DATASET_ARTIFACT, TRAIN_SPRINGS, WANDB_ENTITY, WANDB_PROJECT

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"


def load(from_artifact: bool = False, version: str = "latest") -> pd.DataFrame:
    if from_artifact:
        import wandb
        api = wandb.Api()
        art = api.artifact(f"{WANDB_ENTITY}/{WANDB_PROJECT}/{DATASET_ARTIFACT}:{version}")
        path = Path(art.download(root=str(ROOT / "artifacts" / DATASET_ARTIFACT)))
        return pd.read_parquet(path / "seasons.parquet")
    return pd.read_parquet(PROCESSED / "seasons.parquet")


def training(df: pd.DataFrame, target: str) -> pd.DataFrame:
    """Rows a point model is trained and scored on: included counties, training springs,
    and the per-target record threshold (preregistration §3–4)."""
    d = df[df.included.fillna(False).astype(bool) & df.spring.isin(TRAIN_SPRINGS)]
    return d[d.point_ok] if target == "logit" else d[d.timing_ok & d.median_doy.notna()]
