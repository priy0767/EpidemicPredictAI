import unittest

import pandas as pd

from evaluation_utils import chronological_purged_split


class ChronologicalPurgedSplitTests(unittest.TestCase):
    def setUp(self):
        dates = pd.date_range("2021-01-01", periods=30, freq="D")
        self.frame = pd.DataFrame({
            "Date": dates,
            "Target_End_Date": dates + pd.Timedelta(days=7),
            "feature": range(30),
        })

    def test_training_labels_end_before_test_starts(self):
        train, test, purged = chronological_purged_split(self.frame, 0.8)
        self.assertGreater(len(train), 0)
        self.assertGreater(len(test), 0)
        self.assertGreater(purged, 0)
        self.assertTrue((train["Target_End_Date"] < test["Date"].min()).all())

    def test_purge_uses_calendar_dates_after_missing_rows(self):
        sparse = self.frame.drop(index=[4, 8, 13, 18]).reset_index(drop=True)
        train, test, _ = chronological_purged_split(sparse, 0.8)
        self.assertTrue((train["Target_End_Date"] < test["Date"].min()).all())

    def test_rejects_unsorted_rows(self):
        unsorted = self.frame.iloc[::-1]
        with self.assertRaises(ValueError):
            chronological_purged_split(unsorted)

    def test_rejects_invalid_fraction(self):
        with self.assertRaises(ValueError):
            chronological_purged_split(self.frame, 1.0)


if __name__ == "__main__":
    unittest.main()
