# Model Evaluation Status

## Current status: not yet independently verified

This repository contains country-specific XGBoost model artifacts and feature-importance JSON files. The API loads these artifacts for inference. However, the training/evaluation code needed to establish their performance was not located at the path documented in the previous README.

For that reason, this repository documentation intentionally does not publish MAE, RMSE, R², MAPE, accuracy, or claims such as "high accuracy". Artifact presence alone is not evidence of predictive performance.

## Evidence required before publishing metrics

- Exact dataset sources, versions, date coverage, and licensing.
- Target definition (for example, daily cases versus a multi-day cumulative target).
- Exact feature-generation code, including rolling windows and lag alignment.
- Chronological train/validation/test split with dates recorded.
- Proof that no future observations enter training features.
- Model configuration and random seed.
- Metrics on an untouched chronological test period.
- A baseline using persistence or a suitable historical average.
- Per-country sample counts and metric aggregation method.
- Reproducible commands and dependency versions.

## Recommended evaluation protocol

1. Sort observations by country and date.
2. Construct every feature using information available strictly before its prediction timestamp.
3. Reserve the latest contiguous time interval as the test set; do not randomly shuffle time-series rows.
4. Tune model parameters only on earlier training/validation periods.
5. Compare XGBoost against a persistence baseline and a rolling-mean baseline.
6. Report MAE and RMSE in the target's original units, and R² where meaningful.
7. If using percentage metrics, explicitly handle zero and near-zero targets; MAPE can be misleading in those cases.
8. Report results by country and provide sample counts instead of hiding variation in one global average.

## Reporting template

| Evaluation item | Result |
|---|---|
| Dataset/version | Pending audit |
| Target and forecast horizon | Pending audit |
| Train dates | Pending audit |
| Validation dates | Pending audit |
| Test dates | Pending audit |
| Baseline MAE / RMSE | Pending evaluation |
| Model MAE / RMSE | Pending evaluation |
| R² | Pending evaluation |
| Number of test observations | Pending evaluation |

Replace the pending entries only with reproducible measurements from the audited pipeline.
