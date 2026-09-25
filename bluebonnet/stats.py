"""Scoring and resampling: CRPS, ranked probability score, Wilson interval, and the
year-level paired bootstrap used for every hypothesis test (preregistration §6)."""

import math

import numpy as np

from . import BOOT_SEED


def crps_ensemble(samples, obs: float) -> float:
    """CRPS of an ensemble (Hersbach 2000; Gneiting & Raftery 2007, eq. 21):
    E|X - y| - 0.5 E|X - X'|, computed exactly in O(m log m)."""
    x = np.sort(np.asarray(samples, float))
    m = len(x)
    term1 = np.mean(np.abs(x - obs))
    # E|X - X'| = (2 / m^2) * sum_i (2i - m - 1) x_(i), i = 1..m
    i = np.arange(1, m + 1)
    term2 = 2.0 * np.sum((2 * i - m - 1) * x) / (m * m)
    return float(term1 - 0.5 * term2)


def crps_gaussian(mu: float, sigma: float, obs: float) -> float:
    """Closed form for a normal predictive distribution (Gneiting et al 2005)."""
    z = (obs - mu) / sigma
    pdf = math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
    cdf = 0.5 * (1 + math.erf(z / math.sqrt(2)))
    return sigma * (z * (2 * cdf - 1) + 2 * pdf - 1 / math.sqrt(math.pi))


def rps(probs, category: int) -> float:
    """Ranked probability score for ordered categories (Epstein 1969), not normalized."""
    p = np.cumsum(np.asarray(probs, float))
    o = np.cumsum(np.eye(len(probs))[category])
    return float(np.sum((p - o) ** 2))


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


def bootstrap_mean_ci(values, n_boot: int = 10_000, seed: int = BOOT_SEED, level: float = 0.95):
    """Mean of per-year values and its percentile interval, resampling years with replacement."""
    v = np.asarray(values, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(v), size=(n_boot, len(v)))
    means = v[idx].mean(axis=1)
    a = (1 - level) / 2
    return float(v.mean()), float(np.quantile(means, a)), float(np.quantile(means, 1 - a))


def interval_coverage(obs, lo, hi) -> tuple[int, int]:
    obs, lo, hi = map(lambda a: np.asarray(a, float), (obs, lo, hi))
    ok = ~np.isnan(obs)
    return int(((obs >= lo) & (obs <= hi))[ok].sum()), int(ok.sum())
