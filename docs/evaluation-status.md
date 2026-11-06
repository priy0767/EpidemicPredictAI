# Model Evaluation Status

## Current status: evaluation implemented; real metrics not yet generated

The training script is located at `ai-pipeline/models/train_model.py`. It consumes the Our World in Data (OWID) historical country/date case CSV and country-level Google Community Mobility Reports. The companion `download_datasets.py` downloads and prepares these inputs.

OWID's legacy complete CSV remains available at the stable URL used by the downloader, but the legacy GitHub dataset was last updated on 19 August 2024 and is now archived. Google's Community Mobility Reports stopped updating on 15 October 2022. This pipeline is therefore for reproducible historical experimentation, not live epidemic surveillance. The downloader records the original source URLs in code; users should retain downloaded snapshots and record retrieval dates when reporting results.

The training pipeline uses a chronological 80/20 holdout with a date-aware purge. A training row is retained only when its forward target window ends strictly before the first test feature date. This matters because each target is the seven-day rolling average of daily cases shifted seven days into the future.

For each eligible country, the script writes `evaluation_XX.json` with split dates, sample counts, number of purged training rows, model MAE/RMSE/R², persistence-baseline MAE/RMSE, and whether the model beats the baseline on MAE. These reports are generated when the training script is run; no real-world performance values have yet been generated and verified in this repository.

## What the current script evaluates

- **Input features:** 7-day average daily cases and four mobility features derived from 7-day rolling means shifted by 14 days.
- **Target:** the 7-day rolling average of daily cases shifted seven days into the future (`Target_Cases_Next_Week`).
- **Split:** first 80% of eligible rows form the pre-test period; final 20% are test rows. Pre-test rows whose target end date reaches the test start are purged.
- **Model:** XGBoost regressor with 100 estimators, learning rate 0.1, max depth 5, and random state 42.
- **Primary metric:** MAE, with RMSE and R² also recorded where defined.
- **Baseline:** persistence of the current 7-day average daily-case feature, evaluated on exactly the same test rows.

## Remaining evaluation caveats

1. **No separate validation set.** This is a single chronological holdout, not a complete train/validation/test model-selection workflow. Hyperparameters must not be tuned against this test set.
2. **One split is not a stability analysis.** Results may vary across countries and time periods. A later improvement should add rolling-origin evaluation with multiple forecast origins.
3. **Target interpretation matters.** The target is a next-week average daily case count, not a seven-day cumulative count and not a fourteen-day total.
4. **Missing mobility rows are dropped.** This can make the effective sample timeline irregular. The purge uses dates rather than assuming a fixed number of retained rows.
5. **Historical source coverage.** OWID's legacy full CSV is archived (last updated 2024-08-19); Google's Community Mobility Reports ended on 2022-10-15. This dataset combination cannot support claims about current outbreaks or current mobility patterns.
6. **No results have been independently reproduced here.** Generated reports must be reviewed for sample sizes, baseline comparisons, and plausibility before metrics are quoted in a portfolio.
7. **Forecast unit.** The API returns the model's next-week average daily case count. The global endpoint uses zero mobility inputs and identifies countries where a persistence baseline is used. The single-country endpoint derives its current seven-day average from historical rows.

## Download and train

From the repository root:

```bash
cd backend
pip install -r requirements.txt
cd ../ai-pipeline/models
python download_datasets.py
python train_model.py
```

The downloader writes `ai-pipeline/data/owid-covid-data.csv` and national country/year mobility files. Run the tests from `ai-pipeline/models/`:

```bash
python -m unittest discover -s tests -v
```

Do not describe the models as highly accurate or production-validated until the generated results are reproducible and demonstrate value over a simple baseline.
