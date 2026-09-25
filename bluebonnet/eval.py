"""Leave-one-year-out evaluation with CV+ predictive ensembles (preregistration §6–7).

For each held-out spring k the model is fit on the other springs (point prediction).
To give every point model a predictive distribution, an inner leave-one-year-out is run
on the training springs: the model is refit without spring j, the residuals R on spring j
are kept, and the refit's prediction for each test row is kept. The test row's ensemble is
{prediction without j + residual} over every inner (j, row); its 80% interval is the CV+
interval of Barber et al (2021), built from the absolute residuals. The same ensemble gives
the CRPS. Climatology evaluated this way is the reference every skill score uses.
"""

import copy

import numpy as np
import pandas as pd

from . import TRAIN_SPRINGS
from .stats import crps_ensemble

ALPHA = 0.2   # 80% intervals


def cv_plus(model_proto, train: pd.DataFrame, test: pd.DataFrame, target: str):
    """Signed ensemble (rows x members) and CV+ interval for the test rows."""
    preds, resid = [], []
    for j in sorted(train.spring.unique()):
        inner_tr, inner_te = train[train.spring != j], train[train.spring == j]
        m = copy.deepcopy(model_proto).fit(inner_tr, target)
        r = inner_te[target].values - m.predict(inner_te)
        p = m.predict(test)
        preds.append(np.repeat(p[:, None], len(r), axis=1))
        resid.append(np.repeat(r[None, :], len(test), axis=0))
    P, R = np.hstack(preds), np.hstack(resid)
    ens = P + R
    lo = np.quantile(P - np.abs(R), ALPHA / 2, axis=1, method="lower")
    hi = np.quantile(P + np.abs(R), 1 - ALPHA / 2, axis=1, method="higher")
    return ens, lo, hi


def loyo(model_proto, df: pd.DataFrame, target: str, springs=TRAIN_SPRINGS, intervals: bool = True) -> pd.DataFrame:
    """Held-out predictions for every row of `df` whose spring is in `springs`."""
    out = []
    for k in springs:
        train, test = df[(df.spring != k) & df.spring.isin(springs)], df[df.spring == k]
        if test.empty:
            continue
        assert not set(train.spring) & set(test.spring), "a spring is in both train and test"
        m = copy.deepcopy(model_proto).fit(train, target)
        res = test[["place_id", "county", "spring", target]].rename(columns={target: "obs"}).copy()
        res["pred"] = m.predict(test)
        if intervals:
            ens, lo, hi = cv_plus(model_proto, train, test, target)
            res["lo80"], res["hi80"] = lo, hi
            res["crps"] = [crps_ensemble(e, o) for e, o in zip(ens, res.obs)]
        out.append(res)
    return pd.concat(out, ignore_index=True)


def summarize(pred: pd.DataFrame, clim: pd.DataFrame | None = None) -> dict:
    err = pred.pred - pred.obs
    s = {"n_rows": int(len(pred)), "n_springs": int(pred.spring.nunique()),
         "rmse": float(np.sqrt(np.mean(err ** 2))), "mae": float(np.mean(np.abs(err)))}
    if "crps" in pred:
        s["crps"] = float(pred.crps.mean())
        s["cov80"] = float(((pred.obs >= pred.lo80) & (pred.obs <= pred.hi80)).mean())
        s["width80"] = float((pred.hi80 - pred.lo80).mean())
    if clim is not None:
        s["rmse_skill"] = 1 - s["rmse"] / float(np.sqrt(np.mean((clim.pred - clim.obs) ** 2)))
        if "crps" in pred and "crps" in clim:
            s["crps_skill"] = 1 - s["crps"] / float(clim.crps.mean())
    return s


def per_spring_loss(pred: pd.DataFrame, kind: str = "se") -> pd.Series:
    """Mean squared (or absolute) error per held-out spring, the unit of the paired tests."""
    e = pred.pred - pred.obs
    loss = e ** 2 if kind == "se" else e.abs()
    return loss.groupby(pred.spring).mean()
