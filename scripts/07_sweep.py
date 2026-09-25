"""Register the LightGBM W&B Sweep and, optionally, run an agent for it locally.

A sweep is a search over settings that W&B coordinates: the grid is registered once, then
any number of agents (the Colab notebook, this machine) ask W&B for the next untried cell,
score it, and report back.
  uv run scripts/07_sweep.py --create              # prints the sweep id
  uv run scripts/07_sweep.py --create --smoke      # a one-cell sweep to test the plumbing
  uv run scripts/07_sweep.py --agent <sweep id> [--count N] [--from-artifact]
"""

import argparse
import copy
from pathlib import Path

import wandb
import yaml

from bluebonnet import WANDB_ENTITY, WANDB_PROJECT
from bluebonnet.sweep import run_one

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
    args = ap.parse_args()
    if args.create:
        config = yaml.safe_load(args.config.read_text())
        if args.smoke:
            config = smoke_config(config)
        sweep_id = wandb.sweep(config, entity=WANDB_ENTITY, project=WANDB_PROJECT)
        print(f"\nsweep id: {sweep_id}\nrun an agent: uv run scripts/07_sweep.py --agent {sweep_id}")
    if args.agent:
        wandb.agent(args.agent, function=lambda: run_one(args.from_artifact, ("sweep", "local")),
                    count=args.count, entity=WANDB_ENTITY, project=WANDB_PROJECT)


if __name__ == "__main__":
    main()
