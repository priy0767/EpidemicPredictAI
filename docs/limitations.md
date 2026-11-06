# Known Limitations and Follow-up Work

These notes are based on inspection of the checked-in API and README. They are not a complete security or scientific validation audit.

## Modeling and interpretation

- The training script is `ai-pipeline/models/train_model.py`. It depends on local Google mobility CSV files and downloads a moving Johns Hopkins dataset URL at runtime, so exact data provenance and reproducibility are not yet guaranteed.
- Its chronological 80/20 split has no seven-day purge even though each target uses the following seven days; training target windows near the boundary can overlap the test period. It also has no separate validation set.
- The script prints per-country MAE but does not save split dates, sample counts, baseline comparisons, or a machine-readable evaluation report.
- The prediction endpoint averages a learned model output with a hand-written scenario formula. The scenario formula is not learned from the training data and its coefficients require justification and validation.
- The global prediction endpoint passes zero-valued mobility features and may fall back to a simple baseline when model files or usable cases are missing.
- Multiplying a daily prediction by 14 should not be presented as a validated 14-day trajectory without a clearly defined target and evaluation.
- Feature importance indicates model reliance under a particular model/data setup; it does not establish causality.
- The app should not be used for medical decisions or public-health policy.

## Data and validation

- Dataset source/version, cleaning, missing-value handling, geographic mapping, and temporal coverage need reproducible documentation.
- Time-series evaluation must preserve chronological order and prevent future leakage in rolling and lagged features. The current split should add a seven-day embargo/purge to prevent overlapping target windows across train and test.
- The training script prints holdout MAE, but no values have been independently reproduced or recorded in a versioned report; RMSE and R² are not calculated.

## API and security

- CORS is configured with wildcard origins. Production deployments should restrict origins to the actual frontend domains.
- SQL queries are assembled with string interpolation. Use parameterized queries to avoid SQL injection and quoting bugs.
- Database connections should be managed with context managers and predictable error handling.
- Broad exception handling in global inference hides the underlying error and silently substitutes a fallback. Log structured errors and expose safe diagnostics.
- Validate date formats and numeric ranges at the API boundary.
- Pin and audit dependencies; the current requirements file lists only a small subset of runtime packages.

## Operational and repository hygiene

- Verify that the relative model/database paths work both locally and in deployment.
- Avoid committing generated datasets and model artifacts unless their size, provenance, and redistribution rights are understood.
- Add automated tests for API schemas, country-code mapping, SQL query behavior, missing models, and prediction calculations.
- Add a documented data/model version and artifact checksum strategy.
