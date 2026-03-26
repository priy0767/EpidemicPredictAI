import pandas as pd
import sqlite3
import os

print("🗄️ Building Massive SQLite Historical Database for 130+ Countries...")

# 1. THE MASSIVE HARDCODED DICTIONARY (Matching the AI Factory exactly)
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

# 2. Fetch Johns Hopkins Data
print("Downloading Johns Hopkins Global Case Data...")
JHU_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
global_cases = pd.read_csv(JHU_URL)

# 3. Translate UI names to exact JHU names so we don't miss any data
target_jhu_names = []
for country_name in country_mapping.keys():
    jhu_name = country_name
    if country_name == 'USA': jhu_name = 'US'
    elif country_name == 'UK': jhu_name = 'United Kingdom'
    elif country_name == 'South Korea': jhu_name = 'Korea, South'
    elif country_name == 'Taiwan': jhu_name = 'Taiwan*'
    elif country_name == 'Myanmar (Burma)': jhu_name = 'Burma'
    elif country_name == 'Côte dIvoire': jhu_name = "Cote d'Ivoire"
    
    target_jhu_names.append(jhu_name)

# 4. Filter and clean the massive dataset
df_filtered = global_cases[global_cases['Country/Region'].isin(target_jhu_names)].copy()
df_filtered = df_filtered.drop(columns=['Province/State', 'Lat', 'Long']).groupby('Country/Region').sum().reset_index()

df_long = df_filtered.melt(id_vars=['Country/Region'], var_name='Date', value_name='Total_Cases')
df_long['Date'] = pd.to_datetime(df_long['Date'], format='mixed')
df_long = df_long.sort_values(['Country/Region', 'Date']).reset_index(drop=True)

df_long['Daily_Cases'] = df_long.groupby('Country/Region')['Total_Cases'].diff().fillna(0)
df_long['Daily_Cases'] = df_long['Daily_Cases'].apply(lambda x: max(x, 0))
df_long['Date'] = df_long['Date'].dt.strftime('%Y-%m-%d')
df_long = df_long.rename(columns={'Country/Region': 'Country'})

# 5. Build the SQLite Database
db_path = "epidemic_data.db"
conn = sqlite3.connect(db_path)

df_long.to_sql('historical_cases', conn, if_exists='replace', index=False)
conn.close()

print(f"✅ Database built successfully! Seeded full history for {len(df_filtered['Country/Region'].unique())} countries.")