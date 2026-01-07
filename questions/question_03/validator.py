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
    2. Values match numpy/pandas within tolerance
    """
    try:
        # Check if function exists
        if not hasattr(user_module, "summarize_spend"):
            return "❌ Function `summarize_spend` is not defined."

        func = user_module.summarize_spend

        # Check if it's callable
        if not callable(func):
            return "❌ `summarize_spend` is not callable."

        # Create test data
        test_series = pd.Series([1200, 1500, 1800, 2000, 1500, 2200, 1900, 1700, np.nan, 1600])
        
        result = func(test_series)

        # Check if result is a dictionary
        if not isinstance(result, dict):
            return f"❌ Expected dict, got {type(result).__name__}"

        # Required keys
        required_keys = ['mean', 'median', 'mode', 'std', 'variance', 'min', 'max', 'Q1', 'Q3', 'IQR']
        
        for key in required_keys:
            if key not in result:
                return f"❌ Missing required key: `{key}`"

        # Compute expected values (ignoring NaN)
        clean_series = test_series.dropna()
        
        expected = {
            'mean': clean_series.mean(),
            'median': clean_series.median(),
            'mode': clean_series.mode().iloc[0] if len(clean_series.mode()) > 0 else None,
            'std': clean_series.std(),
            'variance': clean_series.var(),
            'min': clean_series.min(),
            'max': clean_series.max(),
            'Q1': clean_series.quantile(0.25),
            'Q3': clean_series.quantile(0.75),
            'IQR': clean_series.quantile(0.75) - clean_series.quantile(0.25)
        }

        # Validate each value
        for key in required_keys:
            if not _approx_equal(result[key], expected[key]):
                return f"❌ Value mismatch for `{key}`: expected {expected[key]:.2f}, got {result[key]}"

        # Test Case 2: Series without NaN
        test_series2 = pd.Series([100, 200, 300, 400, 500])
        result2 = func(test_series2)
        
        if not isinstance(result2, dict):
            return "❌ Function should return dict for all valid inputs."

        expected_mean2 = 300.0
        if not _approx_equal(result2['mean'], expected_mean2):
            return f"❌ Test case 2: mean mismatch, expected {expected_mean2}, got {result2['mean']}"

        return "✅ Correct! Statistical summary is valid."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"
