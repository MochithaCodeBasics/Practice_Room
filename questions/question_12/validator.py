"""
Validator for Question 1: Simple Linear Regression
"""
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_squared_error
import os
import sys

from validator_utils import (
    check_result_structure,
    extract_metrics,
    check_metric_threshold,
    load_hidden_test_data,
    get_performance_level
)

# ================================
# Question-Specific Configuration
# ================================
TARGET_COLUMN = 'sales'
FEATURE_COLUMNS = ['ad_spend']
REQUIRED_METRICS = ['mse', 'r2']
METRIC_THRESHOLDS = {
    'r2': {'min': 0.85, 'valid_range': (0, 1)},
    'mse': {'max': 50000000,'valid_range':(0,np.inf)}
}
PERFORMANCE_THRESHOLDS = {'excellent': 0.92, 'good': 0.85}
MAX_LEAKAGE_GAP = 0.10


def validate(user_module) -> str:
    """Validate user's solution for Question 1."""
    folder_path = os.path.dirname(__file__)
    try:
        
        # 1. Run main() to get model and result
        try:
            result = user_module.main()
            if not isinstance(result, tuple) or len(result) != 2:
                return "❌ main() must return (model, result) tuple"
            model, your_result = result
        except Exception as e:
            return f"❌ main() failed: {str(e)}"
        
        # 2. Validate result structure FIRST
        error = check_result_structure(your_result, REQUIRED_METRICS)
        if error:
            return error
        
        # 3. Extract your metrics
        error, your_metrics = extract_metrics(your_result, REQUIRED_METRICS)
        if error:
            return error
        
        # 4. Check thresholds on your metrics
        for metric_name, thresholds in METRIC_THRESHOLDS.items():
            error = check_metric_threshold(
                metric_name, your_metrics[metric_name],
                min_val=thresholds.get('min'),
                max_val=thresholds.get('max'),
                valid_range=thresholds.get('valid_range')
            )
            if error:
                return f"{error} (Your result)"
        
        # 5. Load hidden test data
        error, X_test, y_test = load_hidden_test_data(folder_path, TARGET_COLUMN)
        if error:
            return error
        X_test = X_test[FEATURE_COLUMNS]
        
        # 6. Get predictions on hidden data
        try:
            y_pred = model.predict(X_test)
        except Exception as e:
            return f"❌ model.predict() failed on test data: {str(e)}"
        
        # 7. Calculate test metrics ourselves
        test_metrics = {
            'r2': r2_score(y_test, y_pred),
            'mse': mean_squared_error(y_test, y_pred)
        }
        
        # 8. Check thresholds on test metrics
        for metric_name, thresholds in METRIC_THRESHOLDS.items():
            error = check_metric_threshold(
                metric_name, test_metrics[metric_name],
                min_val=thresholds.get('min'),
                max_val=thresholds.get('max'),
                valid_range=thresholds.get('valid_range')
            )
            if error:
                return f"{error} (Test data)"
        
        # 9. Check for overfitting/data leakage (your metrics much better than test)
        r2_gap = your_metrics['r2'] - test_metrics['r2']
        if r2_gap > MAX_LEAKAGE_GAP:
            return f"⚠️ Possible overfitting/data leakage: Your R²={your_metrics['r2']:.4f} >> Test R²={test_metrics['r2']:.4f}"
        
        # 10. Success!
        perf_level = get_performance_level(test_metrics['r2'], PERFORMANCE_THRESHOLDS)
        return (
            f"✅ Correct! Well done.\n"
            f"   📊 Your Metrics:  R²={your_metrics['r2']:.4f}, MSE={your_metrics['mse']:,.2f}\n"
            f"   📊 Test Metrics:  R²={test_metrics['r2']:.4f}, MSE={test_metrics['mse']:,.2f}\n"
            f"   🎯 {perf_level} performance"
        )
    
    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"
