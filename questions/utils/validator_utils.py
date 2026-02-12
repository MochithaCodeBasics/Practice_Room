import pandas as pd
import numpy as np
import os
import math

def approx_equal(a: float, b: float, tol: float = 1e-2) -> bool:
    """Check if two floats are approximately equal within tolerance."""
    if pd.isna(a) and pd.isna(b):
        return True
    if pd.isna(a) or pd.isna(b):
        return False
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.01)

def check_result_structure(df, required_metrics):
    """Check if the provided result is a DataFrame with required metrics columns."""
    if not isinstance(df, pd.DataFrame):
        return f"[FAIL] Result must be a pandas DataFrame, got {type(df).__name__}"
    
    if 'metric' not in df.columns or 'value' not in df.columns:
        return "[FAIL] DataFrame must contain 'metric' and 'value' columns"
    
    # Check if all required metrics are present as rows in 'metric' column
    present_metrics = df['metric'].tolist()
    missing = [m for m in required_metrics if m not in present_metrics]
    if missing:
        return f"[FAIL] Missing required metrics in DataFrame: {', '.join(missing)}"
    
    return None

def extract_metrics(df, required_metrics):
    """Extract metric values into a dictionary from the ('metric', 'value') structure."""
    try:
        metrics = {}
        for m in required_metrics:
            rows = df[df['metric'] == m]
            if rows.empty:
                return f"[FAIL] Metric '{m}' not found in result", None
            val = rows['value'].iloc[0]
            metrics[m] = float(val)
        return None, metrics
    except Exception as e:
        return f"[FAIL] Error extracting metrics: {str(e)}", None

def check_metric_threshold(name, value, min_val=None, max_val=None, valid_range=None):
    """Validate a metric value against thresholds."""
    if valid_range:
        low, high = valid_range
        if value < low or value > high:
            return f"[FAIL] {name.upper()} value {value:.4f} is outside physically valid range [{low}, {high}]."
            
    if min_val is not None and value < min_val:
        return f"[FAIL] {name.upper()} {value:.4f} is too low (minimum required: {min_val})"
        
    if max_val is not None and value > max_val:
        return f"[FAIL] {name.upper()} {value:.4f} is too high (maximum allowed: {max_val})"
        
    return None

def load_hidden_test_data(folder_path, target_column):
    """Load the dataset to use as a hidden test set for validation."""
    data_path = os.path.join(folder_path, "data.csv")
    if not os.path.exists(data_path):
        return "System Error: hidden test data (data.csv) not found.", None, None
    
    try:
        df = pd.read_csv(data_path)
        # Standardize columns to lowercase/stripped
        df.columns = df.columns.str.lower().str.strip()
        
        if target_column not in df.columns:
             return f"System Error: target '{target_column}' not in dataset.", None, None
             
        y = df[target_column]
        X = df.drop(columns=[target_column])
        return None, X, y
    except Exception as e:
        return f"Error loading hidden data: {str(e)}", None, None

def get_performance_level(r2, thresholds):
    """Determine performance category based on R2 score or similar metric."""
    if r2 >= thresholds.get('excellent', 0.9):
        return "Excellent"
    elif r2 >= thresholds.get('good', 0.8):
        return "Good"
    else:
        return "Fair"
