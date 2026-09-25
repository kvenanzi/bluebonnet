"""Log data/processed/ as the W&B dataset artifact `bluebonnet-seasons`.

An artifact is a versioned, content-addressed file bundle in W&B. Every later run declares
it as input, so each result in the project is linked to the exact table it was computed from,
and the Colab notebook downloads the same bytes the local scripts read.
Run from the repo root:  uv run scripts/04_upload_dataset.py
"""

import json
from pathlib import Path

import wandb

from bluebonnet import DATASET_ARTIFACT, WANDB_ENTITY, WANDB_PROJECT

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"


def main() -> None:
    manifest = json.loads((PROCESSED / "manifest.json").read_text())
    run = wandb.init(entity=WANDB_ENTITY, project=WANDB_PROJECT, job_type="dataset", name="upload-seasons")
    meta = {k: v for k, v in manifest.items() if not isinstance(v, dict)}
    art = wandb.Artifact(DATASET_ARTIFACT, type="dataset", metadata={**meta, **manifest["weather_sources"]},
                         description="County-spring bloom targets (iNaturalist) and weather predictors (NOAA), 2016–2026.")
    art.add_file(str(PROCESSED / "seasons.parquet"))
    art.add_file(str(PROCESSED / "manifest.json"))
    run.log_artifact(art)
    run.finish()


if __name__ == "__main__":
    main()
