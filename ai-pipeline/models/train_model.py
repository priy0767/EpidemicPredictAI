import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import json
import os

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

# Fetch Johns Hopkins Data once (it contains all countries)
print("Downloading Johns Hopkins Global Case Data...")
JHU_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
global_cases = pd.read_csv(JHU_URL)

successful_countries = []

# Loop through each country and build a dedicated AI brain
for country_name, country_code in country_mapping.items():
    print(f"\n==================================================")
    print(f"🌍 Initiating Pipeline for: {country_name} ({country_code})")
    
    # --- A. CLEAN CASE DATA ---
    # Fix dataset naming mismatches (JHU uses different names than Google)
    jhu_name = country_name
    if country_name == 'USA': jhu_name = 'US'
    elif country_name == 'UK': jhu_name = 'United Kingdom'
    elif country_name == 'South Korea': jhu_name = 'Korea, South'
    elif country_name == 'Taiwan': jhu_name = 'Taiwan*'
    elif country_name == 'Myanmar (Burma)': jhu_name = 'Burma'
    elif country_name == 'Côte dIvoire': jhu_name = "Cote d'Ivoire"

    # Safety check: Does JHU actually track this country?
    if jhu_name not in global_cases['Country/Region'].values:
        print(f"⚠️ Skipping {country_name}: Not found in JHU database.")
        continue

    country_cases = global_cases[global_cases['Country/Region'] == jhu_name].copy()
    
    # If a country has states/provinces in the dataset (like the US), sum them up
    country_cases = country_cases.drop(columns=['Province/State', 'Lat', 'Long']).groupby('Country/Region').sum().reset_index()
    
    country_long = country_cases.melt(id_vars=['Country/Region'], var_name='Date', value_name='Total_Cases')
    country_long['Date'] = pd.to_datetime(country_long['Date'])
    country_long = country_long.sort_values('Date').reset_index(drop=True)
    country_long['Daily_Cases'] = country_long['Total_Cases'].diff().fillna(0)
    country_long['Daily_Cases'] = country_long['Daily_Cases'].apply(lambda x: max(x, 0))

    # --- B. LOAD LOCAL MOBILITY DATA ---
    print(f"Loading local mobility data for {country_code}...")
    mobility_files = [
        f"../data/2020_{country_code}_Region_Mobility_Report.csv",
        f"../data/2021_{country_code}_Region_Mobility_Report.csv",
        f"../data/2022_{country_code}_Region_Mobility_Report.csv"
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
    final_ml_df = master_df.dropna().copy()

    # Safety check: Is there enough data to train an AI?
    if len(final_ml_df) < 20:
        print(f"❌ Skipping {country_name}: Dataset too small after merging.")
        continue

    # --- D. TRAIN THE XGBOOST MODEL ---
    print(f"🧠 Training XGBoost Model for {country_name}...")
    ai_features = ['Daily_Cases_7d_Avg'] + [f"{f}_lag14" for f in features]
    X = final_ml_df[ai_features]
    y = final_ml_df['Target_Cases_Next_Week']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    error = mean_absolute_error(y_test, model.predict(X_test))
    print(f"📊 Model MAE: {int(error)} cases per day.")

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

print(f"\n🎉 GLOBAL MODEL FACTORY COMPLETE. Successfully built {len(successful_countries)} AI Brains.")