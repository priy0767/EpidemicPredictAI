from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import sqlite3
import json
import os

print("🚀 Starting Epidemic Predict Pro GLOBAL API (Massive 130+ Edition)...")

app = FastAPI(title="Global Epidemic API")

# Set CORS_ORIGINS to a comma-separated list of deployed frontend origins.
# Local development remains available by default; credentials are not needed.
DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = Path(os.getenv("EPIDEMIC_DATABASE_PATH", str(Path(__file__).resolve().parent / "epidemic_data.db")))
MODEL_DIR = Path(os.getenv("EPIDEMIC_MODEL_DIR", str(PROJECT_ROOT / "ai-pipeline" / "models")))


# 1. THE MASSIVE HARDCODED DICTIONARY
COUNTRY_CODES = {
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

# Keep the detailed maps for major countries (Fallback for UI)
MAP_HOTSPOTS = {
    "India": [{"name": "Mumbai", "coords": [19.0760, 72.8777], "risk": "High", "color": "#ff4757", "radius": 25}],
    "USA": [{"name": "New York City", "coords": [40.7128, -74.0060], "risk": "High", "color": "#ff4757", "radius": 25}],
    "Brazil": [{"name": "São Paulo", "coords": [-23.5505, -46.6333], "risk": "High", "color": "#ff4757", "radius": 25}],
    "UK": [{"name": "London", "coords": [51.5074, -0.1278], "risk": "High", "color": "#ff4757", "radius": 20}],
    "Germany": [{"name": "Berlin", "coords": [52.5200, 13.4050], "risk": "Medium", "color": "#ffa502", "radius": 15}],
    "Italy": [{"name": "Rome", "coords": [41.9028, 12.4964], "risk": "High", "color": "#ff4757", "radius": 20}],
    "Russia": [{"name": "Moscow", "coords": [55.7558, 37.6173], "risk": "High", "color": "#ff4757", "radius": 20}],
    "France": [{"name": "Paris", "coords": [48.8566, 2.3522], "risk": "High", "color": "#ff4757", "radius": 20}],
    "Japan": [{"name": "Tokyo", "coords": [35.6762, 139.6503], "risk": "Medium", "color": "#ffa502", "radius": 20}],
    "South Africa": [{"name": "Cape Town", "coords": [-33.9249, 18.4241], "risk": "Medium", "color": "#ffa502", "radius": 15}],
    "Australia": [{"name": "Sydney", "coords": [-33.8688, 151.2093], "risk": "Low", "color": "#2ed573", "radius": 15}],
    "Canada": [{"name": "Toronto", "coords": [43.6510, -79.3470], "risk": "Medium", "color": "#ffa502", "radius": 15}]
}

class PredictionRequest(BaseModel):
    country: str
    region: str
    target_date: date
    retail_recreation_lag14: float = Field(ge=-100, le=200, allow_inf_nan=False)
    transit_stations_lag14: float = Field(ge=-100, le=200, allow_inf_nan=False)
    workplaces_lag14: float = Field(ge=-100, le=200, allow_inf_nan=False)
    residential_lag14: float = Field(ge=-100, le=200, allow_inf_nan=False)

# --- 1. ENDPOINT FOR DROPDOWN ---
@app.get("/api/countries")
def get_available_countries():
    """Tells React exactly what countries are available in our dictionary."""
    return {"countries": sorted(list(COUNTRY_CODES.keys()))}

# --- 2. ENDPOINT FOR THE SMALL REAL CASES CHOROPLETH MAP ---
@app.get("/api/map_snapshot")
def get_map_snapshot(target_date: date = Query(default=date(2021, 11, 5))):
    """Fetches the real cumulative cases for every country up to the target date"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            df = pd.read_sql_query(
                """
                SELECT Country, MAX(Total_Cases) AS Total
                FROM historical_cases
                WHERE Date <= ?
                GROUP BY Country
                """,
                conn,
                params=(target_date,),
            )
        snapshot = dict(zip(df["Country"], df["Total"]))
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail="Historical database query failed") from exc

    return {"snapshot": snapshot}

# --- 3. ENDPOINT FOR THE BIG AI PREDICTION MAP (HEAVY RUN) ---
@app.get("/api/global_predictions")
def get_global_predictions(target_date: date = Query(default=date(2021, 11, 5))):
    """Predicts next-week average daily cases for each country (not a cumulative 14-day total)."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            df = pd.read_sql_query(
                """
                SELECT Country, AVG(Daily_Cases) AS Daily_Cases_7d_Avg
                FROM (
                    SELECT Country, Daily_Cases,
                           ROW_NUMBER() OVER (PARTITION BY Country ORDER BY Date DESC) AS row_num
                    FROM historical_cases
                    WHERE Date <= ?
                )
                WHERE row_num <= 7
                GROUP BY Country
                """,
                conn,
                params=(target_date,),
            )
        recent_cases = dict(zip(df["Country"], df["Daily_Cases_7d_Avg"]))
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail="Historical database query failed") from exc

    predictions = {}
    
    for country_name, code in COUNTRY_CODES.items():
        db_name = country_name
        if country_name == 'USA': db_name = 'US'
        elif country_name == 'UK': db_name = 'United Kingdom'
        elif country_name == 'South Korea': db_name = 'Korea, South'
        elif country_name == 'Taiwan': db_name = 'Taiwan*'
        
        baseline_cases = recent_cases.get(db_name, 0)
        model_path = MODEL_DIR / f"model_{code}.pkl"
        
        if model_path.is_file() and baseline_cases > 0:
            try:
                model = joblib.load(model_path)
                input_df = pd.DataFrame([{
                    'Daily_Cases_7d_Avg': baseline_cases,
                    'retail_and_recreation_percent_change_from_baseline_lag14': 0,
                    'transit_stations_percent_change_from_baseline_lag14': 0,
                    'workplaces_percent_change_from_baseline_lag14': 0,
                    'residential_percent_change_from_baseline_lag14': 0
                }])
                daily_pred = max(0, int(model.predict(input_df)[0]))
                predictions[country_name] = daily_pred 
            except (OSError, ValueError, EOFError):
                predictions[country_name] = max(0, int(baseline_cases))
        else:
            predictions[country_name] = int(baseline_cases * 14)
            
    return {"metric": "next_week_average_daily_cases", "unit": "cases_per_day", "horizon_days": 7, "predictions": predictions}

# --- 4. ENDPOINT FOR THE SLIDERS & CHARTS ---
@app.post("/api/predict")
def predict_cases(data: PredictionRequest):
    if data.country not in COUNTRY_CODES:
        raise HTTPException(status_code=400, detail="Country not supported")
        
    code = COUNTRY_CODES[data.country]
    
    # A. LOAD AI BRAIN
    model_path = MODEL_DIR / f"model_{code}.pkl"
    if not model_path.is_file():
        raise HTTPException(status_code=500, detail=f"AI Model for {data.country} missing!")
    try:
        model = joblib.load(model_path)
    except (OSError, ValueError, EOFError) as exc:
        raise HTTPException(status_code=500, detail=f"Model artifact for {data.country} could not be loaded") from exc

    # B. LOAD FEATURE IMPORTANCE (No Fake Data Fallback)
    importance_path = MODEL_DIR / f"importance_{code}.json"
    feature_data = []
    if importance_path.is_file():
        try:
            with open(importance_path, 'r', encoding='utf-8') as f:
                feature_data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            raise HTTPException(status_code=500, detail="Feature importance artifact is invalid") from exc

    # C. TIME MACHINE SQL QUERY
    sql_name = data.country
    if data.country == 'USA': sql_name = 'US'
    elif data.country == 'UK': sql_name = 'United Kingdom'
    elif data.country == 'South Korea': sql_name = 'Korea, South'
    elif data.country == 'Taiwan': sql_name = 'Taiwan*'
    elif data.country == 'Myanmar (Burma)': sql_name = 'Burma'
    elif data.country == 'Côte dIvoire': sql_name = "Cote d'Ivoire"

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            history_df = pd.read_sql_query(
                """
                SELECT Date, Daily_Cases
                FROM historical_cases
                WHERE Country = ? AND Date <= ?
                ORDER BY Date DESC
                LIMIT 7
                """,
                conn,
                params=(sql_name, data.target_date.isoformat()),
            )
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail="Historical database query failed") from exc
    
    history_df = history_df.sort_values('Date').reset_index(drop=True)
    if len(history_df) < 7:
        raise HTTPException(status_code=422, detail='At least seven days of history are required for a forecast')
    daily_cases_7d_avg = float(history_df['Daily_Cases'].mean())
    
    trend_data = []
    for _, row in history_df.iterrows():
        short_date = "-".join(row['Date'].split('-')[1:])
        trend_data.append({
            "date": short_date,
            "actual": int(row['Daily_Cases']),
            "predicted": None
        })

    if not trend_data:
        trend_data = [{"date": "N/A", "actual": 0, "predicted": None}]

    # D. THE HYBRID AI PREDICTION ENGINE
    input_df = pd.DataFrame([{
        'Daily_Cases_7d_Avg': daily_cases_7d_avg,
        'retail_and_recreation_percent_change_from_baseline_lag14': data.retail_recreation_lag14,
        'transit_stations_percent_change_from_baseline_lag14': data.transit_stations_lag14,
        'workplaces_percent_change_from_baseline_lag14': data.workplaces_lag14,
        'residential_percent_change_from_baseline_lag14': data.residential_lag14
    }])

    # The model target is the next week's average daily cases. Do not multiply
    # this value by seven or fourteen, and do not blend it with an untrained
    # hand-written scenario formula.
    final_prediction = max(0, int(model.predict(input_df)[0]))

    last_actual_cases = trend_data[-1]["actual"]
    trend_data[-1]["predicted"] = None 
    
    trend_data.append({
        "date": "Next 7-day average",
        "actual": None,
        "predicted": final_prediction
    })

    safe_hotspots = MAP_HOTSPOTS.get(data.country, [{"name": f"{data.country} Region", "coords": [20.0, 0.0], "risk": "Medium", "color": "#ffa502", "radius": 15}])

    return {
        "status": "success",
        "predicted_cases_next_week_average_daily": final_prediction,
        "prediction_unit": "cases_per_day",
        "prediction_horizon_days": 7,
        "input_daily_cases_7d_average": round(daily_cases_7d_avg, 2),
        "feature_importance": feature_data,
        "trend_data": trend_data,
        "map_hotspots": safe_hotspots
    }