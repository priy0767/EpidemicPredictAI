import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import download_datasets


class DatasetDownloaderTests(unittest.TestCase):
    def test_mobility_download_writes_only_national_rows_for_supported_years(self):
        source = pd.DataFrame({
            "country_region_code": ["IN", "IN", "IN", "US"],
            "country_region": ["India", "India", "India", "United States"],
            "sub_region_1": [None, "Delhi", None, None],
            "date": ["2020-02-15", "2020-02-15", "2023-01-01", "2021-03-01"],
            "retail_and_recreation_percent_change_from_baseline": [-10, -20, -5, -8],
            "transit_stations_percent_change_from_baseline": [-15, -25, -4, -9],
            "workplaces_percent_change_from_baseline": [-5, -10, -3, -6],
            "residential_percent_change_from_baseline": [4, 8, 2, 3],
        })
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(download_datasets.pd, "read_csv", return_value=source):
                paths = download_datasets.download_mobility_data(
                    country_codes=["IN"], output_dir=directory
                )

            self.assertEqual(len(paths), 1)
            self.assertEqual(Path(paths[0]).name, "2020_IN_Region_Mobility_Report.csv")
            saved = pd.read_csv(paths[0])
            self.assertEqual(len(saved), 1)
            self.assertEqual(saved.iloc[0]["country_region_code"], "IN")
            self.assertTrue(pd.isna(saved.iloc[0]["sub_region_1"]))

    def test_mobility_download_rejects_unexpected_source_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(download_datasets.pd, "read_csv", return_value=pd.DataFrame({"date": []})):
                with self.assertRaisesRegex(ValueError, "missing columns"):
                    download_datasets.download_mobility_data(
                        country_codes=["IN"], output_dir=directory
                    )

    def test_mobility_download_fails_clearly_when_requested_country_is_absent(self):
        source = pd.DataFrame({
            "country_region_code": ["US"],
            "country_region": ["United States"],
            "sub_region_1": [None],
            "date": ["2021-03-01"],
            "retail_and_recreation_percent_change_from_baseline": [-8],
            "transit_stations_percent_change_from_baseline": [-9],
            "workplaces_percent_change_from_baseline": [-6],
            "residential_percent_change_from_baseline": [3],
        })
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(download_datasets.pd, "read_csv", return_value=source):
                with self.assertRaisesRegex(RuntimeError, "No country mobility files"):
                    download_datasets.download_mobility_data(
                        country_codes=["IN"], output_dir=directory
                    )


if __name__ == "__main__":
    unittest.main()
