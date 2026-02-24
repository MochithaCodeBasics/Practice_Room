"""
Validator for Question 5: Hyperparameter Tuning for Multi-class Classification
"""
import pandas as pd
import numpy as np
import os
import sys
import builtins


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from _validator_utils import (
    check_result_structure,
    extract_metrics,
    check_metric_threshold,
    get_performance_level
)

# ================================
# Question-Specific Configuration
# ================================
HYPERPARAMETER_COLUMNS = ['learning_rate', 'hidden_size']
METRICS_COLUMNS = ['accuracy', 'macro_f1', 'is_best']
REQUIRED_COLUMNS = HYPERPARAMETER_COLUMNS + METRICS_COLUMNS
MINIMUM_COMBINATIONS = 6  # At least 2 learning rates × 3 hidden sizes
METRIC_THRESHOLDS = {
    'best_accuracy': {'min': 0.70, 'valid_range': (0, 1)},
    'best_macro_f1': {'min': 0.68, 'valid_range': (0, 1)}
}
PERFORMANCE_THRESHOLDS = {'excellent': 0.80, 'good': 0.75}


def validate(user_module,user_code=None, user_df=None) -> str:
    """
    Validate user's solution for Question 5.
    
    Parameters
    ----------
    user_module : types.SimpleNamespace
        Module containing user's code (with main() function and other variables)
    user_df : pd.DataFrame, optional
        Pre-extracted DataFrame from user's output. If provided, skips calling main().
        If None, will call user_module.main() to get the result.
    user_code : str, optional
        User's source code for implementation verification
    
    Returns
    -------
    str
        Validation message with success/failure feedback
    """
    try:
        # 1. Get result DataFrame (from user_df or by calling main())
        if user_df is not None:
            result = user_df
        else:
            try:
                result = user_module.main()
                if not isinstance(result, pd.DataFrame):
                    return "❌ main() must return a pandas DataFrame with hyperparameter tuning results."
            except Exception as e:
                return f"❌ main() failed: {str(e)}"
        
        # 2. Validate DataFrame structure
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in result.columns]
        if missing_cols:
            return f"❌ Result DataFrame missing columns: {missing_cols}\n   Required: {REQUIRED_COLUMNS}"
        
        # 3. Check if enough combinations were tested
        if len(result) < MINIMUM_COMBINATIONS:
            for col in HYPERPARAMETER_COLUMNS:
                if result[col].nunique() < 2:
                    return (
                        f"❌ Not enough variety in '{col}'. Only {result[col].nunique()} unique values found.\n"
                        f"   💡 Hint: Test at least 2 different values for '{col}'"
                    )
            return (
                f"❌ Only {len(result)} hyperparameter combinations tested.\n"
                f"   Minimum required: {MINIMUM_COMBINATIONS}\n"
                f"   💡 Hint: Test at least 3 learning_rates × 2+ hidden_sizes"
            )
        
        # 4. Validate is_best column
        best_count = (result['is_best'] == 1).sum()
        if best_count == 0:
            return "❌ No combination marked as best (is_best=1). Mark the combination with highest macro_f1."
        if best_count > 1:
            return f"❌ Multiple combinations marked as best ({best_count}). Only mark ONE combination with is_best=1."
        
        # 5. Extract best metrics
        best_row = result[result['is_best'] == 1].iloc[0]
        best_metrics = {
            'best_accuracy': best_row['accuracy'],
            'best_macro_f1': best_row['macro_f1'],
            'best_lr': best_row['learning_rate'],
            'best_hidden_size': best_row['hidden_size']
        }
        
        # 6. Validate that best is actually the best macro_f1
        max_macro_f1 = result['macro_f1'].max()
        if abs(best_metrics['best_macro_f1'] - max_macro_f1) > 0.001:
            return (
                f"❌ is_best marked incorrectly.\n"
                f"   Marked best: macro_f1={best_metrics['best_macro_f1']:.4f}\n"
                f"   Actual best: macro_f1={max_macro_f1:.4f}\n"
                f"   💡 Hint: Mark the combination with the HIGHEST macro_f1"
            )
        
        # 7. Check metric ranges
        for metric_name, thresholds in METRIC_THRESHOLDS.items():
            value = best_metrics[metric_name]
            valid_range = thresholds['valid_range']
            if not (valid_range[0] <= value <= valid_range[1]):
                return f"❌ {metric_name}={value:.4f} is out of valid range {valid_range}"
            
            min_val = thresholds.get('min')
            if min_val and value < min_val:
                if metric_name == 'best_macro_f1':
                    return (
                        f"❌ Best macro_f1={value:.4f} < {min_val}\n"
                        f"   💡 Hint: Try different hyperparameters or increase training epochs"
                    )
                return f"❌ {metric_name}={value:.4f} < {min_val}"
        
        # 9. Validate on hidden test data
        try:
            # Load hidden test data
            data_file = os.path.join(os.path.dirname(__file__), 'hidden_test_case.csv')
            if os.path.exists(data_file):
                hidden_df = pd.read_csv(data_file)
                
                # Check if user_module has 'data' variable to inject
                # We inject into BOTH to be sure (builtins for students using builtin 'data', 
                # and user_module for students who explicitly copied it)
                original_module_data = getattr(user_module, 'data', None)
                original_builtin_data = getattr(builtins, 'data', None)
                
                # Inject hidden data
                user_module.data = hidden_df
                builtins.data = hidden_df
                
                # Run main() again with hidden data (grid search on hidden data)
                try:
                    hidden_result = user_module.main()
                except Exception as e:
                    # Restore data before raising
                    if original_module_data is not None:
                        user_module.data = original_module_data
                    if original_builtin_data is not None:
                        builtins.data = original_builtin_data
                    raise e
                
                # Restore original data
                if original_module_data is not None:
                    user_module.data = original_module_data
                if original_builtin_data is not None:
                    builtins.data = original_builtin_data
                    
                # Check if hidden_result is valid and get best F1
                if not isinstance(hidden_result, pd.DataFrame) or 'macro_f1' not in hidden_result.columns:
                         return "❌ Hidden Test Case Failed: main() did not return valid results on hidden data."
                    
                missing_hidden_cols = [col for col in REQUIRED_COLUMNS if col not in hidden_result.columns]
                if missing_hidden_cols:
                         return f"[FAIL] Hidden Test Case Failed: Missing columns on hidden data: {missing_hidden_cols}."
                if len(hidden_result) < MINIMUM_COMBINATIONS:
                         return "[FAIL] Hidden Test Case Failed: Not enough hyperparameter combinations tested on hidden data."

                max_hidden_f1 = hidden_result['macro_f1'].max()
                    
                # Check threshold on hidden data
                if max_hidden_f1 < 0.65:
                        return f"❌ Hidden Test Case Failed: Best Macro F1 {max_hidden_f1:.4f} is too low on hidden data (expected > 0.65)."
                if hidden_result.equals(result):
                    return "[FAIL] Hidden Test Case Failed: Output appears hardcoded (public and hidden results are identical)."
        except Exception as e:
            return f"[FAIL] Hidden Test Case Execution Failed: {str(e)}"

        # 10. Success!
        perf_level = get_performance_level(best_metrics['best_macro_f1'], PERFORMANCE_THRESHOLDS)
        return (
            f"[PASS] Correct! Your hyperparameter tuning works!\n"
            f"   [INFO] Combinations tested: {len(result)}\n"
            f"   [INFO] Best Hyperparameters:\n"
            f"      - Learning Rate: {best_metrics['best_lr']}\n"
            f"      - Hidden Size: {int(best_metrics['best_hidden_size'])}\n"
            f"   [INFO] Best Performance:\n"
            f"      - Accuracy: {best_metrics['best_accuracy']:.4f}\n"
            f"      - Macro F1: {best_metrics['best_macro_f1']:.4f}\n"
            f"   [INFO] {perf_level} performance\n"
            f"   [INFO] Great job systematically testing hyperparameters!"
        )
    
    except Exception as e:
        return f"[WARN] Validation error: {str(e)}"

