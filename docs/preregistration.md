# Pre-registration: Central Texas bluebonnet bloom, springs 2017–2026 and forecast for 2027

Committed 2026-09-25, before any county-level bloom index was computed, before any weather data was joined to bloom data, and before any model was fit. The git commit that adds this file is the timestamp. Later changes to this file are listed in the change log at the bottom, each with its reason, and none may alter a hypothesis, a test, or a decision rule after the corresponding result has been seen.

**What had been seen before this was written.** During the feasibility check on 2026-09-25, statewide Texas counts of research-grade *Lupinus texensis* records and of all Plantae records were retrieved per year, and per-year counts for eight Austin-area counties. The statewide ratio (bluebonnet records per 1,000 plant records in March–April) was about 21–26 in 2019–2024 and about 16 in 2025 and 2026; the Travis County ratio fell from about 38–43 to 31 (2025) and 26 (2026). Published forecasts described 2025 and 2026 as poor or moderate springs following a dry fall. No weather data had been examined for any year.

## 1. Question

Does fall rainfall predict the strength of the Texas bluebonnet bloom better than winter temperature does? Does the order reverse for bloom timing? Can a model built on 2017–2026 forecast spring 2027 per county around Austin, issued in October 2026, updated in December 2026 and March 2027, and graded in May 2027?

## 2. Data

- **Bloom records.** iNaturalist *verifiable* observations (quality grade research or needs_id) of *Lupinus texensis* (taxon 49564) in Texas (place 18), observed 1 February–30 April of each spring 2016–2026 **and uploaded no later than 15 May of the same year** (`created_d2`). The upload cut-off makes every historical spring look as the 2027 spring will look when it is graded (§9), so that the target does not depend on how many years of late uploads a spring has accumulated. Verifiable rather than research-grade observations are used for the same reason: the share of observations promoted to research grade grows with time since upload. Every record in the window is treated as flowering; the iNaturalist "Flowering" annotation (term 12, value 13) is used only in a sensitivity analysis.
- **Effort.** Verifiable observations of all Plantae in the same county, dates, and upload cut-off, from the iNaturalist histogram endpoint (daily interval).
- **City Nature Challenge.** The four observation days of each year's City Nature Challenge (last weekend of April, dates taken from citynaturechallenge.org) are removed from both numerator and denominator.
- **County assignment.** A record's county is the Texas county whose Census boundary contains its coordinates. Records with obscured coordinates are assigned by the county place identifier iNaturalist attaches to them when one exists, and dropped otherwise.
- **Weather.** NOAA nClimDiv county monthly precipitation, mean temperature, and Palmer Drought Severity Index (1895 onward), and GHCN-Daily station data for daily minimum and maximum temperature (nearest station to the county centroid with at least 90% of daily values present in the season).

## 3. Units and inclusion

- The unit is a county-spring.
- Training springs: 2017–2026 (ten). 2016 is used only in a sensitivity analysis because effort that year was about a fifth of 2017's.
- **County inclusion rule (fixed now):** a Texas county enters the training set if it has at least 20 bluebonnet records (after the masking in §2) in at least 6 of the 10 training springs. A county-spring with fewer than 5 records remains in the Beta-Binomial model (which weights it by its counts) but is excluded from the point-model targets.
- **Forecast counties:** Travis, Williamson, Hays, Burnet, Llano, Blanco, Bastrop, and the pooled region formed by summing their counts ("Central Texas"). A forecast county that fails the inclusion rule is still forecast by the hierarchical model and flagged.

## 4. Targets

1. **Strength.** For county *c* and spring *t*: `y` = bluebonnet records, `n` = all Plantae records, both over 1 February–30 April with the City Nature Challenge days removed. Point models use the empirical logit `log((y + 0.5) / (n − y + 0.5))` minus the county's mean over the training springs in the fold (the anomaly). The hierarchical model uses `y ~ BetaBinomial(n, ·)` directly.
2. **Timing.** The effort-weighted median day of year: each day's bluebonnet count is divided by that day's Plantae count (days with zero Plantae records contribute zero), the ratios are smoothed with a 7-day centred moving sum, and the median of the resulting distribution over 1 February–30 April is the target. The 10% quantile (onset) is reported but not modeled. Timing is modeled only for county-springs with at least 50 bluebonnet records, and for the pooled region.

## 5. Predictors

All weather predictors are county anomalies from the county's 1991–2020 mean, divided by the county's 1991–2020 standard deviation of the same quantity (z-scores), so that coefficients are comparable across predictors. For spring *t*, "fall" is September–November of year *t − 1*.

| Name | Definition |
|---|---|
| `fall_prcp` | Sep–Nov precipitation total (primary H2 predictor) |
| `sepoct_prcp` | Sep–Oct precipitation total (used by the October-issue forecast only as a window check) |
| `octdec_prcp` | Oct–Dec precipitation total (rain-timing sensitivity) |
| `winter_prcp` | Dec–Feb precipitation total |
| `winter_tavg` | Dec–Feb mean temperature (primary H2 comparison predictor) |
| `freeze_days` | Dec–Feb days with minimum temperature ≤ −2 °C at the county's station |
| `gdd_mar1` | Growing degree days, base 5 °C, 1 January–28/29 February, from daily (Tmax + Tmin)/2 at the county's station (primary H3 predictor) |
| `summer_pdsi` | Jun–Aug mean PDSI of year *t − 1* |

ENSO is not a bloom predictor. It is used only to select analog years for the unobserved months of a forecast (§8).

## 6. Hypotheses and decision rules

Each hypothesis states its test and the rule that decides its verdict. "LOYO" is leave-one-year-out cross-validation: every county of one spring is held out together, the model is fit on the other nine springs, and the held-out spring is predicted. Year-level bootstrap resamples the ten springs with replacement (10,000 resamples, seed 20260925).

- **H1 (target validity).** The strength index for the pooled Central Texas region ranks the springs in the same order as independent reports. Test: Spearman ρ between the pooled region's empirical logit and the ordinal codes (poor = 0, moderate = 1, good = 2) from `docs/bloom-year-codes.md`, whose coding rule was written before the codes were assigned. Supported if ρ > 0.5 and both of the two lowest-index springs are coded poor or moderate.
- **H2 (headline).** Fall precipitation predicts bloom strength better than winter mean temperature does. Test: two single-predictor ordinary least squares models on the strength anomaly (`fall_prcp` alone; `winter_tavg` alone), each scored by LOYO mean squared error over all included county-springs. The per-spring difference in mean squared error (winter − fall) is averaged over springs; its 95% CI is the year-level bootstrap percentile interval. **Supported** if the CI excludes zero with fall better. **Reversed** if it excludes zero with winter better. Otherwise **not distinguishable at n = 10 springs**. A second, reported but not decisive, test: in the hierarchical model (M4) the posterior of |β_fall| / |β_winter_tavg| on the standardized scale, with the probability that it exceeds 1.
- **H3 (timing reversal).** Growing degree days to 1 March predict the median bloom date better than fall precipitation does. Test and rule identical to H2, with `gdd_mar1` versus `fall_prcp`, the timing target, and absolute error in days.
- **H4 (model ladder).** On LOYO, LightGBM (best configuration from the sweep, chosen by LOYO on the training springs) does not have lower strength RMSE than ridge regression, and the hierarchical model's posterior-median RMSE is no more than 5% above the better of the two. Each is also reported as skill relative to climatology (B0).
- **H5 (partial pooling).** For counties with a median of fewer than 50 records per spring, the hierarchical model's LOYO RMSE is lower than that of per-county OLS on `fall_prcp` alone.
- **H6 (calibration).** Nominal 80% prediction intervals (hierarchical posterior predictive; jackknife+ around ridge and LightGBM) cover between 70% and 90% of held-out county-springs.
- **H7 (lead time, prospective).** Across the forecast counties, the mean width of the 80% strength interval decreases more from the October to the December forecast (fall observed) than from the December to the March forecast (winter observed). For timing, it decreases more from December to March. Evaluated mechanically in May 2027 from the three committed forecast files.

## 7. Model ladder

| Rung | Model |
|---|---|
| B0 | Climatology: county mean of the target over the training springs in the fold |
| B1 | Persistence: the county's value in the previous spring |
| M1a / M1b | OLS on `fall_prcp` / on `winter_tavg` (strength); `fall_prcp` / `gdd_mar1` (timing) |
| M2 | Ridge regression on all eight predictors, α chosen by inner LOYO; elastic net reported alongside |
| M3 | LightGBM regression on all eight predictors; hyper-parameters by W&B sweep scored on LOYO |
| M4 | Hierarchical Bayesian model, strength: `y ~ BetaBinomial(n, μ·φ, (1−μ)·φ)`, `logit μ = α + a_county + b_year + X·β`, `a_county ~ N(0, σ_c)`, `b_year ~ N(0, σ_y)`, `β ~ N(0, 1)`, half-normal priors on σ, `φ ~ Gamma(2, 0.1)`. Timing: Student-t on median day with county and year effects and the same predictors. Fit in PyMC with NUTS, 4 chains × 1,000 draws after 1,000 tuning steps |
| +C | Jackknife+ intervals from the LOYO residuals, around M2 and M3 |

The model used for the 2027 forecast is M4, fixed now, regardless of how the ladder turns out. If M4 fails its sampling diagnostics (R-hat ≥ 1.01 or any divergence after reparameterization), the forecast uses M2 with jackknife+ intervals and the post says so.

## 8. Forecast protocol

- Forecasts are issued at three dates: October 2026 (tag `forecast-2026-10`; September 2026 observed as far as the data reach), about 5 December 2026 (`forecast-2026-12`; September–November observed), about 3 March 2027 (`forecast-2027-03`; September–February observed).
- The model and its predictors are those of §7, refit on all ten training springs; they are not re-selected at later issues.
- Unobserved months are filled by resampling whole seasons from the county's own nClimDiv history, restricted to El Niño winters since 1950 (Oceanic Niño Index for October–December ≥ +0.5 °C), because the Climate Prediction Center's El Niño advisory of September 2026 gives more than 90% probability of El Niño conditions through the winter. Each analog year supplies all unobserved months jointly, so the correlation between months is preserved. The draws are pushed through the posterior predictive distribution.
- The share of draws outside the 2017–2026 range of each predictor is reported.
- Output per forecast county: median, 50% and 80% central intervals, and probabilities of the three terciles of the county's 2017–2026 distribution, for strength and for timing. Committed as `forecasts/<tag>.csv`; its SHA-256 is printed in the post, in the W&B artifact metadata, and in the Hugging Face dataset commit.

## 9. Grading (May 2027)

- Observed 2027 values are computed by the `targets.py` of tag `forecast-2026-10`, from iNaturalist data retrieved on or after 15 May 2027 with the same filters as §2 (observed 1 February–30 April 2027, uploaded by 15 May 2027).
- Scores, per forecast county and pooled, for each of the three issues: CRPS of the predictive distribution, CRPS of climatology (the ten training values as an ensemble), the skill score 1 − CRPS / CRPS_clim, whether the observation lies inside the 80% interval, and the ranked probability score of the tercile probabilities.
- A forecast issue is called **skilful** if its mean CRPS skill score over the seven counties is positive.

## Change log

- 2026-09-25: initial version.
