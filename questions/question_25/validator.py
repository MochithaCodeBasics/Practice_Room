"""
Validator for Question 4: Customer Churn with Dropout Regularization
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
REQUIRED_METRICS = ['train_accuracy', 'test_accuracy']
METRIC_THRESHOLDS = {
    'train_accuracy': {'min': 0.70, 'valid_range': (0, 1)},
    'test_accuracy': {'min': 0.70, 'valid_range': (0, 1)},
}
OVERFITTING_GAP_THRESHOLD = 0.10  # Max allowed gap between train and test accuracy
PERFORMANCE_THRESHOLDS = {'excellent': 0.80, 'good': 0.75}


def validate(user_module, user_code=None, user_df=None) -> str:
    """
    Validate user's solution for Question 4.
    
    Parameters
    ----------
    user_module : types.SimpleNamespace
        Module containing user's code (with main() function and other variables)
    user_df : pd.DataFrame, optional
        Pre-extracted DataFrame from user's output. If provided, skips calling main().
        If None, will call user_module.main() to get the result.
    user_code : str, optional
        User's source code for implementation verification (e.g., to check for dropout usage)
    
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
                    return "❌ main() must return a pandas DataFrame. Return only the result DataFrame."
            except Exception as e:
                return f"❌ main() failed: {str(e)}"
        # 2. Validate Implementation (e.g., check for PyTorch usage)
        if user_code is not None:
            if 'import torch' not in user_code and 'from torch' not in user_code:
                return "❌ Your implementation should use PyTorch for building the neural network."
            if 'Dropout' not in user_code and 'nn.Dropout' not in user_code and "dropout" not in user_code.lower():
                return "❌ Your implementation should include Dropout layers to reduce overfitting."
        # 3. Validate result structure
        error = check_result_structure(result, REQUIRED_METRICS)
        if error:
            return error
        
        # 4. Extract metrics
        error, metrics = extract_metrics(result, REQUIRED_METRICS)
        if error:
            return error
        metrics['overfitting_gap'] = metrics['train_accuracy'] - metrics['test_accuracy']
        # 5. Check metric thresholds
        for metric_name, thresholds in METRIC_THRESHOLDS.items():
            error = check_metric_threshold(
                metric_name, metrics[metric_name],
                min_val=thresholds.get('min'),
                max_val=thresholds.get('max'),
                valid_range=thresholds.get('valid_range')
            )
            if error:
                # Add helpful hints
                if metric_name == 'test_accuracy' and metrics[metric_name] < 0.65:
                    return f"{error}\n💡 Hint: Low test accuracy. Check categorical encoding and model architecture."
                return error
        
        # 6. Additional validation: Check if dropout was likely used
        if metrics['overfitting_gap'] > OVERFITTING_GAP_THRESHOLD:
            return (
                f"❌ Model is overfitting. Train accuracy is much higher than test accuracy.\n"
                f"   💡 Hint: Add dropout layers to reduce overfitting.\n"
                f"   💡 Ensure model.eval() is called before test evaluation."
            )
        
        # 6. Validate on hidden test data
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
                
                # Run main() again with hidden data
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
                    
                if not isinstance(hidden_result, pd.DataFrame):
                    return "[FAIL] Hidden Test Case Failed: main() must return a pandas DataFrame on hidden data."

                error = check_result_structure(hidden_result, REQUIRED_METRICS)
                if error:
                    return f"[FAIL] Hidden Test Case Failed: {error}"

                # Check metrics on hidden data
                error, hidden_metrics = extract_metrics(hidden_result, REQUIRED_METRICS)
                if error:
                    return f"❌ Hidden Test Case Failed: {error}"
                    
                # Check thresholds (slightly relaxed for hidden data)
                if hidden_metrics['test_accuracy'] < 0.68:
                        return f"❌ Hidden Test Case Failed: Test Accuracy {hidden_metrics['test_accuracy']:.4f} is too low on hidden data (expected > 0.68)."
                    
                hidden_gap = hidden_metrics['train_accuracy'] - hidden_metrics['test_accuracy']
                if hidden_gap > 0.15: # Relaxed gap for hidden data
                         return f"❌ Hidden Test Case Failed: Model is overfitting on hidden data (gap: {hidden_gap:.4f})."
                if (
                    abs(float(hidden_metrics['train_accuracy']) - float(metrics['train_accuracy'])) < 1e-12 and
                    abs(float(hidden_metrics['test_accuracy']) - float(metrics['test_accuracy'])) < 1e-12
                ):
                    return "[FAIL] Hidden Test Case Failed: Output appears hardcoded (public and hidden metrics are identical)."

        except Exception as e:
            return f"[FAIL] Hidden Test Case Execution Failed: {str(e)}"

        # 7. Success!
        perf_level = get_performance_level(metrics['test_accuracy'], PERFORMANCE_THRESHOLDS)
        return (
            f"[PASS] Correct! Your churn prediction model with dropout works!\n"
            f"   [INFO] Train Accuracy: {metrics['train_accuracy']:.4f}\n"
            f"   [INFO] Test Accuracy: {metrics['test_accuracy']:.4f}\n"
            f"   [INFO] {perf_level} performance\n"
            f"   [INFO] Great job implementing dropout regularization!"
        )
    
    except Exception as e:
        return f"[WARN] Validation error: {str(e)}"
           
