---
date: 2026-09-25
date-modified: 2026-11-06
description: "Ten springs of iNaturalist and NOAA data test whether fall rain or winter warmth drives the Texas bluebonnet bloom, with a registered forecast for 2027."
---

# Does Fall Rain Make a Good Bluebonnet Spring?

*Testing what Texas wildflower experts say each year against ten springs of iNaturalist photographs, with a forecast for 2027.*

*Kevin Venanzi · first published 25 September 2026, rewritten 6 November 2026 · The forecast is still open and will be scored in May 2027.*

Every February and March, wildflower experts in Austin tell reporters what kind of bluebonnet season to expect, and they explain it the same way. A good bloom comes from rain the fall before. A warm winter makes the flowers come early. In 2025 the Lady Bird Johnson Wildflower Center predicted fewer bluebonnets in the drier western part of the state and blamed the previous fall's drought ([Wildflower Center 2025](https://www.wildflower.org/pressroom/2025-wildflower-forecast)), and in 2026 its staff said a dry fall and a warm winter had produced a moderate, short season ([Fox 7 Austin, 18 March 2026](https://www.fox7austin.com/news/texas-experts-predict-moderate-bluebonnet-season-due-dry-fall-warm-winter)).

I wanted to know whether the data agree. I could not find a published field study that measures either claim for the Texas bluebonnet, so I tried to measure both from public data, and then used what I found to make a forecast for spring 2027 that can be checked when spring arrives.

## What I found

1. **Winter warmth does predict when bluebonnets bloom.** After warmer winters, the bloom came earlier, by about two days for a winter that is warm for that county (roughly the warmest one in six). A simple model of winter warmth predicted the bloom date better than fall rain did in 8 of 9 springs.
2. **Fall rain did not predict how many bluebonnets a county would have.** County by county, knowing the fall rain predicted the bloom no better than knowing the winter temperature, and neither did better than assuming each county would have its usual year. Eight different prediction methods, from a straight line to a tuned machine-learning model, gave the same answer.
3. **For the Austin area as a whole, fall rain and bloom size did move together.** Added up over seven counties, springs after wet falls had stronger blooms. I noticed this after the planned tests, and ten years are too few to tell it apart from chance.
4. **The bluebonnet share of plant photos has been falling.** Bluebonnets made up a smaller share of plant photographs in 2025 and 2026 than in any earlier spring. These data cannot tell whether that means fewer bluebonnets or a change in what people photograph.
5. **The 2027 forecast** puts the Austin-area bloom at about 20 March (most likely between 13 and 28 March), with a size close to the ten-year average and a wide range. It will be updated in December and March and scored in May.

In practice, the date of the bloom can be forecast a few weeks ahead from winter weather. The size of the bloom in a particular county could not be forecast from weather with these data.

## 1. The plant and the claim

The Texas bluebonnet (*Lupinus texensis*) is an annual. It is sown in fall, forms a rosette of leaves in winter, and flowers from March to May ([Wildflower Center plant database](https://www.wildflower.org/plants/result.php?id_plant=lute)). Its seeds have a hard coat that keeps out water, which slows sprouting. In one greenhouse study of four commercial seed lots, 16–71% of untreated seeds came up within a month, and soaking the seeds in acid raised that to 85–95% in the three lots that responded ([Davis et al 1991](#references)). The state transportation department and the public sow this species along Texas roads. A genetic study found almost no difference between sown and wild populations, and its authors suggest that the large amount of sown seed may explain this ([Turner et al 2018](#references)).

The experts' explanation has two parts: fall rain decides how many plants get started, and winter warmth decides when they flower. Both are reasonable. In the Mojave Desert, the growth of winter annuals usually follows a heavy fall rain of more than 25 mm ([Beatley 1974](#references)). For timing, accumulated warmth, measured as *growing degree days*, is often used to describe the timing of plant development ([McMaster & Wilhelm 1997](#references)). But Central Texas is much wetter than the Mojave, and the bluebonnet's hard seed coat slows sprouting, so not every seed responds to the same rain. Either could weaken a link to one season's rain.

## 2. Measuring a bloom from photographs

There is no official count of bluebonnets. What exists is iNaturalist, a website where the public uploads photographs of plants and animals. From 1 February to 30 April over ten springs (2017–2026), Texans uploaded 23,527 bluebonnet photographs.

The raw count is not usable on its own, because iNaturalist itself grew about forty-fold over those years. More photos could mean more flowers or just more people with the app. So I divided the bluebonnet count by the count of photos of *any* plant taken in the same county on the same days. The result measures how much of people's attention to plants went to bluebonnets that spring. This uses the same idea as the "target-group" method, which treats records of a broad group of species collected the same way, such as all plants, as a measure of how hard people were looking ([Phillips et al 2009](#references)). It has a known weakness: some species are recorded out of proportion to how common they are. In birds, for example, large species are over-represented on iNaturalist compared with a more structured survey, probably in part because they are easier to photograph ([Callaghan et al 2021](#references)). So the measure is only meaningful when comparing one county against its own other springs.

Two other choices mattered:

- **I removed the City Nature Challenge.** This four-day event at the end of April, in which Austin, Dallas–Fort Worth, Houston, and San Antonio compete to log the most observations, supplied 20.5% of all bluebonnet records and created spikes up to twice the real peak.
- **I measured the *median* date, not the peak date.** Weekly counts per county are too irregular to locate a maximum, so the timing measure is the date by which half of the season's effort-adjusted bluebonnet photos had been taken. I call it the median observation date.

I kept the 15 counties that had at least 20 bluebonnet records in at least 6 of the 10 springs, a rule fixed before I looked at any county's numbers.

**Does the measure mean anything?** Before any weather data were joined, a separate reader classified each spring as good, moderate, or poor using only newspaper and Wildflower Center descriptions, under a rule written down in advance. The photo measure ranks the springs in a similar order (a rank correlation of 0.76), and its two lowest springs, 2025 and 2026, are the two that reporters described as poor.

![The Central Texas index by spring, coloured by the independent classification](figures/index_codes.png)

*Figure 1. Bluebonnet photos per 1,000 plant photos in the seven Austin-area forecast counties combined, by spring. Bar colour is the classification from news reports.*

The measure is better at finding poor springs than at separating good from moderate ones. 2017, which reporters described as early and abundant, has the third-lowest value.

## 3. What I decided in advance

A model fit to ten springs can be made to explain those ten springs if it is flexible enough. One effective way to check whether it has learned anything is to write the tests down before running them, then make a prediction before the outcome exists ([Nosek et al 2018](#references)). I committed the questions, the rules for answering them, and the forecast method to the project's public repository on 25 September 2026, before computing any county-level measure or joining any weather ([the plan](https://github.com/kvenanzi/bluebonnet/blob/main/docs/preregistration.md)).

| Question | What would count as yes | Result |
|---|---|---|
| 1. Does the photo measure agree with news descriptions of each spring? | Rank correlation above 0.5, and the two lowest springs described as poor or moderate | **Yes.** 0.76; the two lowest springs were the two described as poor. |
| 2. Does fall rain predict bloom size better than winter temperature? | The error of the fall-rain model is clearly lower | **Could not tell them apart.** Neither did better than assuming a usual year. |
| 3. Does winter warmth predict bloom timing better than fall rain? | The error of the warmth model is clearly lower | **Yes.** By 0.78 days on average, in 8 of 9 springs. |
| 4. Would a tuned machine-learning model fail to improve on a simple regression, with a Bayesian model close to the better of the two? | The machine-learning error is not lower; the Bayesian model within 5% | **Timing: yes. Size: no.** The tuned model was slightly better than the regression, and the Bayesian model was worse than both. |
| 5. Does sharing information between counties help the counties with few photos? | Lower error than a separate model per county | **No.** |
| 6. Are the forecast ranges honest? | 80% ranges contain the true value 70–90% of the time | **Not quite.** 88–92%: the ranges were slightly too wide. |
| 7. Does learning the fall weather narrow the size forecast more than learning the winter weather? | Checked by comparing the December and March forecasts | **Open until May 2027.** |

Every model was tested the same way: hide one whole spring, fit the model on the other nine, and predict the hidden spring, ten times over. Hiding whole springs matters because all counties share a spring's weather and its crowd of photographers, so a hidden Travis County 2019 is not independent of a visible Williamson County 2019. It also means there are really only ten independent tests for any question about weather, which is why most of the ranges below are wide.

## 4. Fall rain and bloom size

![Bloom size against fall rain and winter temperature](figures/scatter.png)

*Figure 2. Each point is one county in one spring. The vertical axis is how far that spring's bloom was above or below the county's usual level; the horizontal axes are how unusual its fall rain and winter temperature were. Lines are least-squares fits.*

Across the 143 county-springs, wetter falls go with slightly stronger blooms and warmer winters with slightly weaker ones, but both relationships are weak (correlations of 0.13 and −0.17). As predictors:

- The fall-rain model and the winter-temperature model had almost the same error. Fall rain had the lower error in 5 of 10 springs; the average difference was small, and its 95% range (−0.018 to +0.043) included zero.
- **Neither one predicted better than the county's usual level.** Assuming every county would have its average spring was slightly more accurate than either weather model.

The Bayesian model (section 9) tells the same story from a different direction. It estimates that a fall that is unusually wet for a county (roughly the wettest one in six) raises the bluebonnet share by about 7%. But one county's share varies from spring to spring by about 36% for reasons the weather does not explain. An effect that small is hard to see under that much noise with ten springs.

![Per-spring differences between the competing models](figures/paired.png)

*Figure 3. Left: how much better fall rain did than winter temperature at predicting bloom size, spring by spring (above zero favours fall rain). Right: how much better winter warmth did than fall rain at predicting the date (above zero favours warmth). The black line is the average and the grey band its 95% range. 2017 had no county with enough photos to measure a date.*

## 5. Winter warmth and bloom timing

This half of the experts' claim held. Growing degree days to 1 March, a measure of how much warmth had built up over the winter, predicted the median observation date with an average error of 4.6 days, against 5.4 days for fall rain and 5.3 days for assuming the county's usual date. Warmth did better than fall rain in 8 of 9 springs, and the 95% range of the difference (0.15 to 1.48 days) excludes zero.

The Bayesian model agrees: a winter that is warm for the county moves the median date about two days earlier. Wetter winters also point earlier. Fall rain points slightly later, but not clearly.

## 6. More complex models did not help

I tried a sequence of models of increasing complexity, all on the same hidden-spring test:

![Skill of every model against the county's usual level](figures/ladder.png)

*Figure 4. How much each model improved on predicting each county's usual value, on springs it had not seen. Below zero means worse than the usual value. Left: bloom size. Right: bloom date.*

- For **bloom size**, no model did better than the county's usual level. The worst was "same as last year", which also gives no support to the idea that one good spring fills the seed bank for the next at the county scale.
- For **bloom date**, every model that used winter warmth improved on the usual date, by up to 11%.
- I tuned the machine-learning model, LightGBM, over 24 combinations of settings. The best combination was the most constrained one, the setting closest to predicting no change at all, and it still did not reach the county's usual level for bloom size.

<!-- qmd
::: {.column-page-right}
```{=html}
<iframe src="figures/sweep_lgbm.html" title="The 24 settings tried for LightGBM, parallel coordinates"
        loading="lazy" style="border:none;width:100%;height:460px"></iframe>
```
:::
-->

The interactive chart [`figures/sweep_lgbm.html`](figures/sweep_lgbm.html) draws each of the 24 settings as a line from its four values to its error for bloom size and bloom date. Dragging along an axis highlights the settings in that range.

The Bayesian model did worst of the serious models for bloom size. It moved its predictions away from each county's average according to weather effects that were small but not zero, and in springs like 2022 that moved them in the wrong direction. Its ranges were also wider than they needed to be. With weather this weak, the model that trusts the weather least does best.

## 7. Two things I noticed afterward

These were not part of the plan, so they are leads for next time rather than findings.

- **The Austin area as a whole.** Adding the seven Austin-area counties together gives one series of ten springs. In that series, fall rain correlates with bloom size (0.63), and winter temperature correlates strongly with bloom date (−0.87). A fall-rain model on this series had lower error than assuming a usual year, although the 95% range of the difference included zero. Adding counties together reduces the counting noise that dominates single counties, and this regional scale is the one the experts talk about. Their claim may be true for the region even though it cannot be seen county by county with ten springs.
- **A downward trend.** The bluebonnet share has fallen by about 5% a year since 2017. A model containing only that trend predicted county bloom size better than the usual level and better than every weather model. It could be a real decline in bluebonnets, a change in what iNaturalist users photograph as more people join, or a result of the two dry falls happening to come at the end of the period. These data cannot separate the three.

The two poorest springs, 2025 and 2026, followed the two driest falls in Travis County (70 mm and 98 mm, against a normal of 263 mm). That is the observation behind the experts' statements. In these data it is equally consistent with the steady decline. The two explanations predict different things for 2027 after a wet fall, which is one reason the forecast below is useful.

## 8. The forecast for spring 2027

On 25 September 2026, before any of the fall or winter weather was known, I issued a forecast using the model fixed in the plan. An El Niño was already under way, and the Climate Prediction Center gave a greater than 90% chance that it would become a very strong event during the fall and winter ([CPC, 10 September 2026](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_disc_sep2026/ensodisc.shtml)). El Niño winters tend to be wet across the southern United States ([Ropelewski & Halpert 1986](#references); [CPC](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensocycle/nawinter.shtml)). So the unknown months were filled in with the weather of the 26 past seasons since 1951 that followed an El Niño fall, each one used whole, for all counties at once.

| County | Size (photos per 1,000) | 80% range | Median date | 80% range |
|---|---|---|---|---|
| Travis | 19.5 | 9.7–34.5 | 20 Mar | 10–30 Mar |
| Williamson | 22.3 | 11.3–38.3 | 22 Mar | 12–31 Mar |
| Hays | 17.3 | 8.1–31.4 | 19 Mar | 10–30 Mar |
| Burnet | 21.6 | 10.6–38.4 | 16 Mar | 6–26 Mar |
| Llano* | 19.9 | 6.9–46.8 | 25 Mar | 10 Mar–8 Apr |
| Blanco* | 19.1 | 6.8–44.1 | 25 Mar | 11 Mar–7 Apr |
| Bastrop* | 20.1 | 7.1–44.2 | 25 Mar | 11 Mar–7 Apr |
| **Austin area** | **20.7** | **13.3–31.2** | **20 Mar** | **13–28 Mar** |

\* These three counties had too few photos to be in the training data, so they are forecast as an average county, not from their own history. Bastrop's own usual level is far below that average, and its size forecast is expected to score poorly.

![The forecast against the ten observed springs](figures/forecast.png)

*Figure 5. The 2027 forecast (dot: median; thick bar: middle 50%; thin bar: 80% range) against each county's ten observed springs (grey ticks).*

**How to read it.**

- **The date forecast is the part I expect to do well.** It has shown real skill on past springs. Its centre, 16–22 March in the four main Austin-area counties, is near the ten-year average because the winter has not happened yet. It will narrow as the winter is observed.
- **The size forecast is close to each county's average, with wide ranges.** That is what a model with near-zero weather effects produces. On past springs this model did worse than simply predicting the usual level, so I expect it to score worse than that in May. I am still publishing it because the plan fixed this model before the comparison was run; switching to the best model afterward would make fixing it in advance meaningless.
- **A second forecast is registered beside it.** After I found the downward trend, and before the forecast was issued, I added a forecast that extends the trend to 2027. It puts every county lower, at 12.3 per 1,000 for the Austin area (8.7–18.3). In May, comparing the two will test the trend against a return to the ten-year average.
- **The scenario winters are partly outside anything the model has seen.** The El Niño winters of the 1950s–1980s were colder than any recent winter, and 30% of the scenario winter temperatures lie outside the 2017–2026 range.

**How it will be scored.** On or after 15 May 2027, the 2027 values will be computed from iNaturalist with the same filters, by code committed with the forecast. Each forecast is scored against the county's usual level with a standard score for probability forecasts. The forecast counts as skilful if, averaged over the seven counties, it does better than the usual level. Updates are due around 5 December 2026 (after the fall is observed) and 3 March 2027 (after the winter).

## 9. What could be wrong

- **Ten springs.** Every comparison between springs rests on ten of them. "Could not tell them apart" means exactly that for this sample. It is not evidence that fall rain and winter temperature matter equally.
- **The measure counts attention, not plants.** It assumes that in an average spring, people give bluebonnets the same share of their plant photos year after year. The downward trend may mean that assumption is failing.
- **Roadside sowing.** Some of what gets photographed was planted along roads. Comparing each county with its own average removes fixed differences between counties, but not changes in sowing from year to year.
- **The median date is not the peak.** It depends on how long into the spring people keep photographing bluebonnets.
- **The 2027 winter may be unlike the training winters,** as described above.

## 10. What I take from this

The experts are right about timing: a warm winter brings bluebonnets earlier, by about two days per unusually warm winter, and that can be forecast a few weeks ahead. Their claim about fall rain and bloom size may be true for the region, but it is too small an effect, against too much year-to-year noise, to see county by county in ten springs of photographs. Several of my planned tests failed, and the most complex models did worst. With data this thin, the simplest forecasts were the most accurate, and that is the most useful thing I learned about modelling from this project.

May 2027 will show whether a wet El Niño fall brings the bloom back to its average or whether the decline continues.

---

## Details for anyone who wants to check the work

### A. Data

- **Bluebonnet records:** verifiable iNaturalist observations of *L. texensis* (taxon 49564) in Texas, observed 1 February–30 April and uploaded by 15 May of the same year, retrieved 25 September 2026. The upload cut-off makes past springs comparable with 2027, which will be retrieved on 15 May 2027. 23,523 of the 23,527 records are research grade.

  | Spring | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | Records, Texas | 208 | 499 | 1,145 | 1,708 | 1,841 | 1,797 | 1,857 | 3,178 | 4,591 | 3,141 | 3,562 |

- **Denominator:** daily counts of verifiable plant records (taxon 47126) in the same county under the same filters.
- **Counties:** Travis, Williamson, Hays, Burnet, Bexar, Comal, Dallas, Tarrant, Denton, Collin, Ellis, Harris, Bell, McLennan, Gillespie: 150 county-springs, 13,606 bluebonnet records, 943,006 plant records. 143 county-springs have at least 5 records (the size target) and 82 in 14 counties have at least 50 (the date target).
- **Weather:** county monthly precipitation, temperature, and drought index from [NOAA nClimDiv](https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/) (release of 4 September 2026); freeze days and growing degree days (base 5 °C, 1 January–1 March) from the nearest [GHCN-Daily](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily) station with 90% of days present (72 stations, median distance 8.1 km). Every predictor is a z-score against the county's 1991–2020 normals.
- **Targets:** size is the empirical logit of bluebonnet records among plant records, modelled as the difference from the county's training mean. Date is the effort-weighted median day of year (daily ratio of bluebonnet to plant records, 7-day moving sum).
- **The iNaturalist "Flowering" annotation** was not used. Its share of records rose from 6 of 73 in 2017 to 546 of 1,175 in 2024, and on its own it does not track the news classifications (ρ = −0.29).

### B. Models

| Model | Description |
|---|---|
| Usual level | Each county's mean over the training springs |
| Same as last year | The county's value in the previous spring |
| Single predictor | Least squares on fall rain or winter temperature (size); fall rain or growing degree days (date) |
| Ridge and elastic net | All eight predictors, penalty chosen by an inner hidden-spring test ([Hoerl & Kennard 1970](#references); [Zou & Hastie 2005](#references); [Park & Mazer 2018](#references)) |
| LightGBM | All eight predictors, settings from a 24-cell search ([Ke et al 2017](#references)) |
| Bayesian hierarchical | Below |

The eight predictors are September–November, September–October, and October–December precipitation; December–February precipitation and mean temperature; freeze days; growing degree days to 1 March; and the preceding summer's drought index.

The hierarchical model for size, with county *c* and spring *t*:

```
y[c,t] ~ BetaBinomial(n[c,t], μ·φ, (1 − μ)·φ)
logit μ = α + a[c] + b[t] + X[c,t]·β
a[c] ~ Normal(0, σ_c),  b[t] ~ Normal(0, σ_y),  β ~ Normal(0, 1),  φ ~ Gamma(2, 0.1)
```

County effects are partially pooled, so a county with few records is drawn toward the average county ([Gelman 2006](#references)). The year effect absorbs anything shared by every county in a spring, including observer behaviour. It uses the six non-overlapping predictors. The date model has the same structure with a Student-t likelihood. Both were fit in PyMC ([Abril-Pla et al 2023](#references)) with the No-U-Turn Sampler ([Hoffman & Gelman 2014](#references)), four chains of 1,000 draws after 1,000 tuning steps. The two forecast fits had maximum R-hat 1.007 and 1.004, below the 1.01 threshold recommended by [Vehtari et al (2021)](#references), effective sample sizes above 1,000, and no divergent transitions.

The non-Bayesian models get forecast ranges from CV+ ([Barber et al 2021](#references)), and every model is scored by the continuous ranked probability score (CRPS; [Gneiting & Raftery 2007](#references)), which for a single-number forecast equals the absolute error. Skill is 1 − CRPS(model) / CRPS(usual level).

### C. Full results

| Model | Size RMSE | Size skill | Size 80% coverage | Date RMSE (days) | Date skill | Date 80% coverage |
|---|---|---|---|---|---|---|
| Usual level | 0.362 | 0 | 0.89 | 7.01 | 0 | 0.90 |
| Same as last year | 0.473 | −0.295 | 0.90 | 8.48 | −0.265 | 0.91 |
| Fall rain | 0.368 | −0.034 | 0.89 | 7.03 | −0.014 | 0.90 |
| Winter temp. / growing degree days | 0.379 | −0.045 | 0.91 | 6.56 | +0.114 | 0.91 |
| Ridge | 0.400 | −0.100 | 0.90 | 6.65 | +0.077 | 0.90 |
| Elastic net | 0.365 | −0.059 | 0.90 | 6.74 | +0.076 | 0.90 |
| LightGBM, default | 0.454 | −0.208 | 0.90 | 7.15 | +0.088 | 0.91 |
| LightGBM, tuned | 0.387 | −0.049 | 0.90 | 6.81 | +0.003 | 0.90 |
| Bayesian hierarchical | 0.443 | −0.236 | 0.92 | 6.61 | +0.109 | 0.88 |

- **Question 2:** mean per-spring difference in MSE, winter temperature minus fall rain, +0.011 (95% CI −0.018 to +0.043); with 2016 added, +0.014 (−0.013 to +0.039). Hierarchical fall-rain coefficient +0.069 logit per SD (90% interval −0.048 to +0.183), winter temperature −0.075 (−0.249 to +0.085).
- **Question 3:** mean per-spring difference in MAE, fall rain minus growing degree days, +0.78 days (95% CI +0.15 to +1.48). Hierarchical growing-degree-day coefficient −2.1 days per SD (90% interval −4.3 to +0.1).
- **Question 5:** in the eight counties with a median under 50 records per spring, RMSE 0.449 (hierarchical) against 0.418 (per-county regression).
- **Question 6:** with 143 and 82 held-out rows, the sampling standard deviation of a coverage near 0.8 is about 0.03 and 0.04, so the excess over 0.90 (at most 0.016) is within sampling error.
- **LightGBM search:** the best cell was learning rate 0.03, 100 trees, at least 30 rows per leaf; the least constrained cell had size RMSE 0.524.

### D. Decisions

| Decision | Reason |
|---|---|
| Bluebonnet records divided by all plant records | iNaturalist effort grew about forty-fold |
| Uploads by 15 May of the same spring only | 2027 will be measured on 15 May 2027 |
| City Nature Challenge days removed | One event supplied 20.5% of records |
| Every record in the window counts as flowering | The Flowering annotation's use grew over time |
| Median date rather than peak | Weekly county counts are too irregular for a maximum |
| County inclusion rule fixed before county counts were computed | A rule chosen afterward could select agreeing counties |
| Hide whole springs; resample springs for ranges | All counties share a spring's weather and observers |
| The Bayesian model fixed as the forecast model in advance | Choosing it after seeing the comparison would undo the registration |
| El Niño analog seasons since 1951, whole seasons, one per draw for all counties | Keeps the correlation between months and between counties |
| Trend forecast added beside the registered one, not instead of it | The trend was found after the plan was written |
| Forecast samples and grading code committed with the forecast | The scoring rules must exist before the outcome |
| Only aggregate counts published | Individual observations carry their observers' licences |

### E. Reproduction

- **Code, plan, news classifications, forecasts:** [github.com/kvenanzi/bluebonnet](https://github.com/kvenanzi/bluebonnet). Thirteen numbered scripts go from the public APIs to the forecast and, in May, the grade.
- **Dataset:** [kvenanzi/texas-bluebonnet-seasons](https://huggingface.co/datasets/kvenanzi/texas-bluebonnet-seasons) (county-spring counts and weather, the plan, every forecast with its samples).
- **Model:** [kvenanzi/bluebonnet-bloom-forecast](https://huggingface.co/kvenanzi/bluebonnet-bloom-forecast).
- **Forecast fingerprints:** `forecast-2026-10.csv` has SHA-256 `ffa92e6e90e161e9ca23b0980f72176eca06bfe81fc21be3af4436fdc5be3a7c`, and its samples file `bd2746bcb99b5e605ba24b9a6cc98f683eafe79bec4c5829dbda5ec3687adeae`, both at git tag `forecast-2026-10`.
- **Runs:** [`figures/runs.json`](figures/runs.json) lists all 48 runs with their settings and results, exported on 4 November 2026 from Weights & Biases, where they were tracked.
- **Cost:** about an hour of API time for the data, then a laptop CPU: 100 seconds for all the models, 47 seconds for the search, a few minutes for the Bayesian fits.

## How this was made

I chose the question, set the rules, and edited the text. Claude Code wrote the code, ran the analysis, found the references, and drafted the post.

I have not read the cited papers myself. Claude checked each citation against its source: against the full text where an open copy existed, and against the abstract for Beatley 1974, Turner et al 2018, Ropelewski & Halpert 1986, McMaster & Wilhelm 1997, Hoerl & Kennard 1970, and Park & Mazer 2018. Sentences the sources did not fully support were narrowed or removed.

## References

**The plant and other wildflowers**

- Beatley JC (1974). "Phenological events and their environmental triggers in Mojave Desert ecosystems". *Ecology* 55(4):856–863. [doi:10.2307/1934421](https://doi.org/10.2307/1934421)
- Davis TD, George SW, Upadhyaya A, Parsons J (1991). "Improvement of seedling emergence of *Lupinus texensis* Hook. following seed scarification treatments". *Journal of Environmental Horticulture* 9(1):17–21. [doi:10.24266/0738-2898-9.1.17](https://doi.org/10.24266/0738-2898-9.1.17)
- McMaster GS, Wilhelm WW (1997). "Growing degree-days: one equation, two interpretations". *Agricultural and Forest Meteorology* 87(4):291–300. [doi:10.1016/S0168-1923(97)00027-0](https://doi.org/10.1016/S0168-1923(97)00027-0)
- Ropelewski CF, Halpert MS (1986). "North American precipitation and temperature patterns associated with the El Niño/Southern Oscillation (ENSO)". *Monthly Weather Review* 114(12):2352–2362. [doi:10.1175/1520-0493(1986)114<2352:NAPATP>2.0.CO;2](https://doi.org/10.1175/1520-0493(1986)114%3C2352:NAPATP%3E2.0.CO;2)
- Turner KG, Huang DI, Cronk QCB, Rieseberg LH (2018). "Homogenization of populations in the wildflower, Texas bluebonnet (*Lupinus texensis*)". *Journal of Heredity* 109(2):152–161. [doi:10.1093/jhered/esx094](https://doi.org/10.1093/jhered/esx094)

**Measuring with citizen-science photographs**

- Callaghan CT, Poore AGB, Hofmann M, Roberts CJ, Pereira HM (2021). "Large-bodied birds are over-represented in unstructured citizen science data". *Scientific Reports* 11:19073. [doi:10.1038/s41598-021-98584-7](https://doi.org/10.1038/s41598-021-98584-7)
- Phillips SJ, Dudík M, Elith J, Graham CH, Lehmann A, Leathwick J, Ferrier S (2009). "Sample selection bias and presence-only distribution models: implications for background and pseudo-absence data". *Ecological Applications* 19(1):181–197. [doi:10.1890/07-2153.1](https://doi.org/10.1890/07-2153.1)

**Methods and software**

- Abril-Pla O, et al (2023). "PyMC: a modern, and comprehensive probabilistic programming framework in Python". *PeerJ Computer Science* 9:e1516. [doi:10.7717/peerj-cs.1516](https://doi.org/10.7717/peerj-cs.1516)
- Barber RF, Candès EJ, Ramdas A, Tibshirani RJ (2021). "Predictive inference with the jackknife+". *The Annals of Statistics* 49(1):486–507. [doi:10.1214/20-AOS1965](https://doi.org/10.1214/20-AOS1965)
- Gelman A (2006). "Multilevel (hierarchical) modeling: what it can and cannot do". *Technometrics* 48(3):432–435. [doi:10.1198/004017005000000661](https://doi.org/10.1198/004017005000000661)
- Gneiting T, Raftery AE (2007). "Strictly proper scoring rules, prediction, and estimation". *Journal of the American Statistical Association* 102(477):359–378. [doi:10.1198/016214506000001437](https://doi.org/10.1198/016214506000001437)
- Hoerl AE, Kennard RW (1970). "Ridge regression: biased estimation for nonorthogonal problems". *Technometrics* 12(1):55–67. [doi:10.1080/00401706.1970.10488634](https://doi.org/10.1080/00401706.1970.10488634)
- Hoffman MD, Gelman A (2014). "The No-U-Turn Sampler: adaptively setting path lengths in Hamiltonian Monte Carlo". *Journal of Machine Learning Research* 15:1593–1623. [jmlr.org/papers/v15/hoffman14a.html](https://jmlr.org/papers/v15/hoffman14a.html)
- Ke G, Meng Q, Finley T, Wang T, Chen W, Ma W, Ye Q, Liu T-Y (2017). "LightGBM: a highly efficient gradient boosting decision tree". *Advances in Neural Information Processing Systems 30*:3146–3154. [papers.nips.cc](https://papers.nips.cc/paper/6907-lightgbm-a-highly-efficient-gradient-boosting-decision-tree)
- Nosek BA, Ebersole CR, DeHaven AC, Mellor DT (2018). "The preregistration revolution". *Proceedings of the National Academy of Sciences* 115(11):2600–2606. [doi:10.1073/pnas.1708274114](https://doi.org/10.1073/pnas.1708274114)
- Park IW, Mazer SJ (2018). "Overlooked climate parameters best predict flowering onset: assessing phenological models using the elastic net". *Global Change Biology* 24(12):5972–5984. [doi:10.1111/gcb.14447](https://doi.org/10.1111/gcb.14447)
- Vehtari A, Gelman A, Simpson D, Carpenter B, Bürkner P-C (2021). "Rank-normalization, folding, and localization: an improved R̂ for assessing convergence of MCMC". *Bayesian Analysis* 16(2):667–718. [doi:10.1214/20-BA1221](https://doi.org/10.1214/20-BA1221)
- Zou H, Hastie T (2005). "Regularization and variable selection via the elastic net". *Journal of the Royal Statistical Society: Series B* 67(2):301–320. [doi:10.1111/j.1467-9868.2005.00503.x](https://doi.org/10.1111/j.1467-9868.2005.00503.x)
