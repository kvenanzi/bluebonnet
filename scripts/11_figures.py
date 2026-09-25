"""Figures for the Part I write-up, from the saved outputs (no network).

Writes docs/post/figures/*.png and docs/post/figures/data.json (the numbers behind each figure).
Run from the repo root:  uv run scripts/11_figures.py [--only name ...]
"""

import argparse
import json
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from bluebonnet import FORECAST_COUNTIES, POOLED, TRAIN_SPRINGS, data

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "post" / "figures"
LADDER, BAYES = ROOT / "outputs" / "ladder", ROOT / "outputs" / "bayes"

# Palette (as in the rxnorm figures): categorical slots in fixed order, light surface.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#8a5cd1"]
SURFACE, INK, INK2, MUTED, GRID, BASELINE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
CODE_COLOR = {0: SERIES[1], 1: SERIES[3], 2: SERIES[0]}
CODE_NAME = {0: "poor", 1: "moderate", 2: "good"}
plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 10, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": BASELINE, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False, "text.color": INK,
    "savefig.dpi": 160, "savefig.bbox": "tight", "savefig.facecolor": SURFACE,
})


def style(ax, axis="y"):
    getattr(ax, f"{axis}axis").grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def title(ax, text):
    ax.set_title(text, loc="left", color=INK, fontsize=11)


def fig_index_codes() -> dict:
    """H1: the pooled index per spring, coloured by the independent code."""
    hyp = json.loads((ROOT / "outputs" / "hypotheses.json").read_text())
    per = hyp["H1_with_2016"]["per_spring"]
    springs = sorted(int(s) for s in per)
    vals = [per[str(s)]["per_1000"] if str(s) in per else per[s]["per_1000"] for s in springs]
    codes = [per[str(s)]["code"] if str(s) in per else per[s]["code"] for s in springs]
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.bar(springs, vals, color=[CODE_COLOR[c] for c in codes], width=0.7)
    for s, v in zip(springs, vals):
        ax.text(s, v + 0.6, f"{v:.1f}", ha="center", color=INK2, fontsize=8.5)
    handles = [plt.Rectangle((0, 0), 1, 1, color=CODE_COLOR[c]) for c in (2, 1, 0)]
    ax.legend(handles, ["coded good", "coded moderate", "coded poor"], frameon=False, loc="upper left", ncol=3, fontsize=8.5)
    ax.set_xticks(springs)
    ax.set_ylabel("bluebonnet records per 1,000 plant records")
    ax.set_ylim(0, max(vals) * 1.25)
    style(ax)
    rho = hyp["H1_primary_2017_2026"]["spearman_rho"]
    title(ax, f"Central Texas index by spring, with independent codes (Spearman ρ = {rho:.2f}, 2017–2026)")
    fig.savefig(OUT / "index_codes.png")
    plt.close(fig)
    return {"springs": springs, "per_1000": vals, "codes": codes, "rho_2017_2026": rho}


def fig_scatter() -> dict:
    """The raw relationship: strength anomaly against fall rain and winter temperature."""
    df = data.load()
    rows = data.training(df, "logit").copy()
    rows["anom"] = rows.logit - rows.groupby("place_id").logit.transform("mean")
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.4), sharey=True)
    out = {}
    for ax, col, lab in zip(axes, ["fall_prcp", "winter_tavg"], ["fall precipitation (z)", "winter mean temperature (z)"]):
        ax.scatter(rows[col], rows.anom, s=12, color=SERIES[0], alpha=0.55, linewidths=0)
        b, a = np.polyfit(rows[col], rows.anom, 1)
        xs = np.linspace(rows[col].min(), rows[col].max(), 50)
        ax.plot(xs, a + b * xs, color=SERIES[1], lw=1.6)
        r = float(np.corrcoef(rows[col], rows.anom)[0, 1])
        ax.text(0.02, 0.95, f"r = {r:.2f}, slope {b:+.2f}", transform=ax.transAxes, va="top", color=INK2, fontsize=9)
        ax.axhline(0, color=BASELINE, lw=0.8)
        ax.set_xlabel(lab)
        style(ax)
        out[col] = {"r": r, "slope": float(b)}
    axes[0].set_ylabel("strength anomaly (logit)")
    title(axes[0], f"All included county-springs (n = {len(rows)})")
    fig.savefig(OUT / "scatter.png")
    plt.close(fig)
    return {**out, "n": int(len(rows))}


def fig_paired() -> dict:
    """H2 and H3: per-spring loss differences with the bootstrap interval."""
    hyp = json.loads((ROOT / "outputs" / "hypotheses.json").read_text())
    fig, axes = plt.subplots(1, 2, figsize=(7.8, 3.4))
    out = {}
    for ax, key, lab, unit in [(axes[0], "H2", "winter temperature − fall rain\n(squared error, strength)", "logit²"),
                               (axes[1], "H3", "fall rain − growing degree days\n(absolute error, timing)", "days")]:
        h = hyp[key]
        per = {int(k): v for k, v in h["per_spring"].items()}
        springs = sorted(per)
        vals = [per[s] for s in springs]
        ax.bar(range(len(springs)), vals, color=[SERIES[0] if v > 0 else SERIES[1] for v in vals], width=0.7)
        ax.axhline(0, color=BASELINE, lw=0.8)
        ax.axhline(h["mean_diff"], color=INK, lw=1.2)
        ax.axhspan(*h["ci95"], color=GRID, alpha=0.7, zorder=0)
        ax.set_xticks(range(len(springs)), [str(s)[2:] for s in springs])
        ax.set_xlabel("held-out spring (20xx)")
        ax.set_ylabel(f"difference ({unit})")
        style(ax)
        lo, hi = h["ci95"]
        ax.set_title(f"{key}: mean {h['mean_diff']:+.3g}, 95% CI {lo:+.3g} to {hi:+.3g}\n{lab}", loc="left", fontsize=9.5, color=INK)
        out[key] = {"per_spring": per, "mean": h["mean_diff"], "ci95": h["ci95"]}
    fig.tight_layout()
    fig.savefig(OUT / "paired.png")
    plt.close(fig)
    return out


LADDER_ORDER = [("climatology", "B0 climatology"), ("persistence", "B1 persistence"), ("ols_fall_prcp", "M1a fall rain"),
                ("ols_second", "M1b second predictor"), ("ridge", "M2 ridge"), ("elastic_net", "M2 elastic net"),
                ("lightgbm", "M3 LightGBM"), ("hierarchical", "M4 hierarchical")]


def fig_ladder() -> dict:
    """H4: CRPS skill relative to climatology for each rung, both targets."""
    summ = json.loads((LADDER / "summary.json").read_text())
    bsum = json.loads((BAYES / "summary.json").read_text())
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.6))   # separate y axes: the M1b label differs
    out = {}
    for ax, target, second, lab in [(axes[0], "logit", "ols_winter_tavg", "strength"), (axes[1], "median_doy", "ols_gdd_mar1", "timing")]:
        names, skills = [], []
        for key, name in LADDER_ORDER:
            k = second if key == "ols_second" else key
            if key == "lightgbm" and f"{target}/lightgbm_best" in summ:
                k = "lightgbm_best"
            s = bsum.get(target) if key == "hierarchical" else summ.get(f"{target}/{k}")
            if s is None:
                continue
            names.append(name.replace("second predictor", "winter temp." if target == "logit" else "GDD to 1 Mar"))
            skills.append(s.get("crps_skill", 0.0))
        y = np.arange(len(names))
        ax.barh(y, skills, color=[SERIES[0] if v > 0 else SERIES[1] for v in skills], height=0.6)
        for yi, v in zip(y, skills):
            ax.text(v + (0.005 if v >= 0 else -0.005), yi, f"{v:+.3f}", va="center", ha="left" if v >= 0 else "right", fontsize=8.5, color=INK2)
        ax.axvline(0, color=BASELINE, lw=0.8)
        ax.set_yticks(y, names)
        ax.invert_yaxis()
        ax.set_xlabel("CRPS skill vs climatology")
        style(ax, "x")
        title(ax, lab)
        lim = max(0.05, max(abs(v) for v in skills) * 1.35)
        ax.set_xlim(-lim, lim)
        out[target] = dict(zip(names, skills))
    fig.tight_layout()
    fig.savefig(OUT / "ladder.png")
    plt.close(fig)
    return out


def fig_coefficients() -> dict:
    """M4 posterior coefficients (90% intervals) for both targets."""
    bsum = json.loads((BAYES / "summary.json").read_text())
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.2))
    out = {}
    for ax, target, lab in [(axes[0], "logit", "strength (logit per SD)"), (axes[1], "median_doy", "timing (days per SD)")]:
        f = bsum[target]["full"]
        names = list(f["beta_mean"])
        y = np.arange(len(names))
        m = [f["beta_mean"][n] for n in names]
        lo = [f["beta_q05"][n] for n in names]
        hi = [f["beta_q95"][n] for n in names]
        ax.hlines(y, lo, hi, color=SERIES[0], lw=2.2)
        ax.plot(m, y, "o", color=INK, ms=4)
        ax.axvline(0, color=BASELINE, lw=0.8)
        ax.set_yticks(y, names if target == "logit" else [""] * len(names))
        ax.invert_yaxis()
        ax.set_xlabel(lab)
        style(ax, "x")
        out[target] = {n: [lo[i], m[i], hi[i]] for i, n in enumerate(names)}
    title(axes[0], "Hierarchical model: posterior mean and 90% interval")
    fig.tight_layout()
    fig.savefig(OUT / "coefficients.png")
    plt.close(fig)
    return out


def fig_forecast(issue: str = "forecast-2026-10") -> dict:
    """The registered forecast against each county's ten observed springs."""
    fc = pd.read_csv(ROOT / "forecasts" / f"{issue}.csv")
    df = data.load()
    counties = list(FORECAST_COUNTIES) + [POOLED]
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8), sharey=True)
    out = {}
    for ax, target, col, lab in [(axes[0], "strength_per_1000", "per_1000", "bluebonnet records per 1,000 plant records"),
                                 (axes[1], "median_doy", "median_doy", "median observation date (day of year)")]:
        rows = fc[fc.target == target].set_index("county")
        for i, c in enumerate(counties):
            hist = df[(df.county == c) & df.spring.isin(TRAIN_SPRINGS)][col].dropna()
            ax.plot(hist, np.full(len(hist), i) + 0.18, "|", color=MUTED, ms=8)
            if c in rows.index:
                r = rows.loc[c]
                ax.hlines(i - 0.1, r.q10, r.q90, color=SERIES[0], lw=2.0)
                ax.hlines(i - 0.1, r.q25, r.q75, color=SERIES[0], lw=5.0)
                ax.plot(r.q50, i - 0.1, "o", color=INK, ms=4)
        ax.set_yticks(range(len(counties)), counties)
        ax.invert_yaxis()
        ax.set_xlabel(lab)
        style(ax, "x")
        out[target] = rows[["q10", "q25", "q50", "q75", "q90", "p_below", "p_near", "p_above"]].round(3).to_dict(orient="index")
    title(axes[0], "Spring 2027 forecast (bars: 50% and 80%) and 2017–2026 springs (ticks)")
    fig.tight_layout()
    fig.savefig(OUT / "forecast.png")
    plt.close(fig)
    return out


FIGURES = {"index_codes": fig_index_codes, "scatter": fig_scatter, "paired": fig_paired, "ladder": fig_ladder,
           "coefficients": fig_coefficients, "forecast": fig_forecast}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "data.json"
    blob = json.loads(path.read_text()) if path.exists() else {}
    for name, fn in FIGURES.items():
        if args.only and name not in args.only:
            continue
        blob[name] = fn()
        print(f"figure {name}")
    path.write_text(json.dumps(blob, indent=2, default=str))


if __name__ == "__main__":
    main()
