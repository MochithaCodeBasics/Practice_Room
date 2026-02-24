import pandas as pd
import numpy as np
import math


def _approx_equal(a, b, tol=1e-2):
    """Check if two values are approximately equal."""
    if pd.isna(a) and pd.isna(b):
        return True
    if pd.isna(a) or pd.isna(b):
        return False
    return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=tol)


def validate(user_module) -> str:
    """
    Validates the summarize_spend function.

    Checks:
    1. All required keys are present
    2. Values match pandas/numpy results within tolerance
    """
    try:
        if not hasattr(user_module, "summarize_spend"):
            return "âŒ Function `summarize_spend` is not defined."

        func = user_module.summarize_spend
        if not callable(func):
            return "âŒ `summarize_spend` is not callable."

        test_series = pd.Series([1200, 1500, 1800, 2000, 1500, 2200, 1900, 1700, np.nan, 1600])
        result = func(test_series)

        if not isinstance(result, dict):
            return f"âŒ Expected dict, got {type(result).__name__}"

        required_keys = ["mean", "median", "mode", "std", "variance", "min", "max", "Q1", "Q3", "IQR"]
        for key in required_keys:
            if key not in result:
                return f"âŒ Missing required key: `{key}`"

        clean_series = test_series.dropna()
        expected = {
            "mean": clean_series.mean(),
            "median": clean_series.median(),
            "mode": clean_series.mode().iloc[0] if len(clean_series.mode()) > 0 else None,
            "std": clean_series.std(),
            "variance": clean_series.var(),
            "min": clean_series.min(),
            "max": clean_series.max(),
            "Q1": clean_series.quantile(0.25),
            "Q3": clean_series.quantile(0.75),
            "IQR": clean_series.quantile(0.75) - clean_series.quantile(0.25),
        }

        for key in required_keys:
            if not _approx_equal(result[key], expected[key]):
                return f"âŒ Value mismatch for `{key}`: expected {expected[key]:.2f}, got {result[key]}"

        # Hidden test 1: no NaN
        test_series2 = pd.Series([100, 200, 300, 400, 500])
        result2 = func(test_series2)
        if not isinstance(result2, dict):
            return "âŒ Hidden test: Function should return dict for all valid inputs."

        expected2 = {
            "mean": test_series2.mean(),
            "median": test_series2.median(),
            "mode": test_series2.mode().iloc[0],
            "std": test_series2.std(),
            "variance": test_series2.var(),
            "min": test_series2.min(),
            "max": test_series2.max(),
            "Q1": test_series2.quantile(0.25),
            "Q3": test_series2.quantile(0.75),
            "IQR": test_series2.quantile(0.75) - test_series2.quantile(0.25),
        }
        for key in required_keys:
            if key not in result2:
                return f"âŒ Hidden test: Missing key `{key}` in result."
            if not _approx_equal(result2[key], expected2[key]):
                return f"âŒ Hidden test: `{key}` mismatch, expected {expected2[key]:.2f}, got {result2[key]}"

        # Hidden test 2: repeated values (mode)
        test_series3 = pd.Series([10, 20, 20, 30, 30, 30, 40])
        result3 = func(test_series3)
        if not isinstance(result3, dict):
            return "âŒ Hidden test: Function should return dict for all valid inputs."
        if not _approx_equal(result3["mode"], 30):
            return f"âŒ Hidden test: mode mismatch, expected 30, got {result3['mode']}"

        return "âœ… Correct! All test cases passed successfully."

    except Exception as e:
        return f"âš ï¸ Validation error: {str(e)}"
