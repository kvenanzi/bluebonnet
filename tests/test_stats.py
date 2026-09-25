import numpy as np

from bluebonnet.stats import bootstrap_mean_ci, crps_ensemble, crps_gaussian, rps, wilson


def test_crps_ensemble_matches_gaussian_closed_form():
    rng = np.random.default_rng(0)
    x = rng.normal(1.0, 2.0, 200_000)
    assert abs(crps_ensemble(x, 0.3) - crps_gaussian(1.0, 2.0, 0.3)) < 0.01


def test_crps_point_mass_is_absolute_error():
    assert crps_ensemble([2.0, 2.0, 2.0], 5.0) == 3.0


def test_rps_perfect_and_worst():
    assert rps([0, 0, 1], 2) == 0.0
    assert rps([1, 0, 0], 2) == 2.0


def test_wilson_contains_p():
    lo, hi = wilson(93, 100)
    assert lo < 0.93 < hi


def test_bootstrap_ci_brackets_mean():
    m, lo, hi = bootstrap_mean_ci([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert lo < m < hi and m == 5.5
