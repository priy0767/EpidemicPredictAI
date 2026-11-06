import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import json
import os
from pathlib import Path
from evaluation_utils import chronological_purged_split, rolling_origin_purged_splits

print("🚀 Starting the Epidemic Predict Pro Global Model Factory...")

# 1. THE MASSIVE HARDCODED DICTIONARY (No shortcuts)
country_mapping = {
    'United Arab Emirates': 'AE', 'Afghanistan': 'AF', 'Antigua and Barbuda': 'AG', 'Angola': 'AO', 
    'Argentina': 'AR', 'Austria': 'AT', 'Australia': 'AU', 'Aruba': 'AW', 'Bosnia and Herzegovina': 'BA', 
    'Barbados': 'BB', 'Bangladesh': 'BD', 'Belgium': 'BE', 'Burkina Faso': 'BF', 'Bulgaria': 'BG', 
    'Bahrain': 'BH', 'Benin': 'BJ', 'Bolivia': 'BO', 'Brazil': 'BR', 'Bahamas': 'BS', 'Botswana': 'BW', 
    'Belarus': 'BY', 'Belize': 'BZ', 'Canada': 'CA', 'Switzerland': 'CH', 'Côte dIvoire': 'CI', 
    'Chile': 'CL', 'Cameroon': 'CM', 'Colombia': 'CO', 'Costa Rica': 'CR', 'Cape Verde': 'CV', 
    'Czechia': 'CZ', 'Germany': 'DE', 'Denmark': 'DK', 'Dominican Republic': 'DO', 'Ecuador': 'EC', 
    'Estonia': 'EE', 'Egypt': 'EG', 'Spain': 'ES', 'Finland': 'FI', 'Fiji': 'FJ', 'France': 'FR', 
    'Gabon': 'GA', 'UK': 'GB', 'Georgia': 'GE', 'Ghana': 'GH', 'Greece': 'GR', 'Guatemala': 'GT', 
    'Guinea-Bissau': 'GW', 'Honduras': 'HN', 'Croatia': 'HR', 'Haiti': 'HT', 'Hungary': 'HU', 
    'Indonesia': 'ID', 'Ireland': 'IE', 'Israel': 'IL', 'India': 'IN', 'Iraq': 'IQ', 'Italy': 'IT', 
    'Jamaica': 'JM', 'Jordan': 'JO', 'Japan': 'JP', 'Kenya': 'KE', 'Kyrgyzstan': 'KG', 'Cambodia': 'KH', 
    'South Korea': 'KR', 'Kuwait': 'KW', 'Kazakhstan': 'KZ', 'Laos': 'LA', 'Lebanon': 'LB', 
    'Liechtenstein': 'LI', 'Sri Lanka': 'LK', 'Lithuania': 'LT', 'Luxembourg': 'LU', 'Latvia': 'LV', 
    'Libya': 'LY', 'Morocco': 'MA', 'Moldova': 'MD', 'North Macedonia': 'MK', 'Mali': 'ML', 
    'Myanmar (Burma)': 'MM', 'Mongolia': 'MN', 'Mauritania': 'MR', 'Malta': 'MT', 'Mauritius': 'MU', 
    'Mexico': 'MX', 'Malaysia': 'MY', 'Mozambique': 'MZ', 'Namibia': 'NA', 'Niger': 'NE', 'Nigeria': 'NG', 
    'Nicaragua': 'NI', 'Netherlands': 'NL', 'Norway': 'NO', 'Nepal': 'NP', 'New Zealand': 'NZ', 
    'Oman': 'OM', 'Panama': 'PA', 'Peru': 'PE', 'Papua New Guinea': 'PG', 'Philippines': 'PH', 
    'Pakistan': 'PK', 'Poland': 'PL', 'Puerto Rico': 'PR', 'Portugal': 'PT', 'Paraguay': 'PY', 
    'Qatar': 'QA', 'Romania': 'RO', 'Serbia': 'RS', 'Russia': 'RU', 'Rwanda': 'RW', 'Saudi Arabia': 'SA', 
    'Sweden': 'SE', 'Singapore': 'SG', 'Slovenia': 'SI', 'Slovakia': 'SK', 'Senegal': 'SN', 
    'El Salvador': 'SV', 'Togo': 'TG', 'Thailand': 'TH', 'Tajikistan': 'TJ', 'Turkey': 'TR', 
    'Trinidad and Tobago': 'TT', 'Taiwan': 'TW', 'Tanzania': 'TZ', 'Ukraine': 'UA', 'Uganda': 'UG', 
    'USA': 'US', 'Uruguay': 'UY', 'Venezuela': 'VE', 'Vietnam': 'VN', 'Yemen': 'YE', 'South Africa': 'ZA', 
    'Zambia': 'ZM', 'Zimbabwe': 'ZW'
}

# Load the public OWID daily country dataset downloaded by download_datasets.py.
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OWID_CASES_PATH = DATA_DIR / "owid-covid-data.csv"
if not OWID_CASES_PATH.exists():
    raise FileNotFoundError(
        f"{OWID_CASES_PATH} not found. Run: python download_datasets.py"
    )
print(f"Loading Our World in Data cases from {OWID_CASES_PATH}...")
global_cases = pd.read_csv(OWID_CASES_PATH, parse_dates=["date"])

successful_countries = []
evaluation_results = []

# Loop through each country and build a dedicated AI brain
for country_name, country_code in country_mapping.items():
    print(f"\n==================================================")
    print(f"🌍 Initiating Pipeline for: {country_name} ({country_code})")
    
    # --- A. CLEAN CASE DATA ---
    # OWID uses standardized location names; map legacy UI labels where needed.
    owid_name = {
        "USA": "United States",
        "UK": "United Kingdom",
        "Côte dIvoire": "Cote d'Ivoire",
        "South Korea": "South Korea",
        "Taiwan": "Taiwan",
        "Myanmar (Burma)": "Myanmar",
    }.get(country_name, country_name)

    country_cases = global_cases[global_cases["location"] == owid_name].copy()
    if country_cases.empty:
        print(f"⚠️ Skipping {country_name}: not found in OWID data.")
        continue

    country_cases["Date"] = pd.to_datetime(country_cases["date"], errors="coerce")
    country_cases["Total_Cases"] = pd.to_numeric(country_cases["total_cases"], errors="coerce")
    country_cases["Daily_Cases"] = pd.to_numeric(country_cases["new_cases"], errors="coerce")
    country_cases["Daily_Cases"] = country_cases["Daily_Cases"].clip(lower=0)
    country_long = (
        country_cases[["Date", "Total_Cases", "Daily_Cases"]]
        .dropna(subset=["Date", "Daily_Cases"])
        .sort_values("Date")
        .drop_duplicates(subset=["Date"], keep="last")
        .reset_index(drop=True)
    )
    if country_long.empty:
        print(f"⚠️ Skipping {country_name}: OWID has no usable daily case observations.")
        continue

    # --- B. LOAD LOCAL MOBILITY DATA ---
    print(f"Loading local mobility data for {country_code}...")
    mobility_files = [
        DATA_DIR / f"2020_{country_code}_Region_Mobility_Report.csv",
        DATA_DIR / f"2021_{country_code}_Region_Mobility_Report.csv",
        DATA_DIR / f"2022_{country_code}_Region_Mobility_Report.csv"
    ]
    
    df_list = []
    for file_path in mobility_files:
        if os.path.exists(file_path):
            df_list.append(pd.read_csv(file_path, low_memory=False))
        else:
            print(f"⚠️ Warning: Missing file {file_path}")
            
    if not df_list:
        print(f"❌ Skipping {country_name}: No mobility data found.")
        continue

    mobility_df = pd.concat(df_list, ignore_index=True)
    mobility_national = mobility_df[mobility_df['sub_region_1'].isnull()].copy()
    mobility_national['Date'] = pd.to_datetime(mobility_national['date'])
    
    cols_to_keep = [
        'Date', 'retail_and_recreation_percent_change_from_baseline',
        'transit_stations_percent_change_from_baseline', 'workplaces_percent_change_from_baseline',
        'residential_percent_change_from_baseline'
    ]
    
    # Check if country has the required mobility columns
    if not all(col in mobility_national.columns for col in cols_to_keep):
        print(f"❌ Skipping {country_name}: Missing core mobility columns.")
        continue
        
    mobility_clean = mobility_national[cols_to_keep]

    # --- C. MERGE & ENGINEER FEATURES ---
    master_df = pd.merge(country_long, mobility_clean, on='Date', how='left')
    master_df = master_df.sort_values('Date').reset_index(drop=True)
    master_df['Daily_Cases_7d_Avg'] = master_df['Daily_Cases'].rolling(window=7).mean()

    features = [
        'retail_and_recreation_percent_change_from_baseline',
        'transit_stations_percent_change_from_baseline',
        'workplaces_percent_change_from_baseline',
        'residential_percent_change_from_baseline'
    ]

    for col in features:
        master_df[f'{col}_lag14'] = master_df[col].rolling(window=7).mean().shift(14)

    master_df['Target_Cases_Next_Week'] = master_df['Daily_Cases_7d_Avg'].shift(-7)
    # Keep the date on which each forward-looking target becomes observable.
    # This is needed to purge training labels that overlap the test period.
    master_df['Target_End_Date'] = master_df['Date'].shift(-7)
    final_ml_df = master_df.dropna().copy()

    # Safety check: Is there enough data to train an AI?
    if len(final_ml_df) < 20:
        print(f"❌ Skipping {country_name}: Dataset too small after merging.")
        continue

    # --- D. TRAIN THE XGBOOST MODEL ---
    print(f"🧠 Training XGBoost Model for {country_name}...")
    ai_features = ['Daily_Cases_7d_Avg'] + [f"{f}_lag14" for f in features]
    # Chronological holdout with label-aware purging. Each target at date t
    # uses the next seven days; remove training rows whose target window reaches
    # the first test feature date. Date-based purging remains correct if rows
    # were removed because mobility observations were missing.
    try:
        train_df, test_df, purged_sample_count = chronological_purged_split(final_ml_df, 0.8)
    except ValueError as split_error:
        print(f"❌ Skipping {country_name}: {split_error}")
        continue

    if len(train_df) < 20 or test_df.empty:
        print(f"❌ Skipping {country_name}: Insufficient samples after purging boundary labels.")
        continue

    X_train = train_df[ai_features]
    y_train = train_df['Target_Cases_Next_Week']
    X_test = test_df[ai_features]
    y_test = test_df['Target_Cases_Next_Week']

    model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    test_predictions = model.predict(X_test)
    baseline_predictions = test_df['Daily_Cases_7d_Avg'].to_numpy()
    model_mae = mean_absolute_error(y_test, test_predictions)
    model_rmse = mean_squared_error(y_test, test_predictions) ** 0.5
    baseline_mae = mean_absolute_error(y_test, baseline_predictions)
    baseline_rmse = mean_squared_error(y_test, baseline_predictions) ** 0.5
    model_r2 = r2_score(y_test, test_predictions) if len(test_df) >= 2 else None

    # Expanding-window validation on three earlier, non-overlapping time windows.
    # The final 20% holdout above remains separate from this diagnostic.
    rolling_fold_results = []
    for fold_number, (fold_train, fold_test, fold_purged) in enumerate(
        rolling_origin_purged_splits(final_ml_df, start_fractions=(0.5, 0.6, 0.7), test_fraction=0.1),
        start=1
    ):
        if len(fold_train) < 20 or fold_test.empty:
            continue
        fold_model = xgb.XGBRegressor(
            n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42
        )
        fold_model.fit(fold_train[ai_features], fold_train["Target_Cases_Next_Week"])
        fold_predictions = fold_model.predict(fold_test[ai_features])
        fold_baseline = fold_test["Daily_Cases_7d_Avg"].to_numpy()
        fold_y = fold_test["Target_Cases_Next_Week"]
        fold_mae = mean_absolute_error(fold_y, fold_predictions)
        fold_baseline_mae = mean_absolute_error(fold_y, fold_baseline)
        rolling_fold_results.append({
            "fold": fold_number,
            "train_samples": int(len(fold_train)),
            "test_samples": int(len(fold_test)),
            "purged_train_samples": int(fold_purged),
            "train_end_date": fold_train["Date"].max().strftime("%Y-%m-%d"),
            "test_start_date": fold_test["Date"].min().strftime("%Y-%m-%d"),
            "test_end_date": fold_test["Date"].max().strftime("%Y-%m-%d"),
            "model_mae": float(fold_mae),
            "persistence_baseline_mae": float(fold_baseline_mae),
            "model_beats_baseline_mae": bool(fold_mae < fold_baseline_mae),
        })

    rolling_model_maes = [item["model_mae"] for item in rolling_fold_results]
    rolling_baseline_maes = [
        item["persistence_baseline_mae"] for item in rolling_fold_results
    ]

    evaluation = {
        "country": country_name,
        "country_code": country_code,
        "target": "next_week_average_daily_cases",
        "split_strategy": "chronological_80_20_with_forward_target_purge",
        "train_start_date": train_df['Date'].min().strftime('%Y-%m-%d'),
        "train_end_date": train_df['Date'].max().strftime('%Y-%m-%d'),
        "test_start_date": test_df['Date'].min().strftime('%Y-%m-%d'),
        "test_end_date": test_df['Date'].max().strftime('%Y-%m-%d'),
        "train_samples": int(len(train_df)),
        "test_samples": int(len(test_df)),
        "purged_train_samples": int(purged_sample_count),
        "model_mae": float(model_mae),
        "model_rmse": float(model_rmse),
        "model_r2": float(model_r2) if model_r2 is not None else None,
        "persistence_baseline_mae": float(baseline_mae),
        "persistence_baseline_rmse": float(baseline_rmse),
        "model_beats_baseline_mae": bool(model_mae < baseline_mae),
        "mae_ratio_to_persistence": float(model_mae / baseline_mae) if baseline_mae > 0 else None,
        "mae_improvement_vs_persistence_pct": (
            float((baseline_mae - model_mae) / baseline_mae * 100)
            if baseline_mae > 0 else None
        ),
        "rolling_origin_evaluation": {
            "strategy": "three_expanding_windows_before_final_20_percent_holdout",
            "fold_count": len(rolling_fold_results),
            "folds": rolling_fold_results,
            "mean_model_mae": (
                float(pd.Series(rolling_model_maes).mean()) if rolling_model_maes else None
            ),
            "mean_persistence_baseline_mae": (
                float(pd.Series(rolling_baseline_maes).mean())
                if rolling_baseline_maes else None
            ),
            "folds_beating_persistence": sum(
                item["model_beats_baseline_mae"] for item in rolling_fold_results
            ),
        },
        "feature_importance": {
            name: float(importance)
            for name, importance in zip(ai_features, model.feature_importances_)
        },
        "xgboost_parameters": {
            "n_estimators": 100, "learning_rate": 0.1, "max_depth": 5, "random_state": 42
        }
    }
    evaluation_results.append(evaluation)
    with open(f'evaluation_{country_code}.json', 'w') as f:
        json.dump(evaluation, f, indent=2)

    print(
        f"📊 {country_name} | Model MAE: {model_mae:.2f} | "
        f"Persistence MAE: {baseline_mae:.2f} | "
        f"Test samples: {len(test_df)}"
    )

    # --- E. EXPORT PRODUCTION ASSETS ---
    joblib.dump(model, f'model_{country_code}.pkl')
    
    importance_data = []
    importances = model.feature_importances_
    for i, col_name in enumerate(ai_features):
        if col_name != 'Daily_Cases_7d_Avg': 
            clean_name = col_name.replace('_percent_change_from_baseline_lag14', '').replace('_', ' ').title()
            importance_data.append({
                "name": clean_name,
                "impact": round(float(importances[i]) * 100, 2)
            })
            
    with open(f'importance_{country_code}.json', 'w') as f:
        json.dump(importance_data, f)
        
    print(f"✅ {country_name} AI Engine and JSON data saved successfully!")
    successful_countries.append(country_name)

if evaluation_results:
    valid_ratios = [
        item["mae_ratio_to_persistence"]
        for item in evaluation_results
        if item["mae_ratio_to_persistence"] is not None
    ]
    summary = {
        "trained_country_count": len(evaluation_results),
        "countries_beating_persistence": sum(
            item["model_beats_baseline_mae"] for item in evaluation_results
        ),
        "countries_not_beating_persistence": sum(
            not item["model_beats_baseline_mae"] for item in evaluation_results
        ),
        "median_mae_ratio_to_persistence": (
            float(pd.Series(valid_ratios).median()) if valid_ratios else None
        ),
        "mean_mae_ratio_to_persistence": (
            float(pd.Series(valid_ratios).mean()) if valid_ratios else None
        ),
        "total_test_samples": sum(item["test_samples"] for item in evaluation_results),
        "interpretation": (
            "A ratio below 1.0 means XGBoost has lower MAE than persistence. "
            "A ratio above 1.0 means persistence performed better."
        ),
    }
    with open("evaluation_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(
        f"📈 Evaluation summary: {summary['countries_beating_persistence']}/"
        f"{summary['trained_country_count']} countries beat persistence; "
        f"median MAE ratio={summary['median_mae_ratio_to_persistence']:.3f}"
    )

print(f"\n🎉 GLOBAL MODEL FACTORY COMPLETE. Successfully built {len(successful_countries)} AI Brains.")