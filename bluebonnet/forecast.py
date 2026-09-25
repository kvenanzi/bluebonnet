"""The registered forecast for spring 2027 (preregistration §8).

Months not yet observed are filled from whole analog seasons: the springs since 1951 that
followed an El Niño fall (Oceanic Niño Index for October–December >= +0.5 °C). One analog
year is drawn per posterior draw and used for every county, so the scenario keeps the
spatial pattern of that year's weather as well as the correlation between its months.
"""

import numpy as np
import pandas as pd

from . import FORECAST_COUNTIES, POOLED
from .targets import empirical_logit

QUANTILES = {"q10": 0.10, "q25": 0.25, "q50": 0.50, "q75": 0.75, "q90": 0.90}


def analog_springs(oni: pd.DataFrame, first: int = 1951, last: int = 2026, threshold: float = 0.5) -> list[int]:
    ond = oni[oni.season == "OND"].set_index("year").anom
    return [s for s in range(first, last + 1) if ond.get(s - 1, np.nan) >= threshold]


def scenarios(z: pd.DataFrame, place_ids: list[int], observed: dict[int, dict], predictors: list[str],
              analogs: list[int], fips_of: dict[int, str]) -> dict[int, pd.DataFrame]:
    """For each analog spring, a table (one row per county) of 2027 predictors: observed
    values where given, the analog spring's z-scores otherwise."""
    zi = z.set_index(["fips", "spring"])
    out = {}
    for a in analogs:
        rows = []
        for pid in place_ids:
            vals = {p: zi.loc[(fips_of[pid], a), p] for p in predictors}
            vals.update({p: v for p, v in observed.get(pid, {}).items() if not pd.isna(v)})
            rows.append({"place_id": pid, **vals})
        out[a] = pd.DataFrame(rows)
    return out


def terciles(values) -> tuple[float, float]:
    v = np.asarray(values, float)
    v = v[~np.isnan(v)]
    return float(np.quantile(v, 1 / 3)), float(np.quantile(v, 2 / 3))


def summarize_samples(samples: np.ndarray, lo_hi: tuple[float, float]) -> dict:
    s = samples[~np.isnan(samples)]
    out = {k: float(np.quantile(s, q)) for k, q in QUANTILES.items()}
    lo, hi = lo_hi
    out.update({"tercile_lo": lo, "tercile_hi": hi, "p_below": float((s < lo).mean()),
                "p_near": float(((s >= lo) & (s <= hi)).mean()), "p_above": float((s > hi).mean())})
    return out


def simulate(post: dict, fitted_counties: list[int], features: list[str], scen: dict[int, pd.DataFrame],
             target: str, n_by_county: dict[int, int] | None = None, seed: int = 2027) -> dict[int, np.ndarray]:
    """Posterior predictive samples per county for one new spring. Each draw uses one analog
    (cycled so every analog is used equally), one year effect shared by all counties, and a
    new county effect for a county the model was not fit on."""
    rng = np.random.default_rng(seed)
    S = len(post["alpha"])
    analogs = sorted(scen)
    pick = np.array([analogs[i % len(analogs)] for i in rng.permutation(S)])
    b = rng.normal(0, post["sigma_y"])                                     # one per draw
    lookup = {c: i for i, c in enumerate(fitted_counties)}
    pids = scen[analogs[0]].place_id.tolist()
    X = np.stack([scen[a].set_index("place_id").loc[pids, features].fillna(0.0).values for a in analogs])  # A x C x F
    aidx = np.array([analogs.index(a) for a in pick])
    out = {}
    for j, pid in enumerate(pids):
        a = post["a"][:, lookup[pid]] if pid in lookup else rng.normal(0, post["sigma_c"])
        eta = post["alpha"] + a + b + np.einsum("sf,sf->s", X[aidx, j, :], post["beta"])
        if target == "strength":
            mu = 1 / (1 + np.exp(-eta))
            phi = post["phi"]
            p = rng.beta(mu * phi, (1 - mu) * phi)
            n = int(n_by_county[pid])
            out[pid] = (rng.binomial(n, p), n)
        else:
            out[pid] = eta + post["sigma"] * rng.standard_t(post["nu"])
    return out, pick
