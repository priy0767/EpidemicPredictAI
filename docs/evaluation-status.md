# Model Evaluation Status

## Current status: leakage-aware evaluation implemented; real metrics not yet generated

The training script is located at `ai-pipeline/models/train_model.py`. It downloads the Johns Hopkins CSSE global confirmed-case time series, joins country-level Google mobility reports, engineers lagged mobility features, and fits one XGBoost regressor per eligible country.

The training pipeline now uses a chronological 80/20 holdout with a date-aware purge. A training row is retained only when its forward target window ends strictly before the first test feature date. This matters because each target is the seven-day rolling average shifted seven rows into the future. The date-based comparison also remains correct when missing mobility observations cause rows to be dropped.

For each eligible country, the script writes `evaluation_XX.json` with split dates, sample counts, number of purged training rows, model MAE/RMSE/R², persistence-baseline MAE/RMSE, and whether the model beats the baseline on MAE. These reports are generated when the training script is run; no new real-world performance values have been generated during this remote repository review.

## What the current script evaluates

- **Input features:** 7-day average daily cases and four mobility features derived from 7-day rolling means shifted by 14 rows.
- **Target:** the 7-day rolling average of daily cases shifted seven rows into the future (`Target_Cases_Next_Week`).
- **Split:** first 80% of eligible rows form the pre-test period; final 20% are test rows. Pre-test rows whose target end date reaches the test start are purged.
- **Model:** XGBoost regressor with 100 estimators, learning rate 0.1, max depth 5, and random state 42.
- **Primary metric:** MAE, with RMSE and R² also recorded where defined.
- **Baseline:** persistence of the current 7-day average daily-case feature, evaluated on exactly the same test rows.

## Remaining evaluation caveats

1. **No separate validation set.** This is a single chronological holdout, not a complete train/validation/test model-selection workflow. Hyperparameters must not be tuned against this test set.
2. **One split is not a stability analysis.** Results may vary across countries and time periods. A later improvement should add rolling-origin evaluation with multiple forecast origins.
3. **Target interpretation matters.** The target is a next-week average daily case count, not a seven-day cumulative count and not a fourteen-day total.
4. **Missing mobility rows are dropped.** This can make the effective sample timeline irregular. The purge uses dates rather than assuming a fixed number of retained rows.
5. **Data reproducibility is incomplete.** The JHU data is downloaded from a moving GitHub URL at runtime, while mobility CSV files are expected locally. Pin data snapshots and record provenance/licensing before publishing results.
6. **No results have been independently reproduced here.** The generated reports must be reviewed for sample sizes, baseline comparisons, and plausibility before metrics are quoted in a portfolio.
7. **The forecast is an average daily count, not a cumulative total.** The API now returns the model's next-week average daily case count without multiplying by seven or fourteen. The global endpoint uses zero mobility inputs and identifies countries where a persistence baseline is used. The single-country endpoint derives its current seven-day average from historical rows.

## Run the split tests

From `ai-pipeline/models/`:

```bash
python -m unittest discover -s tests -v
```

The tests cover label-window purging, missing-row date behavior, unsorted input, and invalid split fractions.

## Next evaluation improvements

1. Pin exact JHU and Google mobility data snapshots and record source dates/checksums.
2. Add an earlier validation period and rolling-origin evaluation.
3. Compare against persistence and rolling-mean baselines at each forecast origin.
4. Report metrics by country and across forecast origins, with sample counts and date ranges.
5. Save the complete data version, package versions, and model configuration alongside every report.

Do not describe the models as highly accurate or production-validated until the generated results are reproducible and demonstrate value over a simple baseline.
