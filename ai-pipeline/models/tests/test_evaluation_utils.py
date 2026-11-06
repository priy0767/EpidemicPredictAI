import unittest

import pandas as pd

from evaluation_utils import chronological_purged_split, rolling_origin_purged_splits


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


class RollingOriginPurgedSplitTests(unittest.TestCase):
    def setUp(self):
        dates = pd.date_range("2021-01-01", periods=100, freq="D")
        self.frame = pd.DataFrame({
            "Date": dates,
            "Target_End_Date": dates + pd.Timedelta(days=7),
            "feature": range(100),
        })

    def test_creates_ordered_non_overlapping_test_windows(self):
        folds = list(rolling_origin_purged_splits(self.frame))
        self.assertEqual(len(folds), 3)
        previous_test_end = None
        for train, test, purged in folds:
            self.assertTrue((train["Target_End_Date"] < test["Date"].min()).all())
            if previous_test_end is not None:
                self.assertGreater(test["Date"].min(), previous_test_end)
            previous_test_end = test["Date"].max()
            self.assertGreater(len(train), 0)
            self.assertGreater(len(test), 0)
            self.assertGreater(purged, 0)

    def test_expanding_training_windows_grow(self):
        folds = list(rolling_origin_purged_splits(self.frame))
        self.assertLess(len(folds[0][0]), len(folds[1][0]))
        self.assertLess(len(folds[1][0]), len(folds[2][0]))

    def test_rejects_invalid_test_fraction(self):
        with self.assertRaises(ValueError):
            list(rolling_origin_purged_splits(self.frame, test_fraction=0))
