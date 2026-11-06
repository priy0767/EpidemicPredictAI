# Known Limitations and Follow-up Work

These notes are based on inspection of the checked-in API and README. They are not a complete security or scientific validation audit.

## Modeling and interpretation

- The training script is `ai-pipeline/models/train_model.py`. It depends on local Google mobility CSV files and downloads a moving Johns Hopkins dataset URL at runtime, so exact data provenance and reproducibility are not yet guaranteed.
- The training script now applies a date-aware purge: training target windows must end before the first test feature date. The helper has unit tests for overlapping windows, missing rows, unsorted data, and invalid split fractions.
- The script writes per-country JSON reports with split dates, sample counts, model MAE/RMSE/R², and a persistence baseline. These reports have not yet been generated against the full local datasets in this remote review.
- The pipeline still has no separate validation set or multi-origin rolling evaluation; do not tune against the test set.
- The previous hand-written scenario blend has been removed; single-country forecasts now use the trained model output directly. Mobility slider values are hypothetical user inputs, not observed future mobility.
- The global prediction endpoint passes zero-valued mobility features and may fall back to a simple baseline when model files or usable cases are missing.
- The forecast target is the next-week average daily case count, not a seven-day cumulative total or fourteen-day total. Do not relabel or rescale it as either.
- The global prediction endpoint uses zero mobility inputs and falls back to the latest seven-day average when model inference is unavailable. Fallback countries are exposed in the response, but the UI should make fallback status visible to users.
- The choropleth's color bands are presentation thresholds, not validated epidemiological risk categories.
- Feature importance indicates model reliance under a particular model/data setup; it does not establish causality.
- The app should not be used for medical decisions or public-health policy.

## Data and validation

- Dataset source/version, cleaning, missing-value handling, geographic mapping, and temporal coverage need reproducible documentation.
- Time-series evaluation must preserve chronological order and prevent future leakage in rolling and lagged features. The current holdout purges overlapping forward target windows by comparing actual dates, rather than assuming a fixed row gap.
- The training script now records MAE, RMSE, R², and persistence-baseline metrics in per-country JSON reports, but no full-dataset run has been independently reproduced during this review.

## API and security

- The API now uses an explicit CORS allowlist from `CORS_ORIGINS`, defaulting to local Vite origins. Production deployments must set this variable to the exact frontend origin(s), or browser requests from the deployed frontend will fail.
- SQL query values are now parameterized in the inspected endpoints.
- Database connections use context managers and database failures return controlled HTTP 500 responses.
- Date fields and mobility inputs have request validation; mobility percentages are constrained to a documented broad range.
- Global inference still falls back to a simple baseline when a model cannot be used; this behavior should be surfaced clearly in the API response rather than silently presented as a model forecast.
- Pin and audit dependencies; the current requirements file lists only a small subset of runtime packages.

## Operational and repository hygiene

- Verify that the relative model/database paths work both locally and in deployment.
- Avoid committing generated datasets and model artifacts unless their size, provenance, and redistribution rights are understood.
- Add automated tests for API schemas, country-code mapping, SQL query behavior, missing models, and prediction calculations.
- Add a documented data/model version and artifact checksum strategy.
