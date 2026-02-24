"""
Validator for Question 2: PyTorch Binary Classification
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
REQUIRED_METRICS = ['accuracy', 'f1']
METRIC_THRESHOLDS = {
    'accuracy': {'min': 0.70, 'valid_range': (0, 1)},
    'f1': {'min': 0.65, 'valid_range': (0, 1)}
}
PERFORMANCE_THRESHOLDS = {'excellent': 0.82, 'good': 0.75}


def validate(user_module, user_code=None, user_df=None) -> str:
    """
    Validate user's solution for Question 2.
    
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
                    return "[FAIL] main() must return a pandas DataFrame. Return only the result DataFrame."
            except Exception as e:
                return f"[FAIL] main() failed: {str(e)}"
        # 2. Validate Implementation (e.g., check for PyTorch usage)
        if user_code is not None:
            if 'import torch' not in user_code and 'from torch' not in user_code:
                return "[FAIL] Your implementation should use PyTorch for building the neural network."
            if "nn.Module" not in user_code and "torch.nn" not in user_code and "sequential" not in user_code:
                return "[FAIL] Define your neural network by creating a class that inherits from nn.Module or using nn.Sequential."
        # 3. Validate result structure
        error = check_result_structure(result, REQUIRED_METRICS)
        if error:
            return error
        
        # 4. Extract metrics
        error, metrics = extract_metrics(result, REQUIRED_METRICS)
        if error:
            return error
        
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
                if metric_name == 'accuracy' and metrics[metric_name] < 0.60:
                    return f"{error}\n[HINT] Low accuracy. Check your model architecture and training loop. Try more epochs or adjust learning rate."
                elif metric_name == 'f1' and metrics['f1'] < 0.60:
                    return f"{error}\n[HINT] Low F1 score. Ensure you're using stratify=y in train_test_split and appropriate loss function."
                return error
        
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
                        return f"[FAIL] Hidden Test Case Failed: {error}"
                    
                # Check thresholds (slightly relaxed for hidden data)
                if hidden_metrics['accuracy'] < 0.65:
                    return f"[FAIL] Hidden Test Case Failed: Accuracy {hidden_metrics['accuracy']:.4f} is too low on hidden data (expected > 0.65)."
                if hidden_metrics['f1'] < 0.60:
                    return f"[FAIL] Hidden Test Case Failed: F1 Score {hidden_metrics['f1']:.4f} is too low on hidden data (expected > 0.60)."

                if (
                    abs(float(hidden_metrics['accuracy']) - float(metrics['accuracy'])) < 1e-12 and
                    abs(float(hidden_metrics['f1']) - float(metrics['f1'])) < 1e-12
                ):
                    return "[FAIL] Hidden Test Case Failed: Output appears hardcoded (public and hidden metrics are identical)."
        except Exception as e:
            return f"[FAIL] Hidden Test Case Execution Failed: {str(e)}"

        # 7. Success!
        perf_level = get_performance_level(metrics['accuracy'], PERFORMANCE_THRESHOLDS)
        return (
            f"[PASS] Correct! Your PyTorch neural network works!\n"
            f"   [INFO] Accuracy: {metrics['accuracy']:.4f}\n"
            f"   [INFO] F1 Score: {metrics['f1']:.4f}\n"
            f"   [INFO] {perf_level} performance\n"
            f"   [INFO] Great job implementing a PyTorch binary classifier!"
        )
    
    except Exception as e:
        return f"[WARN] Validation error: {str(e)}"
