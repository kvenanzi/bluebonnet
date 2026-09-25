"""M4: the hierarchical Bayesian models (preregistration §7).

Strength:  y ~ BetaBinomial(n, mu*phi, (1-mu)*phi)
           logit mu = alpha + a[county] + b[spring] + X beta
           a ~ N(0, sigma_c), b ~ N(0, sigma_y), beta ~ N(0, 1), phi ~ Gamma(2, 0.1)
Timing:    median_doy ~ StudentT(nu, alpha + a[county] + b[spring] + X beta, sigma)

The county and year effects are written non-centred (a = sigma_c * z, z ~ N(0, 1)), which
samples better when a group has few observations. For a spring the model has not seen, the
year effect is unknown: each posterior draw takes one new b ~ N(0, sigma_y) shared by every
county in that spring, so the counties' predictions move together as they do in real years.
"""

import numpy as np
import pandas as pd
import pymc as pm

from .targets import empirical_logit

SAMPLER = dict(draws=1000, tune=1000, chains=4, target_accept=0.95, progressbar=False)


def _index(values, levels=None):
    levels = sorted(set(values)) if levels is None else levels
    lookup = {v: i for i, v in enumerate(levels)}
    return np.array([lookup[v] for v in values]), levels


def fit(df: pd.DataFrame, target: str, features: list[str], seed: int = 0, **sampler) -> dict:
    """Fit on the rows of df. target: 'strength' (uses y, n) or 'median_doy'."""
    c_idx, counties = _index(df.place_id.tolist())
    t_idx, springs = _index(df.spring.tolist())
    X = df[features].fillna(0.0).values
    coords = {"county": counties, "spring": springs, "feature": features}
    with pm.Model(coords=coords) as model:
        if target == "strength":
            alpha = pm.Normal("alpha", -3.5, 2.0)
            sigma_c = pm.HalfNormal("sigma_c", 1.0)
            sigma_y = pm.HalfNormal("sigma_y", 1.0)
            beta = pm.Normal("beta", 0.0, 1.0, dims="feature")
        else:
            alpha = pm.Normal("alpha", 85.0, 15.0)
            sigma_c = pm.HalfNormal("sigma_c", 10.0)
            sigma_y = pm.HalfNormal("sigma_y", 10.0)
            beta = pm.Normal("beta", 0.0, 5.0, dims="feature")
        a = pm.Deterministic("a", sigma_c * pm.Normal("z_c", 0, 1, dims="county"), dims="county")
        b = pm.Deterministic("b", sigma_y * pm.Normal("z_y", 0, 1, dims="spring"), dims="spring")
        eta = alpha + a[c_idx] + b[t_idx] + pm.math.dot(X, beta)
        if target == "strength":
            phi = pm.Gamma("phi", 2.0, 0.1)
            mu = pm.math.sigmoid(eta)
            pm.BetaBinomial("y", alpha=mu * phi, beta=(1 - mu) * phi, n=df.n.values, observed=df.y.values)
        else:
            nu = pm.Gamma("nu", 2.0, 0.1)
            sigma = pm.HalfNormal("sigma", 10.0)
            pm.StudentT("obs", nu=nu, mu=eta, sigma=sigma, observed=df[target].values)
        idata = pm.sample(random_seed=seed, **{**SAMPLER, **sampler})
    return {"idata": idata, "counties": counties, "springs": springs, "features": features,
            "target": target, "model": model}


def posterior(fitted: dict) -> dict:
    p = fitted["idata"].posterior
    flat = lambda v: p[v].stack(s=("chain", "draw")).values
    out = {k: flat(k) for k in ["alpha", "sigma_c", "sigma_y"]}
    out["beta"] = flat("beta").T if flat("beta").ndim == 2 else flat("beta")[:, None]   # draws x features
    out["a"] = flat("a").T                                                                  # draws x counties
    for k in ["phi", "nu", "sigma"]:
        if k in p:
            out[k] = flat(k)
    return out


def predict_new_spring(fitted: dict, rows: pd.DataFrame, seed: int = 1, n_override=None) -> np.ndarray:
    """Posterior predictive samples (rows x draws) for rows that all belong to springs the
    model did not see. Strength samples are empirical logits of simulated counts, on the same
    scale as the observed target; timing samples are days of year.
    Rows may carry several springs; each spring gets its own year-effect draw."""
    rng = np.random.default_rng(seed)
    post = posterior(fitted)
    S = len(post["alpha"])
    X = rows[fitted["features"]].fillna(0.0).values
    lookup = {c: i for i, c in enumerate(fitted["counties"])}
    a = np.column_stack([post["a"][:, lookup[c]] if c in lookup else rng.normal(0, post["sigma_c"])
                         for c in rows.place_id])                                    # draws x rows
    b = {t: rng.normal(0, post["sigma_y"]) for t in rows.spring.unique()}
    b = np.column_stack([b[t] for t in rows.spring])
    eta = post["alpha"][:, None] + a + b + post["beta"] @ X.T                         # draws x rows
    if fitted["target"] == "strength":
        n = np.asarray(rows.n.values if n_override is None else n_override, dtype=int)
        mu = 1 / (1 + np.exp(-eta))
        phi = post["phi"][:, None]
        p = rng.beta(mu * phi, (1 - mu) * phi)
        y = rng.binomial(np.broadcast_to(n, p.shape), p)
        return empirical_logit(y, n).T, y.T, eta.T
    t = rng.standard_t(post["nu"][:, None], size=eta.shape)
    return (eta + post["sigma"][:, None] * t).T, None, eta.T


def diagnostics(fitted: dict) -> dict:
    import arviz as az
    idata = fitted["idata"]
    summ = az.summary(idata, var_names=["alpha", "beta", "sigma_c", "sigma_y"], round_to=4)
    div = int(idata.sample_stats["diverging"].sum())
    return {"rhat_max": float(summ.r_hat.max()), "ess_bulk_min": float(summ.ess_bulk.min()),
            "divergences": div, "summary": summ}
