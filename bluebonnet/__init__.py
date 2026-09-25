"""Central Texas bluebonnet bloom: targets from iNaturalist, predictors from NOAA,
a ladder of models scored by leave-one-year-out, and a registered 2027 forecast."""

WANDB_PROJECT = "bluebonnet-bloom"
WANDB_ENTITY = "within-noise"
DATASET_ARTIFACT = "bluebonnet-seasons"
FORECAST_ARTIFACT = "bluebonnet-forecast"
MODEL_ARTIFACT = "bluebonnet-model"

TAXON_BLUEBONNET = 49564      # Lupinus texensis
TAXON_PLANTAE = 47126
PLACE_TEXAS = 18

TRAIN_SPRINGS = list(range(2017, 2027))   # preregistration §3
SENSITIVITY_SPRINGS = [2016]
SEASON = ("02-01", "04-30")               # observed window, month-day
UPLOAD_CUTOFF = "05-15"                   # created_d2, month-day of the same year

# City Nature Challenge observation days, masked from numerator and denominator
# (preregistration §2). Source: citynaturechallenge.org via Wikipedia's results table.
CNC_DAYS = {
    2016: ("2016-04-14", "2016-04-21"), 2017: ("2017-04-14", "2017-04-18"),
    2018: ("2018-04-27", "2018-04-30"), 2019: ("2019-04-26", "2019-04-29"),
    2020: ("2020-04-24", "2020-04-27"), 2021: ("2021-04-30", "2021-05-03"),
    2022: ("2022-04-29", "2022-05-02"), 2023: ("2023-04-28", "2023-05-01"),
    2024: ("2024-04-26", "2024-04-29"), 2025: ("2025-04-25", "2025-04-28"),
    2026: ("2026-04-24", "2026-04-27"),
}

# Forecast counties (preregistration §3): iNaturalist place id -> county FIPS (Texas 48xxx).
FORECAST_COUNTIES = {
    "Travis": 431, "Williamson": 2442, "Hays": 326, "Burnet": 1909,
    "Llano": 2735, "Blanco": 1767, "Bastrop": 441,
}
POOLED = "Central Texas"

MIN_RECORDS = 20          # inclusion: >= 20 records ...
MIN_SPRINGS = 6           # ... in >= 6 of the 10 training springs
MIN_POINT_RECORDS = 5     # point-model targets need >= 5 records
MIN_TIMING_RECORDS = 50   # timing target needs >= 50 records
BOOT_SEED = 20260925
