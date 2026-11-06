"""Download public COVID-19 case and mobility data for model training.

Sources:
- Our World in Data: country/date case time series.
- Google Community Mobility Reports: historical mobility observations.

Google stopped updating mobility reports on 2022-10-15. The downloader
keeps only the 2020-2022 files expected by the current training pipeline.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OWID_URL = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
GOOGLE_MOBILITY_URL = "https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv"
MOBILITY_COLUMNS = [
    "retail_and_recreation_percent_change_from_baseline",
    "transit_stations_percent_change_from_baseline",
    "workplaces_percent_change_from_baseline",
    "residential_percent_change_from_baseline",
]


def download_case_data(output_dir=DATA_DIR):
    """Download OWID's complete historical COVID-19 CSV."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / "owid-covid-data.csv"
    print(f"Downloading OWID case data to {destination} ...")
    frame = pd.read_csv(OWID_URL, usecols=["iso_code", "location", "date", "new_cases", "total_cases"])
    frame.to_csv(destination, index=False)
    print(f"Saved {len(frame):,} rows.")
    return destination


def download_mobility_data(country_codes=None, output_dir=DATA_DIR):
    """Download Google's global mobility file and split by ISO-2/year."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print("Downloading Google's historical global mobility report ...")
    frame = pd.read_csv(GOOGLE_MOBILITY_URL, low_memory=False)
    required = {
        "country_region_code", "country_region", "sub_region_1", "date",
        *MOBILITY_COLUMNS,
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Google mobility file is missing columns: {sorted(missing)}")

    if country_codes is None:\n        country_codes = frame["country_region_code"].dropna().unique().tolist()\n    frame = frame[frame["country_region_code"].isin(country_codes)].copy()
    frame["Date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame = frame[frame["Date"].dt.year.isin([2020, 2021, 2022])]
    frame = frame[frame["sub_region_1"].isna()]
    frame = frame[["country_region_code", "sub_region_1", "date", "Date", *MOBILITY_COLUMNS]].dropna(subset=["Date"])

    saved = []
    for code in sorted(set(country_codes)):
        country = frame[frame["country_region_code"] == code]
        if country.empty:
            continue
        for year, yearly in country.groupby(country["Date"].dt.year):
            destination = output_dir / f"{year}_{code}_Region_Mobility_Report.csv"
            yearly.to_csv(destination, index=False)
            saved.append(destination)
    print(f"Saved {len(saved)} country-year mobility files.")
    if not saved:
        raise RuntimeError("No country mobility files were produced; check the source schema and ISO-2 codes.")
    return saved


def main():
    # Import the training mapping without starting model training.
    from country_codes import COUNTRY_CODES

    download_case_data()
    download_mobility_data(COUNTRY_CODES.values())


if __name__ == "__main__":
    main()
