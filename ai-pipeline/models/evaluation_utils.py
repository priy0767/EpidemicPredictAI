"""Leakage-aware chronological holdout utilities for the epidemic model pipeline."""

def chronological_purged_split(frame, split_fraction=0.8):
    """Split ordered samples and purge train labels reaching the test start.

    Required columns:
      - Date: timestamp when a feature row is available
      - Target_End_Date: timestamp when that row's forward target is fully known

    Rows must be sorted chronologically before calling this function.
    """
    if not 0 < split_fraction < 1:
        raise ValueError("split_fraction must be between 0 and 1")
    if "Date" not in frame or "Target_End_Date" not in frame:
        raise ValueError("frame must contain Date and Target_End_Date columns")
    if frame.empty:
        raise ValueError("frame must not be empty")
    if not frame["Date"].is_monotonic_increasing:
        raise ValueError("frame must be sorted by Date")

    split_position = int(len(frame) * split_fraction)
    if split_position <= 0 or split_position >= len(frame):
        raise ValueError("not enough rows for both train and test partitions")

    test_frame = frame.iloc[split_position:].copy()
    test_start = test_frame["Date"].min()
    pre_test = frame.iloc[:split_position]
    train_frame = pre_test[pre_test["Target_End_Date"] < test_start].copy()
    purged_count = len(pre_test) - len(train_frame)

    if train_frame.empty or test_frame.empty:
        raise ValueError("purging left an empty train or test partition")
    if not (train_frame["Target_End_Date"] < test_start).all():
        raise AssertionError("training target window overlaps the test period")

    return train_frame, test_frame, purged_count


def rolling_origin_purged_splits(frame, start_fractions=(0.5, 0.6, 0.7), test_fraction=0.1):
    """Yield expanding-window train/test folds with forward-label purging.

    Each test window is a non-overlapping chronological slice. Training rows
    always precede the test window and their target windows must end before its
    first feature date. Fractions are based on row positions after sorting.
    """
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be between 0 and 1")
    if "Date" not in frame or "Target_End_Date" not in frame:
        raise ValueError("frame must contain Date and Target_End_Date columns")
    if frame.empty:
        raise ValueError("frame must not be empty")
    if not frame["Date"].is_monotonic_increasing:
        raise ValueError("frame must be sorted by Date")

    previous_end = 0
    for start_fraction in start_fractions:
        if not 0 < start_fraction < 1 or start_fraction + test_fraction > 1:
            raise ValueError("each fold must fit within the dataset")
        start_position = int(len(frame) * start_fraction)
        end_position = min(len(frame), int(len(frame) * (start_fraction + test_fraction)))
        if start_position <= previous_end or end_position <= start_position:
            raise ValueError("rolling-origin folds must be ordered and non-empty")

        test_frame = frame.iloc[start_position:end_position].copy()
        test_start = test_frame["Date"].min()
        pre_test = frame.iloc[:start_position]
        train_frame = pre_test[pre_test["Target_End_Date"] < test_start].copy()
        purged_count = len(pre_test) - len(train_frame)

        if train_frame.empty:
            raise ValueError("purging left an empty rolling-origin training partition")
        if not (train_frame["Target_End_Date"] < test_start).all():
            raise AssertionError("rolling-origin training labels overlap the test period")

        yield train_frame, test_frame, purged_count
        previous_end = end_position
