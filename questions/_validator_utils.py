import pandas as pd
import numpy as np
import os

def check_result_structure(your_result, required_metrics):
    """
    Checks if the result is a dictionary or DataFrame with required metrics.
    """
    # Handle Pandas DataFrame
    if isinstance(your_result, pd.DataFrame):
        required_cols = {'metric', 'value'}
        if not required_cols.issubset(your_result.columns):
            return f"❌ DataFrame missing required columns: {required_cols - set(your_result.columns)}"
        
        # Check if all required metrics are present in the 'metric' column
        present_metrics = set(your_result['metric'].astype(str).str.lower().values)
        missing_metrics = [m for m in required_metrics if m not in present_metrics]
        if missing_metrics:
            return f"❌ Result DataFrame is missing metrics: {', '.join(missing_metrics)}"
        return None

    # Handle Dictionary
    if not isinstance(your_result, dict):
        return f"❌ Expected result to be a dictionary or DataFrame, got {type(your_result).__name__}"
    
    missing_metrics = [m for m in required_metrics if m not in your_result]
    if missing_metrics:
        return f"❌ Result dictionary is missing metrics: {', '.join(missing_metrics)}"
    
    return None

def extract_metrics(your_result, required_metrics):
    """
    Extracts metrics from the result dictionary or DataFrame.
    """
    metrics = {}
    
    # Handle DataFrame conversion
    if isinstance(your_result, pd.DataFrame):
        try:
            # Create a dict mapping metric -> value
            # Normalize metric names to lowercase
            df_normalized = your_result.copy()
            df_normalized['metric'] = df_normalized['metric'].astype(str).str.lower()
            
            for m in required_metrics:
                rows = df_normalized[df_normalized['metric'] == m]
                if rows.empty:
                     return f"❌ Metric '{m}' not found in DataFrame", None
                val = rows.iloc[0]['value']
                if not isinstance(val, (int, float, np.number)):
                     return f"❌ Metric '{m}' must be a number, got {type(val).__name__}", None
                metrics[m] = float(val)
            return None, metrics
        except Exception as e:
            return f"❌ Error extracting metrics from DataFrame: {str(e)}", None

    # Handle Dictionary
    for m in required_metrics:
        val = your_result.get(m)
        if not isinstance(val, (int, float, np.number)):
             return f"❌ Metric '{m}' must be a number, got {type(val).__name__}", None
        metrics[m] = float(val)
    return None, metrics

def check_metric_threshold(metric_name, value, min_val=None, max_val=None, valid_range=None):
    """
    Checks if a metric value is within acceptable bounds.
    """
    label = metric_name.upper()
    
    if valid_range:
        if not (valid_range[0] <= value <= valid_range[1]):
            return f"❌ {label} {value} is outside valid range {valid_range}"

    # Allow slight tolerance
    tolerance = 1e-5

    if min_val is not None:
        if value < min_val - tolerance:
            return f"❌ {label} {value:.4f} is too low (expected >= {min_val})"
            
    if max_val is not None:
        if value > max_val + tolerance:
            return f"❌ {label} {value:.4f} is too high (expected <= {max_val})"
            
    return None

def load_hidden_test_data(folder_path, target_column):
    """
    Loads hidden test data from the question folder.
    """
    hidden_data_path = os.path.join(folder_path, "hidden_test_data.csv")
    if not os.path.exists(hidden_data_path):
        return "⚠️ hidden_test_data.csv not found. Please upload it.", None, None
        
    try:
        df = pd.read_csv(hidden_data_path)
        # normalize columns
        df.columns = df.columns.str.lower().str.strip()
        
        if target_column not in df.columns:
             return f"❌ hidden_test_data.csv missing target column '{target_column}'", None, None
             
        X_test = df.drop(columns=[target_column])
        y_test = df[target_column]
        return None, X_test, y_test
    except Exception as e:
        return f"❌ Failed to load hidden test data: {str(e)}", None, None

def get_performance_level(r2_score, thresholds):
    """
    Returns a performance level label based on R2 score.
    """
    if r2_score > thresholds.get('excellent', 0.9):
        return "Excellent"
    if r2_score > thresholds.get('good', 0.8):
        return "Good"
    return "Adequate"
