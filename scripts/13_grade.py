"""Grade the registered 2027 forecasts (preregistration §9). Written and committed in
October 2026, before any 2027 data existed; run in May 2027.

  # first add the 2027 City Nature Challenge dates to CNC_DAYS in bluebonnet/__init__.py
  uv run scripts/01_fetch_inat.py --springs 2027      # on or after 15 May 2027
  uv run scripts/13_grade.py

For each issue and each forecast county (and the pooled region), for strength (logit) and
timing (median day of year):
- CRPS of the committed predictive samples against the observed 2027 value;
- CRPS of climatology, the county's ten training values (2017–2026) used as an ensemble;
- skill = 1 - CRPS / CRPS_climatology;
- whether the observation lies inside the committed 80% interval (q10–q90);
- the ranked probability score of the committed tercile probabilities.
An issue is "skilful" if its mean strength skill over the seven counties is positive.
H7 compares the mean 80% interval widths across the three issues.
Writes outputs/grade/grades.csv and outputs/grade/summary.json.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from bluebonnet import FORECAST_COUNTIES, POOLED, TRAIN_SPRINGS
from bluebonnet.stats import crps_ensemble, rps
from bluebonnet.targets import season_table

ROOT = Path(__file__).resolve().parent.parent
FC, OUT = ROOT / "forecasts", ROOT / "outputs" / "grade"
ISSUES = ["forecast-2026-10", "forecast-2026-12", "forecast-2027-03"]
TARGETS = {"strength_logit": "logit", "median_doy": "median_doy"}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    interim = ROOT / "data" / "interim"
    daily = pd.concat([pd.read_parquet(interim / "daily.parquet"), pd.read_parquet(interim / "daily_2027.parquet")])
    seasons = season_table(daily)
    obs27 = seasons[seasons.spring == 2027].set_index("county")
    hist = seasons[seasons.spring.isin(TRAIN_SPRINGS)]
    counties = list(FORECAST_COUNTIES) + [POOLED]
    rows = []
    for issue in ISSUES:
        if not (FC / f"{issue}.csv").exists():
            continue
        fc = pd.read_csv(FC / f"{issue}.csv").set_index(["county", "target"])
        sm = pd.read_parquet(FC / f"{issue}-samples.parquet")
        for county in counties:
            for ft, col in TARGETS.items():
                o = obs27.loc[county, col] if county in obs27.index else np.nan
                if pd.isna(o):
                    continue
                draws = sm[(sm.county == county) & (sm.target == ft)].value.values
                clim = hist[hist.county == county][col].dropna().values
                if len(clim) < 5:
                    clim = hist[hist.county == POOLED][col].dropna().values
                f = fc.loc[(county, ft)]
                cat = 0 if o < f.tercile_lo else (2 if o > f.tercile_hi else 1)
                c, cc = crps_ensemble(draws, o), crps_ensemble(clim, o)
                rows.append({"issue": issue, "county": county, "target": ft, "observed": o,
                             "q10": f.q10, "q50": f.q50, "q90": f.q90, "width80": f.q90 - f.q10,
                             "inside80": bool(f.q10 <= o <= f.q90), "crps": c, "crps_climatology": cc,
                             "skill": 1 - c / cc if cc > 0 else np.nan, "tercile_observed": cat,
                             "rps": rps([f.p_below, f.p_near, f.p_above], cat)})
    g = pd.DataFrame(rows)
    g.to_csv(OUT / "grades.csv", index=False)
    summary = {}
    for issue, d in g.groupby("issue"):
        s7 = d[(d.county != POOLED) & (d.target == "strength_logit")]
        summary[issue] = {"mean_strength_skill_7_counties": float(s7.skill.mean()),
                          "skilful": bool(s7.skill.mean() > 0),
                          "inside80_share": float(d.inside80.mean()),
                          "mean_rps": float(d.rps.mean()),
                          "mean_width80": d[d.county != POOLED].groupby("target").width80.mean().to_dict()}
    w = {i: summary[i]["mean_width80"] for i in summary}
    if all(i in w for i in ISSUES):
        oct_, dec, mar = (w[i] for i in ISSUES)
        summary["H7"] = {
            "strength_narrowing_oct_to_dec": oct_["strength_logit"] - dec["strength_logit"],
            "strength_narrowing_dec_to_mar": dec["strength_logit"] - mar["strength_logit"],
            "timing_narrowing_oct_to_dec": oct_["median_doy"] - dec["median_doy"],
            "timing_narrowing_dec_to_mar": dec["median_doy"] - mar["median_doy"]}
        h = summary["H7"]
        summary["H7"]["supported"] = bool(h["strength_narrowing_oct_to_dec"] > h["strength_narrowing_dec_to_mar"]
                                          and h["timing_narrowing_dec_to_mar"] > h["timing_narrowing_oct_to_dec"])
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print(g.round(3).to_string())
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
