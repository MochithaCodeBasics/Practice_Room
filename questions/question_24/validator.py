"""
Validator for Question 3: PyTorch Regression with Normalization
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
REQUIRED_METRICS = ['r2','mse']
METRIC_THRESHOLDS = {
    'r2': {'min': 0.60, 'valid_range': (-np.inf, 1)},  # R² can be negative
    'mse': {'max': 10000000000, 'valid_range': (0, np.inf)}  # 10 billion max
   
}
PERFORMANCE_THRESHOLDS = {'excellent': 0.75, 'good': 0.65}


def validate(user_module,user_code=None, user_df=None) -> str:
    """
    Validate user's solution for Question 3.
    
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
                    return "❌ main() must return a pandas DataFrame. Return only the result DataFrame."
            except Exception as e:
                return f"❌ main() failed: {str(e)}"
        # 2. Validate Implementation (e.g., check for PyTorch usage)
        if user_code is not None:
            if 'import torch' not in user_code and 'from torch' not in user_code:
                return "❌ Your implementation should use PyTorch for building the neural network."
            if "nn.Module" not in user_code and "torch.nn" not in user_code and "sequential" not in user_code:
                return "❌ Define your neural network by creating a class that inherits from nn.Module or using nn.Sequential."
            if "StandardScaler" not in user_code and "MinMaxScaler" not in user_code and "normalize" not in user_code and 'BatchNorm' not in user_code:
                return "❌ Normalize/standardize the features using StandardScaler or MinMaxScaler for better performance."
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
                if metric_name == 'r2' and metrics[metric_name] < 0.30:
                    return f"{error}\n💡 Hint: Very low R². Did you normalize/standardize features[INFO] Features have vastly different scales."
                elif metric_name == 'mse' and metrics[metric_name] > 5000000000:
                    return f"{error}\n💡 Hint: Very high MSE. Check if you denormalized predictions or if model trained properly."
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
                    return f"❌ Hidden Test Case Failed: {error}"
                    
                # Check thresholds (slightly relaxed for hidden data)
                if hidden_metrics['r2'] < 0.55:
                        return f"[FAIL] Hidden Test Case Failed: R2 Score {hidden_metrics['r2']:.4f} is too low on hidden data (expected > 0.55)."
                if (
                    abs(float(hidden_metrics['r2']) - float(metrics['r2'])) < 1e-12 and
                    abs(float(hidden_metrics['mse']) - float(metrics['mse'])) < 1e-6
                ):
                    return "[FAIL] Hidden Test Case Failed: Output appears hardcoded (public and hidden metrics are identical)."
        except Exception as e:
            return f"[FAIL] Hidden Test Case Execution Failed: {str(e)}"

        # 7. Success!
        perf_level = get_performance_level(metrics['r2'], PERFORMANCE_THRESHOLDS)
        return (
            f"[PASS] Correct! Your regression model works!\n"
            f"   [INFO] R2 Score: {metrics['r2']:.4f}\n"
            f"   [INFO] MSE: {metrics['mse']:,.0f}\n"
            f"   [INFO] {perf_level} performance\n"
            f"   [INFO] Great job implementing regression with normalization!"
        )
    
    except Exception as e:
        return f"[WARN] Validation error: {str(e)}"

