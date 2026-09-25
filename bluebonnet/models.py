"""The point-model rungs of the ladder (preregistration §7). Every model takes the
training rows of a fold and predicts the target on the raw scale.

Most models are fit to the *anomaly*: the target minus the county's mean over the
training springs of the fold. A model that predicts an anomaly of zero is climatology
(B0); a model with predictors explains departures from each county's own normal.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet, LinearRegression, Ridge
from sklearn.model_selection import GridSearchCV, LeaveOneGroupOut


class AnomalyModel:
    """Fit `estimator` to (predictors -> target anomaly from the county's training mean)."""

    def __init__(self, name: str, features: list[str], estimator=None):
        self.name, self.features, self.estimator = name, features, estimator

    def county_means(self, train: pd.DataFrame, target: str) -> pd.Series:
        return train.groupby("place_id")[target].mean()

    def fit(self, train: pd.DataFrame, target: str):
        self.target = target
        self.means = self.county_means(train, target)
        self.grand = train[target].mean()
        if self.estimator is not None and self.features:
            anom = train[target] - train.place_id.map(self.means)
            self.estimator.fit(self.X(train), anom.values, **self.fit_kwargs(train))
        return self

    def fit_kwargs(self, train):
        return {}

    def X(self, df: pd.DataFrame) -> np.ndarray:
        return df[self.features].fillna(0.0).values      # a missing z-score is set to the normal

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        base = df.place_id.map(self.means).fillna(self.grand).values
        if self.estimator is None or not self.features:
            return base
        return base + self.estimator.predict(self.X(df))

    def describe(self) -> dict:
        est = self.estimator
        if est is None:
            return {}
        if isinstance(est, GridSearchCV):
            est = est.best_estimator_
        out = {}
        if hasattr(est, "coef_"):
            out["coef"] = dict(zip(self.features, np.round(np.ravel(est.coef_), 5).tolist()))
            out["intercept"] = float(np.ravel(getattr(est, "intercept_", 0.0))[0])
        if hasattr(est, "alpha"):
            out["alpha"] = float(est.alpha)
        return out


class Climatology(AnomalyModel):
    def __init__(self):
        super().__init__("B0 climatology", [], None)


class Persistence(AnomalyModel):
    """B1: last spring's value of the same county; the county mean when that is missing."""

    def __init__(self):
        super().__init__("B1 persistence", [], None)

    def predict(self, df):
        prev = df[f"prev_{self.target}"].values
        base = df.place_id.map(self.means).fillna(self.grand).values
        return np.where(np.isnan(prev), base, prev)


class GroupedCV(AnomalyModel):
    """An estimator whose regularization is chosen by an inner leave-one-year-out search."""

    def __init__(self, name, features, base, grid):
        super().__init__(name, features, GridSearchCV(base, grid, cv=LeaveOneGroupOut(),
                                                      scoring="neg_mean_squared_error"))

    def fit_kwargs(self, train):
        return {"groups": train.spring.values}


def ridge(features):
    return GroupedCV("M2 ridge", features, Ridge(), {"alpha": np.logspace(-2, 3, 26)})


def elastic_net(features):
    return GroupedCV("M2 elastic net", features, ElasticNet(max_iter=50_000),
                     {"alpha": np.logspace(-3, 0.5, 15), "l1_ratio": [0.2, 0.5, 0.8]})


def ols(name, features):
    return AnomalyModel(name, features, LinearRegression())


def lightgbm(features, params: dict | None = None):
    import lightgbm as lgb
    p = {"n_estimators": 200, "learning_rate": 0.05, "num_leaves": 7, "min_child_samples": 20,
         "subsample": 0.8, "subsample_freq": 1, "colsample_bytree": 0.8, "reg_lambda": 1.0,
         "verbose": -1, "random_state": 0, **(params or {})}
    return AnomalyModel("M3 LightGBM", features, lgb.LGBMRegressor(**p))


class PerCounty(AnomalyModel):
    """OLS fit separately in each county (the no-pooling comparison for H5)."""

    def __init__(self, features):
        super().__init__("per-county OLS", features, None)

    def fit(self, train, target):
        super().fit(train, target)
        self.fits = {}
        for pid, g in train.groupby("place_id"):
            if len(g) >= len(self.features) + 2:
                self.fits[pid] = LinearRegression().fit(g[self.features].fillna(0).values,
                                                        (g[target] - self.means[pid]).values)
        return self

    def predict(self, df):
        base = df.place_id.map(self.means).fillna(self.grand).values
        adj = np.array([self.fits[p].predict(r[None, :])[0] if p in self.fits else 0.0
                        for p, r in zip(df.place_id, df[self.features].fillna(0).values)])
        return base + adj
