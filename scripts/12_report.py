"""Build the W&B Report for Part I, with live panels bound to the runs.

Panels: CRPS skill against climatology for every rung (both targets), a run comparer, the
LightGBM sweep's parallel coordinates, and the registered forecast table. The prose is kept
short; the write-up is the full account. Prints the report URL.
Run from the repo root:  uv run scripts/12_report.py
"""

import json
from pathlib import Path

import wandb_workspaces.reports.v2 as wr

from bluebonnet import WANDB_ENTITY as ENTITY, WANDB_PROJECT as PROJECT

ROOT = Path(__file__).resolve().parent.parent
TITLE = "Texas bluebonnet bloom: fall rain, winter warmth, and a registered forecast for 2027"
GITHUB = "https://github.com/kvenanzi/bluebonnet"
W = 24


def ids_filter(ids) -> str:
    return "ID in [" + ", ".join(f"'{i}'" for i in ids) + "]"


def main() -> None:
    ladder = json.loads((ROOT / "outputs" / "ladder" / "summary.json").read_text())
    bayes = json.loads((ROOT / "outputs" / "bayes" / "summary.json").read_text())
    hyp = json.loads((ROOT / "outputs" / "hypotheses.json").read_text())
    sweep = json.loads((ROOT / "outputs" / "sweep_best.json").read_text())
    runs = {t: [v["wandb_run"] for k, v in ladder.items() if k.startswith(t + "/") and "wandb_run" in v]
            + [bayes[t]["wandb_run"]] for t in ["logit", "median_doy"]}
    strength = wr.Runset(entity=ENTITY, project=PROJECT, name="Ladder, strength", filters=ids_filter(runs["logit"]))
    timing = wr.Runset(entity=ENTITY, project=PROJECT, name="Ladder, timing", filters=ids_filter(runs["median_doy"]))
    sweep_rs = wr.Runset(entity=ENTITY, project=PROJECT, name=f"LightGBM sweep ({sweep['cells']} cells)",
                         filters=f"Metric('Sweep') == '{sweep['sweep_id']}'")
    forecast = wr.Runset(entity=ENTITY, project=PROJECT, name="Registered forecasts", filters="Config('issue') == 'forecast-2026-10'")
    h2, h3 = hyp["H2"], hyp["H3"]
    blocks = [
        wr.TableOfContents(),
        wr.H1("The question"),
        wr.P("Texas wildflower forecasts attribute a good bluebonnet year to fall rain and treat winter temperature as a "
             "matter of timing. This project measures bloom strength and timing per county from iNaturalist records "
             "(bluebonnet records per plant record, 1 February–30 April, 2017–2026), tests that claim with "
             "pre-registered hypotheses and leave-one-year-out cross-validation, and registers a forecast for spring 2027."),
        wr.P([wr.Link(text="Code, pre-registration, and forecasts on GitHub", url=GITHUB)]),
        wr.H1("Verdicts"),
        wr.MarkdownBlock(
            "| | Prediction | Outcome |\n|---|---|---|\n"
            f"| H1 | the effort-normalized index agrees with independent reports | Spearman ρ = {hyp['H1_primary_2017_2026']['spearman_rho']:.2f}; supported |\n"
            f"| H2 | fall rain predicts strength better than winter temperature | mean MSE difference {h2['mean_diff']:+.3f} (95% CI {h2['ci95'][0]:+.3f} to {h2['ci95'][1]:+.3f}); not distinguishable |\n"
            f"| H3 | growing degree days predict timing better than fall rain | {h3['mean_diff']:+.2f} days MAE (95% CI {h3['ci95'][0]:+.2f} to {h3['ci95'][1]:+.2f}); supported |\n"
            "| H4 | LightGBM does not beat ridge; hierarchical within 5% | strength: not supported; timing: supported |\n"
            "| H5 | partial pooling helps thin counties | not supported |\n"
            "| H6 | 80% intervals cover 70–90% | coverage 0.88–0.92; not met by every model |\n"),
        wr.H1("The ladder: strength"),
        wr.P("CRPS skill is 1 − CRPS(model) / CRPS(climatology) on held-out springs; below zero is worse than predicting "
             "each county's usual value. No model predicts county bloom strength better than climatology."),
        wr.PanelGrid(runsets=[strength], panels=[
            wr.BarPlot(title="Strength: CRPS skill vs climatology", metrics=["logit/crps_skill"], layout=wr.Layout(x=0, y=0, w=W // 2, h=9)),
            wr.BarPlot(title="Strength: 80% interval coverage", metrics=["logit/cov80"], layout=wr.Layout(x=W // 2, y=0, w=W // 2, h=9)),
            wr.RunComparer(diff_only=True, layout=wr.Layout(x=0, y=9, w=W, h=10)),
        ]),
        wr.H1("The ladder: timing"),
        wr.P("Winter warmth moves the median observation date: growing degree days to 1 March alone improve on climatology "
             "by about 11% in CRPS, and so does the hierarchical model."),
        wr.PanelGrid(runsets=[timing], panels=[
            wr.BarPlot(title="Timing: CRPS skill vs climatology", metrics=["median_doy/crps_skill"], layout=wr.Layout(x=0, y=0, w=W // 2, h=9)),
            wr.BarPlot(title="Timing: MAE (days)", metrics=["median_doy/mae"], layout=wr.Layout(x=W // 2, y=0, w=W // 2, h=9)),
        ]),
        wr.H1("LightGBM sweep"),
        wr.P("24 cells, each scored by leave-one-year-out. The best cell is the smallest model in the grid (3 leaves, "
             "learning rate 0.03, 100 trees, 30 rows per leaf), the configuration closest to predicting no change."),
        wr.PanelGrid(runsets=[sweep_rs], panels=[
            wr.ParallelCoordinatesPlot(title="Sweep", columns=[
                wr.ParallelCoordinatesPlotColumn(metric=wr.Config("num_leaves")),
                wr.ParallelCoordinatesPlotColumn(metric=wr.Config("learning_rate")),
                wr.ParallelCoordinatesPlotColumn(metric=wr.Config("n_estimators")),
                wr.ParallelCoordinatesPlotColumn(metric=wr.Config("min_child_samples")),
                wr.ParallelCoordinatesPlotColumn(metric=wr.SummaryMetric("logit/rmse")),
            ], layout=wr.Layout(x=0, y=0, w=W, h=10)),
        ]),
        wr.H1("The registered forecast for spring 2027"),
        wr.P("Issued 25 September 2026 from the hierarchical model, with every September–February month drawn from 26 "
             "El Niño analog seasons since 1951. The CSV, its samples, and its SHA-256 are in the W&B artifact "
             "bluebonnet-forecast:forecast-2026-10 and in the repository at tag forecast-2026-10. Updates follow in "
             "December and March; grading in May 2027."),
        wr.PanelGrid(runsets=[forecast], panels=[wr.RunComparer(layout=wr.Layout(x=0, y=0, w=W, h=6))]),
    ]
    report = wr.Report(entity=ENTITY, project=PROJECT, title=TITLE,
                       description="Pre-registered test of fall rain against winter temperature, and a registered forecast.",
                       blocks=blocks)
    report.save()
    print(report.url)
    (ROOT / "outputs" / "report_url.txt").write_text(report.url)


if __name__ == "__main__":
    main()
