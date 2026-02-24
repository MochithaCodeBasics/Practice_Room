"""
Validator for Question 4: SVM with SMOTE (Imbalanced Classification)
"""
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score
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
TARGET_COLUMN = 'quality'
REQUIRED_METRICS = ['f1', 'minority_ratio_after']
METRIC_THRESHOLDS = {
    'f1': {'min': 0.70, 'valid_range': (0, 1)},
    'minority_ratio_after': {'min': 0.9,'max':1.1}
}
PERFORMANCE_THRESHOLDS = {'excellent': 0.80, 'good': 0.70}
MAX_LEAKAGE_GAP = 0.15


def validate(user_module) -> str:
    """Validate user's solution for Question 4."""
    folder_path = os.path.dirname(__file__)
    try:
        
        # 1. Run main() to get model and result
        try:
            result = user_module.main()
            if not isinstance(result, tuple):
                 return "❌ main() must return a tuple (e.g., (scaler, model, result) or (model, result))"
            
            warning = ""
            if len(result) == 3:
                scaler, model, your_result = result
            elif len(result) == 2:
                model, your_result = result
                scaler = None
                warning = "⚠️ Note: Using (model, result) signature. Assuming no scaling was applied.\n"
            else:
                return f"❌ main() returns {len(result)} items, but 2 or 3 are expected."
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
        
        # 4. Check if SMOTE was applied
        if your_metrics['minority_ratio_after'] < METRIC_THRESHOLDS['minority_ratio_after']['min']:
            return f"⚠️ minority_ratio_after={your_metrics['minority_ratio_after']:.2f} seems low. Did you apply SMOTE[FAIL] \n   Hint: After SMOTE, minority ratio should be closer to 0.5"
        
        # 5. Check F1 threshold on your metrics
        error = check_metric_threshold(
            'f1', your_metrics['f1'],
            min_val=METRIC_THRESHOLDS['f1']['min'],
            valid_range=METRIC_THRESHOLDS['f1']['valid_range']
        )
        if error:
            return f"{error} (Your result)"
        
        # 6. Load hidden test data
        error, X_test, y_test = load_hidden_test_data(folder_path, TARGET_COLUMN)
        if error:
            return error
        if scaler is not None:
            try:
                X_test = scaler.transform(X_test)
            except Exception as e:
                return f"❌ Scaler.transform() failed on test data: {str(e)}"
        # 7. Get predictions on hidden data
        try:
            y_pred = model.predict(X_test)
        except Exception as e:
            return f"❌ model.predict() failed on test data: {str(e)}"
        
        # 8. Calculate test metrics ourselves
        test_metrics = {
            'f1': f1_score(y_test, y_pred, pos_label=1, zero_division=0)
        }
        
        # 9. Check thresholds on test metrics
        error = check_metric_threshold(
            'f1', test_metrics['f1'],
            min_val=METRIC_THRESHOLDS['f1']['min'],
            valid_range=METRIC_THRESHOLDS['f1']['valid_range']
        )
        if error:
            return f"{error} (Test data)\n   Hint: Check if SMOTE is applied correctly."
        
        # 10. Check for overfitting/data leakage
        f1_gap = your_metrics['f1'] - test_metrics['f1']
        if f1_gap > MAX_LEAKAGE_GAP:
            return f"⚠️ Possible overfitting/data leakage: Your F1={your_metrics['f1']:.4f} >> Test F1={test_metrics['f1']:.4f}"
        
        # 11. Success!
        perf_level = get_performance_level(test_metrics['f1'], PERFORMANCE_THRESHOLDS)
        return (
            f"{warning}"
            f"✅ Correct! Well done.\n"
            f"   ⚖️ Minority Ratio After SMOTE={your_metrics['minority_ratio_after']:.2f}\n"
            f"   📊 Your Metrics:  F1={your_metrics['f1']:.4f}\n"
            f"   📊 Test Metrics:  F1={test_metrics['f1']:.4f}\n"
            f"   🎯 {perf_level} handling of imbalanced data"
        )

    
    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"
