"""Download public COVID-19 case and mobility data for model training.

Sources:
- Our World in Data's archived complete historical COVID-19 CSV.
- Google's archived Community Mobility Reports (last updated 2022-10-15).

The OWID legacy CSV is a historical snapshot, not a live feed. The downloader
keeps only national-level Google mobility observations from 2020-2022.
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
    """Download OWID's complete historical country/date CSV."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / "owid-covid-data.csv"
    print(f"Downloading OWID case data to {destination} ...")
    frame = pd.read_csv(
        OWID_URL,
        usecols=["iso_code", "location", "date", "new_cases", "total_cases"],
    )
    frame.to_csv(destination, index=False)
    print(f"Saved {len(frame):,} rows.")
    return destination


def download_mobility_data(country_codes=None, output_dir=DATA_DIR):
    """Download Google's global report and split national rows by ISO-2/year.

    If country_codes is omitted, all country codes present in the source are
    included. Pass a list to limit the download/output to selected countries.
    """
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

    if country_codes is None:
        country_codes = frame["country_region_code"].dropna().unique().tolist()
    country_codes = sorted(set(country_codes))
    frame = frame[frame["country_region_code"].isin(country_codes)].copy()
    frame["Date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame = frame[frame["Date"].dt.year.isin([2020, 2021, 2022])]
    frame = frame[frame["sub_region_1"].isna()]
    output_columns = [
        "country_region_code", "sub_region_1", "date", "Date", *MOBILITY_COLUMNS
    ]
    frame = frame[output_columns].dropna(subset=["Date"])

    saved = []
    for code in country_codes:
        country = frame[frame["country_region_code"] == code]
        for year, yearly in country.groupby(country["Date"].dt.year):
            destination = output_dir / f"{year}_{code}_Region_Mobility_Report.csv"
            yearly.to_csv(destination, index=False)
            saved.append(destination)

    print(f"Saved {len(saved)} country-year mobility files.")
    if not saved:
        raise RuntimeError(
            "No country mobility files were produced; check the source schema "
            "and requested ISO-2 country codes."
        )
    return saved


def main():
    download_case_data()
    # Download all available codes. The trainer independently selects the
    # countries it supports, so this script has no import-time training coupling.
    download_mobility_data()


if __name__ == "__main__":
    main()
