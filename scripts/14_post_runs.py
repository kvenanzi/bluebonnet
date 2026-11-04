# /// script
# requires-python = ">=3.10"
# dependencies = ["plotly>=5.24"]
# ///
"""Run records and the interactive sweep chart for docs/post/, from the local W&B export.

    uv run scripts/14_post_runs.py [--export wandb-export/bluebonnet-bloom]

Writes:
  docs/post/figures/runs.json         every W&B run of the project: id, name, job type, group,
                                      sweep, tags, created time, config, final summary
  docs/post/figures/sweep_lgbm.html   the 24-cell LightGBM sweep as parallel coordinates

The export is written by wandb_export.py and is not committed; the files above are.
"""

import argparse
import json
import math
import re
from pathlib import Path

import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/post/figures"
SWEEP_ID = "46na5ws9"
SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
FONT = dict(family="system-ui, -apple-system, Segoe UI, sans-serif", size=13, color=INK)
SECRET = re.compile(r"token|secret|password|api_key|apikey", re.I)
DROP_SUMMARY = ("_wandb", "_runtime", "_timestamp", "_step")


def clean(v):
    if isinstance(v, float):
        return None if math.isnan(v) or math.isinf(v) else round(v, 6)
    if isinstance(v, dict):
        if str(v.get("_type", "")).endswith("-file"):
            return {"file": v.get("path")}
        return {k: clean(x) for k, x in v.items() if not SECRET.search(k)}
    if isinstance(v, list):
        return [clean(x) for x in v]
    return v


def load_runs(export: Path) -> list[dict]:
    runs = []
    for row in json.loads((export / "runs.json").read_text()):
        r = json.loads((export / "runs" / row["id"] / "run.json").read_text())
        config = {k: (v["value"] if isinstance(v, dict) and "value" in v else v)
                  for k, v in r["config"].items()}
        config = {k: v for k, v in config.items()
                  if not k.startswith("_") and not SECRET.search(k) and v not in (None, [], {})}
        summary = {k: v for k, v in r["summary"].items() if not k.startswith(DROP_SUMMARY)}
        runs.append({k: r.get(k) for k in ("id", "name", "group", "job_type", "state", "sweep",
                                           "tags", "notes", "created_at")}
                    | {"config": clean(config), "summary": clean(summary)})
    return sorted(runs, key=lambda r: r["created_at"] or "")


def sweep_chart(runs):
    rows = [r for r in runs if r["sweep"] == SWEEP_ID]
    assert len(rows) == 24, len(rows)
    params = [("learning_rate", "learning rate"), ("n_estimators", "trees"),
              ("min_child_samples", "min. rows per leaf"), ("num_leaves", "max. leaves")]
    dims = []
    for key, label in params:
        levels = sorted({r["config"][key] for r in rows})
        dims.append(dict(label=label, values=[levels.index(r["config"][key]) for r in rows],
                         tickvals=list(range(len(levels))), ticktext=[f"{v:g}" for v in levels],
                         range=[-0.3, len(levels) - 0.7]))
    strength = [r["summary"]["logit/rmse"] for r in rows]
    timing = [r["summary"]["median_doy/rmse"] for r in rows]
    # Lower RMSE is better, so the score axes run downward: the best cells sit at the top.
    dims += [dict(label="strength RMSE (logit)", values=strength, tickformat=".2f",
                  range=[max(strength) + 0.01, min(strength) - 0.01]),
             dict(label="timing RMSE (days)", values=timing, tickformat=".1f",
                  range=[max(timing) + 0.1, min(timing) - 0.1])]
    fig = go.Figure(go.Parcoords(
        dimensions=dims, labelfont=dict(size=13, color=INK), tickfont=dict(size=12, color=INK2),
        rangefont=dict(size=1, color=SURFACE),
        line=dict(color=strength, colorscale=[[0, "#123f80"], [1, "#a9c8ee"]], showscale=True,
                  colorbar=dict(title="strength<br>RMSE", thickness=12, tickformat=".2f"))))
    fig.update_layout(template="simple_white", paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
                      font=FONT, height=440, margin=dict(l=60, r=40, t=60, b=30))
    path = OUT / "sweep_lgbm.html"
    small, wide = {"margin.l": 40, "margin.r": 10}, {"margin.l": 60, "margin.r": 40}
    script = (f"var gd=document.getElementById('{{plot_id}}');var S={json.dumps(small)},"
              f"W={json.dumps(wide)};function fit(){{Plotly.relayout(gd,window.innerWidth<600?S:W);}}"
              "fit();window.addEventListener('resize',fit);")
    fig.write_html(path, include_plotlyjs="cdn", full_html=True, post_script=script,
                   config={"displaylogo": False, "responsive": True})
    # Shown in an iframe on the blog: no body margin, and the figures' surface colour.
    html = path.read_text().replace(
        "<head>", f"<head><style>html,body{{margin:0;background:{SURFACE}}}</style>", 1)
    path.write_text(html)
    print("wrote", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", type=Path, default=ROOT / "wandb-export/bluebonnet-bloom")
    args = ap.parse_args()
    runs = load_runs(args.export)
    meta = json.loads((args.export / "export.json").read_text())
    doc = {"source": f"W&B project {meta['project']}, exported {meta['exported_at']}",
           "n_runs": len(runs), "runs": runs}
    (OUT / "runs.json").write_text(json.dumps(doc, indent=1))
    print("wrote", OUT / "runs.json", f"({len(runs)} runs)")
    sweep_chart(runs)


if __name__ == "__main__":
    main()
