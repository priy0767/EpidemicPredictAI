import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import main as api


class FakeModel:
    def predict(self, frame):
        # The API must pass the same feature schema used by training.
        expected = {
            "Daily_Cases_7d_Avg",
            "retail_and_recreation_percent_change_from_baseline_lag14",
            "transit_stations_percent_change_from_baseline_lag14",
            "workplaces_percent_change_from_baseline_lag14",
            "residential_percent_change_from_baseline_lag14",
        }
        assert set(frame.columns) == expected
        return [11.9]


class ForecastApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.db_path = root / "test.db"
        self.model_dir = root / "models"
        self.model_dir.mkdir()
        self.client = TestClient(api.app)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE historical_cases (
                    Country TEXT NOT NULL,
                    Date TEXT NOT NULL,
                    Daily_Cases REAL NOT NULL,
                    Total_Cases REAL NOT NULL
                )
                """
            )
            rows = [
                ("India", f"2021-11-{day:02d}", float(day), float(day * 100))
                for day in range(1, 9)
            ]
            conn.executemany(
                "INSERT INTO historical_cases VALUES (?, ?, ?, ?)", rows
            )

        (self.model_dir / "model_IN.pkl").touch()
        api.DATABASE_PATH = self.db_path
        api.MODEL_DIR = self.model_dir

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_single_country_prediction_uses_recent_seven_day_average(self):
        with patch.object(api.joblib, "load", return_value=FakeModel()):
            response = self.client.post(
                "/api/predict",
                json={
                    "country": "India",
                    "region": "All",
                    "target_date": "2021-11-08",
                    "retail_recreation_lag14": 0,
                    "transit_stations_lag14": 0,
                    "workplaces_lag14": 0,
                    "residential_lag14": 0,
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["predicted_cases_next_week_average_daily"], 11)
        self.assertEqual(payload["prediction_unit"], "cases_per_day")
        self.assertEqual(payload["prediction_horizon_days"], 7)
        self.assertEqual(payload["input_daily_cases_7d_average"], 4.0)
        self.assertEqual(payload["trend_data"][-1]["date"], "Next 7-day average")

    def test_mobility_values_outside_allowed_range_are_rejected(self):
        response = self.client.post(
            "/api/predict",
            json={
                "country": "India",
                "region": "All",
                "target_date": "2021-11-08",
                "retail_recreation_lag14": 999,
                "transit_stations_lag14": 0,
                "workplaces_lag14": 0,
                "residential_lag14": 0,
            },
        )
        self.assertEqual(response.status_code, 422)

    def test_global_forecast_has_consistent_units_and_labels_fallback(self):
        with patch.object(api.joblib, "load", return_value=FakeModel()):
            response = self.client.get(
                "/api/global_predictions?target_date=2021-11-08"
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["metric"], "next_week_average_daily_cases")
        self.assertEqual(payload["unit"], "cases_per_day")
        self.assertEqual(payload["horizon_days"], 7)
        self.assertEqual(payload["predictions"]["India"], 11)
        self.assertIn("fallback_countries", payload)
        self.assertIn("Afghanistan", payload["fallback_countries"])

    def test_invalid_date_is_rejected(self):
        response = self.client.get(
            "/api/global_predictions?target_date=not-a-date"
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
