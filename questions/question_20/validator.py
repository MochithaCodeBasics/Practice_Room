"""
Validator for Question 5: Random Forest
"""
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from _validator_utils import (
    check_result_structure,
    extract_metrics,
    check_metric_threshold,
    load_hidden_test_data,
    get_performance_level
)

# ================================
# Question-Specific Configuration
# ================================
TARGET_COLUMN = 'repeat_purchase'
REQUIRED_METRICS = ['accuracy', 'f1']
METRIC_THRESHOLDS = {
    'accuracy': {'min': 0.8, 'valid_range': (0, 1)},
    'f1': {'min': 0.75, 'valid_range': (0, 1)}
}
PERFORMANCE_THRESHOLDS = {'excellent': 0.9, 'good': 0.8}
MAX_LEAKAGE_GAP = 0.10


def validate(user_module) -> str:
    """Validate user's solution for Question 5."""
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
        
        # 6. Get predictions on hidden data
        try:
            y_pred = model.predict(X_test)
        except Exception as e:
            return f"❌ model.predict() failed on test data: {str(e)}"
        
        # 7. Calculate test metrics ourselves
        test_metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred, pos_label=1, zero_division=0)
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
        
        # 9. Check for overfitting/data leakage
        acc_gap = your_metrics['accuracy'] - test_metrics['accuracy']
        if acc_gap > MAX_LEAKAGE_GAP:
            return f"⚠️ Possible overfitting/data leakage: Your Accuracy={your_metrics['accuracy']:.4f} >> Test Accuracy={test_metrics['accuracy']:.4f}"
        f1_gap = your_metrics['f1'] - test_metrics['f1']
        if f1_gap > MAX_LEAKAGE_GAP:
            return f"⚠️ Possible overfitting/data leakage: Your F1={your_metrics['f1']:.4f} >> Test F1={test_metrics['f1']:.4f}"
        
        # 10. Success!
        perf_level = get_performance_level(test_metrics['accuracy'], PERFORMANCE_THRESHOLDS)
        return (
            f"✅ Correct! Well done.\n"
            f"   📊 Your Metrics:  Accuracy={your_metrics['accuracy']:.4f}, F1={your_metrics['f1']:.4f}\n"
            f"   📊 Test Metrics:  Accuracy={test_metrics['accuracy']:.4f}, F1={test_metrics['f1']:.4f}\n"
            f"   🎯 {perf_level} performance"
        )
    
    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"
