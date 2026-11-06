# Model Evaluation Status

## Current status: training code found; performance not independently reproduced

The training script is located at `ai-pipeline/models/train_model.py`. It downloads the Johns Hopkins CSSE global confirmed-case time series, joins country-level Google mobility reports, engineers lagged mobility features, and fits one XGBoost regressor per eligible country.

The script creates a chronological 80/20 split with `shuffle=False` and prints mean absolute error (MAE) for each country. However, the repository does not contain a consolidated evaluation report, recorded split dates, baseline comparison, per-country sample counts, or a reproducible environment/data snapshot. The printed MAE values therefore cannot currently be independently verified or compared across runs. No MAE, RMSE, R², MAPE, or accuracy claims are published here.

## What the current script evaluates

- **Input features:** 7-day average daily cases and four mobility features derived from 7-day rolling means shifted by 14 days.
- **Target:** the 7-day rolling average of daily cases shifted seven rows into the future (`Target_Cases_Next_Week`).
- **Split:** first 80% of each country series for training and final 20% for testing, preserving row order.
- **Model:** XGBoost regressor with 100 estimators, learning rate 0.1, max depth 5, and random state 42.
- **Metric:** MAE, printed to the console in target units.

## Important evaluation caveats

1. **No embargo at the split boundary.** The target for a row uses the next seven days. Training rows near the 80% boundary can therefore have target windows that overlap the test period. Use a seven-day gap/purge at the boundary before treating the holdout as independent.
2. **No validation set.** The script uses one train/test split and does not perform hyperparameter selection on a separate validation interval.
3. **Missing mobility rows are dropped.** The merge and subsequent `dropna()` can change the timeline and sample count. Record missingness and the resulting date ranges per country.
4. **No baseline comparison.** Compare against a persistence or rolling-average forecast using exactly the same test timestamps.
5. **No saved evaluation artifact.** MAE is printed but not exported with country, date range, sample count, configuration, or data version.
6. **Data reproducibility is incomplete.** The JHU data is downloaded from a moving GitHub URL at runtime, while mobility CSV files are expected locally. Pin data snapshots and record provenance/licensing.
7. **The model target and API behavior differ in presentation.** The trained target is a next-week average daily case count. The API's global endpoint multiplies a predicted daily value by 14, which is not the model's trained target or a validated 14-day cumulative forecast.

## Recommended next evaluation pass

1. Pin exact JHU and Google mobility data snapshots and record source dates/checksums.
2. Sort each country series by date and preserve an explicit date column through feature construction.
3. Build lagged features using only observations available at forecast time.
4. Reserve the latest contiguous period for testing and purge at least seven target-overlap days at the train/test boundary.
5. Use an earlier validation interval for any model selection.
6. Compare XGBoost against persistence and rolling-mean baselines on identical test dates.
7. Report MAE and RMSE in original units, R² where meaningful, and sample counts/date ranges per country.
8. Save a machine-readable evaluation report alongside model artifacts.

## Reporting template

| Evaluation item | Result |
|---|---|
| Dataset/version and checksum | Not recorded |
| Target and horizon | Next-week average daily cases |
| Train/validation/test dates | Not recorded |
| Split-boundary purge | Not implemented |
| Baseline MAE / RMSE | Not evaluated |
| Model MAE / RMSE | Console MAE only; not independently reproduced |
| R² | Not evaluated |
| Test observations per country | Not recorded |

Do not describe the models as highly accurate or production-validated until this evaluation is reproducible.
