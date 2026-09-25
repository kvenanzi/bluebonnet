# Modeling primer: the methods used in this project

This primer explains each method as it is used here, in the order the models appear on the ladder. The code references are to the `bluebonnet/` package.

## 1. The unit, the target, and why the split is by year

A row is a **county-spring**: for example Travis County, spring 2019. The strength target is the share of all plant observations in that county between 1 February and 30 April that are bluebonnets, expressed as an empirical logit, `log((y + 0.5) / (n − y + 0.5))`, where `y` is bluebonnet records and `n` is plant records (`targets.py`). The logit makes a change from 2% to 4% the same size as a change from 20% to 40% in odds, and it keeps predictions inside (0, 1) when transformed back.

Weather in neighboring counties is correlated within a spring, and so is observer behavior. If Travis 2019 were in the test set while Williamson 2019 were in the training set, the model would already have seen spring 2019. **Leave-one-year-out (LOYO)** cross-validation therefore holds out every county of one spring together, fits on the other nine springs, predicts the held-out spring, and repeats for all ten springs (`eval.loyo`). The number of independent test units for a between-year question is ten, and every hypothesis test resamples springs, not rows.

## 2. Anomalies and climatology

Travis County always has more bluebonnet records per plant record than Harris County, for reasons that have nothing to do with weather (roadside seeding, habitat, who observes). The point models remove this by predicting the **anomaly**: the target minus the county's own mean over the training springs of the fold. A model that always predicts an anomaly of zero is **climatology** (B0), the forecast "this county will have its usual spring". Every model is judged by how much it improves on climatology, as a **skill score**: `1 − score(model) / score(climatology)`. A skill of 0 means no improvement; a negative skill means the model is worse than predicting the usual value.

**Persistence** (B1) predicts last spring's value. If bluebonnet seed that did not germinate one year produces plants the next, persistence would beat climatology.

## 3. Linear models: OLS, ridge, and elastic net

Ordinary least squares (OLS) fits `anomaly = β · x` by minimizing squared error. With one predictor (M1a, M1b) it is the direct test of the headline hypothesis: which single predictor, fall rain or winter temperature, gives lower held-out error?

With eight predictors and about 130 rows that share only ten springs, OLS will fit noise. **Ridge regression** ([Hoerl & Kennard 1970]) adds a penalty `α · Σβ²` that shrinks coefficients toward zero; the **elastic net** ([Zou & Hastie 2005]) mixes that penalty with `α · Σ|β|`, which can set coefficients exactly to zero. The penalty strength α is chosen by an inner leave-one-year-out on the training springs only (`models.GroupedCV`), so the held-out spring never influences it.

All weather predictors are z-scores: the county's departure from its 1991–2020 normal divided by the county's 1991–2020 standard deviation. A coefficient of 0.2 on `fall_prcp` then means "one standard deviation more fall rain than normal raises the logit by 0.2", and coefficients of different predictors are on the same scale.

## 4. Gradient-boosted trees: LightGBM

A regression tree splits the predictor space into boxes ("fall rain z > 0.8 and winter temperature z < −0.3") and predicts the mean of each box. Gradient boosting (Friedman 2001, *The Annals of Statistics* 29(5):1189–1232; LightGBM, [Ke et al 2017]) adds hundreds of small trees, each fit to the errors of the sum so far. Boosted trees capture interactions and thresholds without being told about them, which is why they usually win on large tabular datasets. With ten springs they have little to learn from, and a tree cannot extrapolate: above the largest fall rain it has seen, its prediction stays at the value of the last box. Hypothesis H4 predicts that LightGBM does not beat ridge here. Its hyper-parameters (tree size, learning rate, number of trees, minimum rows per leaf) are chosen by a W&B Sweep (`sweeps/lgbm.yaml`).

## 5. Prediction intervals without a distributional model: CV+

A point prediction says nothing about its own uncertainty. **Conformal prediction** builds intervals from held-out errors and guarantees coverage under mild assumptions. The version used here is **CV+**, the cross-validation form of the jackknife+ ([Barber et al 2021]). For a held-out spring k:

1. For each training spring j, fit the model without j, record its residuals on spring j, and record its prediction for the test row.
2. The test row's interval runs from the 10th percentile of {prediction without j − |residual|} to the 90th percentile of {prediction without j + |residual|}, over every inner spring j and every residual in it.

The same set, with signed residuals, is used as a predictive ensemble to compute the CRPS (§7), so point models and the Bayesian model are scored by the same rule (`eval.cv_plus`). The guarantee assumes exchangeable springs; a spring unlike any of the ten (such as an out-of-range El Niño winter) is exactly where it can fail.

## 6. The hierarchical Bayesian model (M4)

A **Bayesian** model states a probability distribution for everything unknown and updates it with the data. Its output is not one best coefficient but a **posterior distribution**, represented by a few thousand random draws; every forecast is computed once per draw, so uncertainty in the coefficients flows into the forecast automatically.

The strength model (`bayes.py`):

```
y ~ BetaBinomial(n, μ·φ, (1 − μ)·φ)
logit μ = α + a[county] + b[spring] + X·β
a ~ Normal(0, σ_c)     b ~ Normal(0, σ_y)     β ~ Normal(0, 1)
```

- **Beta-Binomial likelihood.** `y` out of `n` is treated as counts, not a ratio, so a county-spring with 15 plant records carries less weight than one with 6,000 without a hand-set threshold. The Beta part (φ) allows more spread than independent binomial sampling would produce, because observers do not sample plants independently.
- **County effects `a` and partial pooling.** Each county has its own baseline, but the baselines are drawn from a common distribution whose width σ_c is also estimated. A county with little data is pulled toward the average; a county with much data keeps its own value. This is **partial pooling** ([Gelman & Hill 2007]), the middle ground between one model for all counties (complete pooling) and a separate model per county (no pooling). Hypothesis H5 tests whether it helps thin counties.
- **Year effects `b`.** Everything that shifts all counties in a spring together, including unmeasured weather and changes in observer behavior, goes into `b`. The weather coefficients β are then identified from two sources: from differences between springs, and from differences between counties within the same spring. For a spring the model has not seen, `b` is unknown; each posterior draw takes a new `b ~ Normal(0, σ_y)` shared by all counties, which is why the forecast intervals are wide.
- **Priors.** `β ~ Normal(0, 1)` on z-scored predictors says that a one-standard-deviation change in weather is unlikely to change the odds of a record being a bluebonnet by more than a factor of e² ≈ 7. The priors are stated in `preregistration.md` before fitting.

**Sampling.** PyMC ([Abril-Pla et al 2023]) draws from the posterior with the No-U-Turn Sampler ([Hoffman & Gelman 2014]), a form of Hamiltonian Monte Carlo. Four independent chains are run. Three diagnostics decide whether the draws can be trusted ([Vehtari et al 2021]):

- **R-hat** compares the chains with each other; values below 1.01 mean they agree.
- **Effective sample size (ESS)** is the number of independent draws the correlated chain is worth; above 400 is adequate for intervals.
- **Divergences** are steps where the sampler met curvature it could not follow; any divergence means part of the posterior may be missed. Writing the county and year effects as `σ · z` with `z ~ Normal(0, 1)` (the **non-centred** form) is the standard remedy when groups have little data.

**Posterior predictive check.** Data are simulated from the fitted model and compared with the real data; if the real values fall inside the simulated 80% intervals about 80% of the time, the model's description of spread is adequate.

## 7. Scoring a forecast distribution

- **RMSE / MAE** score the point prediction (the posterior median for M4).
- **CRPS** (continuous ranked probability score; [Matheson & Winkler 1976]; [Gneiting & Raftery 2007]) scores the whole predictive distribution: it is the area between the forecast's cumulative distribution and a step at the observed value. For a point forecast it equals the absolute error, so it is in the target's units, and lower is better. It rewards a forecast that is both centred correctly and no wider than necessary. `stats.crps_ensemble` computes it exactly from samples.
- **Coverage** is the share of held-out values inside the 80% interval. A well-calibrated forecast covers about 80%; much more means the intervals are too wide, and much less means too narrow.
- **Terciles and the ranked probability score.** For the 2027 forecast each county's ten observed springs are split into thirds: below normal, near normal, above normal. The forecast gives a probability for each third, and the ranked probability score ([Epstein 1969]) measures the squared distance between the cumulative forecast probabilities and the observed category.

## 8. Paired bootstrap over springs

To compare two models (H2, H3), the per-spring mean loss of each is computed, the difference is taken spring by spring, and the ten differences are resampled with replacement 10,000 times (`stats.bootstrap_mean_ci`). The 2.5th and 97.5th percentiles of the resampled means give a 95% interval. Pairing by spring removes the variation that affects both models equally (a spring that is hard for one is usually hard for the other). With ten springs the interval is wide, and the pre-registered rule allows the verdict "not distinguishable" for that reason.

## 9. What W&B records here

- **Runs.** Each (model, target) evaluation is one run in `within-noise/bluebonnet-bloom`, job type `loyo`, group `ladder`, with the held-out predictions as a table.
- **Artifacts.** `bluebonnet-seasons` is the dataset every run declares as input; `hierarchical-logit` and `hierarchical-median_doy` hold the posterior draws; `bluebonnet-forecast:<issue>` holds each registered forecast.
- **Sweep.** The LightGBM grid, run from the Colab notebook.
- **Report.** The runs are assembled into a W&B Report embedded in the post.

References are listed in `docs/post/README.md`.
