# Bluebonnet bloom forecast for Central Texas

Does fall rain predict the strength of the Texas bluebonnet (*Lupinus texensis*) bloom better than winter temperature does? This repository builds bloom targets from iNaturalist observations and predictors from NOAA weather for ten springs (2017–2026), tests that question with pre-registered hypotheses and a ladder of models scored by leave-one-year-out cross-validation, and issues a registered forecast for spring 2027 in seven Austin-area counties. The forecast is issued in October 2026, updated in December 2026 and March 2027, and graded in May 2027.

**Status:** Part I (study and October forecast) in progress.

- Pre-registration: [`docs/preregistration.md`](docs/preregistration.md) (committed before any model was fit)
- Independent year codes: [`docs/bloom-year-codes.md`](docs/bloom-year-codes.md)
- Registered forecasts: [`forecasts/`](forecasts/)
- Primers: [modeling](docs/modeling-primer.md), [phenology and data](docs/phenology-primer.md)
- Write-up: [`docs/post/README.md`](docs/post/README.md)

## Layout

```
bluebonnet/   package: inat, noaa (data), targets, features, models, bayes, eval, stats, forecast, wb, sweep
scripts/      numbered pipeline, 01 (fetch iNaturalist) to 13 (grade, May 2027)
notebooks/    01_sweep_colab.ipynb: the LightGBM W&B Sweep agent for Colab
sweeps/       W&B sweep configurations
forecasts/    registered forecasts; never edited after they are committed
docs/         pre-registration, year codes, primers, posts
tests/        pytest
data/         gitignored: raw API pulls (cached), interim tables, processed/seasons.parquet
outputs/      gitignored: model predictions, summaries, Hugging Face staging
```

## Setup and run

```bash
uv sync
uv run pytest
uv run scripts/01_fetch_inat.py        # iNaturalist; ~1 h cold (API latency), seconds from cache
uv run scripts/02_fetch_noaa.py        # nClimDiv, GHCN-Daily, ONI
uv run scripts/03_build_dataset.py     # data/processed/seasons.parquet
uv run scripts/04_upload_dataset.py    # W&B artifact bluebonnet-seasons
uv run scripts/05_ladder.py            # B0–M3 by leave-one-year-out
uv run scripts/07_sweep.py --create    # then run the agent in Colab (notebooks/01_sweep_colab.ipynb) or locally
uv run scripts/08_bayes.py             # M4, hierarchical Bayesian (about 10 minutes)
uv run scripts/06_hypotheses.py        # the pre-registered decision rules
uv run scripts/09_forecast.py --issue forecast-2026-10 --observed-through 2026-08
uv run scripts/11_figures.py
uv run scripts/10_publish_hf.py
```

## Where things run

| Step | Where | Why |
|---|---|---|
| Data pulls and dataset | local | cached API responses; nothing needs a GPU |
| Ladder, hierarchical model, forecast | local | seconds to minutes on a CPU |
| LightGBM sweep | Colab (or local) | exercises the W&B artifact hand-off; any agent can take cells |

Weights & Biases project: `within-noise/bluebonnet-bloom`.

## Data licensing

The published dataset contains aggregate counts per county and spring, not individual iNaturalist observations, photographs, or observer identities. NOAA data are in the public domain.
